#!/usr/bin/env python3
"""Optimize Heil ad creative prompts, generate images, validate identity, and rank outputs.

This script runs a small evolutionary loop over prompt templates, then executes a capped
image-edit campaign using real Heil reference photos as anchors.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import statistics
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = Path.home() / ".openclaw" / "workspace"
DEFAULT_OUTDIR = WORKSPACE / "outputs" / "autoresearch" / "ad-creative" / "2026-03-12-r3-opt"
GENERATOR = WORKSPACE / "skills" / "nano-banana-pro" / "scripts" / "generate_image.py"
VALIDATOR = ROOT / "scripts" / "validate_ad_creative.py"
PROMPT_LIBRARY_PATH = ROOT / "programs" / "ad-creative-prompt-library.md"
MANIFEST_PATH = ROOT / "programs" / "reference-manifest.json"
DEFAULT_PILOT_TOTAL = 16
DEFAULT_FINAL_TOTAL = 24
MODEL = "gpt-4o"
PRODUCTS = ["capsules", "roots", "tea", "powder"]

CAMERA_ANGLES = [
    "front-facing hero shot",
    "slight 3/4 tabletop angle",
    "overhead editorial flat lay",
    "portrait crop with the package upright and dominant",
]
SCENE_COMPOSITIONS = [
    "single hero package with one supporting ingredient cue and clean negative space",
    "editorial still life with package centered and props pushed to edges",
    "tight premium product-world scene with shallow prop count and clear hierarchy",
    "minimal ritual scene with package anchored in the foreground",
]
LIGHTING_STYLES = [
    "warm early-morning window light",
    "soft directional studio daylight with gentle shadows",
    "moody amber side-light with realistic falloff",
    "clean natural daylight with subtle shadow geometry",
]
NEGATIVE_PROMPTS = [
    "no people, no faces, no bodies, no extra hands, no stock-photo styling, no floating objects, no duplicated products, no gibberish label text, no generic supplement bottle, no fake logo",
    "no AI humans, no blank packaging, no relabeled product, no surreal props, no plastic roots, no chrome wellness aesthetic",
    "no anonymous lifestyle model, no cartoon roots, no extra packaging variants, no overdesigned set, no glossy fake reflections",
]

PRODUCT_GUIDANCE = {
    "capsules": {
        "offer": "daily energy ritual",
        "audience": "health-conscious adults 35-55",
        "season": "late winter reset",
        "morphology": "if a root is visible, keep it secondary and botanically realistic with wrinkled skin and irregular branching",
        "visible_requirement": "The real Heil capsules bottle must be visible, upright, label-forward, and unmistakably the same SKU as the reference.",
    },
    "roots": {
        "offer": "heritage Wisconsin root",
        "audience": "buyers seeking authentic American ginseng",
        "season": "heritage harvest",
        "morphology": "visible roots must match real American ginseng morphology: irregular branching, natural taper, wrinkles, fibrous texture, asymmetric root legs, realistic age cues",
        "visible_requirement": "If packaging is visible, it must match the Heil roots packaging exactly; hero roots must look like real American ginseng from the reference photos.",
    },
    "tea": {
        "offer": "calm daily tea ritual",
        "audience": "premium wellness shoppers",
        "season": "quiet morning routine",
        "morphology": "if roots appear, they must stay subtle and realistic, never stylized",
        "visible_requirement": "The real Heil tea package must remain visible and recognizable with the same label architecture and colorway as the reference.",
    },
    "powder": {
        "offer": "mix-in wellness ritual",
        "audience": "smoothie and functional beverage shoppers",
        "season": "daily routine",
        "morphology": "any roots or powder cues must remain natural-looking and grounded in real ginseng texture",
        "visible_requirement": "The real Heil powder pouch must remain visible, upright, and clearly the same pouch design as the reference.",
    },
}

BASE_PROMPTS = {
    "capsules": [
        "Use the provided real Heil capsules bottle photo as the locked product anchor. Create a premium editorial still life on warm limestone with three loose capsules and a small realistic ginseng root accent.",
        "Transform the real Heil capsules reference into a clean morning-window product scene on linen with subtle shadows and very low prop count.",
        "Keep the exact Heil capsules bottle identity from the input photo and stage it as a dark apothecary hero shot with one root accent and negative space for copy.",
        "Edit the real Heil capsules product photo into a portrait social ad scene with upright bottle, ceramic dish with capsules, and warm daylight.",
        "Use the real Heil capsules bottle as a non-negotiable packaging lock and restyle only the environment into a minimal premium tabletop scene.",
        "Start from the supplied Heil capsules photo and create a scroll-stopping editorial flat lay with restrained props and clear label readability.",
    ],
    "roots": [
        "Use the real Heil roots packaging photo as the anchor and build a natural premium scene with real-looking American ginseng roots on a wood board.",
        "Edit the supplied Heil roots packaging reference into a heritage still life with one dominant authentic root, warm light, and minimal props.",
        "Keep the exact Heil roots packaging identity while creating a moody editorial product-world scene with realistic root texture and earth tones.",
        "Transform the real Heil roots photo into a clean tabletop ad with upright packaging, believable root branching, and copy-friendly negative space.",
        "Use the real Heil roots package and authentic root morphology as hard locks, then create a premium harvest-inspired scene without adding fake product variants.",
        "Start from the approved Heil roots reference and restage it as a portrait product hero with lifelike roots, wrinkles, taper, and asymmetry.",
    ],
    "tea": [
        "Use the real Heil tea package photo as a packaging lock and create a calm editorial tea ritual scene with steam, ceramic mug, and warm morning light.",
        "Edit the supplied Heil tea reference into a premium product-world still life with visible package, teacup, and restrained botanicals.",
        "Keep the exact Heil tea package identity from the input image and restyle only the environment into a warm windowsill ritual scene.",
        "Transform the real Heil tea package photo into a portrait social ad with upright package, mug, steam, and clean negative space.",
        "Use the approved Heil tea photo as the hero anchor and create a premium tabletop scene that preserves label architecture and colorway exactly.",
        "Start from the provided Heil tea package and generate a scroll-stopping editorial composition with real package visibility and no stock-photo model look.",
    ],
    "powder": [
        "Use the real Heil powder pouch photo as a locked anchor and create a premium functional beverage scene with one serving cue and warm natural light.",
        "Edit the supplied Heil powder reference into an editorial still life with upright pouch, spooned powder, and restrained recipe context.",
        "Keep the exact Heil powder pouch identity and restyle only the surface, props, and lighting into a clean product-world ad scene.",
        "Transform the real Heil powder pouch photo into a portrait lifestyle still life with pouch dominant, subtle beverage cue, and copy-friendly space.",
        "Use the approved Heil powder package as a non-negotiable anchor and create a premium morning routine composition without changing the pouch design.",
        "Start from the real Heil powder pouch image and build a warm wood-and-ceramic editorial scene with realistic powder appearance.",
    ],
}


@dataclass
class TemplateResult:
    product: str
    phase: str
    template_id: str
    input_image: str
    output_image: str
    prompt: str
    objective: float
    overall_status: str
    pass_identity: bool
    no_humans_pass: bool
    packaging_status: str
    root_status: str
    visual_score: int
    packaging_score: int
    root_score: int
    notes: list[str]
    validation_json: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--pilot-total", type=int, default=DEFAULT_PILOT_TOTAL)
    parser.add_argument("--final-total", type=int, default=DEFAULT_FINAL_TOTAL)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument("--skip-baseline", action="store_true")
    return parser.parse_args()


def ensure_env() -> None:
    missing = [key for key in ("GEMINI_API_KEY", "OPENAI_API_KEY") if not os.getenv(key)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
    if not GENERATOR.exists():
        raise FileNotFoundError(f"Generator not found: {GENERATOR}")
    if not VALIDATOR.exists():
        raise FileNotFoundError(f"Validator not found: {VALIDATOR}")


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def product_refs(manifest: dict[str, Any], product: str) -> list[Path]:
    entry = manifest["products"][product]
    paths = [Path(x["path"]) for x in entry.get("packaging_references", [])]
    paths.extend(Path(x["path"]) for x in entry.get("root_references", []))
    return paths


def primary_input(manifest: dict[str, Any], product: str) -> Path:
    entry = manifest["products"][product]
    return Path(entry["packaging_references"][0]["path"])


def reference_descriptors(manifest: dict[str, Any], product: str) -> str:
    entry = manifest["products"][product]
    notes = [x.get("notes", "") for x in entry.get("packaging_references", []) + entry.get("root_references", [])]
    return " ".join(note.strip() for note in notes if note.strip())


def mutate_prompt(product: str, base_prompt: str, manifest: dict[str, Any], failure_signals: list[str] | None = None) -> str:
    guidance = PRODUCT_GUIDANCE[product]
    camera = random.choice(CAMERA_ANGLES)
    composition = random.choice(SCENE_COMPOSITIONS)
    lighting = random.choice(LIGHTING_STYLES)
    negative = random.choice(NEGATIVE_PROMPTS)
    packaging_lock = (
        f"Packaging lock: {guidance['visible_requirement']} Preserve the real Heil logo mark, package geometry, label layout, colorway, and proportions from the source image exactly. "
        "Do not invent, simplify, relabel, crop away, or genericize the package."
    )
    root_lock = f"Root realism lock: {guidance['morphology']}. {reference_descriptors(manifest, product)}"
    failure_signals = failure_signals or []
    if any("packaging" in f for f in failure_signals):
        packaging_lock += " Increase label clarity, keep the package larger in frame, and treat the input image as a literal identity anchor rather than inspiration."
    if any("root" in f for f in failure_signals):
        root_lock += " Strengthen wrinkles, natural taper, asymmetry, and fibrous branching. Remove any smooth, plastic, or symmetric root forms."
    prompt = textwrap.dedent(
        f"""
        {base_prompt}

        Camera angle: {camera}.
        Scene composition: {composition}.
        Lighting: {lighting}.
        Offer context: {guidance['offer']} for {guidance['audience']} during {guidance['season']}.
        {packaging_lock}
        {root_lock}
        Negative prompt: {negative}.
        Keep the real product from the input image as the hero. Change the environment and styling only enough to create a premium ad creative. Maintain realism, legibility, and low prop count.
        """
    ).strip()
    return " ".join(prompt.split())


def run_cmd(args: list[str], cwd: Path | None = None, timeout_sec: int = 300) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            env=os.environ.copy(),
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        return subprocess.CompletedProcess(args=args, returncode=124, stdout=stdout, stderr=stderr + "\nTIMEOUT")


def generate_image(prompt: str, input_image: Path, out_path: Path, resolution: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[generate] {out_path.name} <= {input_image.name}", flush=True)
    cmd = [
        "uv", "run", str(GENERATOR),
        "--prompt", prompt,
        "--filename", str(out_path),
        "--input-image", str(input_image),
        "--resolution", resolution,
    ]
    last_err = ""
    for attempt in range(1, 4):
        proc = run_cmd(cmd, cwd=out_path.parent)
        if proc.returncode == 0:
            print(f"[generated] {out_path}", flush=True)
            return
        last_err = (proc.stderr or proc.stdout).strip()
        print(f"[generate-retry] {out_path.name} attempt {attempt} failed: {last_err[:240]}", flush=True)
        time.sleep(2 * attempt)
    raise RuntimeError(f"Image generation failed for {out_path.name}: {last_err}")


def validate_image(image_path: Path, product: str, refs: list[Path], out_json: Path) -> dict[str, Any]:
    print(f"[validate] {image_path.name} ({product})", flush=True)
    cmd = [
        sys.executable, str(VALIDATOR), str(image_path),
        "--model", MODEL,
        "--product-type", product,
        "--strict-identity",
    ]
    for ref in refs:
        cmd += ["--reference-image", str(ref)]
    proc = run_cmd(cmd, cwd=ROOT)
    if proc.returncode == 124:
        payload = {
            "image_path": str(image_path),
            "product_type": product,
            "strict_identity": True,
            "reference_images": [str(r) for r in refs],
            "checks": {
                "file_valid": {"status": "FAIL", "details": "Validator timeout."},
                "reference_images": {"status": "PASS", "details": "References supplied."},
                "minimum_resolution": {"status": "FAIL", "details": "Unknown due to timeout."},
                "aspect_ratio": {"status": "WARN", "details": "Unknown due to timeout."},
                "file_size": {"status": "WARN", "details": "Unknown due to timeout."},
                "ai_humans": {"status": "FAIL", "details": "Unknown due to timeout."},
                "brand_fit": {"status": "WARN", "overall_score": 0, "details": "Unknown due to timeout."},
                "packaging_fidelity": {"status": "FAIL", "score": 0, "details": "Unknown due to timeout."},
                "root_authenticity": {"status": "FAIL", "score": 0, "details": "Unknown due to timeout."},
                "text_overlay": {"status": "WARN", "details": "Unknown due to timeout."},
            },
            "summary": {
                "fail_count": 5,
                "warn_count": 4,
                "pass_count": 1,
                "strict_identity": True,
                "identity_fail_checks": ["packaging_fidelity", "root_authenticity"],
                "overall_status": "FAIL",
            },
        }
        out_json.write_text(json.dumps(payload, indent=2))
        print(f"[validated-timeout] {out_json}", flush=True)
        return payload
    if proc.returncode not in (0, 1):
        raise RuntimeError(f"Validator crashed for {image_path.name}: {proc.stderr or proc.stdout}")
    out_json.write_text(proc.stdout)
    print(f"[validated] {out_json}", flush=True)
    return json.loads(proc.stdout)


def result_from_validation(product: str, phase: str, template_id: str, input_image: Path, output_image: Path, prompt: str, payload: dict[str, Any], validation_json: Path) -> TemplateResult:
    checks = payload["checks"]
    packaging = checks["packaging_fidelity"]
    root = checks["root_authenticity"]
    ai = checks["ai_humans"]
    brand = checks["brand_fit"]
    pass_identity = packaging["status"] != "FAIL" and root["status"] != "FAIL"
    no_humans_pass = ai["status"] == "PASS"
    visual_score = int(brand.get("overall_score", 0))
    objective = (0.45 * (1.0 if pass_identity else 0.0)) + (0.35 * (visual_score / 100.0)) + (0.20 * (1.0 if no_humans_pass else 0.0))
    notes: list[str] = []
    if packaging["status"] == "FAIL":
        notes.append("packaging_fidelity_fail")
    if root["status"] == "FAIL":
        notes.append("root_authenticity_fail")
    if not no_humans_pass:
        notes.append("no_humans_fail")
    if checks["text_overlay"]["status"] == "WARN":
        notes.append("text_overlay_warn")
    return TemplateResult(
        product=product,
        phase=phase,
        template_id=template_id,
        input_image=str(input_image),
        output_image=str(output_image),
        prompt=prompt,
        objective=round(objective, 4),
        overall_status=payload["summary"]["overall_status"],
        pass_identity=pass_identity,
        no_humans_pass=no_humans_pass,
        packaging_status=packaging["status"],
        root_status=root["status"],
        visual_score=visual_score,
        packaging_score=int(packaging.get("score", 0)),
        root_score=int(root.get("score", 0)),
        notes=notes,
        validation_json=str(validation_json),
    )


def choose_templates(manifest: dict[str, Any], pilot_per_product: int) -> dict[str, list[dict[str, str]]]:
    chosen: dict[str, list[dict[str, str]]] = {}
    for product in PRODUCTS:
        bases = BASE_PROMPTS[product][:]
        random.shuffle(bases)
        selected = []
        for idx, base in enumerate(bases[:pilot_per_product], start=1):
            template_id = f"{product}-pilot-{idx:02d}"
            selected.append({"template_id": template_id, "prompt": mutate_prompt(product, base, manifest)})
        chosen[product] = selected
    return chosen


def strengthen_failure_prompt(manifest: dict[str, Any], product: str, prior_prompt: str, notes: list[str]) -> str:
    failure_signals = [n.replace("_fail", "") for n in notes if n.endswith("_fail")]
    return mutate_prompt(product, prior_prompt, manifest, failure_signals=failure_signals)


def write_prompt_library(path: Path) -> None:
    lines = ["# Heil Ad Creative Prompt Library", "", "Generated for 2026-03-12 Round 3 optimization.", ""]
    for product in PRODUCTS:
        lines += [f"## {product.title()}", ""]
        for idx, prompt in enumerate(BASE_PROMPTS[product], start=1):
            lines += [f"### Base template {idx}", prompt, ""]
    path.write_text("\n".join(lines).strip() + "\n")


def markdown_results(results: list[TemplateResult], out_path: Path) -> None:
    grouped: dict[str, list[TemplateResult]] = {p: [] for p in PRODUCTS}
    for r in results:
        grouped[r.product].append(r)
    lines = ["# Prompt Optimizer Results", "", "Objective = pass_rate_identity * 0.45 + avg_visual_score * 0.35 + no_humans_pass_rate * 0.20", ""]
    for product in PRODUCTS:
        lines += [f"## {product.title()}", ""]
        for r in sorted(grouped[product], key=lambda x: x.objective, reverse=True):
            lines += [
                f"- **{r.template_id}** | objective `{r.objective:.4f}` | visual `{r.visual_score}` | packaging `{r.packaging_status}` | root `{r.root_status}` | humans `{'PASS' if r.no_humans_pass else 'FAIL'}`",
                f"  - Image: `{r.output_image}`",
                f"  - Validation: `{r.validation_json}`",
                f"  - Notes: {', '.join(r.notes) if r.notes else 'none'}",
                f"  - Prompt: {r.prompt}",
            ]
        lines.append("")
    out_path.write_text("\n".join(lines))


def compute_summary(results: list[TemplateResult]) -> dict[str, Any]:
    total = len(results)
    identity_pass = sum(1 for r in results if r.pass_identity)
    packaging_fail = sum(1 for r in results if r.packaging_status == "FAIL")
    root_fail = sum(1 for r in results if r.root_status == "FAIL")
    no_humans_fail = sum(1 for r in results if not r.no_humans_pass)
    kept = sum(1 for r in results if r.pass_identity and r.no_humans_pass and r.visual_score >= 50)
    discarded = total - kept
    per_product = {}
    for product in PRODUCTS:
        subset = [r for r in results if r.product == product]
        if not subset:
            continue
        per_product[product] = {
            "generated": len(subset),
            "identity_pass": sum(1 for r in subset if r.pass_identity),
            "identity_pass_rate": round(sum(1 for r in subset if r.pass_identity) / len(subset), 4),
            "avg_visual_score": round(statistics.mean(r.visual_score for r in subset), 1),
        }
    return {
        "total_generated": total,
        "identity_pass_count": identity_pass,
        "identity_pass_rate": round(identity_pass / total, 4) if total else 0,
        "packaging_fidelity_fail_count": packaging_fail,
        "root_authenticity_fail_count": root_fail,
        "no_humans_fail_count": no_humans_fail,
        "kept_count": kept,
        "discarded_count": discarded,
        "per_product": per_product,
    }


def rank_kept(results: list[TemplateResult]) -> list[TemplateResult]:
    return sorted(
        [r for r in results if r.pass_identity and r.no_humans_pass],
        key=lambda r: (r.objective, r.visual_score, r.packaging_score, r.root_score),
        reverse=True,
    )


def write_scorecard(results: list[TemplateResult], out_path: Path, baseline_summary: dict[str, Any] | None = None) -> None:
    summary = compute_summary(results)
    kept_ranked = rank_kept(results)
    lines = [
        "# Ad Creative Scorecard — 2026-03-12 Round 3 Optimization",
        "",
        "Run mode: strict identity prompt optimization + image-edit generation from real Heil reference photos.",
        "",
        "## Summary",
        "",
        f"- Total generated: **{summary['total_generated']}**",
        f"- Identity-pass count and rate: **{summary['identity_pass_count']} / {summary['total_generated']} ({summary['identity_pass_rate']:.1%})**",
        f"- Packaging-fidelity fail count: **{summary['packaging_fidelity_fail_count']}**",
        f"- Root-authenticity fail count: **{summary['root_authenticity_fail_count']}**",
        f"- No-humans fail count: **{summary['no_humans_fail_count']}**",
        f"- Kept count: **{summary['kept_count']}**",
        f"- Discarded count: **{summary['discarded_count']}**",
        "",
        "## Per-product pass rates",
        "",
    ]
    for product, stats in summary["per_product"].items():
        lines.append(f"- {product}: {stats['identity_pass']} / {stats['generated']} identity-pass ({stats['identity_pass_rate']:.1%}), avg visual {stats['avg_visual_score']}")
    if baseline_summary:
        lines += ["", "## Baseline comparison", ""]
        lines.append(
            f"- Prior round baseline identity-pass: {baseline_summary['identity_pass_count']} / {baseline_summary['total_generated']} ({baseline_summary['identity_pass_rate']:.1%})"
        )
        delta = summary['identity_pass_rate'] - baseline_summary['identity_pass_rate']
        lines.append(f"- Optimized run identity-pass delta: {delta:+.1%}")
    lines += ["", "## Top 10 kept variants", ""]
    for idx, r in enumerate(kept_ranked[:10], start=1):
        rationale_bits = [f"visual {r.visual_score}", f"packaging {r.packaging_status}/{r.packaging_score}", f"root {r.root_status}/{r.root_score}"]
        lines += [
            f"### {idx}. {Path(r.output_image).name}",
            f"- Product: {r.product}",
            f"- Objective: {r.objective:.4f}",
            f"- Rationale: {'; '.join(rationale_bits)}; {'no humans pass' if r.no_humans_pass else 'humans fail'}.",
            f"- Validation: `{r.validation_json}`",
            f"- Prompt angle: {r.prompt[:260]}...",
            "",
        ]
    lines += ["## Full inventory", ""]
    for r in sorted(results, key=lambda x: (x.product, x.phase, x.objective), reverse=True):
        lines += [
            f"- `{Path(r.output_image).name}` | {r.product} | {r.phase} | objective {r.objective:.4f} | overall {r.overall_status} | identity {'PASS' if r.pass_identity else 'FAIL'} | humans {'PASS' if r.no_humans_pass else 'FAIL'} | notes {', '.join(r.notes) if r.notes else 'none'}",
        ]
    out_path.write_text("\n".join(lines) + "\n")


def write_top10(results: list[TemplateResult], out_path: Path) -> None:
    ranked = rank_kept(results)[:10]
    lines = ["# Top 10 Strict-Identity Candidates", ""]
    for idx, r in enumerate(ranked, start=1):
        lines += [
            f"## {idx}. {Path(r.output_image).name}",
            f"- Product: {r.product}",
            f"- Objective: {r.objective:.4f}",
            f"- Visual score: {r.visual_score}",
            f"- Why it ranked: Packaging held, no-humans passed, and the scene remained commercially strong.",
            f"- Validation JSON: `{r.validation_json}`",
            f"- Image: `{r.output_image}`",
            "",
        ]
    out_path.write_text("\n".join(lines))


def write_interim(results: list[TemplateResult], preview_dir: Path, out_path: Path) -> None:
    ranked = rank_kept(results)[:4]
    preview_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Interim Top 4 Preview", ""]
    if not ranked:
        lines += ["No strict-identity passes yet. Preview withheld until at least one candidate clears identity + no-humans.", ""]
    for idx, r in enumerate(ranked, start=1):
        src = Path(r.output_image)
        dst = preview_dir / src.name
        if not dst.exists():
            shutil.copy2(src, dst)
        lines += [
            f"## {idx}. {src.name}",
            f"- Product: {r.product}",
            f"- Objective: {r.objective:.4f}",
            f"- Why it made preview: strict identity passed and visual score {r.visual_score} with no AI humans.",
            f"- Preview image: `{dst}`",
            "",
        ]
    out_path.write_text("\n".join(lines))


def validate_baseline(manifest: dict[str, Any], outdir: Path) -> dict[str, Any] | None:
    baseline_dir = WORKSPACE / "outputs" / "autoresearch" / "ad-creative" / "2026-03-12-r3"
    if not baseline_dir.exists():
        return None
    images = sorted(baseline_dir.glob("*.png"))
    if not images:
        return None
    results = []
    for img in images:
        product = img.name.split("-")[0]
        refs = product_refs(manifest, product)
        json_path = outdir / "baseline-validation" / f"{img.stem}.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = validate_image(img, product, refs, json_path)
        results.append(result_from_validation(product, "baseline", img.stem, primary_input(manifest, product), img, "baseline-comparison", payload, json_path))
    return compute_summary(results)


def main() -> int:
    args = parse_args()
    random.seed(args.seed)
    ensure_env()
    manifest = load_manifest(args.manifest)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "prompt-optimizer" / "pilot").mkdir(parents=True, exist_ok=True)
    (args.outdir / "prompt-optimizer" / "final").mkdir(parents=True, exist_ok=True)
    write_prompt_library(PROMPT_LIBRARY_PATH)

    baseline_summary = None if args.skip_baseline else validate_baseline(manifest, args.outdir)

    pilot_per_product = max(1, args.pilot_total // len(PRODUCTS))
    final_per_product = max(1, args.final_total // len(PRODUCTS))
    selected = choose_templates(manifest, pilot_per_product)
    all_results: list[TemplateResult] = []
    top_templates: dict[str, list[TemplateResult]] = {}

    # Pilot phase
    for product in PRODUCTS:
        input_image = primary_input(manifest, product)
        refs = product_refs(manifest, product)
        product_dir = args.outdir / "prompt-optimizer" / "pilot" / product
        product_dir.mkdir(parents=True, exist_ok=True)
        product_results: list[TemplateResult] = []
        for idx, template in enumerate(selected[product], start=1):
            img_path = product_dir / f"{product}-pilot-{idx:02d}.png"
            val_path = product_dir / f"{product}-pilot-{idx:02d}.validation.json"
            generate_image(template["prompt"], input_image, img_path, args.resolution)
            payload = validate_image(img_path, product, refs, val_path)
            result = result_from_validation(product, "pilot", template["template_id"], input_image, img_path, template["prompt"], payload, val_path)
            all_results.append(result)
            product_results.append(result)
            if len(all_results) >= 12 and not (args.outdir / "interim-top-4.md").exists():
                write_interim(all_results, args.outdir / "preview", args.outdir / "interim-top-4.md")
        product_results.sort(key=lambda r: r.objective, reverse=True)
        top_templates[product] = product_results[:2]

    markdown_results(all_results, args.outdir / "prompt-optimizer" / "results.md")

    # Final campaign phase
    for product in PRODUCTS:
        input_image = primary_input(manifest, product)
        refs = product_refs(manifest, product)
        product_dir = args.outdir / product
        product_dir.mkdir(parents=True, exist_ok=True)
        top = top_templates[product] or []
        if not top:
            continue
        for idx in range(1, final_per_product + 1):
            seed_template = top[(idx - 1) % len(top)]
            evolved_prompt = strengthen_failure_prompt(manifest, product, seed_template.prompt, seed_template.notes)
            img_path = product_dir / f"{product}-final-{idx:02d}.png"
            val_path = product_dir / f"{product}-final-{idx:02d}.validation.json"
            generate_image(evolved_prompt, input_image, img_path, args.resolution)
            payload = validate_image(img_path, product, refs, val_path)
            result = result_from_validation(product, "final", f"{product}-final-{idx:02d}", input_image, img_path, evolved_prompt, payload, val_path)
            all_results.append(result)

    if not (args.outdir / "interim-top-4.md").exists():
        write_interim(all_results, args.outdir / "preview", args.outdir / "interim-top-4.md")
    write_scorecard(all_results, args.outdir / "scorecard.md", baseline_summary=baseline_summary)
    write_top10(all_results, args.outdir / "top-10.md")
    (args.outdir / "run-summary.json").write_text(json.dumps({
        "summary": compute_summary(all_results),
        "baseline_summary": baseline_summary,
        "top_candidates": [asdict(r) for r in rank_kept(all_results)[:10]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
