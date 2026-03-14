#!/usr/bin/env python3
"""Generate a CSS-only PDP variant with Claude Opus."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import anthropic
import shutil

PRODUCTS_PATH = Path.home() / "repos/autoresearch/config/products.json"
CRO_BRIEF_PATH = Path("/Users/coltonheil/.openclaw/workspace/outputs/visual-taste-panel/final-optimization/cro-research-brief.md")
VALID_FOCUS = ["trust", "hierarchy", "density", "cta", "reviews", "spacing", "typography"]
MODEL = "claude-opus-4-6"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", required=True, choices=["capsules", "tea", "powder", "root"])
    parser.add_argument("--focus", choices=VALID_FOCUS)
    parser.add_argument("--baseline-dom", type=Path, required=True)
    parser.add_argument("--baseline-screenshot", type=Path, required=True)
    parser.add_argument("--previous-variants", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_products() -> dict[str, Any]:
    return load_json(PRODUCTS_PATH)


def summarize_dom(dom: dict[str, Any]) -> str:
    sections = dom.get("sections", []) or []
    lines = [
        f"Title: {dom.get('title') or dom.get('productTitle') or 'unknown'}",
        f"Section count: {dom.get('sectionCount') or len(sections)}",
        f"Component inventory: {', '.join(dom.get('componentInventory', [])[:20]) or 'none'}",
        f"Image count: {dom.get('imageCount') or 0}",
    ]
    for idx, section in enumerate(sections[:12], start=1):
        preview = re.sub(r"\s+", " ", str(section.get("textPreview") or section.get("text") or "")).strip()
        lines.append(
            f"{idx}. type={section.get('sectionType') or section.get('tag')}, top={section.get('top')}, "
            f"components={','.join(section.get('components', [])[:8]) or 'none'}, text={preview[:260]}"
        )
    return "\n".join(lines)


def summarize_previous_variants(path: Path | None) -> str:
    if not path or not path.exists():
        return "No previous variants provided."
    summaries: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            continue
        css = re.sub(r"\s+", " ", str(item.get("css") or "")).strip()
        summaries.append(
            f"- {item.get('variantId') or item.get('variant_id') or 'unknown'} | focus={item.get('focus') or 'n/a'} | "
            f"decision={item.get('decision') or 'n/a'} | score={item.get('variantScore') or item.get('compositeScore') or 'n/a'} | css={css[:320]}"
        )
    return "\n".join(summaries[:20]) or "No previous variants provided."


def clean_css(text: str) -> str:
    css = text.strip()
    css = re.sub(r"^```(?:css)?\s*", "", css)
    css = re.sub(r"\s*```$", "", css)
    css = css.strip()
    return css


def validate_css(css: str) -> None:
    if not css:
        raise ValueError("Claude returned empty CSS")
    if "<style" in css.lower() or "</style" in css.lower():
        raise ValueError("CSS must not include <style> tags")
    if "```" in css:
        raise ValueError("CSS still contains markdown fences")
    if css.count("{") == 0 or css.count("}") == 0:
        raise ValueError("CSS does not contain any rule blocks")


def build_prompt(product_key: str, product: dict[str, Any], dom_summary: str, cro_brief: str, previous_summary: str, focus: str | None) -> str:
    focus_line = focus or "balanced mobile CRO improvement"
    return f"""
You are designing a CSS-only mobile-first conversion variant for a Shopify Dawn product page.

Product:
- key: {product_key}
- handle: {product.get('handle')}
- url: {product.get('url')}

Primary focus for this variant: {focus_line}

Current DOM/page structure summary:
{dom_summary}

Evidence-backed CRO brief:
{cro_brief}

Previous variants to avoid repeating:
{previous_summary}

Task:
Generate ONE novel CSS-only variant that improves likely mobile conversion for a first-time supplement buyer.
Target the focus area, but keep the page balanced and realistic.

Hard constraints:
- CSS only. No HTML, JS, Liquid, or explanations.
- Do not hide or remove required elements: title, price, CTA, product images, reviews, trust signals, purchase options.
- Do not use display:none, visibility:hidden, opacity:0, or pointer-events:none on those required elements.
- Assume Dawn theme defaults need to be overridden. Use !important where needed.
- Favor selectors that can plausibly match Dawn/Shopify/Judge.me product layouts.
- Improve hierarchy, spacing, scannability, proof visibility, or CTA prominence without breaking layout.
- Output ONLY valid CSS. No markdown fences. No prose.

