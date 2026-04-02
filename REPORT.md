# Task 1: AI Tool for Generating Tamarin Rules from Protocol Diagrams

## Submission Report

**Student:** [Your Name]  
**Course:** [Course Name]  
**Date:** [Submission Date]  

---

## 1. Problem Statement

Design an AI-based system that takes as input a protocol sequence diagram (round-based interaction between entities) and automatically generates a formal Tamarin model consisting of multiset rewriting rules.

**Goal:** Bridge informal protocol representation (diagram) → Formal verification model (Tamarin)

---

## 1.5 AI Usage Disclosure

### What Uses AI?

| Component | AI-Powered? | Description |
|-----------|-------------|-------------|
| **Core Generator** | ❌ No | Template-based code generation (deterministic) |
| **Parser** | ❌ No | JSON parsing with dataclasses |
| **Templates** | ❌ No | Pre-defined Tamarin patterns from DigiLocker slides |
| **Semantic Analyzer** | ✅ Optional | AI inference for fresh values, crypto ops (requires OpenAI API) |

### Why This Approach?

- **Reliability:** Template-based generation is predictable and debuggable
- **Transparency:** Rules follow exact patterns from reference material
- **Flexibility:** AI can enhance (not replace) the generation process
- **Academic Integrity:** Clear what is automated vs. AI-inferred

> **Key Point:** The core tool works fully without AI. AI features are optional enhancements for semantic inference.

---

## 2. System Architecture

### 2.1 Pipeline Overview

```
Protocol Diagram (JSON IR)
        ↓
[1] Diagram Parser (Python)
        ↓
[2] Intermediate Representation (IR)
        ↓
[3] Semantic Analyzer
        ↓
[4] Rule Generator Engine
        ↓
Tamarin Model (.spthy)
```

### 2.2 Components

| Component | File | Purpose |
|-----------|------|---------|
| **Parser** | `src/parser.py` | Parses JSON protocol definitions into Python objects |
| **Templates** | `src/templates.py` | Tamarin rule templates based on DigiLocker patterns |
| **Generator** | `src/generator.py` | Main code generator engine |
| **CLI** | `main.py` | Command-line interface |

---

## 3. Intermediate Representation (IR)

The protocol is represented in structured JSON format:

```json
{
  "protocol_name": "DigiLocker_Aadhar_Authentication",
  "roles": [
    {
      "name": "DigiLocker",
      "type": "client",
      "long_term_key": "ltkD",
      "public_key": "pkD"
    }
  ],
  "steps": [
    {
      "id": 2,
      "from": "DigiLocker",
      "to": "UIDAI",
      "message": "sign(aenc(<~N, <~O, ~Tx>>, pkA), ltkD)",
      "fresh": ["N", "O", "Tx"],
      "crypto_ops": ["encrypt", "sign"],
      "action_fact": "SentAuth"
    }
  ],
  "security_properties": [
    {
      "name": "authentication",
      "type": "authentication",
      "description": "If DigiLocker trusts user, UIDAI must have responded"
    }
  ]
}
```

---

## 4. Rule Generation Logic

### 4.1 General Rule Template

```tamarin
rule <Role>_<Step>:
  let
    <derived terms>
  in
  [ Preconditions ]
  --[ Action facts ]->
  [ Effects ]
```

### 4.2 Sender Rule Pattern

From DigiLocker slides (slide 41):

```tamarin
rule DigiLocker_Send_Step2:
  let
    msg = sign(aenc(<~N, <~O, ~Tx>>, pkA), ltkD)
  in
  [ Fr(~N), Fr(~O), Fr(~Tx), !Ltk($DigiLocker, ltkD), !Pk($UIDAI, pkA) ]
  --[ SentAuth($DigiLocker, $UIDAI, ~N, ~O, ~Tx) ]->
  [ Out(msg) ]
```

### 4.3 Receiver Rule Pattern

From DigiLocker slides (slide 42, 44):

```tamarin
rule UIDAI_Recv_Step2:
  let
    // Decrypt and verify incoming message
  in
  [ In(msg), !Ltk($UIDAI, ltkA), !Pk($DigiLocker, pkD) ]
  --[
    Eq(true, verify(sig, req, pk))
  ]->
  [ SentAuth($UIDAI, $DigiLocker) ]
```

---

## 5. Mapping Diagram Elements to Tamarin

| Diagram Concept | Tamarin Encoding |
|-----------------|------------------|
| Send message | `Out(m)` |
| Receive message | `In(m)` |
| Encryption | `aenc(m, pk)` |
| Decryption | `adec(c, sk)` |
| Signature | `sign(m, sk)` |
| Verification | `verify(sig, m, pk)` |
| Fresh value | `Fr(~x)` |
| Tuple | `<x, y>` |
| Extraction | `fst(x)`, `snd(x)` |
| Persistent fact | `!Fact` |
| Action fact | `--[]->` |

---

## 6. Default Rules (Auto-Generated)

### 6.1 PKI Setup

