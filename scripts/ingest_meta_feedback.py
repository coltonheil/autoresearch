#!/usr/bin/env python3
import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

from jsonschema import Draft202012Validator


REQUIRED_METRICS = [
    "spend",
    "ctr",
    "cpc",
    "cpm",
    "lpv",
    "atc",
    "ic",
    "purchases",
    "roas",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def validate_payload(payload: dict[str, Any], schema_path: Path) -> None:
    validator = Draft202012Validator(load_json(schema_path))
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.absolute_path))
    if errors:
        formatted = [f"{'/'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}" for err in errors]
        raise ValueError("Feedback schema validation failed:\n- " + "\n- ".join(formatted))


def ensure_feedback_matches_handoff(feedback: dict[str, Any], handoff: dict[str, Any]) -> dict[str, dict[str, Any]]:
    handoff_assets = {record["asset_id"]: record for record in handoff["records"]}
    unknown = sorted({result["asset_id"] for result in feedback["results"] if result["asset_id"] not in handoff_assets})
    if unknown:
        raise ValueError("Unknown asset_id values not present in handoff batch: " + ", ".join(unknown))

    missing_rows = sorted(set(handoff_assets) - {result["asset_id"] for result in feedback["results"]})
    if missing_rows:
        raise ValueError("Missing feedback rows for handoff asset_id values: " + ", ".join(missing_rows))

    return handoff_assets


def ensure_required_metrics(feedback: dict[str, Any]) -> None:
    failures: list[str] = []
    for result in feedback["results"]:
        asset_id = result.get("asset_id", "<unknown>")
        for metric in REQUIRED_METRICS:
            value = result.get(metric)
            if value is None:
                failures.append(f"{asset_id}: missing required metric `{metric}`")
    if failures:
        raise ValueError("Feedback metric validation failed:\n- " + "\n- ".join(failures))


