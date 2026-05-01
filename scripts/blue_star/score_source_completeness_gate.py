#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FINAL_VERDICTS = {"pursue_quote", "true_no_fit"}
BLOCKER_VERDICTS = {
    "docs_missing_inaccessible",
    "extraction_failure",
    "drawing_or_vision_review_needed",
    "human_clarification_needed",
}
VALID_VERDICTS = FINAL_VERDICTS | BLOCKER_VERDICTS | {"continue_investigation"}
VALID_SOURCE_STATES = {
    "complete",
    "missing_or_inaccessible",
    "extraction_failed",
    "drawing_review_needed",
    "human_blocked",
}
BLOCKED_SOURCE_STATES = VALID_SOURCE_STATES - {"complete"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: row must be a JSON object")
        row["_line"] = line_no
        rows.append(row)
    return rows


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def direct_evidence_count(decision: dict[str, Any]) -> int:
    evidence = decision.get("evidence")
    if not isinstance(evidence, list):
        return 0
    count = 0
    for item in evidence:
        if not isinstance(item, dict):
            continue
        if (
            item.get("type") == "direct"
            and nonempty(item.get("source"))
            and nonempty(item.get("locator"))
            and nonempty(item.get("summary"))
        ):
            count += 1
    return count


def source_state(decision: dict[str, Any]) -> str | None:
    gate = decision.get("source_completeness")
    if not isinstance(gate, dict):
        return None
    state = gate.get("state")
    return state if isinstance(state, str) else None


def expected_verdict(row: dict[str, Any]) -> str | None:
    expected = row.get("expected")
    if not isinstance(expected, dict):
        return None
    verdict = expected.get("verdict")
    return verdict if isinstance(verdict, str) else None


def expected_source_state(row: dict[str, Any]) -> str | None:
    expected = row.get("expected")
    if not isinstance(expected, dict):
        return None
    state = expected.get("source_state")
    return state if isinstance(state, str) else None


def score_decision(row: dict[str, Any], key: str) -> dict[str, Any]:
    decision = row.get(key)
    if not isinstance(decision, dict):
        return {
            "score": 0,
            "unsupported_final": True,
            "blocker_as_no_fit": False,
            "direct_evidence_count": 0,
            "checks": [{"name": "decision_object", "passed": False, "points": 0, "max_points": 100}],
        }

    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, points: int) -> int:
        checks.append({"name": name, "passed": passed, "points": points if passed else 0, "max_points": points})
        return points if passed else 0

    verdict = decision.get("verdict")
    state = source_state(decision)
    direct_count = direct_evidence_count(decision)
    expected_v = expected_verdict(row)
    expected_s = expected_source_state(row)

    points = 0
    points += check("valid_verdict", verdict in VALID_VERDICTS, 10)
    points += check("valid_source_state", state in VALID_SOURCE_STATES, 10)
    points += check("direct_evidence_present", direct_count > 0, 25)

    final_needs_complete = verdict in FINAL_VERDICTS
    unsupported_final = final_needs_complete and (direct_count == 0 or state != "complete")
    points += check("final_verdict_has_complete_direct_source", not unsupported_final, 15)

    blocker_as_no_fit = verdict == "true_no_fit" and (
        state in BLOCKED_SOURCE_STATES
        or expected_v in BLOCKER_VERDICTS
        or expected_s in BLOCKED_SOURCE_STATES
    )
    points += check("blocker_not_labeled_no_fit", not blocker_as_no_fit, 10)

    if expected_v:
        points += check("expected_verdict_match", verdict == expected_v, 10)
    else:
        points += check("expected_verdict_match", True, 10)

    if expected_s:
        points += check("expected_source_state_match", state == expected_s, 5)
    else:
        points += check("expected_source_state_match", True, 5)

    points += check("next_action_present", nonempty(decision.get("next_action")), 8)
    points += check("owner_present", nonempty(decision.get("owner")), 7)

    return {
        "score": points,
        "verdict": verdict,
        "source_state": state,
        "unsupported_final": unsupported_final,
        "blocker_as_no_fit": blocker_as_no_fit,
        "direct_evidence_count": direct_count,
        "checks": checks,
    }


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def evaluate(rows: list[dict[str, Any]], eval_path: Path) -> dict[str, Any]:
    row_scores = []
    for row in rows:
        row_scores.append({
            "case_id": row.get("case_id") or row.get("bid_id") or f"line:{row.get('_line')}",
            "line": row.get("_line"),
            "baseline": score_decision(row, "baseline"),
            "candidate": score_decision(row, "candidate"),
        })

    baseline_score = round(average([item["baseline"]["score"] for item in row_scores]), 2)
    candidate_score = round(average([item["candidate"]["score"] for item in row_scores]), 2)
    delta = round(candidate_score - baseline_score, 2)

    baseline_unsupported = sum(1 for item in row_scores if item["baseline"]["unsupported_final"])
    candidate_unsupported = sum(1 for item in row_scores if item["candidate"]["unsupported_final"])
    baseline_blocker_no_fit = sum(1 for item in row_scores if item["baseline"]["blocker_as_no_fit"])
    candidate_blocker_no_fit = sum(1 for item in row_scores if item["candidate"]["blocker_as_no_fit"])
    baseline_direct = sum(item["baseline"]["direct_evidence_count"] for item in row_scores)
    candidate_direct = sum(item["candidate"]["direct_evidence_count"] for item in row_scores)

    regressions = []
    if candidate_unsupported > baseline_unsupported:
        regressions.append("unsupported_final_verdicts_increased")
    if candidate_blocker_no_fit > baseline_blocker_no_fit:
        regressions.append("blocker_as_no_fit_increased")
    if candidate_direct < baseline_direct:
        regressions.append("direct_evidence_coverage_decreased")

    status = "keep" if delta >= 5.0 and not regressions and row_scores else "discard"
    return {
        "scored_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "eval_path": str(eval_path),
        "cases": len(row_scores),
        "baseline_score": baseline_score,
        "candidate_score": candidate_score,
        "delta": delta,
        "status": status,
        "regressions": regressions,
        "metrics": {
            "baseline_unsupported_final_verdicts": baseline_unsupported,
            "candidate_unsupported_final_verdicts": candidate_unsupported,
            "baseline_blocker_as_no_fit": baseline_blocker_no_fit,
            "candidate_blocker_as_no_fit": candidate_blocker_no_fit,
            "baseline_direct_evidence_count": baseline_direct,
            "candidate_direct_evidence_count": candidate_direct,
        },
        "rows": row_scores,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score Blue Star source-completeness-gate autoresearch eval JSONL.")
    parser.add_argument("--eval", required=True, type=Path, help="Fixed eval JSONL with baseline and candidate decisions.")
    parser.add_argument("--out", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    rows = load_jsonl(args.eval)
    result = evaluate(rows, args.eval)
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
