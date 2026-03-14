#!/usr/bin/env python3
"""Full visual autoresearch loop for Shopify PDP CSS variants."""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic

PRODUCTS_PATH = Path.home() / "repos/autoresearch/config/products.json"
VISUAL_SCORER = Path("/Users/coltonheil/.openclaw/workspace/outputs/visual-taste-panel/step-2/visual-scorer.py")
DEFAULT_OUTPUT_ROOT = Path.home() / "repos/autoresearch/outputs/visual-runs"
MODEL = "claude-opus-4-6"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", required=True, choices=["capsules", "tea", "powder", "root"])
    parser.add_argument("--cycles", type=int, default=10)
    parser.add_argument("--focus", choices=["trust", "hierarchy", "density", "cta", "reviews", "spacing", "typography"])
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_cmd(cmd: list[str], *, capture: bool = True, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if check and result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{stderr}")
    return result


def make_output_dir(path: Path | None) -> Path:
    if path:
        path.mkdir(parents=True, exist_ok=True)
        return path
    out = DEFAULT_OUTPUT_ROOT / datetime.now().strftime("%Y-%m-%d-%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    return out


def slugify(parts: list[str]) -> str:
    clean = []
    for part in parts:
        for token in str(part).replace("_", "-").split():
            token = "".join(ch.lower() for ch in token if ch.isalnum() or ch == "-").strip("-")
            if token:
                clean.append(token)
    return "-".join(clean)


def parse_trailing_json(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    start = text.rfind("\n{")
    if start != -1:
        candidate = text[start + 1 :]
    else:
        brace = text.find("{")
        if brace == -1:
            raise ValueError(f"No JSON object found in stdout: {stdout}")
        candidate = text[brace:]
    return json.loads(candidate)


def render_variant(product: str, css_path: Path | None, output_dir: Path) -> dict[str, Any]:
    cmd = [sys.executable, str(Path(__file__).with_name("render_variant.py")), "--product", product, "--output", str(output_dir)]
    if css_path is not None:
        cmd += ["--css-file", str(css_path)]
    result = run_cmd(cmd)
    return parse_trailing_json(result.stdout)


def run_fidelity(product: str, desktop: Path, mobile: Path, dom: Path, baseline_dom: Path) -> tuple[bool, dict[str, Any]]:
    cmd = [
        sys.executable,
        str(Path(__file__).with_name("fidelity_gate.py")),
        "--desktop", str(desktop),
        "--mobile", str(mobile),
        "--dom", str(dom),
        "--product", product,
        "--baseline-dom", str(baseline_dom),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    payload = json.loads(result.stdout.strip() or "{}")
    return result.returncode == 0, payload


def run_visual_score(dom_path: Path, mobile_path: Path, desktop_path: Path, baseline_metrics_path: Path, fidelity_report_path: Path) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(VISUAL_SCORER),
        "--dom", str(dom_path),
        "--mobile", str(mobile_path),
        "--desktop", str(desktop_path),
        "--baseline-metrics", str(baseline_metrics_path),
        "--fidelity-report", str(fidelity_report_path),
    ]
    result = run_cmd(cmd)
    return json.loads(result.stdout)


def b64_image(path: Path) -> dict[str, Any]:
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": data,
        },
    }


def heuristic_compare_from_scores(baseline_score: float, variant_score: float) -> dict[str, Any]:
    winner = 'variant' if variant_score >= baseline_score else 'baseline'
    return {
        'dimensions': {},
        'overallBaseline': round(baseline_score, 1),
        'overallVariant': round(variant_score, 1),
        'winner': winner,
        'reasoning': 'Heuristic comparison fell back to composite visual score because no model comparison path succeeded.',
    }


def request_compare_via_openclaw(product: str, baseline_mobile: Path, variant_mobile: Path) -> dict[str, Any]:
    prompt = f"""Use the read tool on these two PNG screenshots before answering:
- baseline: {baseline_mobile}
- variant: {variant_mobile}

You are a mobile CRO expert evaluating two versions of a supplement product page.

Image 1: BASELINE (current best page)
Image 2: VARIANT (proposed CSS changes)

Compare them for the Heil Ginseng {product} product page.

Score each version 1-10 on these dimensions:
1. Visual hierarchy — is the most important info (price, CTA, key benefit) the most visually prominent?
2. Trust signals — are reviews, guarantees, certifications visible and compelling?
3. CTA prominence — does the add-to-cart button demand attention? Size, color contrast, positioning?
4. Information density — is the page scannable without feeling sparse? Right amount of content above the fold?
5. Mobile scannability — can a first-time visitor understand the product value in 3 seconds of scrolling?
6. Professional polish — does the design feel premium/trustworthy or amateur/template-like?

Rules:
- You MUST pick a winner. Ties are not allowed.
- If the differences are subtle, still pick whichever is marginally better and explain why.
- Score as a real mobile shopper who is considering buying ginseng capsules for the first time.

Return ONLY valid JSON (no markdown fences):
{{
  "dimensions": {{
    "visualHierarchy": {{"baseline": N, "variant": N}},
    "trustSignals": {{"baseline": N, "variant": N}},
    "ctaProminence": {{"baseline": N, "variant": N}},
    "informationDensity": {{"baseline": N, "variant": N}},
    "mobileScannability": {{"baseline": N, "variant": N}},
    "professionalPolish": {{"baseline": N, "variant": N}}
  }},
  "overallBaseline": N,
  "overallVariant": N,
  "winner": "baseline" or "variant",
  "reasoning": "specific evidence for why the winner converts better"
}}
"""
    cmd = [
        "openclaw", "agent",
        "--agent", os.environ.get("OPENCLAW_AGENT_ID", "main"),
        "--message", prompt,
        "--json",
        "--timeout", os.environ.get("OPENCLAW_AGENT_TIMEOUT", "240"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "openclaw agent failed")
    payload = json.loads(result.stdout)
    text = "\n".join(item.get("text", "") for item in payload.get("result", {}).get("payloads", []) if item.get("text")).strip()
    if not text:
        raise RuntimeError("openclaw agent returned empty comparison")
    return json.loads(text)


def llm_compare(product: str, baseline_mobile: Path, variant_mobile: Path, baseline_score: float, variant_score: float) -> dict[str, Any]:
    prompt = (
        f"You are a mobile CRO expert evaluating two versions of a supplement product page for Heil Ginseng {product}. "
        "Image 1 is BASELINE (current best page). Image 2 is VARIANT (proposed CSS changes). "
        "Score each version 1-10 on: visual hierarchy, trust signals, CTA prominence, information density, mobile scannability, and professional polish. "
        "You MUST pick a winner. Ties are not allowed. If the differences are subtle, still choose whichever is marginally better and explain why with specific visual evidence. "
        "Return ONLY valid JSON with keys: dimensions, overallBaseline, overallVariant, winner, reasoning. "
        "Winner must be baseline or variant."
    )
    errors: list[str] = []
    try:
        return request_compare_via_openclaw(product, baseline_mobile, variant_mobile)
    except Exception as exc:
        errors.append(f"openclaw={exc}")
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    b64_image(baseline_mobile),
                    b64_image(variant_mobile),
                ],
            }],
        )
        text = "\n".join(block.text for block in response.content if getattr(block, "type", None) == "text").strip()
        return json.loads(text)
    except Exception as exc:
        errors.append(f"anthropic={exc}")
    payload = heuristic_compare_from_scores(baseline_score, variant_score)
    payload["errors"] = errors
    return payload


