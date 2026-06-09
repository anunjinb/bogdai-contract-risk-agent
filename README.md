# BogdAI Contract Risk Agent

> **Microsoft Agents League Hackathon 2026 — Reasoning Agents Track**

AI-powered contract risk monitoring for pharma and healthcare teams.  
Uses a 6-agent pipeline grounded in synthetic knowledge to flag risky clauses, explain reasoning, and return a structured JSON report.

---

## Overview

Pharma and hospital teams sign hundreds of contracts each year. A missed compliance clause, an uncapped liability term, or a 90-day deviation reporting window can delay patient treatment, trigger regulatory action, and expose organizations to significant financial risk.

**BogdAI Contract Risk Agent** reviews synthetic pharma/healthcare contract text through a multi-agent reasoning pipeline and returns a structured JSON risk report with:

- Extracted risk flags by category (Compliance, Financial, Legal, Operational)
- Step-by-step visible reasoning chains per flag
- Grounded citations from synthetic policy documents
- Human-review warnings for all HIGH-risk findings
- Full agent trace for transparency

---

## Hackathon Judging Alignment

| Criterion | Weight | How BogdAI Addresses It |
|-----------|--------|--------------------------|
| **Accuracy & Relevance** | 20% | Contract risks are extracted into structured, categorized flags with clause excerpts and evidence-backed citations |
| **Reasoning & Multi-step Thinking** | 20% | Each flag includes a 3-step reasoning chain (observation → inference); full agent trace shows all 6 agents |
| **Creativity & Originality** | 15% | Pharma/healthcare-specific contract risk monitoring — a high-stakes domain with clear patient impact |
| **User Experience & Presentation** | 15% | Stable, predictable JSON contract supports any frontend; `agent.py` CLI demos the full pipeline |
| **Reliability & Safety** | 20% | Deterministic local fallback, synthetic-only data, PII guardrails, human-review disclaimer |
| **Community Vote** | 10% | Demo video + public repo + clear domain story |

---

## Architecture

```
Synthetic Contract Text
        │
        ▼
┌─────────────────────┐
│  Contract Intake    │  Extracts metadata, validates synthetic marker
│  Agent              │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Clause Extraction  │  Pattern-tags clauses by risk category
│  Agent              │  (Compliance, Pricing, Liability, Delivery...)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Grounding Agent    │  Retrieves citations from synthetic knowledge docs
│  (Foundry IQ layer) │  → synthetic_compliance_policy.md
└────────┬────────────┘     → synthetic_pharma_contracting_guidelines.md
         │                  → synthetic_healthcare_procurement_rules.md
         ▼
┌─────────────────────┐
│  Risk Reasoning     │  Produces 3-step reasoning chain per flag
│  Agent              │  Assigns risk level + score
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Verifier Agent     │  Checks citations, excerpts, safety warnings
│  (Safety guardrail) │  Auto-applies human-review flag for HIGH risks
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Report Agent       │  Pydantic-validates → final JSON report
└─────────────────────┘
         │
         ▼
  BogdAIReport JSON
```

---

## Microsoft Foundry Integration

BogdAI uses **Foundry IQ** as the knowledge grounding layer. When configured:

1. `agent.py --smoke-test` connects to your Azure AI project endpoint.
2. Makes a test call to the configured `gpt-4o` deployment.
3. If successful, Foundry mode is used for the analysis.
4. If not configured or unavailable, the local deterministic fallback runs automatically.

The grounding layer is always labeled `"grounding_layer": "Foundry IQ"` in the JSON output, matching the Microsoft IQ intelligence layer requirement.

---

## Local Setup

### Prerequisites

- Python 3.10+
- Git

### Install

