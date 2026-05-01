#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def title_from_scene(scene: str) -> str:
    base = scene.split(",", 1)[0].strip()
    return " ".join(word.capitalize() for word in base.split())


def asset_id(product: str, run_date: str, phase: str, slug: str) -> str:
    return f"{slugify(product)}-{run_date.replace('-', '')}-{slugify(phase)}-{slug.split('-')[-1]}"


def build_copy_variants(product: str, concept_name: str, scene: str) -> list[str]:
    return [
        f"{concept_name} puts Heil Ginseng {product} front and center in a clean premium scene.",
        f"Draft retail creative built around the real {product} package with minimal props and strong product hierarchy.",
        f"Use this asset to test a polished product-first angle anchored in {scene}."
    ]


def build_headlines(product: str, concept_name: str) -> list[str]:
    return [
        f"Heil Ginseng {product.capitalize()}",
        f"{concept_name}",
        f"Premium {product.capitalize()} Hero"
    ]


def build_primary_texts(product: str, scene: str) -> list[str]:
    return [
        f"Retail test asset for Heil Ginseng {product}. Product identity is preserved and the scene stays clean and premium.",
        f"Built from the locked source package with passing packaging, root, and no-humans gates. Scene: {scene}.",
        "Draft-only creative handoff. Human activation required in Meta Ads Manager."
    ]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def validate_packet(packet: dict[str, Any], schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator(schema).validate(packet)


def build_packet(source_run: Path, output_path: Path) -> dict[str, Any]:
    run_summary = load_json(source_run / "run-summary.json")
    run_date_match = re.search(r"(\d{4}-\d{2}-\d{2})", source_run.name)
    if not run_date_match:
        raise ValueError(f"Could not infer run date from {source_run}")
    run_date = run_date_match.group(1)
    handoff_id = output_path.stem

    records = []
    seen = set()
    for item in run_summary["top_8"]:
        slug = Path(item["image_path"]).stem.split("capsules-", 1)[-1]
        detail = next(r for r in run_summary["all_records"] if Path(r["image_path"]) == Path(item["image_path"]))
        validation = load_json(Path(item["validation_path"]))
        scene = detail.get("scene", slug.replace("-", " "))
        concept_name = title_from_scene(scene)
        stable_id = asset_id(run_summary["product"], run_date, item["phase"], detail["slug"])
        if stable_id in seen:
            raise ValueError(f"Duplicate asset_id generated: {stable_id}")
        seen.add(stable_id)
        record = {
            "asset_id": stable_id,
            "product": run_summary["product"],
            "concept_name": concept_name,
            "rank": item["rank"],
            "phase": item["phase"],
            "scene": scene,
            "image_path": item["image_path"],
            "validation_path": item["validation_path"],
            "packaging_gate": validation["checks"]["packaging_fidelity"]["status"],
            "root_gate": validation["checks"]["root_authenticity"]["status"],
            "no_humans_gate": validation["checks"]["ai_humans"]["status"],
            "composite_score": item["composite"],
            "brand_fit_score": item["brand_fit_score"],
            "copy_variants": build_copy_variants(run_summary["product"], concept_name, scene),
            "headline_variants": build_headlines(run_summary["product"], concept_name),
            "primary_text_variants": build_primary_texts(run_summary["product"], scene),
            "cta": "Shop Now",
            "status": "ready_for_retail",
            "operator_notes": f"Source slug {detail['slug']}; keep asset_id stable in retail naming and feedback."
        }
        records.append(record)

    packet = {
        "schema_version": "1.0.0",
        "handoff_id": handoff_id,
        "source_run": {
            "product": run_summary["product"],
            "run_date": run_date,
            "run_path": str(source_run),
            "source_summary": f"Top 8 kept assets from {source_run.name}"
        },
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "channel_from": "#meta-ads",
        "channel_to": "#ginseng-retail",
        "activation_policy": "draft_only_human_activation_required",
        "notes": "Draft-only retail handoff. Human activation required. Never auto-activate campaigns.",
        "records": records
    }
    schema_path = Path(__file__).resolve().parents[1] / "contracts" / "meta-handoff.schema.json"
    validate_packet(packet, schema_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(packet, indent=2) + "\n")
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Meta handoff packet from an autoresearch run.")
    parser.add_argument("--source-run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    packet = build_packet(args.source_run.expanduser().resolve(), args.output.expanduser().resolve())
    print(json.dumps({"handoff_id": packet["handoff_id"], "records": len(packet["records"]), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
