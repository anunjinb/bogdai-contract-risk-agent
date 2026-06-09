# Repository Guidelines

## Project Structure & Module Organization

This repository is currently minimal: `README.md` documents the project, and implementation files have not yet been added. Keep the Streamlit entry point at the root as `app.py` or under `src/` if the code grows. Place reusable contract-analysis logic in `src/`, tests in `tests/`, sample contracts in `examples/`, and non-secret configuration templates in `.env.example`.

Suggested layout:

```text
app.py
src/
tests/
examples/
.env.example
```

## Build, Test, and Development Commands

Use a virtual environment before installing dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

When the Streamlit app exists, run it locally with:

```powershell
streamlit run app.py
```

When tests are added, run:

```powershell
pytest
```

Add `requirements.txt` or `pyproject.toml` as soon as external packages are introduced.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation, type hints for public functions, and small modules with clear responsibilities. Prefer `snake_case` for functions, variables, and files; use `PascalCase` for classes. Keep AI-provider code isolated from Streamlit UI code so Azure OpenAI, Microsoft Foundry IQ, and scoring logic can be tested independently.

## Testing Guidelines

Use `pytest` for unit tests. Name test files `test_*.py` and keep them in `tests/`, mirroring the source module where practical. Prioritize tests for clause extraction, severity scoring, prompt construction, and error handling around provider responses. Avoid real Azure calls in unit tests; use fixtures or mocks.

## Commit & Pull Request Guidelines

The current git history uses short, imperative commit subjects, for example `Update README with project details and status`. Continue that style: start with a verb and describe the change plainly.

Pull requests should include a short summary, testing notes, linked issue or hackathon task when applicable, and screenshots for Streamlit UI changes. Call out new environment variables, model deployments, or Azure resource assumptions.

## Security & Configuration Tips

Never commit API keys, contract data containing PHI/PII, or real customer agreements. Store secrets in environment variables such as `AZURE_OPENAI_API_KEY` and document required settings in `.env.example`.
