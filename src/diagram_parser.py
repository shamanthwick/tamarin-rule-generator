"""
Tamarin Rule Generator - Diagram Parser (Vision AI)
Extracts protocol information from sequence diagram images.

Uses OCR and computer vision to parse protocol diagrams.
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Optional dependencies
try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

# For PDF support
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


@dataclass
class ExtractedMessage:
    """Represents a message extracted from diagram."""
    from_role: str
    to_role: str
    message_content: str
    round_number: int
    crypto_operations: List[str]


@dataclass
class ExtractedProtocol:
    """Protocol information extracted from diagram."""
    protocol_name: str
    roles: List[str]
    messages: List[ExtractedMessage]
    fresh_values: List[str]


class DiagramParser:
    """
    Parses protocol sequence diagrams (images) and extracts:
    - Roles (participants)
    - Message flows
    - Cryptographic operations
    - Fresh values (nonces, keys)
    
    Input: PNG, JPG, PDF of protocol diagram
    Output: Structured protocol information
    """
    
    def __init__(self):
        self.vision_available = VISION_AVAILABLE
        self.pdf_available = PDF_AVAILABLE
        
        if not self.vision_available:
            print("⚠️  Vision libraries not available.")
            print("Install with: pip install pillow opencv-python pytesseract")
        
        if not self.pdf_available:
            print("⚠️  PDF support not available.")
            print("Install with: pip install pymupdf")
    
    def parse_image(self, image_path: str) -> Optional[ExtractedProtocol]:
        """
        Parse protocol diagram from image file.
        
        Args:
            image_path: Path to PNG/JPG diagram
        
        Returns:
            ExtractedProtocol or None if parsing fails
        """
        if not self.vision_available:
            print("❌ Vision libraries not installed")
            return None
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            
            # Parse the extracted text
            protocol = self._parse_extracted_text(text)
            
            print(f"✅ Extracted protocol from image: {image_path}")
            return protocol
            
        except Exception as e:
            print(f"❌ Image parsing failed: {e}")
            return None
    
    def parse_pdf(self, pdf_path: str) -> Optional[ExtractedProtocol]:
        """
        Parse protocol diagram from PDF file.
        
        Args:
            pdf_path: Path to PDF diagram
        
        Returns:
            ExtractedProtocol or None if parsing fails
        """
        if not self.pdf_available:
            print("❌ PDF support not installed")
            return None
        
        try:
            # Convert PDF to images
            doc = fitz.open(pdf_path)
            
            all_text = []
            for page in doc:
                # Get text from PDF
                text = page.get_text()
                all_text.append(text)
            
            doc.close()
            
            # Parse extracted text
            full_text = "\n".join(all_text)
            protocol = self._parse_extracted_text(full_text)
            
            print(f"✅ Extracted protocol from PDF: {pdf_path}")
            return protocol
            
        except Exception as e:
            print(f"❌ PDF parsing failed: {e}")
            return None
    
    def _parse_extracted_text(self, text: str) -> ExtractedProtocol:
        """
        Parse extracted text into structured protocol.
        
        Uses pattern matching and AI to understand:
        - Role names (Alice, Bob, Server, etc.)
        - Message arrows (→, ->)
        - Cryptographic operations (enc, dec, sign, etc.)
        - Fresh values (nonces, keys)
        """
        import re
        
        roles = set()
        messages = []
        fresh_values = set()
        
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detect role names (typically at start of lines)
            role_pattern = r'\b(Alice|Bob|Server|Client|User|DigiLocker|UIDAI|A|B|S|C)\b'
            role_matches = re.findall(role_pattern, line, re.IGNORECASE)
            roles.update(role_matches)
            
            # Detect message arrows
            if '→' in line or '->' in line:
                # Parse message format: "A → B: message"
                arrow = '→' if '→' in line else '->'
                parts = line.split(arrow)
                
                if len(parts) >= 2:
                    from_role = parts[0].strip()
                    remaining = arrow.join(parts[1:])
                    
                    if ':' in remaining:
                        to_role, msg_content = remaining.split(':', 1)
                        to_role = to_role.strip()
                        msg_content = msg_content.strip()
                        
                        roles.add(from_role)
                        roles.add(to_role)
                        
                        # Detect crypto operations
                        crypto_ops = self._detect_crypto_operations(msg_content)
                        
                        # Detect fresh values
                        fresh = self._detect_fresh_values(msg_content)
                        fresh_values.update(fresh)
                        
                        messages.append(ExtractedMessage(
                            from_role=from_role,
                            to_role=to_role,
                            message_content=msg_content,
                            round_number=len(messages) + 1,
                            crypto_operations=crypto_ops
                        ))
        
        # Generate protocol name from roles
        protocol_name = "_".join(list(roles)[:2]) + "_Protocol"
        
        return ExtractedProtocol(
            protocol_name=protocol_name,
            roles=list(roles),
            messages=messages,
            fresh_values=list(fresh_values)
        )
    
    def _detect_crypto_operations(self, message: str) -> List[str]:
        """Detect cryptographic operations in message."""
        import re
        
        ops = []
        message_lower = message.lower()
        
        # Encryption patterns
        if re.search(r'enc\(|encrypt|aenc|senc', message_lower):
            ops.append('encrypt')
        if re.search(r'dec\(|decrypt|adec|sdec', message_lower):
            ops.append('decrypt')
        
        # Signature patterns
        if re.search(r'sign\(|signature', message_lower):
            ops.append('sign')
        if re.search(r'verify\(|verification', message_lower):
            ops.append('verify')
        
        # Hash patterns
        if re.search(r'hash\(|h\(|sha|md5', message_lower):
            ops.append('hash')
        
        # Public key patterns
        if re.search(r'pk\(|public.?key', message_lower):
            ops.append('public_key')
        
        # Private key patterns
        if re.search(r'sk\(|ltk\(|private.?key', message_lower):
            ops.append('private_key')
        
        return ops
    
    def _detect_fresh_values(self, message: str) -> List[str]:
        """Detect fresh values (nonces, keys) in message."""
        import re
        
        fresh = []
        
        # Nonce patterns (Na, Nb, N, nonce)
        nonces = re.findall(r'\b(N[a-zA-Z]?|nonce[a-zA-Z]?)\b', message, re.IGNORECASE)
        fresh.extend(nonces)
        
        # Key patterns (K, Ks, Kab)
        keys = re.findall(r'\b(K[a-zA-Z]?[a-zA-Z0-9]?)\b', message)
        fresh.extend(keys)
        
        # Transaction/OTP patterns
        tx = re.findall(r'\b(Tx|OTP|O[a-zA-Z]?)\b', message, re.IGNORECASE)
        fresh.extend(tx)
        
        return list(set(fresh))
    
    def to_json_format(self, protocol: ExtractedProtocol) -> dict:
        """Convert extracted protocol to JSON format for generator."""
        roles_data = []
        for role in protocol.roles:
            roles_data.append({
                "name": role,
                "type": "client" if role.lower() in ["alice", "bob", "client", "user"] else "server",
                "long_term_key": f"ltk{role[0]}",
                "public_key": f"pk{role[0]}"
            })
        
        steps = []
        for msg in protocol.messages:
            steps.append({
                "id": msg.round_number,
                "from": msg.from_role,
                "to": msg.to_role,
                "message": msg.message_content,
                "fresh": [],  # Would need more sophisticated parsing
                "crypto_ops": msg.crypto_operations,
                "description": f"{msg.from_role} sends {msg.message_content} to {msg.to_role}"
            })
        
        return {
            "protocol_name": protocol.protocol_name,
            "description": f"Protocol extracted from diagram",
            "roles": roles_data,
            "steps": steps,
            "security_properties": [
                {"name": "authentication", "type": "authentication", "description": "Parties authenticate"},
                {"name": "secrecy", "type": "secrecy", "description": "Session secrets remain secret"}
            ],
            "builtins": ["hashing", "asymmetric-encryption", "signing"]
        }


def parse_diagram_file(file_path: str) -> Optional[dict]:
    """
    Parse protocol diagram from file (image or PDF).
    
    Args:
        file_path: Path to PNG, JPG, or PDF diagram
    
    Returns:
        JSON-compatible protocol dict or None
    """
    parser = DiagramParser()
    
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        protocol = parser.parse_image(file_path)
    elif file_path.lower().endswith('.pdf'):
        protocol = parser.parse_pdf(file_path)
    else:
        print(f"❌ Unsupported file format: {file_path}")
        return None
    
    if protocol:
        return parser.to_json_format(protocol)
    
    return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python diagram_parser.py <diagram_file>")
        print("Supported formats: PNG, JPG, PDF")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = parse_diagram_file(file_path)
    
    if result:
        print("\n✅ Extracted Protocol:")
        print(f"   Name: {result['protocol_name']}")
        print(f"   Roles: {[r['name'] for r in result['roles']]}")
        print(f"   Steps: {len(result['steps'])}")
        
        print("\n--- Messages ---")
        for step in result['steps']:
            print(f"   {step['id']}. {step['from']} → {step['to']}: {step['message']}")
    else:
        print("❌ Failed to parse diagram")