Brand color constraints (MANDATORY — do not violate):
- The brand uses a warm color palette rooted in red and gold. These are intentional choices tied to Chinese cultural trust signals and ginseng heritage.
- ALLOWED colors: reds (#8B0000 to #CC0000 range), golds (#c4a24e, #d4b088), warm blacks (#111, #1a1a1a, #222), warm whites (#fff, #fffdf8, #faf6ee, #f7f4ec), warm grays (#555, #444, #888), earth tones (#3a3020, #5a4a38).
- FORBIDDEN: Do not introduce greens, blues, purples, teals, or any cool-toned colors as primary or accent colors. No forest green, no navy, no teal buttons or backgrounds.
- You may adjust shade/tint within the warm palette (e.g., darker red, lighter gold).
- Focus your changes on layout, spacing, typography, sizing, border treatments, shadows, and structural hierarchy — these are higher-leverage CRO changes than color.
""".strip()


def deterministic_fallback_css(focus: str | None) -> str:
    templates = {
        'trust': """
.product__info-container { background: #fffdf8 !important; border: 1px solid rgba(120,85,24,.14) !important; border-radius: 18px !important; padding: 18px !important; box-shadow: 0 10px 30px rgba(60,40,10,.08) !important; }
.jdgm-widget, .jdgm-preview-badge, .jdgm-star-rating, .shopify-app-block { background: #fff7e8 !important; border-radius: 12px !important; padding: 10px 12px !important; margin-bottom: 12px !important; }
.product__info-container .price, .price__container { font-size: 1.25rem !important; font-weight: 700 !important; }
.product-form__buttons button, button[name='add'], .shopify-payment-button__button { min-height: 54px !important; border-radius: 999px !important; font-weight: 700 !important; box-shadow: 0 8px 20px rgba(19,87,45,.18) !important; }
.product__info-container ul, .product__info-container .icon-with-text { gap: 10px !important; }
""",
        'cta': """
.product-form__buttons, .product__submit, button[name='add'] { position: sticky !important; bottom: 12px !important; z-index: 20 !important; }
.product-form__buttons button, button[name='add'], .shopify-payment-button__button { min-height: 58px !important; border-radius: 999px !important; font-size: 1.05rem !important; font-weight: 800 !important; }
.price__container { margin-bottom: 10px !important; }
""",
        'spacing': """
.product__info-container > * { margin-bottom: 12px !important; }
.product__info-container { padding: 20px !important; }
.product__media-wrapper, .product__info-wrapper { gap: 18px !important; }
.collapsible-content__header, details summary { padding-top: 14px !important; padding-bottom: 14px !important; }
""",
        'typography': """
.product__title, h1 { font-size: clamp(2rem, 5vw, 2.5rem) !important; line-height: 1.05 !important; letter-spacing: -0.02em !important; }
.product__text, .product__description, .rte, p, li { line-height: 1.55 !important; }
.product__info-container strong, .price, .jdgm-prev-badge__text { font-weight: 700 !important; }
""",
        'reviews': """
.jdgm-widget, .jdgm-rev-widg, .shopify-app-block { margin-top: 8px !important; margin-bottom: 16px !important; }
.jdgm-preview-badge, .jdgm-star-rating { display: inline-flex !important; align-items: center !important; gap: 8px !important; }
""",
        'hierarchy': """
.product__title, h1 { margin-bottom: 8px !important; }
.jdgm-widget, .jdgm-preview-badge { order: 2 !important; }
.price__container { order: 3 !important; margin-bottom: 10px !important; }
.product-form__input, .product-form__buttons { order: 4 !important; }
.product__info-container { display: flex !important; flex-direction: column !important; }
""",
        'density': """
.rte p, .product__description p { margin-bottom: 10px !important; }
.product__accordion, details, .collapsible-content { margin-bottom: 8px !important; }
.product__info-container { max-width: 42rem !important; }
""",
        None: """
.product__info-container { background: #fffdf8 !important; border-radius: 16px !important; padding: 18px !important; box-shadow: 0 8px 24px rgba(60,40,10,.07) !important; }
.product-form__buttons button, button[name='add'] { min-height: 54px !important; border-radius: 999px !important; font-weight: 700 !important; }
.jdgm-widget, .jdgm-preview-badge { margin-bottom: 12px !important; }
.price__container { font-weight: 700 !important; }
""",
    }
    return templates.get(focus, templates[None]).strip()


def openclaw_agent_available() -> bool:
    return shutil.which("openclaw") is not None


def build_openclaw_css_prompt(prompt: str, baseline_dom: Path, baseline_screenshot: Path) -> str:
    return f"""Return ONLY valid CSS. No markdown fences. No prose.

Use the read tool on these local files before answering:
- DOM JSON: {baseline_dom}
- Screenshot PNG: {baseline_screenshot}

Then complete this task exactly:
{prompt}
"""


def request_css_via_openclaw(prompt: str, baseline_dom: Path, baseline_screenshot: Path) -> str:
    cmd = [
        "openclaw", "agent",
        "--agent", os.environ.get("OPENCLAW_AGENT_ID", "main"),
        "--message", build_openclaw_css_prompt(prompt, baseline_dom, baseline_screenshot),
        "--json",
        "--timeout", os.environ.get("OPENCLAW_AGENT_TIMEOUT", "240"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "openclaw agent failed")
    payload = json.loads(result.stdout)
    payloads = payload.get("result", {}).get("payloads", [])
    text_blocks = [item.get("text", "") for item in payloads if item.get("text")]
    css = "\n".join(text_blocks).strip()
    if not css:
        raise RuntimeError("openclaw agent returned empty CSS")
    return css


def request_css(prompt: str, focus: str | None, baseline_dom: Path, baseline_screenshot: Path) -> str:
    errors: list[str] = []
    try:
        return request_css_via_openclaw(prompt, baseline_dom, baseline_screenshot)
    except Exception as exc:
        errors.append(f"openclaw={exc}")
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text_blocks = [block.text for block in response.content if getattr(block, "type", None) == "text"]
        css = "\n".join(text_blocks).strip()
        if css:
            return css
        raise RuntimeError("anthropic SDK returned empty CSS")
    except Exception as exc:
        errors.append(f"anthropic={exc}")
    raise RuntimeError("CSS generation failed: " + " | ".join(errors))


def main() -> int:
    args = parse_args()
    products = load_products()
    product = products[args.product]
    baseline_dom = load_json(args.baseline_dom)
    cro_brief = CRO_BRIEF_PATH.read_text(encoding="utf-8")
    dom_summary = summarize_dom(baseline_dom)
    previous_summary = summarize_previous_variants(args.previous_variants)
    prompt = build_prompt(args.product, product, dom_summary, cro_brief, previous_summary, args.focus)

    css = clean_css(request_css(prompt, args.focus, args.baseline_dom, args.baseline_screenshot))
    validate_css(css)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(css + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
