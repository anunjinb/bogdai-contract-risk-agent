"""
Contract Intake Agent.

Accepts contract text or a path to a local synthetic contract file.
Extracts metadata such as contract name, source document, analysis date,
and detected sections.

Agent responsibility:
  - Validate the document is synthetic demo data.
  - Produce a structured intake result for downstream agents.
"""
from __future__ import annotations

import logging
import os
from datetime import date
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Known section headers to look for in pharma/healthcare contracts
KNOWN_SECTIONS = [
    "definitions",
    "scope",
    "pricing",
    "payment",
    "delivery",
    "supply",
    "compliance",
    "regulatory",
    "deviation",
    "reporting",
    "liability",
    "indemnif",
    "audit",
    "termination",
    "dispute",
    "confidential",
    "intellectual property",
    "force majeure",
    "governing law",
]


class ContractIntakeAgent:
    """
    Agent 1: Contract Intake.

    Prepares the raw contract text for downstream analysis.
    """

    name = "Contract Intake Agent"
    role = "Prepared the uploaded contract for analysis."

    def run(self, contract_text: str, source_path: str = "") -> Dict[str, Any]:
        """
        Process raw contract text.

        Args:
            contract_text: The full contract content as a string.
            source_path: Optional filesystem path for the source file.

        Returns:
            dict with keys: contract_name, source_document, analysis_date,
            sections_detected, word_count, is_synthetic, raw_text, intake_ok.
        """
        logger.info("[IntakeAgent] Starting contract intake.")

        # Derive display name from path or fallback
        if source_path:
            contract_name = os.path.basename(source_path)
        else:
            contract_name = "unnamed_contract.txt"

        sections_detected = self._detect_sections(contract_text)
        is_synthetic = self._check_synthetic(contract_text)
        word_count = len(contract_text.split())

        if not is_synthetic:
            logger.warning(
                "[IntakeAgent] Document does not contain a synthetic-data marker. "
                "Proceeding with caution — do not use with real contract data."
            )

        result: Dict[str, Any] = {
            "contract_name": contract_name,
            "source_document": contract_name,
            "analysis_date": date.today().isoformat(),
            "sections_detected": sections_detected,
            "word_count": word_count,
            "is_synthetic": is_synthetic,
            "raw_text": contract_text,
            "intake_ok": True,
        }

        logger.info(
            "[IntakeAgent] Intake complete. Sections: %s | Words: %d | Synthetic: %s",
            sections_detected,
            word_count,
            is_synthetic,
        )
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _detect_sections(self, text: str) -> List[str]:
        """Return section labels found in the contract text."""
        text_lower = text.lower()
        return [s.title() for s in KNOWN_SECTIONS if s in text_lower]

    @staticmethod
    def _check_synthetic(text: str) -> bool:
        """Return True if the text contains a synthetic-data marker."""
        markers = ["synthetic", "demo", "fictitious", "test contract", "sample contract"]
        text_lower = text.lower()
        return any(m in text_lower for m in markers)
