#!/usr/bin/env python3
"""Run one autoresearch PDP copy loop."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

DEFAULT_PROGRAM = Path("programs/pdp-copy.md")
DEFAULT_RESULTS = Path("results/pdp-copy.tsv")
DEFAULT_BASELINE = Path.home() / ".openclaw/workspace/outputs/autoresearch/pdp-copy/2026-03-09/capsules-baseline.md"
DEFAULT_OUTPUT_ROOT = Path.home() / ".openclaw/workspace/outputs/autoresearch/pdp-copy"
PRODUCT_HANDLE = "capsules"
PRODUCT_ID = "7630033420384"
RUBRIC_VERSION = "pdp-cro.md"
MAX_VARIANTS_FALLBACK = 5
RESULT_FIELDS = [
    "run_id",
    "timestamp_utc",
    "product_handle",
    "product_id",
    "variant_path",
    "baseline_score",
    "variant_score",
    "score_delta",
    "clarity_score",
    "benefit_score",
    "trust_score",
    "scanability_score",
    "seo_score",
    "cta_support_score",
    "compliance_score",
    "compliance_pass",
    "keep_decision",
    "notes",
    "rubric_version",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and score PDP copy variants, then log keep/discard decisions.",
    )
    parser.add_argument("--variants", type=int, default=5, help="Number of variants to generate (default: 5)")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE, help="Baseline markdown file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for generated variants (default: ~/.openclaw/workspace/outputs/autoresearch/pdp-copy/YYYY-MM-DD/)",
    )
    parser.add_argument("--program", type=Path, default=DEFAULT_PROGRAM, help="Program markdown file")
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS, help="Results TSV path")
    parser.add_argument(
        "--baseline-score-json",
        type=Path,
        default=None,
        help="Optional cached baseline score JSON from score_pdp.py",
    )
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model to pass through to child scripts")
    return parser.parse_args()


def load_text(path: Path, label: str) -> str:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_program_value(pattern: str, text: str, default: int) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return int(match.group(1)) if match else default


def extract_keep_threshold_note(text: str) -> str:
    match = re.search(r"A variant can only be marked \*\*KEEP\*\* if both conditions are true:(.*?)(?:##|$)", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return " ".join(line.strip() for line in match.group(1).splitlines() if line.strip())


def default_output_dir() -> Path:
    return DEFAULT_OUTPUT_ROOT / date.today().isoformat()


def run_script(script_name: str, script_args: list[str]) -> str:
    script_path = Path(__file__).with_name(script_name)
    cmd = [sys.executable, str(script_path), *script_args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "Unknown error"
        raise RuntimeError(f"{script_name} failed: {stderr}")
    return result.stdout.strip()


def load_score(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def score_variant(variant_path: Path, model: str) -> dict[str, Any]:
    output = run_script("score_pdp.py", [str(variant_path), "--model", model])
    return json.loads(output)


def generate_variant(baseline_path: Path, output_path: Path, model: str, focus: str = "") -> None:
    args = [str(baseline_path), str(output_path), "--model", model]
    if focus:
        args.extend(["--focus", focus])
    run_script("generate_variant.py", args)


def next_run_id(results_path: Path, day_token: str) -> str:
    prefix = f"{PRODUCT_HANDLE}-{day_token}-r"
    max_index = 0
    if results_path.exists():
        with results_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                run_id = (row.get("run_id") or "").strip()
                if run_id.startswith(prefix):
                    try:
                        max_index = max(max_index, int(run_id.split("-r")[-1]))
                    except ValueError:
                        continue
    return f"{prefix}{max_index + 1:02d}"


def ensure_results_header(results_path: Path) -> None:
    expected_header = "\t".join(RESULT_FIELDS)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    if not results_path.exists():
        results_path.write_text(expected_header + "\n", encoding="utf-8")
        return

    lines = results_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        results_path.write_text(expected_header + "\n", encoding="utf-8")
        return

    if lines[0].strip() != expected_header:
        results_path.write_text("\n".join([expected_header, *lines[1:]]) + "\n", encoding="utf-8")


def append_result(results_path: Path, row: dict[str, Any]) -> None:
    with results_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS, delimiter="\t")
        writer.writerow(row)


def format_bool(value: bool) -> str:
    return "true" if value else "false"


def print_summary(rows: list[dict[str, Any]]) -> None:
    ranked = sorted(rows, key=lambda item: float(item["variant_score"]), reverse=True)
    headers = ["variant", "score", "delta", "keep", "compliance", "notes"]
    table_rows = []
    for row in ranked:
        table_rows.append([
            Path(row["variant_path"]).name,
            row["variant_score"],
            row["score_delta"],
            row["keep_decision"],
            row["compliance_pass"],
            row["notes"],
        ])

    widths = [len(header) for header in headers]
    for table_row in table_rows:
        for idx, cell in enumerate(table_row):
            widths[idx] = max(widths[idx], len(str(cell)))

    print(" | ".join(header.ljust(widths[idx]) for idx, header in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for table_row in table_rows:
        print(" | ".join(str(cell).ljust(widths[idx]) for idx, cell in enumerate(table_row)))


def main() -> int:
    args = parse_args()
    try:
        if args.variants < 1:
            raise ValueError("--variants must be at least 1")

        program_text = load_text(args.program, "Program file")
        max_variants = extract_program_value(r"Maximum variants to generate and score in a single run:\s*\*\*(\d+)\*\*", program_text, MAX_VARIANTS_FALLBACK)
        requested_variants = min(args.variants, max_variants)
        keep_threshold_note = extract_keep_threshold_note(program_text)
        output_dir = args.output_dir or default_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)

        if args.baseline_score_json:
            baseline_score = load_score(args.baseline_score_json)
        else:
            baseline_score = score_variant(args.baseline, args.model)

        ensure_results_header(args.results)

        now = datetime.now(UTC)
        day_token = now.strftime("%Y%m%d")
        run_id = next_run_id(args.results, day_token)

        focus_cycle = ["clarity", "benefit", "trust", "scanability", "seo"]
        logged_rows: list[dict[str, Any]] = []

        for index in range(1, requested_variants + 1):
            focus = focus_cycle[(index - 1) % len(focus_cycle)]
            variant_path = output_dir / f"{PRODUCT_HANDLE}-v{index}-{focus}.md"
            generate_variant(args.baseline, variant_path, args.model, focus=focus)
            variant_score = score_variant(variant_path, args.model)

            keep = (variant_score["total"] > baseline_score["total"]) and (not variant_score["hard_fail"])
            notes_parts = [f"focus={focus}"]
            if variant_score["discard_reasons"]:
                notes_parts.append("discard=" + "; ".join(variant_score["discard_reasons"]))
            if keep_threshold_note:
                notes_parts.append("rule=" + keep_threshold_note)
            row = {
                "run_id": run_id,
                "timestamp_utc": now.isoformat(),
                "product_handle": PRODUCT_HANDLE,
                "product_id": PRODUCT_ID,
                "variant_path": str(variant_path),
                "baseline_score": f"{baseline_score['total']:.2f}",
                "variant_score": f"{variant_score['total']:.2f}",
                "score_delta": f"{variant_score['total'] - baseline_score['total']:.2f}",
                "clarity_score": str(variant_score["clarity"]),
                "benefit_score": str(variant_score["benefit"]),
                "trust_score": str(variant_score["trust"]),
                "scanability_score": str(variant_score["scanability"]),
                "seo_score": str(variant_score["seo"]),
                "cta_support_score": str(variant_score["cta"]),
                "compliance_score": str(variant_score["compliance"]),
                "compliance_pass": format_bool(not variant_score["hard_fail"]),
                "keep_decision": "KEEP" if keep else "DISCARD",
                "notes": " | ".join(notes_parts),
                "rubric_version": RUBRIC_VERSION,
            }
            append_result(args.results, row)
            logged_rows.append(row)

        print(f"Run ID: {run_id}")
        print(f"Baseline score: {baseline_score['total']:.2f}")
        print_summary(logged_rows)
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