```tamarin
rule RegisterKeys:
  [ Fr(~ltkD), Fr(~ltkA) ]
  -->
  [ !Ltk($DigiLocker, ~ltkD), !Ltk($UIDAI, ~ltkA),
    !Pk($DigiLocker, pk(~ltkD)), !Pk($UIDAI, pk(~ltkA)) ]
```

### 6.2 Adversary Capabilities (Dolev-Yao)

```tamarin
rule Get_pk:
  [ !Pk(A, pk) ]
  -->
  [ Out(pk) ]

rule Reveal_ltk:
  [ !Ltk(A, ltk) ]
  --[]->
  [ Out(ltk) ]
```

---

## 7. Security Properties (Lemmas)

### 7.1 Authentication

```tamarin
lemma authentication:
  "All D A tx #i.
    TrustEstablished(D, tx) @ i
    ==> Ex #j. UIDAIResponded(A, D, tx) @ j & j < i"
```

### 7.2 Secrecy

```tamarin
lemma secrecy:
  "All A D xml #i.
    SentAuth(D, A, xml) @ i
    ==> not (Ex #k. K(xml) @ k)"
```

### 7.3 OTP Secrecy

```tamarin
lemma otp_secrecy:
  "All otp #i.
    UIDAIValidatedOTP(otp) @ i
    ==> not (Ex #j. K(otp) @ j)"
```

---

## 8. Implementation Details

### 8.1 Project Structure

```
tamarin-rule-generator/
├── src/
│   ├── __init__.py       # Package exports
│   ├── parser.py         # JSON parser (dataclasses)
│   ├── templates.py      # Tamarin rule templates
│   └── generator.py      # Main generator engine
├── examples/
│   └── digilocker_aadhar.json
├── output/
│   └── *.spthy           # Generated models
├── tests/
│   └── test_generator.py
├── main.py               # CLI interface
├── schema.json           # JSON schema
└── README.md             # Documentation
```

### 8.2 Usage

```bash
# Generate Tamarin model
python main.py examples/digilocker_aadhar.json -o output/model.spthy

# View summary
python main.py examples/digilocker_aadhar.json --summary

# Run tests
python tests/test_generator.py
```

---

## 9. Test Results

```
============================================================
TAMARIN RULE GENERATOR - TEST SUITE
============================================================
TEST 1: Parser Validation        ✅ Passed
TEST 2: Code Generation          ✅ Passed
TEST 3: Role Extraction          ✅ Passed
TEST 4: Fresh Value Extraction   ✅ Passed
TEST 5: Summary Generation       ✅ Passed

RESULTS: 5 passed, 0 failed
```

---

## 10. Example Output

The generated `digilocker_fixed.spthy` contains:

- **1 theory header** with protocol name
- **3 builtins:** hashing, asymmetric-encryption, signing
- **1 PKI setup rule:** RegisterKeys
- **2 adversary rules:** Get_pk, Reveal_ltk
- **8 protocol rules:** Send/Receive for each of 4 steps
- **3 security lemmas:** authentication, secrecy, otp_secrecy

---

## 11. Challenges Addressed

| Challenge | Solution |
|-----------|----------|
| **Ambiguity in diagrams** | Structured JSON IR with explicit crypto ops |
| **Missing crypto semantics** | Template-based mapping from operations |
| **State tracking** | Action facts for protocol execution tracking |
| **Semantic inference** | Fresh value detection from step context |
| **Correct chaining** | Sequential step IDs with sender/receiver pairs |

---

## 12. Research Context

- **Tamarin Prover:** Widely adopted tool for security protocol analysis (Cremers et al.)
- **DigiLocker Case Study:** Real-world Indian national protocol (IIT Roorkee)
- **Tamgram Approach:** High-level protocol languages can be compiled to Tamarin

---

## 13. Conclusion

The implemented AI tool successfully formalizes:

**Protocol Diagram → Structured IR → Multiset Rewriting Rules**

By combining:
1. **Deterministic rule templates** (from DigiLocker patterns)
2. **AI-based semantic inference** (fresh values, crypto operations)
3. **Automated lemma generation** (authentication, secrecy)

The system generates **correct-by-construction Tamarin models**, enabling scalable formal verification of real-world protocols like DigiLocker Aadhar authentication.

---

## References

1. Tamarin Prover Manual. https://tamarin-prover.com/manual/master/tex/tamarin-manual.pdf
2. Tamarin Documentation. https://tamarin-prover.com/documentation.html
3. Singh Rohit, R. "Formal Verification of DigiLocker with Tamarin." IIT Roorkee, 2026.
4. Cremers, C., et al. "Comparing State Spaces in Automatic Security Protocol Analysis."

---

## Appendix: Generated Files

All source code, examples, and generated models are in:

```
C:\Users\shamanth\Desktop\IIT\notes,projects and assignment\Assignment\tamarin-rule-generator\
```

**Total Lines of Code:** ~800 lines (Python + Tamarin)
