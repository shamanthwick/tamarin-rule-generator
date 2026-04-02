"""
Tamarin Rule Generator - Parser Module
Parses JSON protocol definitions and converts to intermediate Python objects.
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class RoleType(Enum):
    CLIENT = "client"
    SERVER = "server"
    AUTHORITY = "authority"
    USER = "user"


class CryptoOp(Enum):
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    HASH = "hash"


@dataclass
class Role:
    name: str
    type: RoleType
    long_term_key: Optional[str] = None
    public_key: Optional[str] = None
    description: str = ""
    
    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = RoleType(self.type)


@dataclass
class ProtocolStep:
    id: int
    from_role: str
    to_role: str
    message: str
    fresh: List[str] = field(default_factory=list)
    crypto_ops: List[CryptoOp] = field(default_factory=list)
    action_fact: Optional[str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.crypto_ops:
            self.crypto_ops = [
                CryptoOp(op) if isinstance(op, str) else op 
                for op in self.crypto_ops
            ]


@dataclass
class SecurityProperty:
    name: str
    type: str
    description: str


@dataclass
class Protocol:
    name: str
    description: str = ""
    roles: List[Role] = field(default_factory=list)
    steps: List[ProtocolStep] = field(default_factory=list)
    security_properties: List[SecurityProperty] = field(default_factory=list)
    builtins: List[str] = field(default_factory=lambda: [
        "hashing", "asymmetric-encryption", "signing"
    ])


class ProtocolParser:
    """Parses JSON protocol definitions into Python objects."""
    
    def __init__(self, json_path: Optional[str] = None):
        self.json_path = json_path
        self.protocol: Optional[Protocol] = None
    
    def load_from_file(self, json_path: str) -> Protocol:
        """Load and parse protocol from JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self._parse(data)
    
    def load_from_string(self, json_str: str) -> Protocol:
        """Load and parse protocol from JSON string."""
        data = json.loads(json_str)
        return self._parse(data)
    
    def _parse(self, data: dict) -> Protocol:
        """Parse JSON data into Protocol object."""
        self.protocol = Protocol(
            name=data.get("protocol_name", "Unnamed_Protocol"),
            description=data.get("description", ""),
            roles=self._parse_roles(data.get("roles", [])),
            steps=self._parse_steps(data.get("steps", [])),
            security_properties=self._parse_security_properties(
                data.get("security_properties", [])
            ),
            builtins=data.get("builtins", [
                "hashing", "asymmetric-encryption", "signing"
            ])
        )
        return self.protocol
    
    def _parse_roles(self, roles_data: list) -> List[Role]:
        """Parse role definitions."""
        roles = []
        for role in roles_data:
            roles.append(Role(
                name=role.get("name", "Unknown"),
                type=role.get("type", "client"),
                long_term_key=role.get("long_term_key"),
                public_key=role.get("public_key"),
                description=role.get("description", "")
            ))
        return roles
    
    def _parse_steps(self, steps_data: list) -> List[ProtocolStep]:
        """Parse protocol steps."""
        steps = []
        for step in steps_data:
            steps.append(ProtocolStep(
                id=step.get("id", 0),
                from_role=step.get("from", ""),
                to_role=step.get("to", ""),
                message=step.get("message", ""),
                fresh=step.get("fresh", []),
                crypto_ops=step.get("crypto_ops", []),
                action_fact=step.get("action_fact"),
                description=step.get("description", "")
            ))
        return steps
    
    def _parse_security_properties(
        self, props_data: list
    ) -> List[SecurityProperty]:
        """Parse security property definitions."""
        props = []
        for prop in props_data:
            props.append(SecurityProperty(
                name=prop.get("name", ""),
                type=prop.get("type", "authentication"),
                description=prop.get("description", "")
            ))
        return props
    
    def get_roles_with_keys(self) -> List[Role]:
        """Get roles that have long-term keys."""
        return [
            r for r in self.protocol.roles 
            if r.long_term_key and r.public_key
        ]
    
    def get_fresh_values(self) -> List[str]:
        """Get all fresh values from all steps."""
        fresh = []
        for step in self.protocol.steps:
            fresh.extend(step.fresh)
        return list(set(fresh))
    
    def validate(self) -> List[str]:
        """Validate protocol definition and return list of errors."""
        errors = []
        
        if not self.protocol:
            return ["No protocol loaded"]
        
        if not self.protocol.roles:
            errors.append("No roles defined")
        
        if not self.protocol.steps:
            errors.append("No steps defined")
        
        # Check role references
        role_names = {r.name for r in self.protocol.roles}
        for step in self.protocol.steps:
            if step.from_role not in role_names:
                errors.append(
                    f"Step {step.id}: unknown sender '{step.from_role}'"
                )
            if step.to_role not in role_names:
                errors.append(
                    f"Step {step.id}: unknown receiver '{step.to_role}'"
                )
        
        return errors


def parse_protocol(json_path: str) -> Protocol:
    """Convenience function to parse a protocol file."""
    parser = ProtocolParser(json_path)
    protocol = parser.load_from_file(json_path)
    
    errors = parser.validate()
    if errors:
        print("⚠️  Validation warnings:")
        for err in errors:
            print(f"   - {err}")
    
    return protocol


if __name__ == "__main__":
    # Test with DigiLocker example
    protocol = parse_protocol("examples/digilocker_aadhar.json")
    
    print(f"\n✅ Protocol: {protocol.name}")
    print(f"📝 Description: {protocol.description}")
    print(f"👥 Roles: {[r.name for r in protocol.roles]}")
    print(f"📊 Steps: {len(protocol.steps)}")
    print(f"🔒 Security Properties: {len(protocol.security_properties)}")
    print(f"🛠️  Builtins: {protocol.builtins}")
    
    print("\n--- Steps ---")
    for step in protocol.steps:
        print(f"\nStep {step.id}: {step.from_role} → {step.to_role}")
        print(f"  Message: {step.message}")
        print(f"  Fresh: {step.fresh}")
        print(f"  Crypto: {[op.value for op in step.crypto_ops]}")
        if step.action_fact:
            print(f"  Action: {step.action_fact}")
