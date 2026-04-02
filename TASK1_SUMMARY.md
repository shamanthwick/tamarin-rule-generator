# Task 1 Submission Summary

## AI Tool for Generating Tamarin Rules from Protocol Diagrams

**Student:** [Your Name]  
**Course:** Formal Verification of Security Protocols  
**Instructor:** Prof. Raghavendra Singh Rohit, IIT Roorkee  
**Date:** [Submission Date]

---

## ✅ Task 1 Requirements (From Professor's Transcript)

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| **Input:** Protocol diagram (PNG, PDF) | ✅ Complete | `diagram_parser.py` with OCR |
| **Extract:** Message sequences | ✅ Complete | Vision AI extracts roles, arrows |
| **Generate:** Tamarin rules | ✅ Complete | `generator.py` with templates |
| **Handle:** Key setup rules | ✅ Complete | `RegisterKeys` auto-generated |
| **Generic:** Multiple protocols | ✅ Complete | Pattern-based extraction |
| **AI-based:** "Develop an AI tool" | ✅ Complete | OCR + LLM enhancement |

---

## 🎯 Solution Overview

### The AI Pipeline

```
Protocol Diagram (PNG/PDF)
        ↓
[AI Component 1: Vision/OCR]
        ↓
Extracted Protocol Structure
        ↓
[AI Component 2: LLM Enhancement]
        ↓
Enhanced Protocol JSON
        ↓
[Template Generator]
        ↓
Tamarin Rules (.spthy)
```

---

## 📁 Deliverables

### Main Entry Point

**File:** `task1_ai_tool.py`

```bash
# Usage
python task1_ai_tool.py protocol_diagram.png -o output.spthy
```

### AI Components

| File | Purpose | AI Technology |
|------|---------|---------------|
| `src/diagram_parser.py` | Parse diagram images | OCR (Tesseract) + Computer Vision |
| `src/ai_analyzer.py` | Semantic enhancement | LLM (GPT-4) |
| `src/generator.py` | Tamarin rule generation | Template-based |

### Supporting Files

- `README.md` - Usage documentation
- `AI_USAGE.md` - AI component documentation
- `REPORT.md` - Technical report
- `examples/digilocker_aadhar.json` - Example protocol
- `tests/test_generator.py` - Test suite (5/5 passing)

---

## 🔧 How to Use

### Step 1: Install Dependencies

```bash
# For diagram parsing (Vision AI)
pip install pillow opencv-python pytesseract pymupdf

# For AI enhancement (LLM)
pip install openai
export OPENAI_API_KEY=sk-...
```

### Step 2: Run the AI Tool

```bash
# From diagram image
python task1_ai_tool.py tls_handshake.png -o tls.spthy

# From PDF diagram
python task1_ai_tool.py protocol.pdf -o output.spthy

# From JSON (structured protocol)
python task1_ai_tool.py protocol.json -o output.spthy
```

### Step 3: Verify Output

```bash
# View generated Tamarin rules
type output.spthy

# Verify with Tamarin prover
tamarin-prover output.spthy
```

---

## 📊 Example: DigiLocker Aadhar Authentication

### Input (Diagram Description)

```
User → DigiLocker: Aadhaar + OTP
DigiLocker → UIDAI: sign(aenc(AuthXML, pk_UIDAI), ltk_DigiLocker)
UIDAI → DigiLocker: sign(aenc(Response, pk_DigiLocker), ltk_UIDAI)
DigiLocker → User: Authenticated
```

### Output (Generated Tamarin Rules)

```tamarin
theory DigiLocker_Aadhar_Authentication
begin

builtins: hashing, asymmetric-encryption, signing

rule RegisterKeys:
  [ Fr(~ltkD), Fr(~ltkA) ]
  -->
  [ !Ltk($DigiLocker, ~ltkD), !Ltk($UIDAI, ~ltkA),
    !Pk($DigiLocker, pk(~ltkD)), !Pk($UIDAI, pk(~ltkA)) ]

rule DigiLocker_Send_Step2:
  let
    msg = sign(aenc(<~N, <~O, ~Tx>>, pkA), ltkD)
  in
  [ Fr(~N), Fr(~O), Fr(~Tx), !Ltk($DigiLocker, ltkD), !Pk($UIDAI, pkA) ]
  --[ SentAuth($DigiLocker, $UIDAI, ~N, ~O, ~Tx) ]->
  [ Out(msg) ]

lemma authentication:
  "All D A tx #i.
    TrustEstablished(D, tx) @ i
    ==> Ex #j. UIDAIResponded(A, D, tx) @ j & j < i"

end
```

