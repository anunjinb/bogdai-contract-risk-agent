"""
BogdAI Pydantic schema models.

These models enforce the JSON response contract for the frontend.
Schema version: 1.0
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Citation / Grounding
# ---------------------------------------------------------------------------

class Citation(BaseModel):
    citation_id: str = Field(..., description="Unique citation identifier, e.g. CIT-001")
    source_title: str
    source_document: str
    section: str
    quoted_evidence: str
    grounding_layer: str = "Foundry IQ"
    retrieval_confidence: float = Field(..., ge=0.0, le=1.0)


# ---------------------------------------------------------------------------
# Reasoning Step
# ---------------------------------------------------------------------------

class ReasoningStep(BaseModel):
    step: int
    observation: str
    inference: str


# ---------------------------------------------------------------------------
# Risk Flag
# ---------------------------------------------------------------------------

class RiskFlag(BaseModel):
    flag_id: str = Field(..., description="Unique flag identifier, e.g. FLAG-001")
    clause: str = Field(..., description="Contract clause reference, e.g. '4.2'")
    title: str
    risk_category: str
    risk_level: str = Field(..., description="HIGH | MEDIUM | LOW | INFORMATIONAL")
    risk_score: int = Field(..., ge=0, le=100)
    issue: str
    clause_excerpt: str
    business_impact: str
    patient_impact: str
    reasoning_steps: List[ReasoningStep]
    recommendation: str
    citations: List[Citation]
    confidence: float = Field(..., ge=0.0, le=1.0)
    needs_human_review: bool


# ---------------------------------------------------------------------------
# Overall Assessment
# ---------------------------------------------------------------------------

class OverallAssessment(BaseModel):
    overall_risk_level: str
    risk_score: int = Field(..., ge=0, le=100)
    summary: str
    human_review_required: bool


# ---------------------------------------------------------------------------
# Risk Breakdown
# ---------------------------------------------------------------------------

class RiskBreakdown(BaseModel):
    high: int = 0
    medium: int = 0
    low: int = 0
    informational: int = 0


# ---------------------------------------------------------------------------
# Agent Trace Entry
# ---------------------------------------------------------------------------

class AgentTraceEntry(BaseModel):
    agent_name: str
    role: str
    tool_used: Optional[str] = None
    output: str


# ---------------------------------------------------------------------------
# Grounding Summary
# ---------------------------------------------------------------------------

class GroundingSummary(BaseModel):
    iq_layer_used: str = "Foundry IQ"
    knowledge_sources_used: List[str]
    total_citations: int
    unsupported_claims_detected: int = 0


# ---------------------------------------------------------------------------
# Safety & Limits
# ---------------------------------------------------------------------------

class SafetyAndLimits(BaseModel):
    synthetic_data_only: bool = True
    contains_pii: bool = False
    legal_advice_disclaimer: str = (
        "This analysis is for hackathon demonstration only and does not replace "
        "legal, regulatory, clinical, or compliance review."
    )
    requires_human_approval_before_action: bool = True


# ---------------------------------------------------------------------------
# UI Hints
# ---------------------------------------------------------------------------

class UIHints(BaseModel):
    primary_badge: str
    recommended_next_action: str
    show_agent_trace: bool = True
    show_citations: bool = True


# ---------------------------------------------------------------------------
# Full Report (Root Response)
# ---------------------------------------------------------------------------

class BogdAIReport(BaseModel):
    schema_version: str = "1.0"
    analysis_id: str
    contract_name: str
    source_document: str
    analysis_date: str  # ISO 8601 date string
    analysis_mode: str = "synthetic_demo"
    overall_assessment: OverallAssessment
    risk_breakdown: RiskBreakdown
    flags: List[RiskFlag]
    agent_trace: List[AgentTraceEntry]
    grounding_summary: GroundingSummary
    safety_and_limits: SafetyAndLimits
    ui_hints: UIHints