def build_capture_index(product: str, slug: str, dom_path: Path, desktop_path: Path, mobile_path: Path) -> dict[str, Any]:
    dom = load_json(dom_path)
    return {
        "results": [
            {
                "success": True,
                "slug": slug,
                "brand": "heil",
                "kind": product,
                "url": dom.get("url") or dom.get("preview_url"),
                "pageTitle": dom.get("title") or dom.get("productTitle"),
                "domExtractPath": str(dom_path),
                "screenshots": {
                    "desktop": str(desktop_path),
                    "mobile": str(mobile_path),
                },
                "capturedAt": dom.get("capturedAt"),
                "metaDescription": dom.get("meta", {}).get("description") if isinstance(dom.get("meta"), dict) else None,
            }
        ]
    }


def extract_baseline_metrics(product: str, product_conf: dict[str, Any], output_dir: Path, screenshots_dir: Path) -> tuple[dict[str, Any], Path, Path, Path, Path]:
    baseline_dir = output_dir / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    render_result = render_variant(product, None, baseline_dir)
    baseline_desktop = Path(render_result["desktop"])
    baseline_mobile = Path(render_result["mobile"])
    baseline_dom = Path(render_result["dom"])

    baseline_desktop_copy = screenshots_dir / "baseline-desktop.png"
    baseline_mobile_copy = screenshots_dir / "baseline-mobile.png"
    baseline_desktop_copy.write_bytes(baseline_desktop.read_bytes())
    baseline_mobile_copy.write_bytes(baseline_mobile.read_bytes())

    fidelity_ok, fidelity_payload = run_fidelity(product, baseline_desktop, baseline_mobile, baseline_dom, Path(product_conf["baseline_dom"]))
    if not fidelity_ok:
        raise RuntimeError(f"Baseline fidelity failed: {json.dumps(fidelity_payload)}")
    fidelity_report_path = baseline_dir / "baseline-fidelity.json"
    write_json(fidelity_report_path, fidelity_payload)

    baseline_score = run_visual_score(
        baseline_dom,
        baseline_mobile,
        baseline_desktop,
        Path(product_conf["baseline_dom"]),
        fidelity_report_path,
    )
    baseline_metrics_path = baseline_dir / "baseline-metrics.json"
    write_json(baseline_metrics_path, baseline_score.get("auditMetrics", {}))
    return baseline_score, baseline_metrics_path, baseline_mobile_copy, baseline_desktop_copy, baseline_dom


