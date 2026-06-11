"""
Grounding Agent.

Retrieves or matches supporting evidence from synthetic knowledge documents.
This represents the Foundry IQ grounding layer for the hackathon.

When real Foundry IQ retrieval is unavailable, the agent uses local keyword-based
retrieval from the synthetic knowledge base, behaving like a grounding layer.

Every risk flag includes structured citation objects.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from bogdai.core.foundry_client import foundry_client

logger = logging.getLogger(__name__)

# Resolve the synthetic knowledge directory relative to this file
_KNOWLEDGE_DIR = (
    Path(__file__).parent.parent / "data" / "synthetic_knowledge"
)


class GroundingAgent:
    """
    Agent 3: Grounding.

    Provides citation evidence from synthetic knowledge sources.
    Simulates Foundry IQ knowledge retrieval for the hackathon.
    """

    name = "Grounding Agent"
    role = "Retrieved supporting evidence from approved synthetic knowledge sources."
    tool_used = "Foundry IQ (local synthetic fallback)"

    def __init__(self) -> None:
        self._knowledge_store: Dict[str, str] = {}
        self._load_knowledge()

    def _load_knowledge(self) -> None:
        """Load synthetic knowledge documents into memory."""
        if not _KNOWLEDGE_DIR.exists():
            logger.warning(
                "[GroundingAgent] Knowledge dir not found: %s", _KNOWLEDGE_DIR
            )
            return

        for doc_path in _KNOWLEDGE_DIR.glob("*.md"):
            try:
                self._knowledge_store[doc_path.name] = doc_path.read_text(
                    encoding="utf-8"
                )
                logger.info("[GroundingAgent] Loaded knowledge doc: %s", doc_path.name)
            except OSError as exc:
                logger.warning("[GroundingAgent] Could not read %s: %s", doc_path.name, exc)

    def run(self, matched_rules: List[Dict[str, Any]], foundry_mode: str = "local_fallback") -> Dict[str, Any]:
        """
        Ground each matched risk rule with a citation from the knowledge store.

        Args:
            matched_rules: List of rules from risk_rules.get_applicable_rules().
            foundry_mode: Mode passed from orchestrator.

        Returns:
            dict with key ``grounded_rules``: each rule augmented with a citation.
        """
        logger.info("[GroundingAgent] Grounding %d rules.", len(matched_rules))
        grounded: List[Dict[str, Any]] = []

        for rule in matched_rules:
            citation = None
            if foundry_mode == "foundry":
                citation = self._build_citation_llm(rule)
            
            if not citation:
                citation = self._build_citation(rule)
                
            grounded.append({**rule, "citation": citation})

        sources_used = list(
            {r["citation_source_doc"] for r in matched_rules if "citation_source_doc" in r}
        )

        return {
            "grounded_rules": grounded,
            "knowledge_sources_used": sources_used,
            "output_summary": (
                f"Retrieved citations for {len(grounded)} risk flags from "
                f"{len(sources_used)} synthetic knowledge source(s)."
            ),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_citation_llm(self, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use the LLM to retrieve the best citation from loaded knowledge docs."""
        issue = rule.get("issue", "")
        if not issue or not self._knowledge_store:
            return None
            
        docs_text = []
        for name, text in self._knowledge_store.items():
            docs_text.append(f"--- Document: {name} ---\n{text}\n")
        all_docs = "\n".join(docs_text)
        
        prompt = f"""You are the BogdAI Grounding Agent.
Your task is to find the most relevant citation from the provided knowledge documents that supports the following risk issue.

Risk Issue: {issue}

Knowledge Documents:
{all_docs}

Return ONLY a JSON object with the following schema:
{{
  "source_document": "filename of the document (e.g., synthetic_compliance_policy.md)",
  "section": "The section header where the evidence was found",
  "quoted_evidence": "1-2 sentences of exact quoted evidence supporting the risk",
  "retrieval_confidence": a float between 0.0 and 1.0
}}
"""
        response_text = foundry_client.call_model(prompt, max_tokens=300, response_format={"type": "json_object"})
        if not response_text:
            return None
        
        try:
            data = json.loads(response_text)
            doc_name = data.get("source_document", "synthetic_compliance_policy.md")
            return {
                "source_title": self._doc_title(doc_name),
                "source_document": doc_name,
                "section": data.get("section", "General"),
                "quoted_evidence": data.get("quoted_evidence", ""),
                "grounding_layer": "Foundry IQ",
                "retrieval_confidence": data.get("retrieval_confidence", 0.90),
            }
        except json.JSONDecodeError:
            logger.warning("[GroundingAgent] LLM returned invalid JSON.")
            return None

    def _build_citation(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Build a citation object for one rule."""
        doc_name: str = rule.get("citation_source_doc", "synthetic_compliance_policy.md")
        section: str = rule.get("citation_section", "General")
        evidence: str = rule.get("citation_evidence", "")
        confidence: float = rule.get("citation_confidence", 0.80)

        # Verify evidence can be found (or close match) in the loaded doc
        doc_text = self._knowledge_store.get(doc_name, "")
        retrieval_ok = bool(doc_text) and self._fuzzy_match(evidence, doc_text)

        if not retrieval_ok and doc_text:
            # Fall back to a broader section search
            evidence = self._retrieve_section_snippet(doc_text, section) or evidence

        return {
            "source_title": self._doc_title(doc_name),
            "source_document": doc_name,
            "section": section,
            "quoted_evidence": evidence,
            "grounding_layer": "Foundry IQ",
            "retrieval_confidence": confidence if retrieval_ok else max(0.5, confidence - 0.1),
        }

    @staticmethod
    def _fuzzy_match(evidence: str, doc_text: str) -> bool:
        """Return True if at least half the evidence words appear in the doc."""
        evidence_words = [w.lower() for w in evidence.split() if len(w) > 4]
        if not evidence_words:
            return True
        doc_lower = doc_text.lower()
        matches = sum(1 for w in evidence_words if w in doc_lower)
        return matches / len(evidence_words) >= 0.5

    @staticmethod
    def _retrieve_section_snippet(doc_text: str, section: str) -> Optional[str]:
        """Find and return the paragraph under a matching section header."""
        lines = doc_text.splitlines()
        section_lower = section.lower()
        found = False
        snippet_lines: List[str] = []

        for line in lines:
            if section_lower in line.lower() and line.strip().startswith("#"):
                found = True
                continue
            if found:
                stripped = line.strip()
                if stripped.startswith("#"):
                    break  # Next section
                if stripped:
                    snippet_lines.append(stripped)
                if len(snippet_lines) >= 3:
                    break

        return " ".join(snippet_lines) if snippet_lines else None

    @staticmethod
    def _doc_title(doc_name: str) -> str:
        """Convert a filename to a human-readable title."""
        stem = doc_name.replace(".md", "").replace("_", " ").replace("-", " ")
        return stem.title()
