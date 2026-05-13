#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CAT1_FIELDS = [
    "power_kw",
    "fuel_type",
    "voltage",
    "phase",
    "ats_required",
    "ats_amp_rating",
]

VALID_FIELD_STATUSES = {"resolved", "unresolved", "not_required"}
VALID_SUPPORT_LEVELS = {
    "literal_bid_text",
    "visual_read",
    "semantic_bid_inference",
    "product_model_join",
}
QUOTE_READY_STATES = {"ready_to_price", "packet_ready_with_caveats", "formal_proposal"}
NEEDS_INFO_STATES = {"needs_more_bid_information", "needs_clarification", "blocked"}


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


def normalize(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "").replace(",", "")


def expected_fields(row: dict[str, Any]) -> dict[str, Any]:
    expected = row.get("expected")
    if not isinstance(expected, dict):
        return {}
    fields = expected.get("fields")
    return fields if isinstance(fields, dict) else {}


def decision_fields(decision: dict[str, Any]) -> dict[str, Any]:
    fields = decision.get("fields")
    return fields if isinstance(fields, dict) else {}


def has_direct_evidence(field: dict[str, Any]) -> bool:
    evidence = field.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return False
    for item in evidence:
        if not isinstance(item, dict):
            continue
        has_source = nonempty(item.get("source")) or nonempty(item.get("evidence_id")) or nonempty(item.get("artifact_id"))
        has_locator = nonempty(item.get("locator")) or nonempty(item.get("page")) or nonempty(item.get("sheet"))
        has_summary = nonempty(item.get("summary")) or nonempty(item.get("excerpt")) or nonempty(item.get("visual_summary"))
        if has_source and has_locator and has_summary:
            return True
    return False


def field_support_level(field: dict[str, Any]) -> str | None:
    support = field.get("support_level")
    return support if isinstance(support, str) else None


def field_is_supported(field: dict[str, Any]) -> bool:
    return has_direct_evidence(field) and field_support_level(field) in VALID_SUPPORT_LEVELS