def main() -> int:
    args = parse_args()
    products = load_json(PRODUCTS_PATH)
    product_conf = products[args.product]
    output_dir = make_output_dir(args.output_dir)
    screenshots_dir = output_dir / "screenshots"
    cycle_dir = output_dir / "cycles"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    cycle_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = output_dir / "ledger.jsonl"
    results_path = output_dir / "cycle-results.json"
    summary_path = output_dir / "summary.json"
    trajectory_path = output_dir / "improvement-trajectory.md"
    best_css_path = output_dir / "best-variant.css"

    baseline_score, baseline_metrics_path, baseline_mobile, baseline_desktop, baseline_dom = extract_baseline_metrics(
        args.product, product_conf, output_dir, screenshots_dir
    )
    baseline_composite = float(baseline_score["compositeScore"])
    best_score = (0.3 * baseline_composite) + (0.7 * baseline_composite)
    best_dom_score = baseline_composite
    best_variant_id = "baseline"
    best_variant_css = ""
    best_mobile_path = baseline_mobile
    cycles: list[dict[str, Any]] = []
    passes = 0
    kept = 0
    killed = 0
    fidelity_failures = 0

    for cycle in range(1, args.cycles + 1):
        cycle_slug = slugify([f"cycle-{cycle:02d}", args.focus or "balanced"])
        variant_id = cycle_slug
        work_dir = cycle_dir / variant_id
        work_dir.mkdir(parents=True, exist_ok=True)
        css_path = work_dir / f"{variant_id}.css"
        fidelity_report_path = work_dir / "fidelity-report.json"
        capture_index_path = work_dir / "capture-index.json"
        entry: dict[str, Any] = {
            "cycle": cycle,
            "variantId": variant_id,
            "focus": args.focus,
            "status": "started",
        }
        try:
            gen_cmd = [
                sys.executable,
                str(Path(__file__).with_name("generate_css_variant.py")),
                "--product", args.product,
                "--baseline-dom", str(baseline_dom),
                "--baseline-screenshot", str(baseline_mobile),
                "--output", str(css_path),
            ]
            if args.focus:
                gen_cmd += ["--focus", args.focus]
            if ledger_path.exists() and ledger_path.stat().st_size > 0:
                gen_cmd += ["--previous-variants", str(ledger_path)]
            run_cmd(gen_cmd)
            css_text = css_path.read_text(encoding="utf-8")
            entry["css"] = css_text

            render_result = render_variant(args.product, css_path, work_dir)
            variant_desktop = Path(render_result["desktop"])
            variant_mobile = Path(render_result["mobile"])
            variant_dom = Path(render_result["dom"])
            shot_mobile_copy = screenshots_dir / f"{variant_id}-mobile.png"
            shot_desktop_copy = screenshots_dir / f"{variant_id}-desktop.png"
            shot_mobile_copy.write_bytes(variant_mobile.read_bytes())
            shot_desktop_copy.write_bytes(variant_desktop.read_bytes())

            fidelity_ok, fidelity_payload = run_fidelity(args.product, variant_desktop, variant_mobile, variant_dom, Path(product_conf["baseline_dom"]))
            write_json(fidelity_report_path, fidelity_payload)
            entry["fidelity"] = fidelity_payload
            if not fidelity_ok:
                entry.update({
                    "status": "killed",
                    "decision": "KILL",
                    "reasoning": f"Fidelity FAIL: {', '.join(fidelity_payload.get('failures', []))}",
                })
                fidelity_failures += 1
                killed += 1
            else:
                capture_index = build_capture_index(args.product, variant_id, variant_dom, variant_desktop, variant_mobile)
                write_json(capture_index_path, capture_index)
                score_payload = run_visual_score(variant_dom, variant_mobile, variant_desktop, baseline_metrics_path, fidelity_report_path)
                composite_score = float(score_payload["compositeScore"])
                llm_payload = llm_compare(args.product, best_mobile_path, variant_mobile, best_dom_score, composite_score)
                dom_score = composite_score
                llm_variant_score = float(llm_payload.get("overallVariant", composite_score))
                llm_baseline_score = float(llm_payload.get("overallBaseline", best_dom_score))
                llm_winner = llm_payload.get("winner", "baseline")
                hybrid_score = (0.3 * dom_score) + (0.7 * llm_variant_score)
                hybrid_baseline = (0.3 * best_dom_score) + (0.7 * llm_baseline_score)

                entry["visualScore"] = score_payload
                entry["llmComparison"] = llm_payload
                entry["variantScore"] = composite_score
                entry["baselineScore"] = best_dom_score
                entry["hybridScore"] = hybrid_score
                entry["hybridBaseline"] = hybrid_baseline

                if best_variant_id == "baseline" and llm_payload.get("overallBaseline") is not None:
                    llm_baseline_actual = float(llm_payload["overallBaseline"])
                    calibrated_baseline = (0.3 * baseline_composite) + (0.7 * llm_baseline_actual)
                    best_score = calibrated_baseline
                    entry["baselineRecalibrated"] = True
                    entry["originalBaselineHybrid"] = baseline_composite
                    entry["calibratedBaselineHybrid"] = calibrated_baseline

                passes += 1
                if hybrid_score > best_score and llm_winner == "variant":
                    decision = "KEEP"
                    reasoning = f"Variant won LLM comparison ({llm_variant_score} vs {llm_baseline_score}) and hybrid score {hybrid_score:.2f} > {best_score:.2f}"
                    best_score = hybrid_score
                    best_dom_score = dom_score
                    best_variant_id = variant_id
                    best_variant_css = css_text
                    best_mobile_path = shot_mobile_copy
                    best_css_path.write_text(css_text + "\n", encoding="utf-8")
                    kept += 1
                elif hybrid_score >= best_score and llm_winner == "variant":
                    decision = "KEEP"
                    reasoning = f"Variant tied on hybrid ({hybrid_score:.2f}) but won LLM comparison"
                    best_score = hybrid_score
                    best_dom_score = dom_score
                    best_variant_id = variant_id
                    best_variant_css = css_text
                    best_mobile_path = shot_mobile_copy
                    best_css_path.write_text(css_text + "\n", encoding="utf-8")
                    kept += 1
                else:
                    decision = "KILL"
                    reasoning = f"LLM picked {llm_winner}, hybrid {hybrid_score:.2f} vs best {best_score:.2f}"
                    killed += 1
                entry.update({
                    "status": "scored",
                    "decision": decision,
                    "reasoning": reasoning,
                    "compositeScore": composite_score,
                })
        except Exception as exc:
            entry.update({
                "status": "error",
                "decision": "KILL",
                "reasoning": f"Cycle error: {exc}",
            })
            killed += 1
        cycles.append(entry)
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        if cycle < args.cycles:
            time.sleep(5)

    improvement_lines = [
        f"# Visual Loop Trajectory — {args.product}",
        "",
        f"- Baseline composite score: {baseline_composite}",
        f"- Best hybrid score: {best_score}",
        f"- Best variant: {best_variant_id}",
        "",
        "## Cycle outcomes",
    ]
    for item in cycles:
        improvement_lines.append(
            f"- Cycle {item['cycle']}: {item['variantId']} — {item.get('decision', 'KILL')} — composite {item.get('compositeScore', 'n/a')} — hybrid {item.get('hybridScore', 'n/a')} vs ref {item.get('hybridBaseline', 'n/a')} — {item.get('reasoning', '')}"
        )
    trajectory_path.write_text("\n".join(improvement_lines) + "\n", encoding="utf-8")

    summary = {
        "status": "pass" if passes >= 1 and len(cycles) == args.cycles else "fail",
        "product": args.product,
        "cyclesCompleted": len(cycles),
        "cyclesPassed": passes,
        "cyclesKilled": killed,
        "baselineScore": baseline_composite,
        "bestScore": best_score,
        "bestHybridScore": best_score,
        "bestVariantId": best_variant_id,
        "bestVariantCss": best_variant_css,
        "fidelityFailures": fidelity_failures,
        "keptVariants": kept,
    }
    write_json(results_path, {"product": args.product, "baseline": baseline_score, "cycles": cycles})
    write_json(summary_path, summary)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
