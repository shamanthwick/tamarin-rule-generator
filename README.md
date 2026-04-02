# Tamarin Rule Generator

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-5%20passed-green)](tests/test_generator.py)

> **AI-powered tool that generates formal Tamarin prover models from protocol diagrams.**

**Task 1 Submission:** IIT Roorkee - Formal Verification of Security Protocols

**Input:** Protocol diagram (PNG, JPG, PDF)  
**Output:** Tamarin rules (.spthy file)

---

## 🎯 Task 1: AI Tool for Protocol Verification

This tool automatically generates **Tamarin prover rules** from **protocol sequence diagrams**.

Given a protocol diagram (challenge-response, key exchange, TLS, etc.), the AI:
1. **Parses the diagram** using OCR/vision AI
2. **Extracts protocol structure** (roles, messages, crypto operations)
3. **Generates Tamarin rules** for formal verification
4. **Creates security lemmas** (authentication, secrecy)

---

## 🌟 Features

### Core Features (Always Available)

- ✅ **JSON-based Intermediate Representation (IR)** for protocol definitions
- ✅ **Automatic Tamarin rule generation** from protocol steps
- ✅ **PKI setup rules** (long-term keys, public keys)
- ✅ **Adversary capability rules** (Dolev-Yao model)
- ✅ **Cryptographic operation mapping** (encrypt, decrypt, sign, verify)
- ✅ **Security property (lemma) generation** (authentication, secrecy)
- ✅ **Based on real-world DigiLocker Aadhar authentication** model

### Optional AI Features (Requires OpenAI API Key)

- 🤖 **AI Semantic Inference** - Automatically detect fresh values, crypto operations
- 🤖 **Security Property Suggestions** - LLM-suggested lemmas
- 🤖 **Natural Language Input** - Describe protocols in plain English

> **Note:** The core tool works perfectly without AI! AI features are optional enhancements.

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/tamarin-rule-generator.git
cd tamarin-rule-generator
```

### For Task 1: Diagram → Tamarin Rules

```bash
# Install dependencies for diagram parsing
pip install pillow opencv-python pytesseract pymupdf

# Install OpenAI for AI enhancement (optional but recommended)
pip install openai
export OPENAI_API_KEY=sk-...

# Run the AI tool (Task 1 main entry point)
python task1_ai_tool.py diagram.png -o output.spthy

# Or from PDF
python task1_ai_tool.py protocol.pdf -o output.spthy

# Or from JSON (if you have structured protocol)
python task1_ai_tool.py protocol.json -o output.spthy
```

### Without AI (Template-Based Only)

```bash
# Works without any AI dependencies
python main.py examples/digilocker_aadhar.json -o output/model.spthy

# Run tests
python tests/test_generator.py
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Quick start and usage guide |
| [REPORT.md](REPORT.md) | Full technical documentation |
| [schema.json](schema.json) | JSON IR schema specification |

---

## 📋 Example Input (JSON)

```json
{
  "protocol_name": "My_Protocol",
  "roles": [
    {
      "name": "A",
      "type": "client",
      "long_term_key": "ltkA",
      "public_key": "pkA"
    }
  ],
  "steps": [
    {
      "id": 1,
      "from": "A",
      "to": "B",
      "message": "sign(aenc(<nonce>, pkB), ltkA)",
      "fresh": ["nonce"],
      "crypto_ops": ["encrypt", "sign"],
      "action_fact": "SentMessage"
    }
  ],
  "security_properties": [
    {
      "name": "authentication",
      "type": "authentication",
      "description": "Parties agree on session"
    }
  ]
}
```

---

## 📤 Example Output (Tamarin)