def build_summary_by_asset(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for result in results:
        summary[result["asset_id"]] = {
            "verdict": result["verdict"],
            "spend": result["spend"],
            "ctr": result["ctr"],
            "cpc": result["cpc"],
            "cpm": result["cpm"],
            "lpv": result["lpv"],
            "atc": result["atc"],
            "ic": result["ic"],
            "purchases": result["purchases"],
            "roas": result["roas"],
            "cppurchase": result["cppurchase"],
            "meta_ids": {
                "campaign": result["meta_campaign_id"],
                "adset": result["meta_adset_id"],
                "ad": result["meta_ad_id"],
            },
        }
    return summary


def build_summary_by_verdict(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {"win": [], "hold": [], "kill": []}
    for result in results:
        grouped[result["verdict"]].append(result)

    summary: dict[str, dict[str, Any]] = {}
    for verdict, items in grouped.items():
        summary[verdict] = {
            "count": len(items),
            "asset_ids": [item["asset_id"] for item in items],
            "total_spend": round(sum(item["spend"] for item in items), 2),
            "total_purchases": sum(item["purchases"] for item in items),
            "avg_ctr": round(mean([item["ctr"] for item in items]), 4) if items else 0.0,
            "avg_roas": round(mean([item["roas"] for item in items]), 4) if items else 0.0,
        }
    return summary


def infer_directives(winners: list[dict[str, Any]], holds: list[dict[str, Any]], kills: list[dict[str, Any]], handoff_assets: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    creative: list[str] = []
    copy: list[str] = []

    if winners:
        winner_phases = Counter(handoff_assets[item["asset_id"]]["phase"] for item in winners)
        winner_scenes = [handoff_assets[item["asset_id"]]["scene"] for item in winners]
        creative.append(f"Scale the strongest visual territory from winners, especially {', '.join(sorted(set(winner_scenes[:3])))}.")
        creative.append(f"Bias next iteration toward `{winner_phases.most_common(1)[0][0]}`-style compositions because that phase produced the best verdict set.")
        copy.append("Keep product-first framing and premium presentation language in the top line and headline stack.")
        copy.append("Retain direct-response CTA structure around Shop Now and reinforce clean premium product hierarchy.")
    if holds:
        hold_scenes = [handoff_assets[item["asset_id"]]["concept_name"] for item in holds]
        creative.append(f"Refine hold concepts before scaling: {', '.join(sorted(set(hold_scenes)))} need tighter differentiation or cleaner staging.")
        copy.append("For holds, test sharper benefit-led headline angles while preserving the winning product-first structure.")
    if kills:
        kill_scenes = [handoff_assets[item["asset_id"]]["concept_name"] for item in kills]
        creative.append(f"Deprioritize or replace weak concepts: {', '.join(sorted(set(kill_scenes)))}.")
        copy.append("Drop copy tied to underperforming concepts and avoid vague premium language without a stronger hook.")
    if not creative:
        creative.append("No directives available because no feedback rows were ingested.")
    if not copy:
        copy.append("No copy directives available because no feedback rows were ingested.")
    return {"creative": creative, "copy": copy}


def render_next_brief(feedback: dict[str, Any], handoff_assets: dict[str, dict[str, Any]], normalized: dict[str, Any]) -> str:
    results = feedback["results"]
    winners = [item for item in results if item["verdict"] == "win"]
    holds = [item for item in results if item["verdict"] == "hold"]
    kills = [item for item in results if item["verdict"] == "kill"]
    directives = infer_directives(winners, holds, kills, handoff_assets)

    def section(title: str, items: list[dict[str, Any]]) -> list[str]:
        lines = [f"## {title}"]
        if not items:
            lines.append("- None")
            return lines
        for item in items:
            asset = handoff_assets[item["asset_id"]]
            lines.append(
                f"- `{item['asset_id']}` | {asset['concept_name']} | phase={asset['phase']} | spend=${item['spend']:.2f} | ctr={item['ctr']:.4f} | purchases={item['purchases']} | roas={item['roas']:.2f}"
            )
        return lines

    lines = [
        f"# Next Iteration Brief — {feedback['handoff_id']}",
        "",
        f"- feedback_id: `{feedback['feedback_id']}`",
        f"- returned_at: `{feedback['returned_at']}`",
        f"- total_assets: `{len(results)}`",
        "",
    ]
    lines.extend(section("Winners (win)", winners))
    lines.append("")
    lines.extend(section("Holds", holds))
    lines.append("")
    lines.extend(section("Kills", kills))
    lines.append("")
    lines.append("## Creative Directives")
    for item in directives["creative"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Copy Directives")
    for item in directives["copy"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Summary Metrics")
    for verdict, summary in normalized["summary_by_verdict"].items():
        lines.append(
            f"- {verdict}: count={summary['count']}, spend=${summary['total_spend']:.2f}, purchases={summary['total_purchases']}, avg_ctr={summary['avg_ctr']:.4f}, avg_roas={summary['avg_roas']:.4f}"
        )
    return "\n".join(lines) + "\n"


def ingest_feedback(feedback_path: Path, handoff_path: Path, output_path: Path, next_brief_path: Path | None) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / "contracts" / "meta-feedback.schema.json"
    feedback = load_json(feedback_path)
    handoff = load_json(handoff_path)

    validate_payload(feedback, schema_path)
    ensure_required_metrics(feedback)
    handoff_assets = ensure_feedback_matches_handoff(feedback, handoff)

    normalized = {
        "schema_version": "1.0.0",
        "feedback_id": feedback["feedback_id"],
        "handoff_id": feedback["handoff_id"],
        "returned_at": feedback["returned_at"],
        "asset_ids_verified_against_handoff": True,
        "summary_by_asset": build_summary_by_asset(feedback["results"]),
        "summary_by_verdict": build_summary_by_verdict(feedback["results"]),
        "results": feedback["results"],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(normalized, indent=2) + "\n")

    if next_brief_path is not None:
        next_brief_path.parent.mkdir(parents=True, exist_ok=True)
        next_brief_path.write_text(render_next_brief(feedback, handoff_assets, normalized))

    return normalized


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and ingest Meta retail feedback into a normalized summary.")
    parser.add_argument("--feedback", required=True, type=Path)
    parser.add_argument("--handoff", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--next-brief", type=Path)
    args = parser.parse_args()

    normalized = ingest_feedback(
        args.feedback.expanduser().resolve(),
        args.handoff.expanduser().resolve(),
        args.output.expanduser().resolve(),
        args.next_brief.expanduser().resolve() if args.next_brief else None,
    )
    print(json.dumps({
        "feedback_id": normalized["feedback_id"],
        "handoff_id": normalized["handoff_id"],
        "results": len(normalized["results"]),
        "output": str(args.output),
        "next_brief": str(args.next_brief) if args.next_brief else None,
    }, indent=2))


if __name__ == "__main__":
    main()