```powershell
git clone https://github.com/anunjinb/bogdai-contract-risk-agent.git
cd bogdai-contract-risk-agent
git checkout dev

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your Azure credentials:

```powershell
Copy-Item .env.example .env
```

```
AZURE_AI_PROJECT_ENDPOINT=https://your-foundry-project-endpoint
AZURE_AI_MODEL_DEPLOYMENT=gpt-4o
BOGDAI_USE_FOUNDRY=true
BOGDAI_ALLOW_LOCAL_FALLBACK=true
```

> ⚠️ **Never commit `.env` to version control.** It is listed in `.gitignore`.

---

## Running the Backend

### Local fallback demo (no Azure credentials needed)

```powershell
python agent.py
```

### Analyze a specific contract

```powershell
python agent.py --analyze bogdai/data/synthetic_contracts/test_contract_1.txt
python agent.py --analyze bogdai/data/synthetic_contracts/test_contract_2.txt
```

### Foundry smoke test

```powershell
python agent.py --smoke-test
```

### Force Foundry mode (with fallback)

```powershell
python agent.py --foundry --analyze bogdai/data/synthetic_contracts/test_contract_1.txt
```

### Force local-only mode

```powershell
python agent.py --local-only
```

---

## Running Tests

```powershell
python -m pytest tests/ -v
```

Tests verify:
- JSON schema contract compliance
- All flags have citations and reasoning steps
- HIGH-risk flags require human review
- Agent trace includes all 6 required agents
- Synthetic data markers are present
- No PII or secrets in any file
- Both synthetic contracts can be analyzed
- Local fallback works without Azure credentials

---

## Example JSON Output

```json
{
  "schema_version": "1.0",
  "analysis_id": "BDA-2026-0001",
  "contract_name": "test_contract_1.txt",
  "analysis_mode": "synthetic_demo",
  "overall_assessment": {
    "overall_risk_level": "HIGH",
    "risk_score": 82,
    "human_review_required": true
  },
  "flags": [
    {
      "flag_id": "FLAG-001",
      "risk_level": "HIGH",
      "risk_score": 90,
      "reasoning_steps": [
        {"step": 1, "observation": "...", "inference": "..."},
        {"step": 2, "observation": "...", "inference": "..."},
        {"step": 3, "observation": "...", "inference": "..."}
      ],
      "citations": [
        {
          "grounding_layer": "Foundry IQ",
          "retrieval_confidence": 0.91
        }
      ],
      "needs_human_review": true
    }
  ],
  "safety_and_limits": {
    "synthetic_data_only": true,
    "contains_pii": false,
    "legal_advice_disclaimer": "..."
  }
}
```

---

## Project Structure

```
agent.py                         ← CLI entry point (smoke test + analysis)
requirements.txt
.env.example
bogdai/
  agents/
    intake_agent.py              ← Agent 1: Metadata extraction
    clause_extraction_agent.py   ← Agent 2: Clause tagging
    grounding_agent.py           ← Agent 3: Foundry IQ knowledge retrieval
    risk_reasoning_agent.py      ← Agent 4: Reasoning chains + scoring
    verifier_agent.py            ← Agent 5: Safety checks + citation validation
    report_agent.py              ← Agent 6: Pydantic report assembly
  core/
    config.py                    ← Environment variable loading
    schemas.py                   ← Pydantic JSON contract models
    orchestrator.py              ← Agent pipeline coordinator
    foundry_client.py            ← Azure AI / Foundry connection
    risk_rules.py                ← Deterministic fallback rules
  data/
    synthetic_contracts/
      test_contract_1.txt        ← HIGH-risk sample contract
      test_contract_2.txt        ← Lower-risk sample contract
    synthetic_knowledge/
      synthetic_compliance_policy.md
      synthetic_pharma_contracting_guidelines.md
      synthetic_healthcare_procurement_rules.md
tests/
  test_schema_contract.py
  test_orchestrator.py
  test_synthetic_data_safety.py
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `python-dotenv` | Load `.env` variables |
| `pydantic>=2` | JSON schema enforcement |
| `pytest` | Test suite |
| `azure-identity` | `DefaultAzureCredential` for Foundry auth |

Microsoft Foundry SDK (`azure-ai-projects`) is used when available. If not installed, the local deterministic fallback runs transparently.

---

## Responsible AI & Legal Disclaimer

> ⚠️ **This project uses synthetic data only.** No real patient data, real hospital contracts, real company information, or personally identifiable information (PII) is used anywhere in this repository.

> ⚠️ **This tool is for hackathon demonstration only.** It does not constitute legal, regulatory, clinical, or compliance advice. All risk flags require human review by qualified professionals before any action is taken.

> ⚠️ **All sample contracts and knowledge documents are fictitious** and created solely for demonstrating multi-agent reasoning capability.

---

## Submission Information

- **Hackathon**: Microsoft Agents League @ AI Skills Fest 2026
- **Track**: Reasoning Agents (Microsoft Foundry)
- **Microsoft IQ Layer**: Foundry IQ (knowledge grounding)
- **Submission Deadline**: June 14, 2026

---

## Status

🚧 In development — Agents League Hackathon 2026 | Branch: `dev`
