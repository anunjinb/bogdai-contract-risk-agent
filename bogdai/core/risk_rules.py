"""
BogdAI Deterministic Risk Rules.

These rules form the local fallback engine. They produce meaningful risk flags
without any external AI call — critical for demo reliability.

Each rule is a dict with:
  - pattern: string(s) to look for in contract text (case-insensitive)
  - clause_hint: label used to identify the clause
  - title: human-readable risk title
  - risk_category: category bucket
  - risk_level: HIGH | MEDIUM | LOW | INFORMATIONAL
  - risk_score: 0–100
  - issue: one-line problem description
  - business_impact: business consequence
  - patient_impact: patient/care consequence
  - recommendation: what to do about it
  - citation_source_doc: which synthetic knowledge doc to cite
  - citation_section: section within that doc
  - citation_evidence: quoted evidence text
"""
from __future__ import annotations

from typing import List, Dict, Any

RISK_RULES: List[Dict[str, Any]] = [
    # -----------------------------------------------------------------------
    # Rule 1: Long deviation reporting window (90-day / 60-day)
    # -----------------------------------------------------------------------
    {
        "id": "RULE-001",
        "patterns": ["ninety days", "90 days", "sixty days", "60 days", "90-day", "60-day"],
        "context_keywords": ["deviation", "report", "notify", "notify", "material"],
        "clause_hint": "Deviation Reporting",
        "title": "Regulatory Compliance – Delayed Deviation Reporting",
        "risk_category": "Compliance",
        "risk_level": "HIGH",
        "risk_score": 90,
        "issue": (
            "Deviation reporting window of 90 days or more may delay escalation "
            "of quality or safety issues, increasing regulatory exposure."
        ),
        "business_impact": (
            "Delayed reporting can increase regulatory exposure, audit risk, and "
            "operational remediation cost."
        ),
        "patient_impact": (
            "Delayed deviation reporting could slow response to quality issues that "
            "affect treatment availability or patient safety."
        ),
        "recommendation": (
            "Reduce the reporting window to 30 days or less. Define urgent escalation "
            "triggers and require immediate notice for patient-impacting deviations."
        ),
        "citation_source_doc": "synthetic_compliance_policy.md",
        "citation_section": "Deviation Reporting",
        "citation_evidence": (
            "Material deviations should be escalated promptly when they may affect "
            "product quality, availability, or patient safety."
        ),
        "citation_confidence": 0.91,
    },

    # -----------------------------------------------------------------------
    # Rule 2: Vague pricing adjustment language
    # -----------------------------------------------------------------------
    {
        "id": "RULE-002",
        "patterns": [
            "price may change",
            "prices may change",
            "market conditions",
            "subject to adjustment",
            "adjusted based on",
            "pricing adjustment",
        ],
        "context_keywords": ["price", "pricing", "cost", "fee", "rate"],
        "clause_hint": "Pricing Terms",
        "title": "Pricing – Vague Adjustment Language",
        "risk_category": "Financial",
        "risk_level": "HIGH",
        "risk_score": 80,
        "issue": (
            "Vague pricing adjustment terms without a defined cap or review mechanism "
            "expose the buyer to unpredictable cost increases."
        ),
        "business_impact": (
            "Uncapped pricing adjustments can create budget overruns and contract "
            "disputes, destabilizing procurement planning."
        ),
        "patient_impact": (
            "Uncontrolled cost increases may force formulary changes or reduce "
            "treatment access for patients on budget-constrained programs."
        ),
        "recommendation": (
            "Define a maximum annual price adjustment percentage, tie any adjustment "
            "to a published index (e.g., CPI), and require 90-day advance notice."
        ),
        "citation_source_doc": "synthetic_pharma_contracting_guidelines.md",
        "citation_section": "Pricing Terms",
        "citation_evidence": (
            "Vague pricing adjustment language without a defined cap or structured "
            "review process materially increases financial dispute risk."
        ),
        "citation_confidence": 0.87,
    },

    # -----------------------------------------------------------------------
    # Rule 3: Missing or unlimited liability cap
    # -----------------------------------------------------------------------
    {
        "id": "RULE-003",
        "patterns": [
            "unlimited liability",
            "no cap on liability",
            "liability shall not be limited",
            "without limitation",
        ],
        "context_keywords": ["liability", "damages", "indemnif"],
        "clause_hint": "Liability",
        "title": "Liability – Missing or Unlimited Cap",
        "risk_category": "Legal",
        "risk_level": "HIGH",
        "risk_score": 88,
        "issue": (
            "The contract imposes unlimited liability or explicitly removes any "
            "liability cap, creating extreme financial risk exposure."
        ),
        "business_impact": (
            "Unlimited liability exposure can result in catastrophic financial loss "
            "in the event of breach, product recall, or regulatory action."
        ),
        "patient_impact": (
            "Excessive liability exposure may deter suppliers from contracting, "
            "risking supply disruption and treatment delays."
        ),
        "recommendation": (
            "Negotiate a mutual liability cap tied to contract value or insurance "
            "coverage. Define exclusions clearly (e.g., gross negligence, fraud)."
        ),
        "citation_source_doc": "synthetic_pharma_contracting_guidelines.md",
        "citation_section": "Liability and Indemnification",
        "citation_evidence": (
            "Pharma contracts should define explicit liability caps, exclusions, "
            "and a structured review process to protect both parties."
        ),
        "citation_confidence": 0.89,
    },

    # -----------------------------------------------------------------------
    # Rule 4: Missing liability cap (absence pattern)
    # -----------------------------------------------------------------------
    {
        "id": "RULE-004",
        "patterns": ["liability cap", "liability limit", "maximum liability"],
        "context_keywords": [],
        "clause_hint": "Liability",
        "title": "Liability – Absent Liability Cap Clause",
        "risk_category": "Legal",
        "risk_level": "HIGH",
        "risk_score": 85,
        "issue": (
            "No explicit liability cap or limitation clause was found. "
            "This leaves financial exposure undefined."
        ),
        "business_impact": (
            "Without a liability cap, both parties face unpredictable financial "
            "exposure in any dispute or breach scenario."
        ),
        "patient_impact": (
            "Supplier withdrawal risk increases when liability terms are open-ended, "
            "potentially impacting treatment supply continuity."
        ),
        "recommendation": (
            "Add a clearly defined mutual liability cap clause specifying maximum "
            "liability amounts, exclusions, and indemnification obligations."
        ),
        "citation_source_doc": "synthetic_pharma_contracting_guidelines.md",
        "citation_section": "Liability and Indemnification",
        "citation_evidence": (
            "Pharma contracts should define explicit liability caps, exclusions, "
            "and a structured review process to protect both parties."
        ),
        "citation_confidence": 0.85,
        "absence_check": True,  # Flag if this pattern is NOT found in the text
    },

    # -----------------------------------------------------------------------
    # Rule 5: Delivery subject to availability without escalation
    # -----------------------------------------------------------------------
    {
        "id": "RULE-005",
        "patterns": [
            "subject to availability",
            "delivery subject to",
            "availability permitting",
            "as available",
        ],
        "context_keywords": ["delivery", "supply", "shipment", "order"],
        "clause_hint": "Delivery / Supply Obligations",
        "title": "Supply Chain – Delivery Without Escalation Timeline",
        "risk_category": "Operational",
        "risk_level": "HIGH",
        "risk_score": 82,
        "issue": (
            "Delivery terms conditioned on availability without a defined escalation "
            "timeline or substitution process create supply continuity risk."
        ),
        "business_impact": (
            "Open-ended delivery terms prevent effective inventory planning and "
            "can lead to treatment stock-outs."
        ),
        "patient_impact": (
            "Supply interruptions without escalation obligations may directly delay "
            "patient access to critical treatments."
        ),
        "recommendation": (
            "Specify maximum delivery lead times, define escalation steps when "
            "availability is constrained, and require advance notification of "
            "supply interruptions."
        ),
        "citation_source_doc": "synthetic_healthcare_procurement_rules.md",
        "citation_section": "Supply Continuity and Escalation",
        "citation_evidence": (
            "Procurement contracts must define delivery timelines, escalation paths, "
            "and contingency obligations when primary supply is unavailable."
        ),
        "citation_confidence": 0.88,
    },

    # -----------------------------------------------------------------------
    # Rule 6: Missing or unclear audit rights
    # -----------------------------------------------------------------------
    {
        "id": "RULE-006",
        "patterns": ["audit rights", "right to audit", "audit access"],
        "context_keywords": [],
        "clause_hint": "Audit Rights",
        "title": "Audit Rights – Missing or Unclear",
        "risk_category": "Compliance",
        "risk_level": "MEDIUM",
        "risk_score": 60,
        "issue": (
            "Audit rights are absent or insufficiently defined, limiting visibility "
            "into supplier compliance, quality, and pricing."
        ),
        "business_impact": (
            "Without clear audit rights, billing discrepancies and non-compliance "
            "may go undetected until significant damage has occurred."
        ),
        "patient_impact": (
            "Inadequate audit rights may mask quality or GMP compliance gaps "
            "that affect product safety."
        ),
        "recommendation": (
            "Include clear audit rights specifying frequency, scope, notice period, "
            "records access, and remediation obligations."
        ),
        "citation_source_doc": "synthetic_compliance_policy.md",
        "citation_section": "Audit and Oversight",
        "citation_evidence": (
            "Contracts with regulated suppliers should include defined audit rights "
            "with clear scope, frequency, and escalation procedures."
        ),
        "citation_confidence": 0.82,
        "absence_check": True,
    },

    # -----------------------------------------------------------------------
    # Rule 7: Termination without cause notice period too short or missing
    # -----------------------------------------------------------------------
    {
        "id": "RULE-007",
        "patterns": [
            "terminate for convenience",
            "terminate without cause",
            "terminate at will",
            "immediate termination",
        ],
        "context_keywords": ["terminat"],
        "clause_hint": "Termination",
        "title": "Termination – Convenience Termination Without Adequate Notice",
        "risk_category": "Operational",
        "risk_level": "MEDIUM",
        "risk_score": 65,
        "issue": (
            "Termination for convenience clause may allow abrupt contract end "
            "without sufficient transition time, risking supply disruption."
        ),
        "business_impact": (
            "Abrupt termination without a wind-down period disrupts procurement "
            "planning and may require emergency sourcing."
        ),
        "patient_impact": (
            "Sudden termination of a drug supply contract can interrupt patient "
            "treatment programs with no transition plan."
        ),
        "recommendation": (
            "Require a minimum 90-day notice for termination for convenience. "
            "Include transition obligations and supply bridge commitments."
        ),
        "citation_source_doc": "synthetic_healthcare_procurement_rules.md",
        "citation_section": "Contract Termination",
        "citation_evidence": (
            "Healthcare procurement contracts should require adequate notice periods "
            "for termination to protect supply continuity and patient care."
        ),
        "citation_confidence": 0.79,
    },
]


def get_applicable_rules(contract_text: str) -> List[Dict[str, Any]]:
    """
    Match deterministic risk rules against contract text.

    Rules with ``absence_check=True`` are flagged when the pattern is NOT
    found in the text (i.e., the protective clause is missing).

    Returns only rules that match.
    """
    text_lower = contract_text.lower()
    matched: List[Dict[str, Any]] = []

    for rule in RISK_RULES:
        absence = rule.get("absence_check", False)
        patterns: List[str] = rule["patterns"]
        found = any(p.lower() in text_lower for p in patterns)

        if absence:
            # Flag when the protective term is ABSENT from the contract
            if not found:
                matched.append(rule)
        else:
            # Flag when the risky term IS present
            if found:
                matched.append(rule)

    return matched
