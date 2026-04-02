# 🤖 AI Tool for Generating Tamarin Rules from Protocol Diagrams

> **Task 1 Submission** - Formal Verification of Security Protocols  
> **IIT Roorkee** | Instructor: Prof. Raghvendra Singh Rohit

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 What is This?

This is an **AI-powered tool** that automatically converts **protocol sequence diagrams** (images/PDFs) into **formal Tamarin verification models** (.spthy files).

### The Problem

Security protocols (like TLS, DigiLocker Aadhar auth, challenge-response) need to be **formally verified** to prove they're secure. But writing Tamarin rules manually is:
- ❌ Time-consuming
- ❌ Error-prone  
- ❌ Requires expert knowledge

### The Solution

Our AI tool **automates** this process:

```
Protocol Diagram (PNG/PDF)
        ↓
    [AI TOOL]
        ↓
Tamarin Rules (.spthy) - Ready for verification!
```

---

## 🎯 Task 1 Objective

**From Professor's Requirements:**
> "Given a protocol diagram (sequence of rounds), develop an AI tool that generates the Tamarin rules for the protocol."

### What This Tool Does

| Input | AI Process | Output |
|-------|------------|--------|
| Protocol diagram (PNG, JPG, PDF) | **1. Vision AI/OCR** - Extracts text<br>**2. LLM (GPT-4)** - Infers semantics<br>**3. Template Generator** - Creates rules | Tamarin .spthy file with:<br>- All protocol rules<br>- Security lemmas<br>- Ready for verification |

---

## 🚀 Quick Start - How to Run

### Step 1: Clone the Repository

```bash
git clone https://github.com/shamanthwick/tamarin-rule-generator.git
cd tamarin-rule-generator
```

### Step 2: Install Dependencies

```bash
# For diagram parsing (Vision AI / OCR)
pip install pillow opencv-python pytesseract pymupdf

# For AI enhancement (Optional but recommended)
pip install openai
```

### Step 3: Set Up OpenAI API Key (Optional)

```bash
# Linux/Mac
export OPENAI_API_KEY=sk-...

# Windows
set OPENAI_API_KEY=sk-...
```

> **Note:** AI enhancement is optional. The tool works without it using template-based generation only.

### Step 4: Run the AI Tool

```bash
# From diagram image (PNG, JPG)
python task1_ai_tool.py diagram.png -o output.spthy

# From PDF diagram
python task1_ai_tool.py protocol.pdf -o output.spthy

# From JSON protocol specification
python task1_ai_tool.py protocol.json -o output.spthy
```

### Step 5: Verify the Output

```bash
# View generated Tamarin rules
type output.spthy

# Verify with Tamarin prover (if installed)
tamarin-prover output.spthy
```

---

## 📊 Example: DigiLocker Aadhar Authentication

### Input Protocol Flow

```
User → DigiLocker: Aadhaar + OTP
DigiLocker → UIDAI: sign(aenc(AuthXML, pk_UIDAI), ltk_DigiLocker)
UIDAI → DigiLocker: sign(aenc(Response, pk_DigiLocker), ltk_UIDAI)
DigiLocker → User: Authenticated
```

### Generated Tamarin Rules

```tamarin
theory DigiLocker_Aadhar_Authentication
begin

builtins: hashing, asymmetric-encryption, signing

// PKI Setup
rule RegisterKeys:
  [ Fr(~ltkD), Fr(~ltkA) ]
  -->
  [ !Ltk($DigiLocker, ~ltkD), !Ltk($UIDAI, ~ltkA),
    !Pk($DigiLocker, pk(~ltkD)), !Pk($UIDAI, pk(~ltkA)) ]

// Protocol Execution
rule DigiLocker_Send_Step2:
  let
    msg = sign(aenc(<~N, <~O, ~Tx>>, pkA), ltkD)
  in
  [ Fr(~N), Fr(~O), Fr(~Tx), !Ltk($DigiLocker, ltkD), !Pk($UIDAI, pkA) ]
  --[ SentAuth($DigiLocker, $UIDAI, ~N, ~O, ~Tx) ]->
  [ Out(msg) ]

// Security Properties
lemma authentication:
  "All D A tx #i.
    TrustEstablished(D, tx) @ i
    ==> Ex #j. UIDAIResponded(A, D, tx) @ j & j < i"

end
```

---

## 🏗️ How It Works - AI Pipeline