```tamarin
theory My_Protocol
begin

builtins: hashing, asymmetric-encryption, signing

rule RegisterKeys:
  [ Fr(~ltkA), Fr(~ltkB) ]
  -->
  [ !Ltk($A, ~ltkA), !Pk($A, pk(~ltkA)),
    !Ltk($B, ~ltkB), !Pk($B, pk(~ltkB)) ]

rule A_Send_Step1:
  [ Fr(~nonce), !Ltk($A, ltkA), !Pk($B, pkB) ]
  --[ SentMessage($A, $B, ~nonce) ]->
  [ Out(sign(aenc(<~nonce>, pkB), ltkA)) ]

lemma authentication:
  "All A B m #i. Received(A, B, m) @ i
   ==> Ex #j. SentMessage(B, A, m) @ j & j < i"

end
```

---

## 🤖 AI Features (Optional)

The tool can optionally use AI/LLM to enhance protocol definitions:

### Enable AI Features

```bash
# Install OpenAI package
pip install openai

# Set your API key
export OPENAI_API_KEY=sk-...  # Linux/Mac
set OPENAI_API_KEY=sk-...     # Windows
```

### What AI Does

| Feature | Without AI | With AI |
|---------|-----------|---------|
| **Fresh Values** | Manual specification | Auto-inferred from description |
| **Crypto Ops** | Manual specification | Auto-detected from context |
| **Security Lemmas** | Default templates | Custom suggestions |
| **Input Format** | Structured JSON | Natural language |

> **No API key?** The tool works perfectly with manual JSON specification!

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Protocol JSON (examples/*.json)                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Parser (src/parser.py)                                 │
│  - Loads JSON                                           │
│  - Validates schema                                     │
│  - Extracts roles, steps, fresh values                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Generator (src/generator.py)                           │
│  - Applies Tamarin templates (src/templates.py)         │
│  - Generates PKI, adversary, protocol rules             │
│  - Creates security lemmas                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Tamarin Model (output/*.spthy)                         │
│  - Ready for formal verification                        │
│  - Compatible with Tamarin Prover                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

```bash
# Run test suite
python tests/test_generator.py

# Expected output:
# RESULTS: 5 passed, 0 failed ✅
```

---

## 📁 Project Structure

```
tamarin-rule-generator/
├── src/
│   ├── __init__.py       # Package exports
│   ├── parser.py         # JSON parser (dataclasses)
│   ├── templates.py      # Tamarin rule templates
│   └── generator.py      # Main generator engine
├── examples/
│   └── digilocker_aadhar.json   # DigiLocker example
├── output/
│   └── *.spthy           # Generated models
├── tests/
│   └── test_generator.py # Test suite
├── main.py               # CLI interface
├── schema.json           # JSON schema
├── REPORT.md             # Full documentation
├── README.md             # This file
└── LICENSE               # MIT License
```

---

## 🔬 Research Context

This project implements concepts from:

- **Tamarin Prover** - Formal security protocol verification tool
- **DigiLocker Aadhar Authentication** - Real-world Indian national protocol
- **IIT Roorkee** - Formal Verification of DigiLocker (2026)

### References

1. [Tamarin Prover Manual](https://tamarin-prover.com/manual/master/tex/tamarin-manual.pdf)
2. [Tamarin Documentation](https://tamarin-prover.com/documentation.html)
3. Singh Rohit, R. "Formal Verification of DigiLocker with Tamarin." IIT Roorkee, 2026

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎓 Academic Use

This project was developed as part of an IIT Roorkee assignment on formal verification of security protocols. Feel free to use it for:

- ✅ Learning Tamarin prover
- ✅ Understanding protocol verification
- ✅ Building AI-powered code generation tools
- ✅ Academic research

**Citation:**
```bibtex
@software{tamarin_rule_generator,
  author = {Your Name},
  title = {Tamarin Rule Generator: AI-Powered Protocol Model Generation},
  year = {2026},
  url = {https://github.com/YOUR_USERNAME/tamarin-rule-generator}
}
```

---

## 📬 Contact

- **GitHub Issues:** [Report bugs or request features](https://github.com/YOUR_USERNAME/tamarin-rule-generator/issues)
- **Email:** your.email@example.com

---

<div align="center">

**Made with ❤️ for formal verification and security research**

[⬆ Back to Top](#tamarin-rule-generator)

</div>