---

## 🎓 AI Technologies Used

### 1. Vision AI / OCR

**Technology:** Tesseract OCR + OpenCV

**Purpose:**
- Extract text from protocol diagram images
- Detect message arrows and participant roles
- Identify cryptographic operations

### 2. Large Language Models

**Technology:** OpenAI GPT-4

**Purpose:**
- Infer protocol semantics from extracted text
- Detect fresh values (nonces, keys)
- Suggest security properties (lemmas)

### 3. Template-Based Generation

**Technology:** Pattern matching from DigiLocker slides

**Purpose:**
- Generate syntactically correct Tamarin rules
- Ensure reliability and correctness
- Based on reference material (IIT Roorkee)

---

## ✅ Academic Integrity

### AI Disclosure

```
This submission uses AI components:

1. Tesseract OCR (Apache 2.0) - Diagram text extraction
2. OpenAI GPT-4 - Semantic enhancement (optional)
3. Pattern-based extraction - Original implementation

Template patterns based on:
- DigiLocker Formal Verification Slides (IIT Roorkee)
- Tamarin Prover Manual
```

### What's Original

- Diagram parser implementation (`diagram_parser.py`)
- AI analyzer integration (`ai_analyzer.py`)
- Template generator (`generator.py`)
- Complete pipeline orchestration (`task1_ai_tool.py`)

---

## 🧪 Testing

### Run Test Suite

```bash
python tests/test_generator.py

# Output:
# RESULTS: 5 passed, 0 failed ✅
```

### Test Coverage

- ✅ Parser validation
- ✅ Code generation
- ✅ Role extraction
- ✅ Fresh value extraction
- ✅ Summary generation

---

## 📋 Repository Structure

```
tamarin-rule-generator/
├── task1_ai_tool.py          ← MAIN ENTRY POINT (Task 1)
├── main.py                    ← Fallback (non-AI)
├── src/
│   ├── diagram_parser.py      ← Vision AI / OCR
│   ├── ai_analyzer.py         ← LLM enhancement
│   ├── parser.py              ← JSON parser
│   ├── templates.py           ← Tamarin templates
│   └── generator.py           ← Code generator
├── examples/
│   └── digilocker_aadhar.json
├── output/
│   └── *.spthy
├── tests/
│   └── test_generator.py
├── README.md
├── AI_USAGE.md
├── REPORT.md
└── TASK1_SUMMARY.md          ← This file
```

---

## 🚀 GitHub Repository

**Repository Name:** `tamarin-rule-generator`

**Description:**
```
AI-powered tool that generates formal Tamarin prover models 
from protocol diagrams. Task 1 submission for IIT Roorkee 
Formal Verification course.
```

**Topics:**
- tamarin-prover
- formal-verification
- security-protocols
- ai-tools
- ocr
- python
- iit-roorkee

---

## 📬 Submission Checklist

- [x] AI tool implemented (`task1_ai_tool.py`)
- [x] Diagram parsing with OCR (`diagram_parser.py`)
- [x] AI enhancement with LLM (`ai_analyzer.py`)
- [x] Tamarin rule generation (`generator.py`)
- [x] Example protocol (DigiLocker)
- [x] Test suite (5 passing tests)
- [x] Documentation (README, AI_USAGE, REPORT)
- [x] This summary document

---

## 🎯 How This Meets Task 1

From professor's transcript:

> "Given a protocol diagram... develop an AI tool that generates the Tamarin rules"

**Our Solution:**

1. ✅ **Accepts protocol diagrams** (PNG, JPG, PDF)
2. ✅ **Uses AI** (OCR + LLM)
3. ✅ **Generates Tamarin rules** (complete .spthy files)
4. ✅ **Generic** (works for multiple protocols)
5. ✅ **Based on reference material** (DigiLocker slides, Tamarin manual)

---

## 💡 Key Innovations

1. **Hybrid AI Approach**
   - AI for understanding (OCR + LLM)
   - Templates for correctness (reliable generation)

2. **Multi-Format Support**
   - Images (PNG, JPG)
   - PDFs
   - JSON (structured)

3. **Optional AI Enhancement**
   - Works with or without OpenAI API
   - Graceful fallback to template-only mode

4. **Academic Integrity**
   - Clear AI disclosure
   - Original implementation
   - Based on course material

---

## 📞 Questions?

See documentation:
- `README.md` - Quick start
- `AI_USAGE.md` - AI component details
- `REPORT.md` - Technical report

---

**Submitted by:** [Your Name]  
**Date:** [Submission Date]  
**Course:** Formal Verification of Security Protocols, IIT Roorkee
