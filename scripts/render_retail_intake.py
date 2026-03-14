#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def validate_handoff(packet: dict[str, Any], schema_path: Path) -> None:
    Draft202012Validator(load_json(schema_path)).validate(packet)


def render_brief(packet: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Retail Intake Brief — {packet['handoff_id']}")
    lines.append("")
    lines.append("## Batch Summary")
    lines.append(f"- batch_id: `{packet['handoff_id']}`")
    lines.append(f"- created_at: `{packet['generated_at']}`")
    lines.append(f"- source_product: `{packet['source_run']['product']}`")
    lines.append(f"- assets_in_batch: `{len(packet['records'])}`")
    lines.append(f"- activation_policy: `{packet['activation_policy']}`")
    lines.append("")
    lines.append("## Retail Reporting Instructions")
    lines.append("- Preserve `asset_id` exactly as provided. Do not rename, shorten, or reformat it.")
    lines.append("- Include Meta identifiers for every test row: `meta_campaign_id`, `meta_adset_id`, and `meta_ad_id`.")
    lines.append("- Return these performance metrics for every asset: `spend`, `ctr`, `cpc`, `cpm`, `lpv`, `atc`, `ic`, `purchases`, `roas`.")
    lines.append("- Return a final verdict for each asset as one of: `win`, `hold`, `kill`.")
    lines.append("- One result row per `asset_id`, with exact test window via `date_start` and `date_end`.")
    lines.append("- Keep any operator observations in `notes`.")
    lines.append("")
    lines.append("## Asset Packet")
    for idx, record in enumerate(packet["records"], start=1):
        lines.append("")
        lines.append(f"### {idx}. {record['asset_id']} — {record['concept_name']}")
        lines.append(f"- phase: `{record['phase']}`")
        lines.append(f"- rank: `{record['rank']}`")
        lines.append(f"- image_path: `{record['image_path']}`")
        lines.append(f"- scene: {record['scene']}")
        lines.append(f"- cta: `{record['cta']}`")
        lines.append("- headlines:")
        for item in record["headline_variants"]:
            lines.append(f"  - {item}")
        lines.append("- copy_variants:")
        for item in record["copy_variants"]:
            lines.append(f"  - {item}")
        lines.append("- primary_text_variants:")
        for item in record["primary_text_variants"]:
            lines.append(f"  - {item}")
    lines.append("")
    lines.append("## Return Path")
    lines.append("- Feedback packet must validate against `contracts/meta-feedback.schema.json`.")
    lines.append("- Returned file should keep this `handoff_id` so autoresearch can join results back to source prompts and validation artifacts.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a retail-facing Markdown brief from a Meta handoff packet.")
    parser.add_argument("--handoff", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    handoff_path = args.handoff.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / "contracts" / "meta-handoff.schema.json"

    packet = load_json(handoff_path)
    validate_handoff(packet, schema_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_brief(packet))
    print(json.dumps({"handoff_id": packet["handoff_id"], "records": len(packet["records"]), "output": str(output_path)}, indent=2))


if __name__ == "__main__":
    main()
