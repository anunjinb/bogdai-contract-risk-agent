"""FastAPI server for BogdAI contract analysis."""
from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from bogdai.core.config import settings
from bogdai.core.orchestrator import BogdAIOrchestrator

app = FastAPI(title="BogdAI API", version="1.0")

# Allow local frontend/backend origins used in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://[::1]:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze")
async def analyze_contract(file: UploadFile = File(...)) -> dict:
    """Analyze an uploaded .txt contract and return BogdAIReport JSON."""
    filename = file.filename or "uploaded_contract.txt"
    if not filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported.")

    raw = await file.read()
    try:
        contract_text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be UTF-8 encoded text.",
        ) from exc

    orchestrator = BogdAIOrchestrator()
    foundry_mode = (
        "foundry"
        if settings.use_foundry and settings.foundry_available
        else "local_fallback"
    )

    try:
        report = orchestrator.analyze_text(
            contract_text=contract_text,
            source_path=filename,
            foundry_mode=foundry_mode,
        )
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc

    return report.model_dump()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("bogdai.api.server:app", host="127.0.0.1", port=8000, reload=True)
