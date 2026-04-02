"""
Tamarin Rule Generator - Template Module
Contains Tamarin rule templates based on DigiLocker modeling patterns.
"""

from typing import List, Optional
from .parser import Protocol, Role, ProtocolStep, CryptoOp


class TamarinTemplates:
    """Generates Tamarin rule templates from protocol components."""
    
    # ========== SETUP RULES ==========
    
    @staticmethod
    def theory_header(protocol_name: str) -> str:
        """Generate theory header."""
        return f"""theory {protocol_name}
begin"""
    
    @staticmethod
    def builtins_section(builtins: List[str]) -> str:
        """Generate builtins declaration."""
        builtins_str = ", ".join(builtins)
        return f"""
builtins: {builtins_str}
"""
    
    @staticmethod
    def register_keys_rule(roles: List[Role]) -> str:
        """
        Generate PKI setup rule.
        From DigiLocker slides - rule RegisterKeys (slide 39)
        """
        roles_with_keys = [r for r in roles if r.long_term_key and r.public_key]
        
        if not roles_with_keys:
            return ""
        
        fresh_ltk = ", ".join([f"Fr(~{r.long_term_key})" for r in roles_with_keys])
        
        ltk_facts = []
        pk_facts = []
        for r in roles_with_keys:
            ltk_facts.append(f"!Ltk(${r.name}, ~{r.long_term_key})")
            pk_facts.append(f"!Pk(${r.name}, pk(~{r.long_term_key}))")
        
        all_facts = ", ".join(ltk_facts + pk_facts)
        
        return f"""
// ========== PKI Setup ==========
rule RegisterKeys:
  [ {fresh_ltk} ]
  -->
  [ {all_facts} ]
"""
    
    @staticmethod
    def get_public_key_rule() -> str:
        """
        Generate adversary rule for accessing public keys.
        From DigiLocker slides - rule Get_pk (slide 40)
        """
        return """
// ========== Adversary Capabilities ==========
rule Get_pk:
  [ !Pk(A, pk) ]
  -->
  [ Out(pk) ]
"""
    
    @staticmethod
    def reveal_ltk_rule() -> str:
        """
        Generate adversary rule for key compromise.
        From DigiLocker slides - rule Reveal_ltk (slide 40)
        """
        return """
rule Reveal_ltk:
  [ !Ltk(A, ltk) ]
  --[]->
  [ Out(ltk) ]
"""
    
    # ========== PROTOCOL EXECUTION RULES ==========
    
    @staticmethod
    def sender_rule(step: ProtocolStep, role_map: dict) -> str:
        """
        Generate sender rule for a protocol step.
        Pattern from DigiLockerPrepare rule (slide 41)
        """
        rule_name = f"{step.from_role}_Send_Step{step.id}"
        
        # Build let bindings for message construction
        let_bindings = ""
        msg_var = "msg"
        if step.message and any(op in step.message for op in ["sign", "aenc", "h"]):
            let_bindings = f"let\n  msg = {step.message}\nin\n"
            msg_var = "msg"
        elif step.message:
            msg_var = step.message
        
        # Build precondition facts
        preconditions = []
        
        # Add fresh values
        for fresh_var in step.fresh:
            preconditions.append(f"Fr(~{fresh_var})")
        
        # Add long-term key facts for sender
        sender_role = role_map.get(step.from_role)
        if sender_role and sender_role.long_term_key:
            preconditions.append(f"!Ltk(${step.from_role}, {sender_role.long_term_key})")
        
        # Add public key facts for receiver
        receiver_role = role_map.get(step.to_role)
        if receiver_role and receiver_role.public_key:
            preconditions.append(f"!Pk(${step.to_role}, {receiver_role.public_key})")
        
        preconditions_str = ", ".join(preconditions) if preconditions else "[]"
        
        # Build action facts
        action_fact = ""
        if step.action_fact:
            action_params = [f"${step.from_role}", f"${step.to_role}"]
            for fresh_var in step.fresh[:3]:  # Limit to first 3 fresh values
                action_params.append(f"~{fresh_var}")
            action_fact = f"--[ {step.action_fact}({', '.join(action_params)}) ]->"
        else:
            action_fact = "-->"
        
        # Build conclusion
        conclusion = f"Out({msg_var})"
        
        return f"""
// Step {step.id}: {step.from_role} → {step.to_role}
rule {rule_name}:
  {let_bindings}[ {preconditions_str} ]
  {action_fact}
  [ {conclusion} ]
"""
    
    @staticmethod
    def receiver_rule(step: ProtocolStep, role_map: dict) -> str:
        """
        Generate receiver rule for a protocol step.
        Pattern from UIDAIProcess rule (slide 42) and DigiLockerVerify (slide 44)
        """
        rule_name = f"{step.to_role}_Recv_Step{step.id}"
        
        # Build let bindings for message deconstruction
        let_bindings = ""
        needs_decrypt = "aenc" in step.message and "sign" in step.message
        needs_verify = "sign" in step.message
        
        if needs_decrypt or needs_verify:
            let_bindings = "let\n  // Decrypt and verify incoming message\nin\n"
        
        # Build precondition facts
        preconditions = ["In(msg)"]
        
        # Add long-term key facts for receiver
        receiver_role = role_map.get(step.to_role)
        if receiver_role and receiver_role.long_term_key:
            preconditions.append(f"!Ltk(${step.to_role}, {receiver_role.long_term_key})")
        
        # Add public key facts for sender (for verification)
        sender_role = role_map.get(step.from_role)
        if sender_role and sender_role.public_key:
            preconditions.append(f"!Pk(${step.from_role}, {sender_role.public_key})")
        
        preconditions_str = ", ".join(preconditions)
        
        # Build action facts with verification
        action_fact = ""
        if needs_verify:
            action_fact = "--[\n  Eq(true, verify(sig, req, pk))\n]->"
        elif step.action_fact:
            action_fact = f"--[ {step.action_fact} ]->"
        else:
            action_fact = "-->"
        
        # Build conclusion
        conclusion_facts = []
        if step.action_fact:
            conclusion_facts.append(f"{step.action_fact}(${step.to_role}, ${step.from_role})")
        
        conclusion_str = ", ".join(conclusion_facts) if conclusion_facts else "[]"
        
        return f"""
rule {rule_name}:
  {let_bindings}[ {preconditions_str} ]
  {action_fact}
  [ {conclusion_str} ]
"""
    
    # ========== SECURITY PROPERTIES (LEMMAS) ==========
    
    @staticmethod
    def authentication_lemma(
        protocol_name: str,
        trust_fact: str = "TrustEstablished",
        response_fact: str = "UIDAIResponded"
    ) -> str:
        """
        Generate authentication property lemma.
        Based on DigiLocker security property (slide 45)
        """
        return f"""
// ========== Security Properties ==========
lemma authentication:
  "All D A tx #i.
    {trust_fact}(D, tx) @ i
    ==> Ex #j. {response_fact}(A, D, tx) @ j & j < i"
"""
    
    @staticmethod
    def secrecy_lemma(
        protocol_name: str,
        secret_fact: str = "SentAuth",
        secret_content: str = "xml"
    ) -> str:
        """
        Generate secrecy property lemma.
        """
        return f"""
lemma secrecy:
  "All A D {secret_content} #i.
    {secret_fact}(D, A, {secret_content}) @ i
    ==> not (Ex #k. K({secret_content}) @ k)"
"""
    
    @staticmethod
    def otp_secrecy_lemma() -> str:
        """
        Generate OTP secrecy lemma.
        """
        return f"""
lemma otp_secrecy:
  "All otp #i.
    UIDAIValidatedOTP(otp) @ i
    ==> not (Ex #j. K(otp) @ j)"
"""
    
    @staticmethod
    def theory_footer() -> str:
        """Generate theory footer."""
        return "\nend"


if __name__ == "__main__":
    # Test templates
    print("=== Theory Header ===")
    print(TamarinTemplates.theory_header("Test_Protocol"))
    
    print("\n=== Builtins ===")
    print(TamarinTemplates.builtins_section([
        "hashing", "asymmetric-encryption", "signing"
    ]))
    
    print("\n=== Register Keys ===")
    from .parser import Role, RoleType
    roles = [
        Role(name="D", type=RoleType.CLIENT, 
             long_term_key="ltkD", public_key="pkD"),
        Role(name="A", type=RoleType.AUTHORITY,
             long_term_key="ltkA", public_key="pkA")
    ]
    print(TamarinTemplates.register_keys_rule(roles))
    
    print("\n=== Get PK ===")
    print(TamarinTemplates.get_public_key_rule())
    
    print("\n=== Theory Footer ===")
    print(TamarinTemplates.theory_footer())