def field_value_matches(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    expected_status = expected.get("status")
    actual_status = actual.get("status")
    if expected_status != "resolved":
        return actual_status == expected_status
    if actual_status != "resolved":
        return False
    expected_value = normalize(expected.get("value"))
    actual_value = normalize(actual.get("value"))
    if not expected_value:
        return bool(actual_value)
    if expected_value == actual_value:
        return True
    aliases = expected.get("aliases")
    if isinstance(aliases, list):
        return actual_value in {normalize(alias) for alias in aliases}
    return False


def score_fields(row: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    expected = expected_fields(row)
    actual_fields = decision_fields(decision)
    points = 0.0
    max_points = 0.0
    unsupported = 0
    resolved_supported = 0
    newly_recovered_candidates = []
    details = {}

    for name in CAT1_FIELDS:
        expected_field = expected.get(name)
        actual_field = actual_fields.get(name)
        if not isinstance(expected_field, dict):
            continue
        max_points += 6.0
        if not isinstance(actual_field, dict):
            details[name] = {"points": 0, "reason": "missing_field_object"}
            continue
        status = actual_field.get("status")
        if status not in VALID_FIELD_STATUSES:
            details[name] = {"points": 0, "reason": "invalid_status"}
            continue
        if field_value_matches(expected_field, actual_field):
            if status == "resolved":
                if field_is_supported(actual_field):
                    points += 6.0
                    resolved_supported += 1
                    if actual_field.get("recovered_by_candidate") is True:
                        newly_recovered_candidates.append(name)
                    details[name] = {"points": 6, "reason": "resolved_supported"}
                else:
                    points += 2.0
                    unsupported += 1
                    details[name] = {"points": 2, "reason": "resolved_but_unsupported"}
            else:
                points += 4.0
                details[name] = {"points": 4, "reason": "correct_unresolved_or_not_required"}
        elif status == "resolved" and not field_is_supported(actual_field):
            unsupported += 1
            details[name] = {"points": 0, "reason": "wrong_unsupported_resolution"}
        else:
            details[name] = {"points": 0, "reason": "wrong_value_or_status"}

    scaled_points = 36.0 * (points / max_points) if max_points else 0.0
    return {
        "points": round(scaled_points, 2),
        "unsupported": unsupported,
        "resolved_supported": resolved_supported,
        "newly_recovered_candidates": newly_recovered_candidates,
        "details": details,
    }


def citation_score(decision: dict[str, Any]) -> dict[str, Any]:
    fields = decision_fields(decision)
    resolved = [
        field
        for field in fields.values()
        if isinstance(field, dict) and field.get("status") == "resolved"
    ]
    if not resolved:
        return {"points": 0.0, "direct_count": 0, "resolved_count": 0}
    direct_count = sum(1 for field in resolved if field_is_supported(field))
    return {
        "points": round(24.0 * direct_count / len(resolved), 2),
        "direct_count": direct_count,
        "resolved_count": len(resolved),
    }


def quote_readiness_score(row: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    expected = row.get("expected") if isinstance(row.get("expected"), dict) else {}
    expected_readiness = expected.get("quote_readiness")
    actual = decision.get("quote_readiness")
    fields = decision_fields(decision)
    unresolved_required = [
        name
        for name in CAT1_FIELDS
        if isinstance(fields.get(name), dict) and fields[name].get("status") == "unresolved"
    ]
    ready_with_missing = actual in QUOTE_READY_STATES and unresolved_required
    if actual == expected_readiness and not ready_with_missing:
        points = 15.0
    elif actual in NEEDS_INFO_STATES and expected_readiness in NEEDS_INFO_STATES:
        points = 10.0
    else:
        points = 0.0
    return {"points": points, "ready_with_missing": bool(ready_with_missing)}


def doc_completeness_score(decision: dict[str, Any]) -> dict[str, Any]:
    gate = decision.get("doc_completeness")
    if not isinstance(gate, dict):
        return {"points": 0.0, "has_gate": False}
    required = ["source_inventory_checked", "download_completeness", "glm_complete", "vision_complete"]
    present = sum(1 for key in required if key in gate)
    blockers_typed = gate.get("blockers_typed") is True or isinstance(gate.get("blockers"), list)
    points = 8.0 * present / len(required) + (2.0 if blockers_typed else 0.0)
    return {"points": round(points, 2), "has_gate": True}


def boundary_score(decision: dict[str, Any]) -> dict[str, Any]:
    violations = []
    if decision.get("uses_sizing_model_as_truth") is True:
        violations.append("uses_sizing_model_as_truth")
    if decision.get("uses_configurator_defaults_for_bid_facts") is True:
        violations.append("uses_configurator_defaults_for_bid_facts")
    if decision.get("uses_regex_as_truth") is True:
        violations.append("uses_regex_as_truth")
    if decision.get("uses_stale_field_fallback") is True:
        violations.append("uses_stale_field_fallback")
    return {"points": 0.0 if violations else 10.0, "violations": violations}


def next_action_score(decision: dict[str, Any]) -> dict[str, Any]:
    return {"points": 5.0 if nonempty(decision.get("next_action")) else 0.0}


def score_decision(row: dict[str, Any], key: str) -> dict[str, Any]:
    decision = row.get(key)
    if not isinstance(decision, dict):
        return {
            "score": 0.0,
            "unsupported": 0,
            "regression_violations": ["missing_decision_object"],
            "newly_recovered_candidates": [],
        }

    field_result = score_fields(row, decision)
    citation_result = citation_score(decision)
    readiness_result = quote_readiness_score(row, decision)
    doc_result = doc_completeness_score(decision)
    boundary_result = boundary_score(decision)
    next_result = next_action_score(decision)

    score = round(
        field_result["points"]
        + citation_result["points"]
        + readiness_result["points"]
        + doc_result["points"]
        + boundary_result["points"]
        + next_result["points"],
        2,
    )

    regression_violations = list(boundary_result["violations"])
    if readiness_result["ready_with_missing"]:
        regression_violations.append("quote_ready_with_unresolved_required_fields")

    return {
        "score": score,
        "field_score": field_result,
        "citation_score": citation_result,
        "quote_readiness_score": readiness_result,
        "doc_completeness_score": doc_result,
        "boundary_score": boundary_result,
        "next_action_score": next_result,
        "unsupported": field_result["unsupported"],
        "regression_violations": regression_violations,
        "newly_recovered_candidates": field_result["newly_recovered_candidates"],
    }


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def evaluate(rows: list[dict[str, Any]], eval_path: Path) -> dict[str, Any]:
    row_scores = []
    for row in rows:
        row_scores.append({
            "case_id": row.get("case_id") or row.get("bid_id") or f"line:{row.get('_line')}",
            "bid_id": row.get("bid_id"),
            "role": row.get("role"),
            "baseline": score_decision(row, "baseline"),
            "candidate": score_decision(row, "candidate"),
        })

    baseline_score = round(average([item["baseline"]["score"] for item in row_scores]), 2)
    candidate_score = round(average([item["candidate"]["score"] for item in row_scores]), 2)
    delta = round(candidate_score - baseline_score, 2)

    baseline_unsupported = sum(item["baseline"]["unsupported"] for item in row_scores)
    candidate_unsupported = sum(item["candidate"]["unsupported"] for item in row_scores)
    baseline_direct = sum(item["baseline"]["citation_score"]["direct_count"] for item in row_scores)
    candidate_direct = sum(item["candidate"]["citation_score"]["direct_count"] for item in row_scores)
    newly_recovered = sorted({
        f"{item['case_id']}:{field}"
        for item in row_scores
        for field in item["candidate"]["newly_recovered_candidates"]
    })

    regressions = []
    if candidate_unsupported > baseline_unsupported:
        regressions.append("unsupported_recovered_facts_increased")
    if candidate_direct < baseline_direct:
        regressions.append("direct_citation_coverage_decreased")
    for item in row_scores:
        if item["role"] == "protected_positive" and item["candidate"]["score"] < item["baseline"]["score"]:
            regressions.append(f"protected_control_regressed:{item['case_id']}")
        for violation in item["candidate"]["regression_violations"]:
            regressions.append(f"{item['case_id']}:{violation}")

    status = "keep" if delta >= 8.0 and not regressions and newly_recovered and row_scores else "discard"

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
            "baseline_unsupported_facts": baseline_unsupported,
            "candidate_unsupported_facts": candidate_unsupported,
            "baseline_direct_citation_count": baseline_direct,
            "candidate_direct_citation_count": candidate_direct,
            "newly_recovered_candidates": newly_recovered,
        },
        "rows": row_scores,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score Blue Star Cat-1 wiki recovery autoresearch eval JSONL.")
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
