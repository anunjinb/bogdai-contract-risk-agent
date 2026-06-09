"""
Verifier Agent.

Checks every risk flag for:
  - Missing citation
  - Unsupported claim (no quoted evidence)
  - Missing clause excerpt
  - Unsafe legal/medical advice
  - Absence of human-review warning for HIGH-risk issues

Adds verification_status and any warnings to each flag.
This agent implements the safety guardrail layer.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Phrases that constitute unsafe legal/medical advice
UNSAFE_PATTERNS = [
    "you should sign",
    "this contract is safe",
    "no legal risk",
    "medically approved",
    "clinically safe",
    "legal advice",
    "guaranteed compliance",
]


class VerifierAgent:
    """
    Agent 5: Verifier.

    Validates every risk flag for completeness, safety, and accuracy.
    Adds 'verification_status' and 'verification_warnings' to each flag.
    """

    name = "Verifier Agent"
    role = "Checked for unsupported claims, missing citations, and unsafe recommendations."

    def run(self, reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify all risk flags.

        Args:
            reasoning_result: Output from RiskReasoningAgent.

        Returns:
            dict with key ``verified_flags``: list of verified flag dicts.
        """
        flags: List[Dict[str, Any]] = reasoning_result.get("risk_flags", [])
        logger.info("[VerifierAgent] Verifying %d flags.", len(flags))

        verified_flags: List[Dict[str, Any]] = []
        unsupported_count = 0

        for flag in flags:
            warnings: List[str] = []
            status = "VERIFIED"

            # Check 1: At least one citation
            citations = flag.get("citations", [])
            if not citations:
                warnings.append("MISSING_CITATION: No citation attached to this flag.")
                status = "NEEDS_REVIEW"
                unsupported_count += 1

            # Check 2: Citation has quoted evidence
            for cit in citations:
                if not cit.get("quoted_evidence", "").strip():
                    warnings.append(
                        f"UNSUPPORTED_CLAIM: Citation {cit.get('citation_id', '?')} "
                        "has no quoted evidence."
                    )
                    status = "NEEDS_REVIEW"
                    unsupported_count += 1

            # Check 3: Clause excerpt present
            if not flag.get("clause_excerpt", "").strip():
                warnings.append("MISSING_EXCERPT: No clause excerpt provided.")
                status = "NEEDS_REVIEW"

            # Check 4: Reasoning steps present
            if not flag.get("reasoning_steps"):
                warnings.append("MISSING_REASONING: No reasoning steps found.")
                status = "NEEDS_REVIEW"

            # Check 5: HIGH risk must have needs_human_review = True
            if flag.get("risk_level") == "HIGH" and not flag.get("needs_human_review", False):
                warnings.append(
                    "SAFETY_VIOLATION: HIGH-risk flag must require human review."
                )
                flag["needs_human_review"] = True  # Auto-correct
                status = "CORRECTED"

            # Check 6: Recommendation must not contain unsafe advice
            recommendation = flag.get("recommendation", "")
            issue = flag.get("issue", "")
            unsafe = self._check_unsafe_advice(recommendation + " " + issue)
            if unsafe:
                warnings.append(
                    f"UNSAFE_CONTENT: Recommendation contains potentially unsafe language: {unsafe}"
                )
                status = "NEEDS_REVIEW"

            # Append verification metadata to flag
            verified_flag = {
                **flag,
                "verification_status": status,
                "verification_warnings": warnings,
            }
            verified_flags.append(verified_flag)

        logger.info(
            "[VerifierAgent] Verification complete. Unsupported claims: %d",
            unsupported_count,
        )

        return {
            "verified_flags": verified_flags,
            "unsupported_claims_detected": unsupported_count,
            "output_summary": (
                f"Marked {sum(1 for f in verified_flags if f['risk_level'] == 'HIGH')} "
                "high-risk flags as requiring human legal/compliance review."
            ),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_unsafe_advice(text: str) -> str:
        """Return the offending phrase if unsafe language is detected."""
        text_lower = text.lower()
        for phrase in UNSAFE_PATTERNS:
            if phrase in text_lower:
                return phrase
        return ""
