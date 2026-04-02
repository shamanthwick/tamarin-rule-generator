"""
Tamarin Rule Generator - AI Semantic Analyzer (OPTIONAL)
Uses LLM APIs to infer protocol semantics from natural language descriptions.

This is the AI component that makes the tool truly "AI-powered".
"""

import json
import os
from typing import Optional, Dict, List

# Optional: Install with `pip install openai`
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AISemanticAnalyzer:
    """
    Uses LLM to infer protocol semantics:
    - Fresh values (nonces, session IDs, OTPs)
    - Cryptographic intent
    - Security properties
    - Action facts
    
    Requires OpenAI API key (set OPENAI_API_KEY env var)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def is_available(self) -> bool:
        """Check if AI analyzer is available."""
        return self.client is not None
    
    def infer_fresh_values(self, step_description: str) -> List[str]:
        """
        Use LLM to identify fresh values from natural language description.
        
        Example:
        Input: "Alice sends a nonce and session ID to Bob"
        Output: ["nonce", "session_id"]
        """
        if not self.client:
            return []  # Fallback: empty list
        
        prompt = f"""
Analyze this protocol step and identify values that should be FRESH 
(nonces, session IDs, OTPs, timestamps, transaction IDs).

Step: {step_description}

Return ONLY a JSON list of fresh value names. Example: ["nonce", "session_id"]
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a security protocol analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            fresh_values = json.loads(result)
            return fresh_values if isinstance(fresh_values, list) else []
            
        except Exception as e:
            print(f"⚠️  AI inference failed: {e}")
            return []
    
    def infer_crypto_ops(self, message_description: str) -> List[str]:
        """
        Use LLM to identify cryptographic operations.
        
        Example:
        Input: "Encrypt with Bob's public key and sign with Alice's private key"
        Output: ["encrypt", "sign"]
        """
        if not self.client:
            return []
        
        prompt = f"""
Analyze this message and identify cryptographic operations.
Choose from: encrypt, decrypt, sign, verify, hash

Message: {message_description}

Return ONLY a JSON list. Example: ["encrypt", "sign"]
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a cryptography expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            crypto_ops = json.loads(result)
            return crypto_ops if isinstance(crypto_ops, list) else []
            
        except Exception as e:
            print(f"⚠️  AI inference failed: {e}")
            return []
    
    def suggest_security_properties(self, protocol_description: str) -> List[Dict]:
        """
        Use LLM to suggest security properties (lemmas).
        """
        if not self.client:
            return []
        
        prompt = f"""
Analyze this protocol and suggest security properties to verify.
Choose property types: authentication, secrecy, forward_secrecy, agreement

Protocol: {protocol_description}

Return JSON list with format:
[
  {{"name": "auth", "type": "authentication", "description": "..."}},
  {{"name": "secrecy", "type": "secrecy", "description": "..."}}
]
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a formal verification expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            properties = json.loads(result)
            return properties if isinstance(properties, list) else []
            
        except Exception as e:
            print(f"⚠️  AI inference failed: {e}")
            return []
    
    def enhance_protocol(self, protocol_data: dict) -> dict:
        """
        Use AI to enhance a protocol definition with inferred semantics.
        """
        if not self.client:
            print("⚠️  AI not available. Returning original protocol.")
            return protocol_data
        
        print("🤖 AI Semantic Analysis in progress...")
        
        # Enhance each step
        for step in protocol_data.get("steps", []):
            description = step.get("description", "")
            
            if description and not step.get("fresh"):
                fresh = self.infer_fresh_values(description)
                if fresh:
                    step["fresh"] = fresh
                    print(f"  ✓ Inferred fresh values for step {step['id']}: {fresh}")
            
            if description and not step.get("crypto_ops"):
                crypto = self.infer_crypto_ops(description)
                if crypto:
                    step["crypto_ops"] = crypto
                    print(f"  ✓ Inferred crypto ops for step {step['id']}: {crypto}")
        
        # Suggest security properties
        if not protocol_data.get("security_properties"):
            protocol_desc = protocol_data.get("description", "")
            props = self.suggest_security_properties(protocol_desc)
            if props:
                protocol_data["security_properties"] = props
                print(f"  ✓ Suggested {len(props)} security properties")
        
        return protocol_data


def analyze_with_ai(json_path: str, output_path: Optional[str] = None):
    """
    Load a protocol JSON, enhance with AI, save enhanced version.
    """
    analyzer = AISemanticAnalyzer()
    
    if not analyzer.is_available():
        print("❌ AI not available. Set OPENAI_API_KEY or install openai package.")
        return
    
    # Load protocol
    with open(json_path, 'r') as f:
        protocol = json.load(f)
    
    # Enhance with AI
    enhanced = analyzer.enhance_protocol(protocol)
    
    # Save
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(enhanced, f, indent=2)
        print(f"✅ Enhanced protocol saved to: {output_path}")
    
    return enhanced


if __name__ == "__main__":
    # Example usage
    print("AI Semantic Analyzer for Tamarin Rule Generator")
    print("=" * 60)
    
    analyzer = AISemanticAnalyzer()
    
    if analyzer.is_available():
        print("✅ AI Available (OpenAI API)")
        
        # Test inference
        test_desc = "Alice generates a nonce and encrypts it with Bob's public key"
        fresh = analyzer.infer_fresh_values(test_desc)
        crypto = analyzer.infer_crypto_ops(test_desc)
        
        print(f"\nTest: {test_desc}")
        print(f"  Fresh values: {fresh}")
        print(f"  Crypto ops: {crypto}")
    else:
        print("❌ AI Not Available")
        print("\nTo enable AI features:")
        print("  1. pip install openai")
        print("  2. Set env var: OPENAI_API_KEY=your-key")
        print("\nWithout AI, the tool uses deterministic templates (still works!)")
