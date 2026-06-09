# Repository Guidelines

## Project Structure & Module Organization

This repository contains a Python contract-risk agent for synthetic pharma and healthcare agreements.

- `agent.py` is the CLI entry point for smoke tests and local analysis.
- `bogdai/agents/` contains the six-agent pipeline: intake, clause extraction, grounding, reasoning, verification, and reporting.
- `bogdai/core/` contains schemas, orchestration, configuration, risk rules, and the Foundry client.
- `bogdai/data/synthetic_contracts/` and `bogdai/data/synthetic_knowledge/` hold demo-safe sample inputs and grounding documents.
- `tests/` contains pytest coverage for schemas, orchestration, and synthetic-data safety.
- `.env.example` documents non-secret configuration; `.env` must remain local.

## Build, Test, and Development Commands

Create and activate a virtual environment before installing dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the local agent smoke test:

```powershell
python agent.py --smoke-test
```

Run the test suite:

```powershell
pytest
```

Use `.env.example` as the template when configuring Azure AI Project or model deployment settings.

## Coding Style & Naming Conventions

Use Python 3.10+ with 4-space indentation and type hints on public functions. Keep Streamlit or CLI presentation code separate from provider, orchestration, and scoring logic. Use `snake_case` for files, functions, and variables; use `PascalCase` for Pydantic models and classes. Prefer small modules with a single clear responsibility.

## Testing Guidelines

Use `pytest`. Name test files `test_*.py` and place them in `tests/`, mirroring source modules where practical. Prioritize tests for clause extraction, severity scoring, schema validation, prompt construction, fallback behavior, and provider error handling. Do not call Azure or external services in unit tests; use fixtures, mocks, or deterministic local fallbacks.

## Commit & Pull Request Guidelines

Recent history uses short, imperative commit subjects such as `Update README with project details and status` and `Fix Foundry client to use azure-ai-projects v2.1.0 API; add openai dep`. Continue that style: start with a verb and state the change plainly.

Pull requests should include a concise summary, testing notes, linked issue or hackathon task when applicable, and screenshots for any UI changes. Call out new environment variables, Azure resource assumptions, model deployments, or data files.

## Security & Configuration Tips

Never commit API keys, real customer contracts, PHI, PII, or regulated agreements. Keep samples synthetic and clearly labeled. Store secrets in environment variables such as `AZURE_OPENAI_API_KEY`, and document required settings in `.env.example`.
