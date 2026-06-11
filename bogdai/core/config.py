"""
BogdAI configuration loader.

Reads environment variables (from .env or real environment) and exposes
a typed Config dataclass to the rest of the application.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Runtime configuration for BogdAI Contract Risk Agent."""

    # Microsoft Foundry / Azure AI
    azure_ai_project_endpoint: str = field(
        default_factory=lambda: os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
    )
    azure_ai_model_deployment: str = field(
        default_factory=lambda: os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")
    )

    # BogdAI runtime flags
    use_foundry: bool = field(
        default_factory=lambda: os.getenv("BOGDAI_USE_FOUNDRY", "true").lower() == "true"
    )
    allow_local_fallback: bool = field(
        default_factory=lambda: os.getenv("BOGDAI_ALLOW_LOCAL_FALLBACK", "true").lower() == "true"
    )

    @property
    def foundry_available(self) -> bool:
        """Return True only if both endpoint and deployment are configured."""
        return bool(self.azure_ai_project_endpoint and self.azure_ai_model_deployment)


# Singleton instance used across the app
settings = Config()
