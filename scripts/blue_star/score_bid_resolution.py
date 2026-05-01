#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_SLUG = "blue-star"
LOOP_SLUG = "bid-resolution"
LOOP_NAME = f"{REPO_SLUG}/{LOOP_SLUG}"
OUTPUT_ROOT = Path.home() / ".openclaw" / "workspace" / "outputs" / "autoresearch" / REPO_SLUG / LOOP_SLUG
VALID_VERDICTS = {
    "pursue_quote",
    "true_no_fit",
    "docs_missing_inaccessible",
    "extraction_failure",
    "drawing_or_vision_review_needed",
    "human_clarification_needed",
    "continue_investigation",
}
BLOCKER_VERDICTS = {
    "docs_missing_inaccessible",
    "extraction_failure",
    "drawing_or_vision_review_needed",
    "human_clarification_needed",
}
HIGH_IMPACT_VERDICTS = {"pursue_quote", "true_no_fit"}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def today_dir() -> Path:
    day = OUTPUT_ROOT / datetime.now().strftime("%Y-%m-%d")
    day.mkdir(parents=True, exist_ok=True)
    return day


def find_latest_ledger() -> Optional[Path]:
    if not OUTPUT_ROOT.exists():
        return None
    ledgers = sorted(OUTPUT_ROOT.glob("*/ledger.jsonl"), key=lambda path: path.stat().st_mtime)
    return ledgers[-1] if ledgers else None


