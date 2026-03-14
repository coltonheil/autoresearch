#!/usr/bin/env python3
"""Build a markdown review package for Tier 2 draft variants."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_DOMAIN = "ad-creative"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Format a review-ready package from variant directories.")
    parser.add_argument("--variants-dir", type=Path, required=True, help="Directory containing variant subdirectories")
    parser.add_argument("--output", type=Path, required=True, help="Path to write review-package.md")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN, help=f"Domain label for the package (default: {DEFAULT_DOMAIN})")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def find_first(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def summarize_validation(data: dict[str, Any] | None) -> tuple[str, list[str], list[str]]:
    if not data:
        return "missing", [], ["Validation file missing"]
    checks = data.get("checks", {})
    status = data.get("summary", {}).get("overall_status", "unknown")
    warnings: list[str] = []
    failures: list[str] = []
    for name, payload in checks.items():
        detail = f"{name}: {payload.get('details', '')}".strip()
        if payload.get("status") == "FAIL":
            failures.append(detail)
        elif payload.get("status") == "WARN":
            warnings.append(detail)
    return str(status).lower(), warnings, failures


def extract_scores(score_data: dict[str, Any] | None) -> dict[str, Any]:
    if not score_data:
        return {}
    keep = {}
    for key in ["total", "overall_score", "proxy_score", "score", "compliance", "brand_voice", "clarity", "trust"]:
        if key in score_data:
            keep[key] = score_data[key]
    if not keep:
        for key, value in score_data.items():
            if isinstance(value, (int, float, str, bool)):
                keep[key] = value
    return keep


def pick_copy_files(variant_dir: Path) -> list[Path]:
    return sorted(
        [p for p in variant_dir.iterdir() if p.is_file() and p.suffix.lower() in {".md", ".txt"} and "package" not in p.name.lower()]
    )


def pick_image_files(variant_dir: Path) -> list[Path]:
    return sorted([p for p in variant_dir.iterdir() if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}])


def recommendation(score_data: dict[str, Any] | None, creative_status: str, copy_status: str) -> str:
    if creative_status == "fail" or copy_status == "fail":
        return "DISCARD"
    total = None
    if score_data:
        for key in ["total", "overall_score", "proxy_score", "score"]:
            if key in score_data and isinstance(score_data[key], (int, float)):
                total = float(score_data[key])
                break
    if creative_status == "warn" or copy_status == "warn":
        return "KEEP WITH WARNINGS"
    if total is not None and total < 50:
        return "DISCARD"
    return "KEEP"


def build_variant_entry(variant_dir: Path) -> dict[str, Any]:
    image_files = pick_image_files(variant_dir)
    copy_files = pick_copy_files(variant_dir)
    creative_validation_path = find_first([
        variant_dir / "creative_validation.json",
        variant_dir / "validate_ad_creative.json",
        variant_dir / "ad_creative_validation.json",
    ])
    copy_validation_path = find_first([
        variant_dir / "copy_validation.json",
        variant_dir / "validate_ad_copy.json",
        variant_dir / "ad_copy_validation.json",
    ])
    score_path = find_first([
        variant_dir / "score.json",
        variant_dir / "scores.json",
        variant_dir / "variant_score.json",
        variant_dir / "result.json",
    ])

    creative_validation = read_json(creative_validation_path) if creative_validation_path else None
    copy_validation = read_json(copy_validation_path) if copy_validation_path else None
    score_data = read_json(score_path) if score_path else None

    creative_status, creative_warn, creative_fail = summarize_validation(creative_validation)
    copy_status, copy_warn, copy_fail = summarize_validation(copy_validation)

    return {
        "name": variant_dir.name,
        "path": str(variant_dir),
        "images": [str(p) for p in image_files],
        "copy": {p.name: read_text(p) for p in copy_files},
        "scores": extract_scores(score_data),
        "creative_validation": creative_validation,
        "copy_validation": copy_validation,
        "creative_status": creative_status,
        "copy_status": copy_status,
        "warnings": creative_warn + copy_warn,
        "failures": creative_fail + copy_fail,
        "recommendation": recommendation(score_data, creative_status, copy_status),
    }


def sort_key(entry: dict[str, Any]) -> tuple[int, float, str]:
    recommendation_rank = {"KEEP": 0, "KEEP WITH WARNINGS": 1, "DISCARD": 2}
    score = 0.0
    for key in ["total", "overall_score", "proxy_score", "score"]:
        value = entry["scores"].get(key)
        if isinstance(value, (int, float)):
            score = float(value)
            break
    return (recommendation_rank.get(entry["recommendation"], 3), -score, entry["name"])


def format_dict_list(data: dict[str, Any]) -> str:
    if not data:
        return "- None"
    return "\n".join(f"- {key}: {value}" for key, value in data.items())


def build_markdown(entries: list[dict[str, Any]], domain: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d %H:%M %Z")
    lines = [
        f"# Review Package: {domain}",
        "",
        f"- Package date: {today}",
        f"- Domain: {domain}",
        f"- Variant count: {len(entries)}",
        "- Approval: ⚠️ REQUIRES COLTON APPROVAL BEFORE ACTIVATION",
        "",
        "## Summary Table",
        "",
        "| Rank | Variant | Recommendation | Score | Creative | Copy |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for idx, entry in enumerate(entries, start=1):
        score = next((entry["scores"].get(key) for key in ["total", "overall_score", "proxy_score", "score"] if key in entry["scores"]), "—")
        lines.append(
            f"| {idx} | {entry['name']} | {entry['recommendation']} | {score} | {entry['creative_status']} | {entry['copy_status']} |"
        )

    compliance_status = "issues-flagged" if any(e["failures"] or e["warnings"] for e in entries) else "all-clear"
    lines += [
        "",
        "## Compliance Status",
        "",
        f"- {compliance_status}",
    ]

    for entry in entries:
        lines += [
            "",
            f"## Variant: {entry['name']}",
            "",
            f"- Variant path: `{entry['path']}`",
            f"- Image path(s): {', '.join(f'`{p}`' for p in entry['images']) if entry['images'] else 'None found'}",
            f"- Thumbnail reference: {entry['images'][0] if entry['images'] else 'None'}",
            f"- Keep/discard recommendation: **{entry['recommendation']}**",
            "",
            "### Proxy Scores",
            "",
            format_dict_list(entry["scores"]),
            "",
            "### Copy Text",
            "",
        ]
        if entry["copy"]:
            for name, body in entry["copy"].items():
                lines += [f"#### {name}", "", body, ""]
        else:
            lines += ["- No copy files found.", ""]

        lines += [
            "### Creative Validation",
            "",
            f"- Status: {entry['creative_status']}",
            format_dict_list((entry.get("creative_validation") or {}).get("summary", {})),
            "",
            "### Copy Validation",
            "",
            f"- Status: {entry['copy_status']}",
            format_dict_list((entry.get("copy_validation") or {}).get("summary", {})),
            "",
            "### Warnings / Flags",
            "",
        ]
        if entry["warnings"] or entry["failures"]:
            for item in entry["failures"]:
                lines.append(f"- FAIL: {item}")
            for item in entry["warnings"]:
                lines.append(f"- WARN: {item}")
        else:
            lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    if not args.variants_dir.exists() or not args.variants_dir.is_dir():
        raise SystemExit(f"Variants directory not found: {args.variants_dir}")
    variant_dirs = sorted([p for p in args.variants_dir.iterdir() if p.is_dir()])
    entries = [build_variant_entry(path) for path in variant_dirs]
    entries.sort(key=sort_key)
    markdown = build_markdown(entries, args.domain)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
