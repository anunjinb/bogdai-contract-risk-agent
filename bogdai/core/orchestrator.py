"""
BogdAI Orchestrator.

Coordinates the full multi-agent pipeline:

  ContractIntakeAgent
    → ClauseExtractionAgent
      → GroundingAgent
        → RiskReasoningAgent
          → VerifierAgent
            → ReportAgent
              → BogdAIReport (JSON)

Supports both Foundry-assisted and local deterministic modes.
"""
from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Optional, Union

from bogdai.agents.intake_agent import ContractIntakeAgent
from bogdai.agents.clause_extraction_agent import ClauseExtractionAgent
from bogdai.agents.grounding_agent import GroundingAgent
from bogdai.agents.risk_reasoning_agent import RiskReasoningAgent
from bogdai.agents.verifier_agent import VerifierAgent
from bogdai.agents.report_agent import ReportAgent
from bogdai.core.risk_rules import get_applicable_rules
from bogdai.core.schemas import BogdAIReport

logger = logging.getLogger(__name__)

# Synthetic data directory
_DATA_DIR = Path(__file__).parent.parent / "data" / "synthetic_contracts"


class BogdAIOrchestrator:
    """
    Multi-agent orchestrator for the BogdAI Contract Risk Agent.

    Instantiates each agent once and wires them together.
    """

    def __init__(self) -> None:
        self._intake = ContractIntakeAgent()
        self._clause = ClauseExtractionAgent()
        self._grounding = GroundingAgent()
        self._reasoning = RiskReasoningAgent()
        self._verifier = VerifierAgent()
        self._report = ReportAgent()

    def analyze_file(
        self,
        file_path: Union[str, Path],
        analysis_id: Optional[str] = None,
        foundry_mode: str = "local_fallback",
    ) -> BogdAIReport:
        """
        Analyze a synthetic contract file.

        Args:
            file_path: Path to the contract text file.
            analysis_id: Optional unique ID; auto-generated if not given.
            foundry_mode: 'foundry' or 'local_fallback'.

        Returns:
            Validated BogdAIReport.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Contract file not found: {path}")

        contract_text = path.read_text(encoding="utf-8")
        return self.analyze_text(
            contract_text=contract_text,
            source_path=str(path),
            analysis_id=analysis_id,
            foundry_mode=foundry_mode,
        )

    def analyze_text(
        self,
        contract_text: str,
        source_path: str = "",
        analysis_id: Optional[str] = None,
        foundry_mode: str = "local_fallback",
    ) -> BogdAIReport:
        """
        Analyze raw contract text through the full agent pipeline.

        Args:
            contract_text: The contract content as a string.
            source_path: Optional display path / filename.
            analysis_id: Optional unique ID; auto-generated if not given.
            foundry_mode: 'foundry' or 'local_fallback'.

        Returns:
            Validated BogdAIReport.
        """
        if not analysis_id:
            analysis_id = f"BDA-{uuid.uuid4().hex[:8].upper()}"

        logger.info("=" * 60)
        logger.info("[Orchestrator] Starting analysis | ID: %s", analysis_id)
        logger.info("[Orchestrator] Mode: %s", foundry_mode)
        logger.info("=" * 60)

        # Step 1: Contract Intake
        logger.info("[Orchestrator] Agent 1/6 → Contract Intake")
        intake_result = self._intake.run(contract_text, source_path)

        # Step 2: Clause Extraction
        logger.info("[Orchestrator] Agent 2/6 → Clause Extraction")
        _clause_result = self._clause.run(intake_result)

        # Step 3: Deterministic risk rule matching
        logger.info("[Orchestrator] Matching deterministic risk rules")
        matched_rules = get_applicable_rules(contract_text)
        logger.info("[Orchestrator] %d rules matched", len(matched_rules))

        # Step 4: Grounding
        logger.info("[Orchestrator] Agent 3/6 → Grounding")
        grounding_result = self._grounding.run(matched_rules)

        # Step 5: Risk Reasoning
        logger.info("[Orchestrator] Agent 4/6 → Risk Reasoning")
        reasoning_result = self._reasoning.run(grounding_result)

        # Step 6: Verifier
        logger.info("[Orchestrator] Agent 5/6 → Verifier")
        verifier_result = self._verifier.run(reasoning_result)

        # Step 7: Report Assembly
        logger.info("[Orchestrator] Agent 6/6 → Report")
        report = self._report.run(
            intake_result=intake_result,
            grounding_result=grounding_result,
            verifier_result=verifier_result,
            foundry_mode=foundry_mode,
            analysis_id=analysis_id,
        )

        logger.info(
            "[Orchestrator] Analysis complete. Risk: %s | Score: %d | Flags: %d",
            report.overall_assessment.overall_risk_level,
            report.overall_assessment.risk_score,
            len(report.flags),
        )

        return report

    def analyze_default(self, foundry_mode: str = "local_fallback") -> BogdAIReport:
        """Run analysis on the default test contract (test_contract_1.txt)."""
        default_path = _DATA_DIR / "test_contract_1.txt"
        return self.analyze_file(
            default_path,
            analysis_id="BDA-2026-0001",
            foundry_mode=foundry_mode,
        )

    @staticmethod
    def report_to_json(report: BogdAIReport, indent: int = 2) -> str:
        """Serialize a BogdAIReport to a pretty-printed JSON string."""
        return report.model_dump_json(indent=indent)
