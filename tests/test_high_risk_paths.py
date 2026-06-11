"""Targeted tests for the HIGH-risk flag path.

These tests focus on the behavior that matters most for the multi-agent
contract risk pipeline:
- 3-step reasoning chains for HIGH-risk flags
- citation / quoted evidence guardrails
- human-review escalation for HIGH-risk output
- no HIGH-risk outcome when the contract is low risk
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from bogdai.agents.risk_reasoning_agent import RiskReasoningAgent
from bogdai.agents.verifier_agent import VerifierAgent
from bogdai.core.orchestrator import BogdAIOrchestrator
from bogdai.core.risk_rules import RISK_RULES
from bogdai.core.schemas import BogdAIReport


_ROOT = Path(__file__).resolve().parent.parent
_CONTRACT_1 = _ROOT / "bogdai" / "data" / "synthetic_contracts" / "test_contract_1.txt"
_CONTRACT_2 = _ROOT / "bogdai" / "data" / "synthetic_contracts" / "test_contract_2.txt"
_FROZEN_DEMO_OUTPUT = _ROOT / "demo_outputs" / "test_contract_1_analysis.json"


def _load_frozen_demo_contract() -> dict:
    """Load the frozen demo output contract from the UTF-16 transcript file."""
    text = _FROZEN_DEMO_OUTPUT.read_text(encoding="utf-16")
    start = text.index("{")
    end = text.rindex("}") + 1
    return json.loads(text[start:end])


def _high_risk_rule() -> dict:
    """Return a detached copy of a known HIGH-risk rule."""
    return copy.deepcopy(RISK_RULES[0])


def _clean_high_flag_from_rule(rule: dict) -> dict:
    """Build a high-risk flag shaped like the reasoning agent output."""
    return {
        "flag_id": "FLAG-001",
        "clause": "4.2",
        "title": rule["title"],
        "risk_category": rule["risk_category"],
        "risk_level": "HIGH",
        "risk_score": rule["risk_score"],
        "issue": rule["issue"],
        "clause_excerpt": "[Synthetic excerpt] The contract states: '...'.",
        "business_impact": rule["business_impact"],
        "patient_impact": rule["patient_impact"],
        "reasoning_steps": [
            {
                "step": 1,
                "observation": "A risky contract pattern was identified.",
                "inference": "The pattern maps to a known risk area.",
            },
            {
                "step": 2,
                "observation": "The grounded policy evidence is missing.",
                "inference": "Without quoted policy support, the claim must be reviewed.",
            },
            {
                "step": 3,
                "observation": "The clause affects regulated supply and compliance.",
                "inference": "This is still a high-impact issue requiring escalation.",
            },
        ],
        "recommendation": rule["recommendation"],
        "citations": [
            {
                "citation_id": "CIT-001",
                "source_title": "Synthetic Pharma Contracting Guidelines",
                "source_document": "synthetic_pharma_contracting_guidelines.md",
                "section": "Pricing Terms",
                "quoted_evidence": "",
                "grounding_layer": "Foundry IQ",
                "retrieval_confidence": 0.0,
            }
        ],
        "confidence": 0.75,
        "needs_human_review": True,
    }


def _assert_matches_frozen_demo_contract(report: BogdAIReport) -> None:
    frozen = _load_frozen_demo_contract()
    report_dump = report.model_dump()

    assert set(report_dump) == set(frozen)
    assert set(report_dump["overall_assessment"]) == set(frozen["overall_assessment"])
    assert set(report_dump["risk_breakdown"]) == set(frozen["risk_breakdown"])
    assert set(report_dump["grounding_summary"]) == set(frozen["grounding_summary"])
    assert set(report_dump["safety_and_limits"]) == set(frozen["safety_and_limits"])
    assert set(report_dump["ui_hints"]) == set(frozen["ui_hints"])

    if frozen["flags"]:
        assert set(report_dump["flags"][0]) == set(frozen["flags"][0])
    if frozen["agent_trace"]:
        assert set(report_dump["agent_trace"][0]) == set(frozen["agent_trace"][0])


def test_high_risk_happy_path_matches_demo_contract() -> None:
    """A clean HIGH-risk analysis should match the frozen report contract."""
    orchestrator = BogdAIOrchestrator()
    report = orchestrator.analyze_file(_CONTRACT_1, foundry_mode="local_fallback")

    assert isinstance(report, BogdAIReport)
    _assert_matches_frozen_demo_contract(report)
    assert report.overall_assessment.overall_risk_level in ("HIGH", "CRITICAL")
    assert report.overall_assessment.human_review_required is True

    high_flags = [flag for flag in report.flags if flag.risk_level == "HIGH"]
    assert high_flags, "Expected at least one HIGH-risk flag"

    for flag in high_flags:
        assert flag.needs_human_review is True
        assert len(flag.reasoning_steps) == 3
        assert len(flag.citations) >= 1
        assert flag.citations[0].quoted_evidence.strip()


def test_high_risk_missing_quoted_evidence_is_marked_for_review(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing grounded evidence should trigger review, not a clean HIGH pass."""
    rule = _high_risk_rule()

    monkeypatch.setattr(
        "bogdai.core.orchestrator.get_applicable_rules",
        lambda contract_text: [rule],
    )

    def fake_grounding_run(self, matched_rules, foundry_mode="local_fallback"):
        grounded_rules = []
        for matched_rule in matched_rules:
            grounded_rules.append(
                {
                    **matched_rule,
                    "citation": {
                        "source_title": "Synthetic Pharma Contracting Guidelines",
                        "source_document": "synthetic_pharma_contracting_guidelines.md",
                        "section": matched_rule.get("citation_section", "General"),
                        "quoted_evidence": "",
                        "grounding_layer": "Foundry IQ",
                        "retrieval_confidence": 0.0,
                    },
                }
            )

        return {
            "grounded_rules": grounded_rules,
            "knowledge_sources_used": ["synthetic_pharma_contracting_guidelines.md"],
            "output_summary": "Retrieved citations for 1 risk flag from 1 synthetic knowledge source.",
        }

    monkeypatch.setattr(
        "bogdai.agents.grounding_agent.GroundingAgent.run",
        fake_grounding_run,
    )

    verifier = VerifierAgent()
    reasoning_result = {
        "risk_flags": [
            _clean_high_flag_from_rule(rule),
        ]
    }
    verifier_result = verifier.run(reasoning_result)

    assert verifier_result["unsupported_claims_detected"] == 1
    assert verifier_result["verified_flags"][0]["verification_status"] == "NEEDS_REVIEW"
    assert verifier_result["verified_flags"][0]["verification_warnings"]

    orchestrator = BogdAIOrchestrator()
    report = orchestrator.analyze_text(
        "SYNTHETIC DEMO CONTRACT WITH HIGH-RISK PRICING LANGUAGE",
        source_path="synthetic_missing_evidence.txt",
    )

    assert report.risk_breakdown.high == 1
    assert report.grounding_summary.unsupported_claims_detected == 1
    assert report.overall_assessment.human_review_required is True
    assert report.flags[0].risk_level == "HIGH"
    assert report.flags[0].citations[0].quoted_evidence.strip() == ""


