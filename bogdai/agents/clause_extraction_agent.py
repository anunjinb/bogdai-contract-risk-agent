"""
Clause Extraction Agent.

Identifies clauses related to risk categories: regulatory compliance,
deviation reporting, pricing, delivery/supply, liability, audit rights,
termination, and patient-impacting delays.

Returns clause IDs, titles, excerpts, and clause categories.
"""
from __future__ import annotations

import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Map of risk category → patterns to identify clauses of that type
CLAUSE_PATTERNS: Dict[str, List[str]] = {
    "Compliance": [
        r"compli\w*",
        r"regulat\w*",
        r"gmp\b",
        r"fda\b",
        r"cder\b",
        r"quality\s+system",
    ],
    "Deviation Reporting": [
        r"deviation\w*",
        r"report\w*\s+material",
        r"material\s+\w+\s+report",
        r"notify\w*\s+within",
        r"within\s+\w+\s+days\s+of\s+(discovery|identification)",
    ],
    "Pricing": [
        r"pric\w*",
        r"fee\w*",
        r"cost\w*\s+adjust",
        r"market\s+condition",
        r"price\s+may\s+change",
        r"subject\s+to\s+adjustment",
    ],
    "Supply / Delivery": [
        r"deliver\w*",
        r"supply\w*",
        r"shipment\w*",
        r"lead\s+time",
        r"subject\s+to\s+availability",
    ],
    "Liability": [
        r"liabilit\w*",
        r"indemni\w*",
        r"damag\w*",
        r"cap\s+on\s+liabilit",
        r"unlimited\s+liabilit",
    ],
    "Audit": [
        r"audit\w*",
        r"inspection\w*",
        r"right\s+to\s+review",
        r"access\s+to\s+records",
    ],
    "Termination": [
        r"terminat\w*",
        r"cancel\w*",
        r"expir\w*",
    ],
    "Force Majeure": [
        r"force\s+majeure",
        r"act\s+of\s+god",
        r"unforeseen\s+event",
    ],
    "Confidentiality": [
        r"confidential\w*",
        r"non-disclosure",
        r"nda\b",
    ],
    "Governing Law": [
        r"govern\w*\s+law",
        r"jurisdiction",
        r"dispute\s+resolution",
        r"arbitrat\w*",
    ],
}


class ClauseExtractionAgent:
    """
    Agent 2: Clause Extraction.

    Identifies and tags contract clauses by risk category.
    """

    name = "Clause Extraction Agent"
    role = "Identified contract clauses relevant to pharma and healthcare risk."

    def run(self, intake_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract clauses from the ingested contract text.

        Args:
            intake_result: Output from ContractIntakeAgent.

        Returns:
            dict with key ``clauses``: a list of clause dicts, each with:
            clause_id, category, title, excerpt, line_start.
        """
        logger.info("[ClauseExtractionAgent] Starting clause extraction.")
        raw_text: str = intake_result["raw_text"]
        clauses = self._extract_clauses(raw_text)
        logger.info("[ClauseExtractionAgent] Extracted %d clauses.", len(clauses))

        return {
            "clauses": clauses,
            "clause_count": len(clauses),
            "output_summary": (
                f"Extracted {len(clauses)} clauses covering compliance, pricing, "
                "liability, reporting, and delivery topics."
            ),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Split text into paragraphs and tag each by risk category."""
        paragraphs = self._split_paragraphs(text)
        clauses: List[Dict[str, Any]] = []
        clause_index = 1

        for para_idx, para in enumerate(paragraphs):
            categories = self._classify_paragraph(para)
            if not categories:
                continue

            # Extract a clean clause reference from the paragraph opening
            clause_ref = self._extract_clause_ref(para, para_idx)

            clauses.append(
                {
                    "clause_id": f"CLS-{clause_index:03d}",
                    "clause_ref": clause_ref,
                    "categories": categories,
                    "title": self._title_for_categories(categories),
                    "excerpt": para[:400].strip(),
                    "paragraph_index": para_idx,
                }
            )
            clause_index += 1

        return clauses

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split on blank lines or numbered section headers."""
        # Split on blank lines first
        raw_paras = re.split(r"\n\s*\n", text)
        result = []
        for para in raw_paras:
            stripped = para.strip()
            if stripped and len(stripped) > 20:
                result.append(stripped)
        return result

    def _classify_paragraph(self, para: str) -> List[str]:
        """Return list of category names that match the paragraph."""
        para_lower = para.lower()
        matched: List[str] = []
        for category, patterns in CLAUSE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, para_lower):
                    if category not in matched:
                        matched.append(category)
                    break
        return matched

    @staticmethod
    def _extract_clause_ref(para: str, para_idx: int) -> str:
        """Try to find a numeric clause reference like '4.2' or 'Section 3'."""
        match = re.match(r"^(\d+\.\d+|\d+\.|\bSection\s+\d+\b)", para.strip())
        if match:
            return match.group(1).strip().rstrip(".")
        return str(para_idx + 1)

    @staticmethod
    def _title_for_categories(categories: List[str]) -> str:
        return " / ".join(categories[:2])
