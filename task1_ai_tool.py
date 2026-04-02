#!/usr/bin/env python3
"""
AI Tool for Generating Tamarin Rules from Protocol Diagrams
Task 1 Submission - IIT Roorkee

This is the MAIN ENTRY POINT that accepts protocol diagrams (images/PDF)
and generates formal Tamarin verification models.

Input: Protocol diagram (PNG, JPG, PDF)
Output: Tamarin rules (.spthy file)
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.diagram_parser import parse_diagram_file, DiagramParser
from src.ai_analyzer import AISemanticAnalyzer
from src.generator import TamarinGenerator


class DiagramToTamarinAI:
    """
    Complete AI pipeline for Task 1:
    
    Protocol Diagram (Image/PDF)
            ↓
    [Vision AI - OCR]
            ↓
    Extracted Protocol Structure
            ↓
    [LLM - Semantic Enhancement]
            ↓
    Enhanced Protocol JSON
            ↓
    [Template Generator]
            ↓
    Tamarin Rules (.spthy)
    """
    
    def __init__(self, api_key: str = None):
        self.diagram_parser = DiagramParser()
        self.ai_analyzer = AISemanticAnalyzer(api_key)
    
    def process_diagram(
        self,
        diagram_path: str,
        output_path: str,
        use_ai_enhancement: bool = True
    ) -> bool:
        """
        Process protocol diagram and generate Tamarin model.
        
        Args:
            diagram_path: Path to diagram image/PDF
            output_path: Path to save .spthy file
            use_ai_enhancement: Whether to use LLM for enhancement
        
        Returns:
            True if successful, False otherwise
        """
        print("=" * 70)
        print("AI TOOL FOR GENERATING TAMARIN RULES FROM PROTOCOL DIAGRAMS")
        print("Task 1 Submission - IIT Roorkee")
        print("=" * 70)
        
        # Step 1: Parse diagram (Vision AI / OCR)
        print(f"\n📷 Step 1: Parsing diagram: {diagram_path}")
        protocol_json = parse_diagram_file(diagram_path)
        
        if not protocol_json:
            print("❌ Failed to parse diagram")
            return False
        
        print(f"   ✅ Extracted: {protocol_json['protocol_name']}")
        print(f"   ✅ Roles: {[r['name'] for r in protocol_json['roles']]}")
        print(f"   ✅ Steps: {len(protocol_json['steps'])}")
        
        # Step 2: AI Enhancement (Optional but recommended)
        if use_ai_enhancement and self.ai_analyzer.is_available():
            print(f"\n🤖 Step 2: AI Semantic Enhancement...")
            protocol_json = self.ai_analyzer.enhance_protocol(protocol_json)
            print("   ✅ AI enhancement complete")
        elif use_ai_enhancement:
            print(f"\n⚠️  Step 2: AI not available (set OPENAI_API_KEY for enhancement)")
        else:
            print(f"\nℹ️  Step 2: Skipping AI enhancement")
        
        # Step 3: Generate Tamarin model
        print(f"\n📝 Step 3: Generating Tamarin rules...")
        
        try:
            generator = TamarinGenerator()
            generator.load_protocol_from_dict(protocol_json)
            
            content = generator.generate_with_comments()
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Generated: {output_path}")
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            return False
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"\nInput:  {diagram_path}")
        print(f"Output: {output_path}")
        print(f"\nTo verify with Tamarin:")
        print(f"  tamarin-prover {output_path}")
        print()
        
        return True
    
    def process_json(
        self,
        json_path: str,
        output_path: str,
        use_ai_enhancement: bool = True
    ) -> bool:
        """
        Process protocol JSON (alternative to diagram input).
        
        Args:
            json_path: Path to protocol JSON file
            output_path: Path to save .spthy file
            use_ai_enhancement: Whether to use LLM enhancement
        
        Returns:
            True if successful, False otherwise
        """
        print("=" * 70)
        print("AI TOOL FOR GENERATING TAMARIN RULES")
        print("Task 1 Submission - IIT Roorkee")
        print("=" * 70)
        
        # Load JSON
        print(f"\n📄 Step 1: Loading JSON: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            protocol_json = json.load(f)
        
        print(f"   ✅ Loaded: {protocol_json.get('protocol_name', 'Unknown')}")
        
        # AI Enhancement
        if use_ai_enhancement and self.ai_analyzer.is_available():
            print(f"\n🤖 Step 2: AI Semantic Enhancement...")
            protocol_json = self.ai_analyzer.enhance_protocol(protocol_json)
            print("   ✅ AI enhancement complete")
        elif use_ai_enhancement:
            print(f"\n⚠️  Step 2: AI not available")
        
        # Generate Tamarin
        print(f"\n📝 Step 3: Generating Tamarin rules...")
        
        try:
            generator = TamarinGenerator()
            generator.load_protocol_from_dict(protocol_json)
            
            content = generator.generate_with_comments()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Generated: {output_path}")
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            return False
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print()
        
        return True


def main():
    """Main entry point for Task 1 AI Tool."""
    
    parser = argparse.ArgumentParser(
        description="AI Tool: Protocol Diagram → Tamarin Rules (Task 1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Task 1: Generate Tamarin rules from protocol diagrams.

Examples:
  # From diagram image (PNG, JPG)
  python task1_ai_tool.py diagram.png -o output.spthy
  
  # From PDF diagram
  python task1_ai_tool.py protocol.pdf -o output.spthy
  
  # From JSON file
  python task1_ai_tool.py --input protocol.json -o output.spthy
  
  # With AI enhancement (recommended)
  export OPENAI_API_KEY=sk-...
  python task1_ai_tool.py diagram.png -o output.spthy
  
  # Without AI enhancement
  python task1_ai_tool.py diagram.png -o output.spthy --no-ai
        """
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        help="Input diagram file (PNG, JPG, PDF) or JSON"
    )
    
    parser.add_argument(
        "--input", "-i",
        dest="input_file",
        help="Input file (alternative to positional argument)"
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output .spthy file"
    )
    
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI enhancement"
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Get input file
    input_file = args.input or args.input_file
    if not input_file:
        print("❌ Error: Input file required")
        print("Usage: python task1_ai_tool.py <diagram> -o <output.spthy>")
        sys.exit(1)
    
    # Check file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: File not found: {input_file}")
        sys.exit(1)
    
    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    
    # Create AI tool
    ai_tool = DiagramToTamarinAI(api_key=api_key)
    
    # Process based on file type
    success = False
    
    if input_file.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
        # Diagram input
        success = ai_tool.process_diagram(
            input_file,
            args.output,
            use_ai_enhancement=not args.no_ai
        )
    elif input_file.lower().endswith('.json'):
        # JSON input
        success = ai_tool.process_json(
            input_file,
            args.output,
            use_ai_enhancement=not args.no_ai
        )
    else:
        print(f"❌ Unsupported file format: {input_file}")
        print("Supported: PNG, JPG, PDF, JSON")
        sys.exit(1)
    
    sys.exit(0 if success else 1)