@pytest.mark.xfail(reason="Current reasoning agent still emits HIGH without grounded citation; expected guardrail is not yet implemented.")
def test_pattern_match_without_grounding_does_not_create_high_conclusion() -> None:
    """A missing grounded citation should not be enough to justify HIGH severity."""
    rule = _high_risk_rule()
    reasoning_agent = RiskReasoningAgent()

    result = reasoning_agent.run(
        {
            "grounded_rules": [
                {
                    **rule,
                    "citation": {
                        "source_title": "Synthetic Pharma Contracting Guidelines",
                        "source_document": "synthetic_pharma_contracting_guidelines.md",
                        "section": "Pricing Terms",
                        "quoted_evidence": "",
                        "grounding_layer": "Foundry IQ",
                        "retrieval_confidence": 0.0,
                    },
                }
            ]
        },
        foundry_mode="local_fallback",
    )

    assert result["risk_flags"][0]["risk_level"] != "HIGH"


def test_lower_risk_contract_has_no_high_flags() -> None:
    """A contract with no HIGH-risk clauses should stay at MEDIUM or below."""
    orchestrator = BogdAIOrchestrator()
    report = orchestrator.analyze_file(_CONTRACT_2, foundry_mode="local_fallback")

    assert isinstance(report, BogdAIReport)
    assert report.risk_breakdown.high == 0
    assert report.overall_assessment.human_review_required is False
    assert report.overall_assessment.overall_risk_level in ("LOW", "MEDIUM")
    assert report.overall_assessment.risk_score <= 55