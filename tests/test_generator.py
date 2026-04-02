#!/usr/bin/env python3
"""
Tamarin Rule Generator - Test Script
Validates the generator with multiple protocol examples.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import parse_protocol, ProtocolParser
from src.generator import TamarinGenerator


def test_parser():
    """Test the JSON parser."""
    print("\n" + "="*60)
    print("TEST 1: Parser Validation")
    print("="*60)
    
    protocol = parse_protocol("examples/digilocker_aadhar.json")
    
    assert protocol.name == "DigiLocker_Aadhar_Authentication"
    assert len(protocol.roles) == 3
    assert len(protocol.steps) == 4
    assert len(protocol.security_properties) == 3
    
    print("✅ Parser test passed")
    return True


def test_generator():
    """Test the code generator."""
    print("\n" + "="*60)
    print("TEST 2: Code Generation")
    print("="*60)
    
    generator = TamarinGenerator()
    protocol = generator.load_protocol("examples/digilocker_aadhar.json")
    
    content = generator.generate()
    
    # Check required sections
    assert "theory DigiLocker_Aadhar_Authentication" in content
    assert "builtins:" in content
    assert "rule RegisterKeys" in content
    assert "rule Get_pk" in content
    assert "rule Reveal_ltk" in content
    assert "lemma authentication" in content
    assert "lemma secrecy" in content
    
    print("✅ Generator test passed")
    return True


def test_role_extraction():
    """Test role extraction with keys."""
    print("\n" + "="*60)
    print("TEST 3: Role Extraction")
    print("="*60)
    
    parser = ProtocolParser()
    protocol = parser.load_from_file("examples/digilocker_aadhar.json")
    
    roles_with_keys = parser.get_roles_with_keys()
    
    assert len(roles_with_keys) == 2  # DigiLocker and UIDAI
    assert roles_with_keys[0].name == "DigiLocker"
    assert roles_with_keys[1].name == "UIDAI"
    
    print("✅ Role extraction test passed")
    return True


def test_fresh_values():
    """Test fresh value extraction."""
    print("\n" + "="*60)
    print("TEST 4: Fresh Value Extraction")
    print("="*60)
    
    parser = ProtocolParser()
    protocol = parser.load_from_file("examples/digilocker_aadhar.json")
    
    fresh_values = parser.get_fresh_values()
    
    expected_fresh = {"N", "O", "Tx", "aadhaar_number", "OTP"}
    assert set(fresh_values) == expected_fresh
    
    print("✅ Fresh value extraction test passed")
    return True


def test_summary():
    """Test protocol summary generation."""
    print("\n" + "="*60)
    print("TEST 5: Summary Generation")
    print("="*60)
    
    generator = TamarinGenerator()
    generator.load_protocol("examples/digilocker_aadhar.json")
    
    summary = generator.summary()
    
    assert "DigiLocker_Aadhar_Authentication" in summary
    assert "User" in summary
    assert "DigiLocker" in summary
    assert "UIDAI" in summary
    assert "4" in summary  # 4 steps
    
    print("✅ Summary generation test passed")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("TAMARIN RULE GENERATOR - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Parser", test_parser),
        ("Generator", test_generator),
        ("Role Extraction", test_role_extraction),
        ("Fresh Values", test_fresh_values),
        ("Summary", test_summary),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ {name} test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {name} test error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
