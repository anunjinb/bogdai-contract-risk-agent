"""
Tests for the full orchestrator pipeline.

Verifies end-to-end analysis of both synthetic contracts using
the local deterministic fallback (no Azure credentials required).
"""
import pytest
from pathlib import Path

from bogdai.core.orchestrator import BogdAIOrchestrator
from bogdai.core.schemas import BogdAIReport

_CONTRACTS_DIR = (
    Path(__file__).parent.parent / "bogdai" / "data" / "synthetic_contracts"
)
_CONTRACT_1 = _CONTRACTS_DIR / "test_contract_1.txt"
_CONTRACT_2 = _CONTRACTS_DIR / "test_contract_2.txt"

REQUIRED_AGENTS = [
    "Contract Intake Agent",
    "Clause Extraction Agent",
    "Grounding Agent",
    "Risk Reasoning Agent",
    "Verifier Agent",
    "Report Agent",
]


@pytest.fixture(scope="module")
def orchestrator() -> BogdAIOrchestrator:
    return BogdAIOrchestrator()


@pytest.fixture(scope="module")
def report_1(orchestrator: BogdAIOrchestrator) -> BogdAIReport:
    """Analyze the HIGH-risk contract."""
    return orchestrator.analyze_file(_CONTRACT_1, foundry_mode="local_fallback")


@pytest.fixture(scope="module")
def report_2(orchestrator: BogdAIOrchestrator) -> BogdAIReport:
    """Analyze the lower-risk contract."""
    return orchestrator.analyze_file(_CONTRACT_2, foundry_mode="local_fallback")


class TestOrchestratorContract1:
    """High-risk contract should produce HIGH flags."""

    def test_report_is_bogdai_report(self, report_1: BogdAIReport) -> None:
        assert isinstance(report_1, BogdAIReport)

    def test_contract_1_is_high_risk(self, report_1: BogdAIReport) -> None:
        assert report_1.overall_assessment.overall_risk_level in ("HIGH", "CRITICAL"), (
            f"Expected HIGH or CRITICAL, got {report_1.overall_assessment.overall_risk_level}"
        )

    def test_contract_1_has_flags(self, report_1: BogdAIReport) -> None:
        assert len(report_1.flags) >= 1, "Contract 1 should produce at least one risk flag"

    def test_all_flags_have_citations(self, report_1: BogdAIReport) -> None:
        for flag in report_1.flags:
            assert len(flag.citations) >= 1, f"{flag.flag_id} has no citations"

    def test_all_high_flags_have_reasoning(self, report_1: BogdAIReport) -> None:
        for flag in report_1.flags:
            if flag.risk_level == "HIGH":
                assert len(flag.reasoning_steps) >= 1

    def test_all_high_flags_need_human_review(self, report_1: BogdAIReport) -> None:
        for flag in report_1.flags:
            if flag.risk_level == "HIGH":
                assert flag.needs_human_review is True

    def test_agent_trace_has_all_required_agents(self, report_1: BogdAIReport) -> None:
        trace_names = [entry.agent_name for entry in report_1.agent_trace]
        for agent_name in REQUIRED_AGENTS:
            assert agent_name in trace_names, f"Missing agent in trace: {agent_name}"

    def test_safety_fields(self, report_1: BogdAIReport) -> None:
        assert report_1.safety_and_limits.synthetic_data_only is True
        assert report_1.safety_and_limits.contains_pii is False

    def test_analysis_mode_is_synthetic_demo(self, report_1: BogdAIReport) -> None:
        assert report_1.analysis_mode == "synthetic_demo"

    def test_grounding_summary_has_sources(self, report_1: BogdAIReport) -> None:
        assert len(report_1.grounding_summary.knowledge_sources_used) >= 1

    def test_grounding_summary_citation_count(self, report_1: BogdAIReport) -> None:
        expected = sum(len(f.citations) for f in report_1.flags)
        assert report_1.grounding_summary.total_citations == expected

    def test_risk_score_in_bounds(self, report_1: BogdAIReport) -> None:
        assert 0 <= report_1.overall_assessment.risk_score <= 100

    def test_human_review_required_for_high_risk(self, report_1: BogdAIReport) -> None:
        if report_1.risk_breakdown.high > 0:
            assert report_1.overall_assessment.human_review_required is True


class TestOrchestratorContract2:
    """Lower-risk contract should produce fewer / lower-severity flags."""

    def test_report_is_bogdai_report(self, report_2: BogdAIReport) -> None:
        assert isinstance(report_2, BogdAIReport)

    def test_contract_2_has_fewer_high_flags_than_contract_1(
        self, report_1: BogdAIReport, report_2: BogdAIReport
    ) -> None:
        assert report_2.risk_breakdown.high <= report_1.risk_breakdown.high, (
            "Contract 2 (lower-risk) should have fewer HIGH flags than Contract 1"
        )

    def test_contract_2_safety_fields(self, report_2: BogdAIReport) -> None:
        assert report_2.safety_and_limits.synthetic_data_only is True
        assert report_2.safety_and_limits.contains_pii is False

    def test_contract_2_agent_trace(self, report_2: BogdAIReport) -> None:
        trace_names = [entry.agent_name for entry in report_2.agent_trace]
        for agent_name in REQUIRED_AGENTS:
            assert agent_name in trace_names


class TestDeterministicFallback:
    """Verify the deterministic fallback works without Azure credentials."""

    def test_local_fallback_produces_valid_report(self) -> None:
        """Should complete successfully with BOGDAI_USE_FOUNDRY=false."""
        orch = BogdAIOrchestrator()
        report = orch.analyze_file(_CONTRACT_1, foundry_mode="local_fallback")
        assert isinstance(report, BogdAIReport)
        assert report.schema_version == "1.0"

    def test_local_fallback_grounding_layer_label(self) -> None:
        orch = BogdAIOrchestrator()
        report = orch.analyze_file(_CONTRACT_1, foundry_mode="local_fallback")
        for flag in report.flags:
            for cit in flag.citations:
                assert cit.grounding_layer == "Foundry IQ"