def load_jsonl(path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    entries: List[Dict[str, Any]] = []
    parse_errors: List[Dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            parse_errors.append({"line": line_number, "error": str(exc)})
            continue
        if not isinstance(payload, dict):
            parse_errors.append({"line": line_number, "error": "Entry is not a JSON object."})
            continue
        payload["_line"] = line_number
        entries.append(payload)
    return entries, parse_errors


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def has_direct_evidence(entry: Dict[str, Any]) -> bool:
    evidence = entry.get("evidence")
    if not isinstance(evidence, list):
        return False
    for item in evidence:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "direct":
            continue
        if nonempty(item.get("source")) and nonempty(item.get("locator")) and nonempty(item.get("summary")):
            return True
    return False


def docs_present_and_readable(entry: Dict[str, Any]) -> bool:
    quality = entry.get("doc_quality")
    if not isinstance(quality, dict):
        return False
    return quality.get("docs_present") is True and quality.get("readable") is True


def has_blocker(entry: Dict[str, Any]) -> bool:
    quality = entry.get("doc_quality")
    if isinstance(quality, dict) and nonempty(quality.get("blocker")):
        return True
    return nonempty(entry.get("blocker"))


def artifact_depth(entry: Dict[str, Any]) -> int:
    artifacts = entry.get("artifacts_inspected")
    if not isinstance(artifacts, list):
        return 0
    text = "\n".join(str(item) for item in artifacts)
    depth = 0
    if "bid-intelligence/wiki" in text or "/wiki/" in text:
        depth += 1
    if "evidence-index.json" in text or "requirement-graph.json" in text or "source-map.json" in text:
        depth += 1
    if "bid-intelligence/raw" in text or "/raw/" in text:
        depth += 1
    if "original-pdfs" in text or ".pdf" in text.lower() or ".xlsx" in text.lower() or ".docx" in text.lower():
        depth += 1
    return min(depth, 4)


def score_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    verdict = entry.get("verdict")
    checks: List[Dict[str, Any]] = []

    def check(name: str, passed: bool, points: int, message: str) -> int:
        checks.append({"name": name, "passed": passed, "points": points if passed else 0, "max_points": points, "message": message})
        return points if passed else 0

    decision_points = 0
    decision_points += check("valid_verdict", verdict in VALID_VERDICTS, 8, "Verdict must be one of the rubric verdicts.")
    decision_points += check("bid_id_present", nonempty(entry.get("bid_id")), 4, "Entry must include bid_id.")
    decision_points += check("confidence_present", entry.get("confidence") in {"low", "medium", "high"}, 4, "Confidence must be low, medium, or high.")
    decision_points += check("decision_present", nonempty(entry.get("decision")), 4, "Entry must state the decision being improved.")

    direct = has_direct_evidence(entry)
    evidence_points = 0
    evidence_points += check("evidence_list_present", nonempty_list(entry.get("evidence")), 5, "Entry must include evidence.")
    evidence_points += check("direct_evidence_for_high_impact", verdict not in HIGH_IMPACT_VERDICTS or direct, 15, "Pursue/no-fit require direct evidence.")
    evidence_points += check("no_fit_docs_present_readable", verdict != "true_no_fit" or docs_present_and_readable(entry), 5, "true_no_fit requires docs present and readable.")

    depth = artifact_depth(entry)
    ladder_points = 0
    ladder_points += check("artifacts_inspected", nonempty_list(entry.get("artifacts_inspected")), 5, "Entry must list inspected artifacts.")
    ladder_points += check("uses_wiki_or_graph", depth >= 1, 5, "Entry should start from wiki/graph artifacts.")
    ladder_points += check("escalates_when_needed", verdict in HIGH_IMPACT_VERDICTS or depth >= 2, 10, "Blocker/continue verdicts should show escalation beyond a bare label.")

    blocker_points = 0
    blocker_points += check("blocker_separated", verdict not in BLOCKER_VERDICTS or has_blocker(entry), 10, "Blocker verdicts need a concrete blocker.")
    blocker_points += check("no_fit_not_blocker", verdict != "true_no_fit" or not has_blocker(entry), 5, "Do not label known blockers as true_no_fit.")

    hypothesis_points = 0
    hypothesis_points += check("leading_hypothesis", nonempty(entry.get("leading_hypothesis")), 3, "Entry needs a leading hypothesis.")
    hypothesis_points += check("disconfirming_test", nonempty(entry.get("disconfirming_test")), 4, "Entry needs a disconfirming test.")
    hypothesis_points += check("rejected_hypotheses", nonempty_list(entry.get("rejected_hypotheses")), 3, "Entry should name rejected hypotheses.")

    action_points = 0
    action_points += check("next_action", nonempty(entry.get("next_action")), 5, "Entry needs a concrete next action.")
    action_points += check("owner", nonempty(entry.get("owner")), 5, "Entry needs an owner.")

    total = decision_points + evidence_points + ladder_points + blocker_points + hypothesis_points + action_points
    return {
        "line": entry.get("_line"),
        "bid_id": entry.get("bid_id"),
        "verdict": verdict,
        "score": total,
        "max_score": 100,
        "category_points": {
            "decision_validity": decision_points,
            "direct_evidence_and_provenance": evidence_points,
            "evidence_ladder_use": ladder_points,
            "blocker_diagnosis": blocker_points,
            "hypothesis_discipline": hypothesis_points,
            "operational_next_action": action_points,
        },
        "checks": checks,
    }


def average(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def run(ledger: Optional[Path]) -> Dict[str, Any]:
    selected_ledger = ledger or find_latest_ledger()
    if selected_ledger is None:
        return {
            "loop": LOOP_NAME,
            "score": 0,
            "status": "no_ledger",
            "ledger": None,
            "message": f"No ledger found under {OUTPUT_ROOT}. Create <date>/ledger.jsonl first.",
            "entries": [],
            "parse_errors": [],
            "regression_gates_passed": False,
        }

    entries, parse_errors = load_jsonl(selected_ledger)
    scored_entries = [score_entry(entry) for entry in entries]
    unsupported = [
        item
        for item in scored_entries
        if any(not check["passed"] and check["name"] in {"direct_evidence_for_high_impact", "no_fit_docs_present_readable", "next_action", "owner"} for check in item["checks"])
    ]
    score = round(average(item["score"] for item in scored_entries), 2)
    valid_decisions = sum(1 for item in scored_entries if item["verdict"] in HIGH_IMPACT_VERDICTS and item["score"] >= 75)
    blocked_decisions = sum(1 for item in scored_entries if item["verdict"] in BLOCKER_VERDICTS and item["score"] >= 75)
    regression_gates_passed = len(parse_errors) == 0 and len(unsupported) == 0 and len(scored_entries) > 0
    status = "keep_candidate" if score >= 75 and regression_gates_passed else "revise"

    return {
        "loop": LOOP_NAME,
        "score": score,
        "status": status,
        "ledger": str(selected_ledger),
        "entries_scored": len(scored_entries),
        "valid_decisions": valid_decisions,
        "blocked_decisions": blocked_decisions,
        "unsupported_decisions": len(unsupported),
        "parse_errors": parse_errors,
        "regression_gates_passed": regression_gates_passed,
        "entries": scored_entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score Blue Star bid-resolution autoresearch ledger.")
    parser.add_argument("--ledger", type=Path, help="Path to ledger.jsonl. Defaults to latest dated ledger.")
    parser.add_argument("--no-write", action="store_true", help="Print score without writing artifact JSON.")
    args = parser.parse_args()

    result = run(args.ledger)
    if not args.no_write:
        out_dir = today_dir()
        out_path = out_dir / f"score-{utc_stamp()}.json"
        result["score_artifact"] = str(out_path)
        out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
