#!/usr/bin/env python3
"""
Tamarin Rule Generator - AI-Powered Main Entry Point
Uses LLM to interpret protocol diagrams and generate Tamarin rules.

This is the AI tool referenced in Task 1.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ai_analyzer import AISemanticAnalyzer
from src.generator import TamarinGenerator


class AIPoweredTamarinGenerator:
    """
    AI-powered tool that:
    1. Takes protocol description (natural language or structured)
    2. Uses LLM to infer semantics (fresh values, crypto ops, etc.)
    3. Generates Tamarin rules automatically
    
    This is the AI tool for Task 1.
    """
    
    def __init__(self, api_key: str = None):
        self.analyzer = AISemanticAnalyzer(api_key)
        
        if not self.analyzer.is_available():
            print("⚠️  Warning: AI not available.")
            print("\nTo enable full AI features:")
            print("  1. pip install openai")
            print("  2. Set OPENAI_API_KEY environment variable")
            print("\nContinuing with template-based generation only...\n")
    
    def generate_from_description(self, protocol_description: str) -> str:
        """
        Generate Tamarin model from natural language description.
        
        Example input:
        "DigiLocker Aadhar auth: User sends OTP to DigiLocker, 
         which encrypts and signs it to UIDAI. UIDAI verifies 
         and sends back encrypted response."
        """
        print("🤖 AI Protocol Analysis...")
        
        # Use AI to parse natural language into structured protocol
        protocol_json = self._ai_parse_description(protocol_description)
        
        if not protocol_json:
            print("⚠️  AI parsing failed. Using template fallback.")
            protocol_json = self._fallback_template()
        
        # Enhance with AI
        protocol_json = self.analyzer.enhance_protocol(protocol_json)
        
        # Generate Tamarin model
        print("\n📝 Generating Tamarin model...")
        generator = TamarinGenerator(protocol_json)
        content = generator.generate_with_comments()
        
        return content
    
    def _ai_parse_description(self, description: str) -> dict:
        """Use LLM to parse natural language into protocol JSON."""
        
        if not self.analyzer.client:
            return None
        
        prompt = f"""
Convert this protocol description into JSON format for Tamarin rule generation.

Protocol Description:
{description}

Output JSON in this exact format:
{{
  "protocol_name": "Protocol_Name",
  "description": "Brief description",
  "roles": [
    {{"name": "A", "type": "client", "long_term_key": "ltkA", "public_key": "pkA"}}
  ],
  "steps": [
    {{"id": 1, "from": "A", "to": "B", "description": "A sends nonce to B", "fresh": ["Na"], "crypto_ops": ["encrypt"]}}
  ],
  "security_properties": [
    {{"name": "authentication", "type": "authentication", "description": "Parties authenticate"}}
  ],
  "builtins": ["hashing", "asymmetric-encryption", "signing"]
}}

Return ONLY valid JSON, no explanation.
"""
        
        try:
            response = self.analyzer.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a security protocol analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            protocol = json.loads(result)
            
            print(f"  ✓ Parsed protocol: {protocol.get('protocol_name', 'Unknown')}")
            print(f"  ✓ Roles: {[r['name'] for r in protocol.get('roles', [])]}")
            print(f"  ✓ Steps: {len(protocol.get('steps', []))}")
            
            return protocol
            
        except Exception as e:
            print(f"⚠️  AI parsing failed: {e}")
            return None
    
    def _fallback_template(self) -> dict:
        """Return a minimal fallback protocol structure."""
        return {
            "protocol_name": "Unknown_Protocol",
            "description": "Protocol parsed from description",
            "roles": [],
            "steps": [],
            "security_properties": [],
            "builtins": ["hashing", "asymmetric-encryption", "signing"]
        }


def main():
    """
    AI-Powered Tamarin Rule Generator - Task 1
    
    Usage:
        python ai_tool.py "protocol description" -o output.spthy
        python ai_tool.py --file input.json -o output.spthy
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Tool for Generating Tamarin Rules (Task 1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from natural language description
  python ai_tool.py "Alice sends nonce to Bob encrypted with his key" -o output.spthy
  
  # Generate from JSON file (AI-enhanced)
  python ai_tool.py --file protocol.json -o output.spthy
  
  # Summary only
  python ai_tool.py --file protocol.json --summary
        """
    )
    
    parser.add_argument(
        "description",
        nargs="?",
        help="Natural language protocol description"
    )
    
    parser.add_argument(
        "--file", "-f",
        help="Input JSON file with protocol definition"
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output .spthy file"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary only, don't generate file"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.description and not args.file:
        print("❌ Error: Provide either description or --file")
        sys.exit(1)
    
    # Create AI-powered generator
    ai_gen = AIPoweredTamarinGenerator()
    
    # Generate from description or file
    if args.description:
        # AI mode: Natural language → Tamarin
        print("=" * 60)
        print("AI-POWERED TAMARIN RULE GENERATOR (Task 1)")
        print("=" * 60)
        print(f"\n📝 Input: {args.description}\n")
        
        content = ai_gen.generate_from_description(args.description)
        
    elif args.file:
        # File mode: JSON → AI enhancement → Tamarin
        print("=" * 60)
        print("AI-POWERED TAMARIN RULE GENERATOR (Task 1)")
        print("=" * 60)
        
        with open(args.file, 'r') as f:
            protocol = json.load(f)
        
        # Enhance with AI
        protocol = ai_gen.analyzer.enhance_protocol(protocol)
        
        # Generate
        generator = TamarinGenerator(protocol)
        print(generator.summary())
        
        if args.summary:
            sys.exit(0)
        
        content = generator.generate_with_comments()
    
    # Save output
    with open(args.output, 'w') as f:
        f.write(content)
    
    print(f"\n✅ Generated: {args.output}")


if __name__ == "__main__":
    main()