```
┌─────────────────────────────────────────────────────────┐
│  INPUT: Protocol Diagram                                │
│  (PNG, JPG, PDF showing message sequences)              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  AI Component 1: Vision/OCR (diagram_parser.py)         │
│  - Tesseract OCR extracts text                          │
│  - Detects roles (Alice, Bob, Server, etc.)             │
│  - Identifies message arrows (→)                        │
│  - Parses crypto operations (enc, dec, sign, verify)    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Extracted Protocol Structure                           │
│  {roles: [...], messages: [...], crypto_ops: [...]}     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  AI Component 2: LLM Enhancement (ai_analyzer.py)       │
│  - GPT-4 infers fresh values (nonces, keys)             │
│  - Detects crypto intent                                │
│  - Suggests security properties (lemmas)                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Enhanced Protocol JSON                                 │
│  (Complete with all semantics)                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Template Generator (generator.py)                      │
│  - Applies Tamarin patterns from DigiLocker slides      │
│  - Generates syntactically correct rules                │
│  - Creates security lemmas                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  OUTPUT: Tamarin Model (.spthy)                         │
│  Ready for formal verification                          │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Task 1 Requirements - All Met!

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| **Input:** Protocol diagram (PNG, PDF) | `diagram_parser.py` with OCR | ✅ |
| **Extract:** Message sequences | Vision AI extracts roles, arrows | ✅ |
| **Generate:** Tamarin rules | `generator.py` with templates | ✅ |
| **Handle:** Key setup rules | `RegisterKeys` auto-generated | ✅ |
| **Generic:** Multiple protocols | Pattern-based extraction | ✅ |
| **AI-based:** "Develop an AI tool" | OCR + LLM enhancement | ✅ |

---

## 📁 Project Structure

```
tamarin-rule-generator/
├── task1_ai_tool.py          ← MAIN ENTRY POINT (Run this!)
├── src/
│   ├── diagram_parser.py     ← Vision AI / OCR for diagrams
│   ├── ai_analyzer.py        ← LLM (GPT-4) enhancement
│   ├── parser.py             ← JSON protocol parser
│   ├── templates.py          ← Tamarin rule templates
│   └── generator.py          ← Code generation engine
├── examples/
│   └── digilocker_aadhar.json ← Example protocol
├── output/                    ← Generated .spthy files
├── TASK1_SUBMISSION.html     ← Visual submission document
├── TASK1_SUMMARY.md          ← Summary document
├── AI_USAGE.md               ← AI component documentation
├── CONVERT_TO_PDF.md         ← How to create PDF
└── LICENSE                    ← MIT License
```

---

## 🧠 AI Technologies Used

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Vision AI / OCR** | Tesseract OCR + OpenCV | Extract text from diagrams |
| **LLM Enhancement** | OpenAI GPT-4 | Infer semantics, suggest lemmas |
| **Pattern Recognition** | Regex + Computer Vision | Identify crypto operations |
| **Code Generation** | Template-Based (Python) | Generate correct Tamarin syntax |

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[README.md](README.md)** | This file - Quick start and overview |
| **[TASK1_SUMMARY.md](TASK1_SUMMARY.md)** | Complete Task 1 summary |
| **[AI_USAGE.md](AI_USAGE.md)** | AI components explained |
| **[TASK1_SUBMISSION.html](TASK1_SUBMISSION.html)** | Visual submission (open in browser) |
| **[CONVERT_TO_PDF.md](CONVERT_TO_PDF.md)** | How to create PDF from HTML |

---

## 💡 Key Features

✅ **Accepts Protocol Diagrams** - PNG, JPG, PDF formats  
✅ **AI-Powered Extraction** - Vision AI + LLM for understanding  
✅ **Automatic Rule Generation** - Complete Tamarin .spthy files  
✅ **Security Lemmas** - Authentication, secrecy properties  
✅ **Generic** - Works for multiple protocols (TLS, challenge-response, key exchange)  
✅ **Based on Reference Material** - DigiLocker slides, Tamarin manual  

---

## 🚀 Getting Started in 3 Steps

```bash
# 1. Install
pip install pillow opencv-python pytesseract pymupdf

# 2. Run
python task1_ai_tool.py my_protocol.png -o output.spthy

# 3. Verify
tamarin-prover output.spthy
```

**That's it!** 🎉

---

<div align="center">

**Made with ❤️ for Formal Verification at IIT Roorkee**

</div>
