"""
Tamarin Rule Generator - Code Generator Engine
Combines parser and templates to generate complete Tamarin models.
"""

import os
from typing import Optional
from .parser import Protocol, ProtocolParser, Role
from .templates import TamarinTemplates


class TamarinGenerator:
    """
    Main code generator that produces complete Tamarin models (.spthy files)
    from protocol JSON definitions.
    """
    
    def __init__(self, protocol: Optional[Protocol] = None):
        self.protocol = protocol
        self.role_map = {}
        if protocol:
            self.role_map = {r.name: r for r in protocol.roles}
    
    def load_protocol(self, json_path: str) -> Protocol:
        """Load protocol from JSON file."""
        parser = ProtocolParser(json_path)
        self.protocol = parser.load_from_file(json_path)
        self.role_map = {r.name: r for r in self.protocol.roles}
        
        # Validate
        errors = parser.validate()
        if errors:
            print("⚠️  Validation warnings:")
            for err in errors:
                print(f"   - {err}")
        
        return self.protocol
    
    def generate(self) -> str:
        """
        Generate complete Tamarin model from loaded protocol.
        """
        if not self.protocol:
            raise ValueError("No protocol loaded. Call load_protocol() first.")
        
        output = []
        
        # 1. Theory Header
        output.append(TamarinTemplates.theory_header(self.protocol.name))
        
        # 2. Builtins
        output.append(TamarinTemplates.builtins_section(self.protocol.builtins))
        
        # 3. PKI Setup Rules
        output.append(TamarinTemplates.register_keys_rule(self.protocol.roles))
        
        # 4. Adversary Rules
        output.append(TamarinTemplates.get_public_key_rule())
        output.append(TamarinTemplates.reveal_ltk_rule())
        
        # 5. Protocol Execution Rules
        output.append("\n// ========== Protocol Execution ==========")
        
        for step in self.protocol.steps:
            # Generate sender rule
            sender_rule = TamarinTemplates.sender_rule(step, self.role_map)
            output.append(sender_rule)
            
            # Generate receiver rule
            receiver_rule = TamarinTemplates.receiver_rule(step, self.role_map)
            output.append(receiver_rule)
        
        # 6. Security Properties (Lemmas)
        if self.protocol.security_properties:
            output.append("\n// ========== Security Properties ==========")
            
            for prop in self.protocol.security_properties:
                if prop.type == "authentication":
                    output.append(TamarinTemplates.authentication_lemma(
                        self.protocol.name
                    ))
                elif prop.type == "secrecy":
                    if "otp" in prop.name.lower():
                        output.append(TamarinTemplates.otp_secrecy_lemma())
                    else:
                        output.append(TamarinTemplates.secrecy_lemma(
                            self.protocol.name
                        ))
        
        # 7. Theory Footer
        output.append(TamarinTemplates.theory_footer())
        
        return "\n".join(output)
    
    def save_to_file(
        self,
        output_path: str,
        overwrite: bool = True
    ) -> str:
        """
        Generate and save Tamarin model to file.
        
        Args:
            output_path: Path to save .spthy file
            overwrite: Whether to overwrite existing file
        
        Returns:
            Path to generated file
        """
        if not output_path.endswith(".spthy"):
            output_path += ".spthy"
        
        if os.path.exists(output_path) and not overwrite:
            raise FileExistsError(f"File exists: {output_path}")
        
        content = self.generate()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Generated: {output_path}")
        return output_path
    
    def generate_with_comments(self) -> str:
        """
        Generate Tamarin model with detailed comments for documentation.
        """
        if not self.protocol:
            raise ValueError("No protocol loaded.")
        
        output = []
        
        # Header comment
        output.append(f"""// ============================================================
// Protocol: {self.protocol.name}
// Description: {self.protocol.description}
// Roles: {', '.join([r.name for r in self.protocol.roles])}
// Steps: {len(self.protocol.steps)}
// Security Properties: {len(self.protocol.security_properties)}
// ============================================================
""")
        
        output.append(self.generate())
        
        return "\n".join(output)
    
    def summary(self) -> str:
        """Generate a human-readable summary of the protocol."""
        if not self.protocol:
            return "No protocol loaded."
        
        lines = [
            f"\n{'='*60}",
            f"PROTOCOL: {self.protocol.name}",
            f"{'='*60}",
            f"\n📝 Description: {self.protocol.description}",
            f"\n👥 Roles ({len(self.protocol.roles)}):"
        ]
        
        for role in self.protocol.roles:
            key_info = ""
            if role.long_term_key:
                key_info = f" [LTK: {role.long_term_key}, PK: {role.public_key}]"
            lines.append(f"   - {role.name} ({role.type.value}){key_info}")
        
        lines.append(f"\n📊 Protocol Steps ({len(self.protocol.steps)}):")
        
        for step in self.protocol.steps:
            crypto = ""
            if step.crypto_ops:
                crypto = f" [{', '.join([op.value for op in step.crypto_ops])}]"
            fresh = ""
            if step.fresh:
                fresh = f" [fresh: {', '.join(step.fresh)}]"
            
            lines.append(
                f"   {step.id}. {step.from_role} → {step.to_role}{crypto}{fresh}"
            )
            if step.description:
                lines.append(f"      └─ {step.description}")
        
        if self.protocol.security_properties:
            lines.append(
                f"\n🔒 Security Properties ({len(self.protocol.security_properties)}):"
            )
            for prop in self.protocol.security_properties:
                lines.append(f"   - {prop.name} ({prop.type}): {prop.description}")
        
        lines.append(f"\n🛠️  Builtins: {', '.join(self.protocol.builtins)}")
        lines.append(f"{'='*60}\n")
        
        return "\n".join(lines)


def generate_from_file(
    input_json: str,
    output_spthy: str,
    with_comments: bool = True
) -> str:
    """
    Convenience function to generate Tamarin model from JSON file.
    
    Args:
        input_json: Path to protocol JSON file
        output_spthy: Path to output .spthy file
        with_comments: Include detailed comments
    
    Returns:
        Path to generated file
    """
    generator = TamarinGenerator()
    generator.load_protocol(input_json)
    
    print(generator.summary())
    
    if with_comments:
        content = generator.generate_with_comments()
    else:
        content = generator.generate()
    
    with open(output_spthy, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Generated: {output_spthy}")
    return output_spthy


if __name__ == "__main__":
    # Test with DigiLocker example
    generator = TamarinGenerator()
    generator.load_protocol("examples/digilocker_aadhar.json")
    
    print(generator.summary())
    
    content = generator.generate_with_comments()
    print("\n=== Generated Tamarin Model ===\n")
    print(content)