# Add method to load protocol from dict
def load_protocol_from_dict(self, protocol_dict: dict):
    """Load protocol from dictionary (not file)."""
    from src.parser import Protocol, Role, ProtocolStep, SecurityProperty, RoleType, CryptoOp
    
    self.protocol = Protocol(
        name=protocol_dict.get("protocol_name", "Protocol"),
        description=protocol_dict.get("description", ""),
        roles=[
            Role(
                name=r.get("name", ""),
                type=r.get("type", "client"),
                long_term_key=r.get("long_term_key"),
                public_key=r.get("public_key"),
                description=r.get("description", "")
            )
            for r in protocol_dict.get("roles", [])
        ],
        steps=[
            ProtocolStep(
                id=s.get("id", 0),
                from_role=s.get("from", ""),
                to_role=s.get("to", ""),
                message=s.get("message", ""),
                fresh=s.get("fresh", []),
                crypto_ops=s.get("crypto_ops", []),
                action_fact=s.get("action_fact"),
                description=s.get("description", "")
            )
            for s in protocol_dict.get("steps", [])
        ],
        security_properties=[
            SecurityProperty(
                name=p.get("name", ""),
                type=p.get("type", ""),
                description=p.get("description", "")
            )
            for p in protocol_dict.get("security_properties", [])
        ],
        builtins=protocol_dict.get("builtins", ["hashing", "asymmetric-encryption", "signing"])
    )
    
    self.role_map = {r.name: r for r in self.protocol.roles}


# Monkey-patch the method
TamarinGenerator.load_protocol_from_dict = load_protocol_from_dict


if __name__ == "__main__":
    main()
