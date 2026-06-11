"""
BogdAI Contract Risk Agent — Main CLI Entry Point

Microsoft Agents League Hackathon 2026 | Reasoning Agents Track

Usage:
    python agent.py                          # Analyze default contract (local fallback)
    python agent.py --smoke-test             # Test Foundry connectivity
    python agent.py --local-only             # Force local deterministic mode
    python agent.py --analyze <path>         # Analyze a specific contract file
    python agent.py --analyze <path> --foundry  # Try Foundry first, then fallback

Environment variables (from .env):
    AZURE_AI_PROJECT_ENDPOINT   — Microsoft Foundry project endpoint
    AZURE_AI_MODEL_DEPLOYMENT   — Model deployment name (e.g., gpt-4o)
    BOGDAI_USE_FOUNDRY          — true/false
    BOGDAI_ALLOW_LOCAL_FALLBACK — true/false
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Load .env before importing any bogdai modules
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("bogdai.agent")

# Defaults
_DEFAULT_CONTRACT = (
    Path(__file__).parent / "bogdai" / "data" / "synthetic_contracts" / "test_contract_1.txt"
)


def print_banner() -> None:
    print()
    print("=" * 65)
    print("  BogdAI Contract Risk Agent")
    print("  Microsoft Agents League Hackathon 2026 — Reasoning Agents")
    print("=" * 65)
    print()


def run_smoke_test() -> bool:
    """
    Test connectivity to Microsoft Foundry.

    Returns True if Foundry responded successfully, False if falling back.
    """
    from bogdai.core.foundry_client import foundry_client

    print("[SMOKE TEST] Testing Microsoft Foundry connectivity...")
    result = foundry_client.smoke_test()
    print(f"[SMOKE TEST] Mode      : {result['mode']}")
    print(f"[SMOKE TEST] Success   : {result['success']}")
    print(f"[SMOKE TEST] Response  : {result['response']}")
    print()
    return result["mode"] == "foundry"


def run_analysis(contract_path: Path, foundry_mode: str) -> None:
    """Run the full multi-agent pipeline and print the JSON report."""
    from bogdai.core.orchestrator import BogdAIOrchestrator

    print(f"[ANALYZE] Contract : {contract_path}")
    print(f"[ANALYZE] Mode     : {foundry_mode}")
    print()

    if not contract_path.exists():
        print(f"[ERROR] File not found: {contract_path}", file=sys.stderr)
        sys.exit(1)

    orchestrator = BogdAIOrchestrator()
    report = orchestrator.analyze_file(contract_path, foundry_mode=foundry_mode)

    # Pretty-print the JSON report
    print("-" * 65)
    print("FINAL JSON REPORT")
    print("-" * 65)
    print(BogdAIOrchestrator.report_to_json(report))
    print("-" * 65)

    # Print summary
    print()
    print("[SUMMARY]")
    print(f"  Analysis ID    : {report.analysis_id}")
    print(f"  Contract       : {report.contract_name}")
    print(f"  Overall Risk   : {report.overall_assessment.overall_risk_level}")
    print(f"  Risk Score     : {report.overall_assessment.risk_score}/100")
    print(f"  Flags          : {len(report.flags)}")
    print(f"  High Risk      : {report.risk_breakdown.high}")
    print(f"  Medium Risk    : {report.risk_breakdown.medium}")
    print(f"  Human Review   : {report.overall_assessment.human_review_required}")
    print(f"  Synthetic Only : {report.safety_and_limits.synthetic_data_only}")
    print(f"  Contains PII   : {report.safety_and_limits.contains_pii}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="BogdAI Contract Risk Agent — Multi-agent pharma contract analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Test Microsoft Foundry connectivity and exit.",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Run in local deterministic mode without Foundry.",
    )
    parser.add_argument(
        "--foundry",
        action="store_true",
        help="Attempt Foundry call before falling back to local mode.",
    )
    parser.add_argument(
        "--analyze",
        metavar="CONTRACT_PATH",
        type=Path,
        default=None,
        help="Path to a contract file to analyze.",
    )

    args = parser.parse_args()
    print_banner()

    # Determine foundry mode
    if args.local_only:
        foundry_mode = "local_fallback"
    elif args.foundry:
        is_foundry = run_smoke_test()
        foundry_mode = "foundry" if is_foundry else "local_fallback"
    else:
        # Default: try smoke test quietly
        from bogdai.core.config import settings

        if settings.use_foundry and settings.foundry_available:
            is_foundry = run_smoke_test()
            foundry_mode = "foundry" if is_foundry else "local_fallback"
        else:
            foundry_mode = "local_fallback"
            print(
                "[INFO] BOGDAI_USE_FOUNDRY is false or endpoint not configured. "
                "Running local deterministic mode.\n"
            )

    # Smoke-test-only mode
    if args.smoke_test:
        if foundry_mode != "foundry":
            run_smoke_test()  # Run explicitly if not already done
        print("[DONE] Smoke test complete.")
        return

    # Determine which contract to analyze
    contract_path = args.analyze if args.analyze else _DEFAULT_CONTRACT

    run_analysis(contract_path, foundry_mode)

    print("[DONE] BogdAI analysis complete.")
    print()
    print("HOW TO RUN:")
    print("  python agent.py                     # local fallback (default)")
    print("  python agent.py --smoke-test        # test Foundry connectivity")
    print("  python agent.py --analyze <file>    # analyze a specific contract")
    print("  python agent.py --foundry           # try Foundry, fallback to local")
    print()
    print("HOW TO RUN TESTS:")
    print("  python -m pytest tests/ -v")
    print()


if __name__ == "__main__":
    main()
