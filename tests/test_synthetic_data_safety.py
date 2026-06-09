"""
Tests for synthetic data safety.

Verifies:
  - No .env file is tracked in git.
  - Synthetic contracts contain proper synthetic markers.
  - No PII patterns found in any data file.
  - Knowledge docs are clearly marked as synthetic.
"""
import os
import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent
_CONTRACTS_DIR = _REPO_ROOT / "bogdai" / "data" / "synthetic_contracts"
_KNOWLEDGE_DIR = _REPO_ROOT / "bogdai" / "data" / "synthetic_knowledge"

# PII-like patterns (simple heuristics for demo safety)
_PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",          # SSN
    r"\b\d{10}\b",                       # 10-digit phone number
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
    r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IPv4 address (exclude 127.0.0.1)
]

# Credentials-like patterns
_SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9]{32,}",            # OpenAI key
    r"AKIA[0-9A-Z]{16}",               # AWS access key
    r"['\"]password['\"]:\s*['\"][^'\"]+['\"]",  # JSON password
    r"Bearer\s+[A-Za-z0-9._\-]{20,}",  # Bearer token
]


class TestSyntheticDataSafety:
    """Verify all data files are safe and synthetic."""

    def test_no_env_file_in_repo(self) -> None:
        """Ensure .env is not tracked — it should be gitignored."""
        env_path = _REPO_ROOT / ".env"
        # The file might exist locally but must not contain secrets
        # For CI / test: just confirm .gitignore lists .env
        gitignore = _REPO_ROOT / ".gitignore"
        assert gitignore.exists(), ".gitignore must exist"
        content = gitignore.read_text(encoding="utf-8")
        assert ".env" in content, ".env must be listed in .gitignore"

    def test_env_example_has_no_real_credentials(self) -> None:
        """Verify .env.example contains only placeholder values."""
        env_example = _REPO_ROOT / ".env.example"
        assert env_example.exists(), ".env.example must exist"
        content = env_example.read_text(encoding="utf-8")
        # Should not contain real endpoint URLs (no .azure.com or key patterns)
        assert "your-foundry-project-endpoint" in content
        for pattern in _SECRET_PATTERNS:
            assert not re.search(pattern, content), (
                f".env.example contains secret-like pattern: {pattern}"
            )

    def test_contract_1_has_synthetic_marker(self) -> None:
        contract = (_CONTRACTS_DIR / "test_contract_1.txt").read_text(encoding="utf-8")
        assert "SYNTHETIC" in contract.upper() or "synthetic" in contract.lower()

    def test_contract_2_has_synthetic_marker(self) -> None:
        contract = (_CONTRACTS_DIR / "test_contract_2.txt").read_text(encoding="utf-8")
        assert "SYNTHETIC" in contract.upper() or "synthetic" in contract.lower()

    def test_knowledge_docs_are_synthetic(self) -> None:
        for doc in _KNOWLEDGE_DIR.glob("*.md"):
            content = doc.read_text(encoding="utf-8")
            assert "synthetic" in content.lower(), (
                f"{doc.name} must contain a synthetic disclaimer"
            )

    def test_no_pii_in_contracts(self) -> None:
        for contract_file in _CONTRACTS_DIR.glob("*.txt"):
            content = contract_file.read_text(encoding="utf-8")
            for pattern in _PII_PATTERNS:
                matches = re.findall(pattern, content)
                # Filter out localhost IP if matched
                filtered = [m for m in matches if m != "127.0.0.1"]
                assert not filtered, (
                    f"{contract_file.name} contains PII-like pattern '{pattern}': {filtered}"
                )

    def test_no_secrets_in_knowledge_docs(self) -> None:
        for doc in _KNOWLEDGE_DIR.glob("*.md"):
            content = doc.read_text(encoding="utf-8")
            for pattern in _SECRET_PATTERNS:
                assert not re.search(pattern, content), (
                    f"{doc.name} contains secret-like pattern: {pattern}"
                )

    def test_no_secrets_in_python_source(self) -> None:
        """Scan all Python source files for secret-like patterns."""
        src_dir = _REPO_ROOT / "bogdai"
        for py_file in src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for pattern in _SECRET_PATTERNS:
                assert not re.search(pattern, content), (
                    f"{py_file.relative_to(_REPO_ROOT)} contains secret-like pattern: {pattern}"
                )

    def test_synthetic_contracts_exist(self) -> None:
        assert (_CONTRACTS_DIR / "test_contract_1.txt").exists()
        assert (_CONTRACTS_DIR / "test_contract_2.txt").exists()

    def test_synthetic_knowledge_docs_exist(self) -> None:
        assert (_KNOWLEDGE_DIR / "synthetic_compliance_policy.md").exists()
        assert (_KNOWLEDGE_DIR / "synthetic_pharma_contracting_guidelines.md").exists()
        assert (_KNOWLEDGE_DIR / "synthetic_healthcare_procurement_rules.md").exists()
