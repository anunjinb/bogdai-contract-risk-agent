"""
Report Agent.

Converts the full verified result into the final BogdAIReport — a stable,
predictable JSON response contract for the UI layer.

This is the last agent in the pipeline and produces a Pydantic-validated
BogdAIReport object.
"""
from __future__ import annotations

import logging
from datetime import date
from typing import Dict, Any, List

from bogdai.core.schemas import (
    BogdAIReport,
    OverallAssessment,
    RiskBreakdown,
    RiskFlag,
    ReasoningStep,
    Citation,
    AgentTraceEntry,
    GroundingSummary,
    SafetyAndLimits,
    UIHints,
)

logger = logging.getLogger(__name__)

# Required agent names that must appear in every trace
REQUIRED_AGENTS = [
    "Contract Intake Agent",
    "Clause Extraction Agent",
    "Grounding Agent",
    "Risk Reasoning Agent",
    "Verifier Agent",
    "Report Agent",
]


class ReportAgent:
    """
    Agent 6: Report.

    Formats the final Pydantic-validated JSON response for UI display.
    """

    name = "Report Agent"
    role = "Formatted the final JSON response for UI display."

    def run(
        self,
        intake_result: Dict[str, Any],
        grounding_result: Dict[str, Any],
        verifier_result: Dict[str, Any],
        foundry_mode: str = "local_fallback",
        analysis_id: str = "BDA-2026-0001",
    ) -> BogdAIReport:
        """
        Assemble and validate the final BogdAIReport.

        Args:
            intake_result: Output from ContractIntakeAgent.
            grounding_result: Output from GroundingAgent.
            verifier_result: Output from VerifierAgent.
            foundry_mode: 'foundry' or 'local_fallback'.
            analysis_id: Unique ID for this analysis run.

        Returns:
            A fully validated BogdAIReport instance.
        """
        logger.info("[ReportAgent] Assembling final report.")

        verified_flags: List[Dict[str, Any]] = verifier_result.get("verified_flags", [])
        pydantic_flags = [self._to_risk_flag(f) for f in verified_flags]

        # Build breakdown counts
        breakdown = self._build_breakdown(pydantic_flags)

        # Compute overall assessment
        overall = self._compute_overall(pydantic_flags, breakdown)

        # Build agent trace
        agent_trace = self._build_trace(
            intake_result, grounding_result, verifier_result, foundry_mode
        )

        # Build grounding summary
        sources = grounding_result.get("knowledge_sources_used", [])
        grounding_summary = GroundingSummary(
            iq_layer_used="Foundry IQ",
            knowledge_sources_used=sources,
            total_citations=sum(len(f.citations) for f in pydantic_flags),
            unsupported_claims_detected=verifier_result.get("unsupported_claims_detected", 0),
        )

        # Build UI hints
        ui_hints = self._build_ui_hints(overall)

        report = BogdAIReport(
            schema_version="1.0",
            analysis_id=analysis_id,
            contract_name=intake_result.get("contract_name", "unknown.txt"),
            source_document=intake_result.get("source_document", "unknown.txt"),
            analysis_date=intake_result.get("analysis_date", date.today().isoformat()),
            analysis_mode="synthetic_demo",
            overall_assessment=overall,
            risk_breakdown=breakdown,
            flags=pydantic_flags,
            agent_trace=agent_trace,
            grounding_summary=grounding_summary,
            safety_and_limits=SafetyAndLimits(
                synthetic_data_only=True,
                contains_pii=False,
                legal_advice_disclaimer=(
                    "This analysis is for hackathon demonstration only and does not "
                    "replace legal, regulatory, clinical, or compliance review."
                ),
                requires_human_approval_before_action=True,
            ),
            ui_hints=ui_hints,
        )

        logger.info("[ReportAgent] Report assembled. Overall risk: %s", overall.overall_risk_level)
        return report

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_risk_flag(flag_dict: Dict[str, Any]) -> RiskFlag:
        """Convert a raw flag dict to a validated RiskFlag Pydantic model."""
        citations = [
            Citation(
                citation_id=c["citation_id"],
                source_title=c.get("source_title", ""),
                source_document=c.get("source_document", ""),
                section=c.get("section", ""),
                quoted_evidence=c.get("quoted_evidence", ""),
                grounding_layer=c.get("grounding_layer", "Foundry IQ"),
                retrieval_confidence=float(c.get("retrieval_confidence", 0.75)),
            )
            for c in flag_dict.get("citations", [])
        ]

        steps = [
            ReasoningStep(
                step=s["step"],
                observation=s.get("observation", ""),
                inference=s.get("inference", ""),
            )
            for s in flag_dict.get("reasoning_steps", [])
        ]

        return RiskFlag(
            flag_id=flag_dict["flag_id"],
            clause=flag_dict.get("clause", "N/A"),
            title=flag_dict.get("title", ""),
            risk_category=flag_dict.get("risk_category", "General"),
            risk_level=flag_dict.get("risk_level", "MEDIUM"),
            risk_score=int(flag_dict.get("risk_score", 50)),
            issue=flag_dict.get("issue", ""),
            clause_excerpt=flag_dict.get("clause_excerpt", ""),
            business_impact=flag_dict.get("business_impact", ""),
            patient_impact=flag_dict.get("patient_impact", ""),
            reasoning_steps=steps,
            recommendation=flag_dict.get("recommendation", ""),
            citations=citations,
            confidence=float(flag_dict.get("confidence", 0.75)),
            needs_human_review=bool(flag_dict.get("needs_human_review", False)),
        )

    @staticmethod
    def _build_breakdown(flags: List[RiskFlag]) -> RiskBreakdown:
        counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFORMATIONAL": 0}
        for flag in flags:
            level = flag.risk_level.upper()
            if level in counts:
                counts[level] += 1
        return RiskBreakdown(
            high=counts["HIGH"],
            medium=counts["MEDIUM"],
            low=counts["LOW"],
            informational=counts["INFORMATIONAL"],
        )

    @staticmethod
    def _compute_overall(
        flags: List[RiskFlag], breakdown: RiskBreakdown
    ) -> OverallAssessment:
        """Derive overall risk level and score from flag distribution."""
        if breakdown.high >= 3:
            level = "CRITICAL"
            base_score = 90
        elif breakdown.high >= 1:
            level = "HIGH"
            base_score = 75
        elif breakdown.medium >= 2:
            level = "MEDIUM"
            base_score = 55
        elif breakdown.medium >= 1:
            level = "LOW"
            base_score = 35
        else:
            level = "LOW"
            base_score = 20

        # Weighted average of flag scores
        if flags:
            avg_score = sum(f.risk_score for f in flags) / len(flags)
            final_score = int((base_score + avg_score) / 2)
        else:
            final_score = base_score

        high_count = breakdown.high
        med_count = breakdown.medium
        summary_parts = []
        if high_count:
            summary_parts.append(f"{high_count} high-risk clause(s)")
        if med_count:
            summary_parts.append(f"{med_count} medium-risk clause(s)")

        if flags:
            top_issues = [f.title for f in flags[:3]]
            summary = (
                f"{', '.join(summary_parts)} identified. "
                f"Key issues: {'; '.join(top_issues)}."
            )
        else:
            summary = "No significant risk flags detected in this contract."

        return OverallAssessment(
            overall_risk_level=level,
            risk_score=min(final_score, 100),
            summary=summary,
            human_review_required=breakdown.high > 0,
        )

    def _build_trace(
        self,
        intake_result: Dict[str, Any],
        grounding_result: Dict[str, Any],
        verifier_result: Dict[str, Any],
        foundry_mode: str,
    ) -> List[AgentTraceEntry]:
        """Build the ordered agent trace list."""
        iq_label = "Foundry IQ" if foundry_mode == "foundry" else "Foundry IQ (local synthetic fallback)"

        return [
            AgentTraceEntry(
                agent_name="Contract Intake Agent",
                role="Prepared the uploaded contract for analysis.",
                output=(
                    f"Detected contract '{intake_result.get('contract_name')}' "
                    f"with {len(intake_result.get('sections_detected', []))} sections "
                    f"and {intake_result.get('word_count', 0)} words. "
                    f"Synthetic: {intake_result.get('is_synthetic', False)}."
                ),
            ),
            AgentTraceEntry(
                agent_name="Clause Extraction Agent",
                role="Identified contract clauses relevant to pharma and healthcare risk.",
                output="Extracted compliance, pricing, liability, reporting, and delivery clauses.",
            ),
            AgentTraceEntry(
                agent_name="Grounding Agent",
                role="Retrieved supporting evidence from approved synthetic knowledge sources.",
                tool_used=iq_label,
                output=grounding_result.get("output_summary", "Citations retrieved."),
            ),
            AgentTraceEntry(
                agent_name="Risk Reasoning Agent",
                role="Compared contract language against grounded rules and inferred risk severity.",
                output="Assigned risk levels and produced step-by-step reasoning.",
            ),
            AgentTraceEntry(
                agent_name="Verifier Agent",
                role="Checked for unsupported claims, missing citations, and unsafe recommendations.",
                output=verifier_result.get(
                    "output_summary",
                    "Verification complete.",
                ),
            ),
            AgentTraceEntry(
                agent_name="Report Agent",
                role="Formatted the final JSON response for UI display.",
                output="Generated structured risk report.",
            ),
        ]

    @staticmethod
    def _build_ui_hints(overall: OverallAssessment) -> UIHints:
        level = overall.overall_risk_level
        if level in ("CRITICAL", "HIGH"):
            badge = f"{level} RISK"
            action = "Send to compliance reviewer immediately"
        elif level == "MEDIUM":
            badge = "MEDIUM RISK"
            action = "Schedule compliance review"
        else:
            badge = "LOW RISK"
            action = "File for record — no immediate action required"

        return UIHints(
            primary_badge=badge,
            recommended_next_action=action,
            show_agent_trace=True,
            show_citations=True,
        )
