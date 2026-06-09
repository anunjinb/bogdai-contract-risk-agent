"""
BogdAI Foundry Client.

Wraps the Azure AI / Microsoft Foundry connection.  Attempts a real model
call when credentials are present.  Falls back gracefully if they are not.

Authentication uses DefaultAzureCredential (supports AzureCliCredential,
ManagedIdentity, environment, etc.) – no hard-coded credentials.
"""
from __future__ import annotations

import logging
from typing import Optional

from bogdai.core.config import settings

logger = logging.getLogger(__name__)


class FoundryClient:
    """Thin wrapper around the Azure AI / Foundry model endpoint."""

    def __init__(self) -> None:
        self._client = None
        self._mode: str = "uninitialized"

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _try_connect(self) -> bool:
        """
        Attempt to create an Azure AI Projects client.

        Returns True on success, False on any failure.
        """
        if not settings.foundry_available:
            logger.info("[FoundryClient] No endpoint configured — skipping Foundry connection.")
            return False

        try:
            # Lazy import so the app runs without azure-ai-projects installed
            from azure.identity import DefaultAzureCredential  # type: ignore
            from azure.ai.projects import AIProjectClient  # type: ignore

            credential = DefaultAzureCredential()
            self._client = AIProjectClient(
                endpoint=settings.azure_ai_project_endpoint,
                credential=credential,
            )
            logger.info(
                "[FoundryClient] Connected to Azure AI project at %s",
                settings.azure_ai_project_endpoint,
            )
            return True
        except ImportError as exc:
            logger.warning(
                "[FoundryClient] azure-ai-projects SDK not installed (%s). "
                "Using local fallback.",
                exc,
            )
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning(
                "[FoundryClient] Connection failed (%s). Using local fallback.", exc
            )
        return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def smoke_test(self) -> dict:
        """
        Perform a lightweight model call to verify Foundry connectivity.

        Returns a dict with keys: success (bool), mode (str), response (str).
        """
        if not self._try_connect():
            return self._local_smoke_result()

        try:
            # azure-ai-projects v2.1.0: get_openai_client() is on the client directly
            openai_client = self._client.get_openai_client()  # type: ignore
            response = openai_client.chat.completions.create(
                model=settings.azure_ai_model_deployment,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Reply with exactly: 'BogdAI Foundry smoke test OK.' "
                            "Do not add anything else."
                        ),
                    }
                ],
                max_tokens=20,
            )
            content = response.choices[0].message.content.strip()
            logger.info("[FoundryClient] Smoke test SUCCESS: %s", content)
            self._mode = "foundry"
            return {"success": True, "mode": "foundry", "response": content}
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("[FoundryClient] Smoke test call failed (%s). Falling back.", exc)
            return self._local_smoke_result()

    def call_model(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """
        Call the configured model with *prompt*.

        Returns the response string, or None when unavailable.
        """
        if self._client is None:
            if not self._try_connect():
                return None

        try:
            openai_client = self._client.get_openai_client()  # type: ignore
            response = openai_client.chat.completions.create(
                model=settings.azure_ai_model_deployment,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content.strip()
            self._mode = "foundry"
            return content
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("[FoundryClient] Model call failed (%s).", exc)
            return None

    @property
    def mode(self) -> str:
        return self._mode

    # ------------------------------------------------------------------
    # Local fallback helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _local_smoke_result() -> dict:
        logger.info("[FoundryClient] Running local smoke test fallback.")
        return {
            "success": True,
            "mode": "local_fallback",
            "response": (
                "BogdAI local fallback active. "
                "Foundry endpoint not configured or unreachable. "
                "Deterministic analysis engine will be used."
            ),
        }


# Module-level singleton
foundry_client = FoundryClient()
