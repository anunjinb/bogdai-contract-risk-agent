"""
Tests for JSON schema contract compliance.

Verifies that the BogdAIReport output matches required field shapes.
"""
import pytest
from bogdai.core.schemas import (
    BogdAIReport,
    RiskFlag,
    Citation,
    ReasoningStep,
    OverallAssessment,
    RiskBreakdown,
    AgentTraceEntry,
    GroundingSummary,
    SafetyAndLimits,
    UIHints,
)


def _make_minimal_report() -> BogdAIReport:
    """Build a valid BogdAIReport with one HIGH-risk flag."""
    citation = Citation(
        citation_id="CIT-001",
        source_title="Synthetic Compliance Policy",
        source_document="synthetic_compliance_policy.md",
        section="Deviation Reporting",
        quoted_evidence="Material deviations should be escalated promptly.",
        grounding_layer="Foundry IQ",
        retrieval_confidence=0.91,
    )
    steps = [
        ReasoningStep(step=1, observation="90-day window found.", inference="Long window."),
        ReasoningStep(step=2, observation="Policy says 30 days.", inference="Misaligned."),
        ReasoningStep(step=3, observation="Affects regulated supply.", inference="HIGH risk."),
    ]
    flag = RiskFlag(
        flag_id="FLAG-001",
        clause="4.2",
        title="Deviation Reporting",
        risk_category="Compliance",
        risk_level="HIGH",
        risk_score=90,
        issue="90-day window is too long.",
        clause_excerpt="Shall report within ninety days.",
        business_impact="Audit risk.",
        patient_impact="Treatment delays.",
        reasoning_steps=steps,
        recommendation="Reduce to 30 days.",
        citations=[citation],
        confidence=0.88,
        needs_human_review=True,
    )
    return BogdAIReport(
        schema_version="1.0",
        analysis_id="BDA-2026-0001",
        contract_name="test_contract_1.txt",
        source_document="test_contract_1.txt",
        analysis_date="2026-06-09",
        analysis_mode="synthetic_demo",
        overall_assessment=OverallAssessment(
            overall_risk_level="HIGH",
            risk_score=82,
            summary="1 high-risk clause identified.",
            human_review_required=True,
        ),
        risk_breakdown=RiskBreakdown(high=1, medium=0, low=0, informational=0),
        flags=[flag],
        agent_trace=[
            AgentTraceEntry(agent_name="Contract Intake Agent", role="Intake", output="Done"),
            AgentTraceEntry(agent_name="Clause Extraction Agent", role="Extract", output="Done"),
            AgentTraceEntry(agent_name="Grounding Agent", role="Ground", output="Done"),
            AgentTraceEntry(agent_name="Risk Reasoning Agent", role="Reason", output="Done"),
            AgentTraceEntry(agent_name="Verifier Agent", role="Verify", output="Done"),
            AgentTraceEntry(agent_name="Report Agent", role="Report", output="Done"),
        ],
        grounding_summary=GroundingSummary(
            iq_layer_used="Foundry IQ",
            knowledge_sources_used=["synthetic_compliance_policy.md"],
            total_citations=1,
            unsupported_claims_detected=0,
        ),
        safety_and_limits=SafetyAndLimits(
            synthetic_data_only=True,
            contains_pii=False,
        ),
        ui_hints=UIHints(
            primary_badge="HIGH RISK",
            recommended_next_action="Send to compliance reviewer",
        ),
    )


class TestSchemaContract:
    """Validate the BogdAIReport JSON schema contract."""

    def test_schema_version(self) -> None:
        report = _make_minimal_report()
        assert report.schema_version == "1.0"

    def test_required_top_level_fields(self) -> None:
        report = _make_minimal_report()
        data = report.model_dump()
        required = [
            "schema_version", "analysis_id", "contract_name", "source_document",
            "analysis_date", "analysis_mode", "overall_assessment", "risk_breakdown",
            "flags", "agent_trace", "grounding_summary", "safety_and_limits", "ui_hints",
        ]
        for field in required:
            assert field in data, f"Missing top-level field: {field}"

    def test_overall_assessment_fields(self) -> None:
        report = _make_minimal_report()
        oa = report.overall_assessment
        assert oa.overall_risk_level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert 0 <= oa.risk_score <= 100
        assert isinstance(oa.summary, str) and oa.summary
        assert isinstance(oa.human_review_required, bool)

    def test_flag_has_required_fields(self) -> None:
        report = _make_minimal_report()
        flag = report.flags[0]
        assert flag.flag_id.startswith("FLAG-")
        assert flag.clause
        assert flag.title
        assert flag.risk_category
        assert flag.risk_level in ("HIGH", "MEDIUM", "LOW", "INFORMATIONAL")
        assert 0 <= flag.risk_score <= 100
        assert flag.issue
        assert flag.clause_excerpt
        assert flag.business_impact
        assert flag.patient_impact
        assert flag.recommendation
        assert flag.reasoning_steps
        assert flag.citations

    def test_every_flag_has_at_least_one_citation(self) -> None:
        report = _make_minimal_report()
        for flag in report.flags:
            assert len(flag.citations) >= 1, f"{flag.flag_id} has no citations"

    def test_every_high_risk_flag_has_reasoning_steps(self) -> None:
        report = _make_minimal_report()
        for flag in report.flags:
            if flag.risk_level == "HIGH":
                assert len(flag.reasoning_steps) >= 1, (
                    f"{flag.flag_id} is HIGH but has no reasoning steps"
                )

    def test_every_high_risk_flag_needs_human_review(self) -> None:
        report = _make_minimal_report()
        for flag in report.flags:
            if flag.risk_level == "HIGH":
                assert flag.needs_human_review is True, (
                    f"{flag.flag_id} is HIGH but needs_human_review is False"
                )

    def test_safety_synthetic_data_only(self) -> None:
        report = _make_minimal_report()
        assert report.safety_and_limits.synthetic_data_only is True

    def test_safety_contains_pii_false(self) -> None:
        report = _make_minimal_report()
        assert report.safety_and_limits.contains_pii is False

    def test_citation_confidence_bounds(self) -> None:
        report = _make_minimal_report()
        for flag in report.flags:
            for cit in flag.citations:
                assert 0.0 <= cit.retrieval_confidence <= 1.0

    def test_json_serialization(self) -> None:
        """Verify the report serializes to valid JSON."""
        import json
        report = _make_minimal_report()
        json_str = report.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["schema_version"] == "1.0"
        assert isinstance(parsed["flags"], list)

    def test_risk_breakdown_types(self) -> None:
        report = _make_minimal_report()
        rb = report.risk_breakdown
        assert isinstance(rb.high, int)
        assert isinstance(rb.medium, int)
        assert isinstance(rb.low, int)
        assert isinstance(rb.informational, int)
