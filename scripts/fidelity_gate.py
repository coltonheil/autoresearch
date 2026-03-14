#!/usr/bin/env python3
"""Validate rendered PDP screenshots and DOM metadata before scoring."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat

PRODUCTS_PATH = Path.home() / "repos/autoresearch/config/products.json"
FAILURES_ROOT = Path.home() / "repos/autoresearch/outputs/fidelity-failures"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--desktop", type=Path, required=True)
    parser.add_argument("--mobile", type=Path, required=True)
    parser.add_argument("--dom", type=Path, required=True)
    parser.add_argument("--product", required=True)
    parser.add_argument("--baseline-dom", type=Path, default=None)
    return parser.parse_args()


def load_products() -> dict[str, Any]:
    return json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def image_metrics(path: Path) -> tuple[int, int, float]:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        stat = ImageStat.Stat(rgb)
        std_channels = stat.stddev
        avg_std = float(sum(std_channels) / len(std_channels))
        return rgb.width, rgb.height, avg_std


def count_buttons(dom: dict[str, Any]) -> int:
    if isinstance(dom.get("ctaButtons"), list) and dom["ctaButtons"]:
        return len(dom["ctaButtons"])
    if isinstance(dom.get("buttons"), list):
        return sum(1 for button in dom["buttons"] if isinstance(button, dict) and button.get("text"))
    if isinstance(dom.get("buttons_from_html"), list):
        return sum(1 for button in dom["buttons_from_html"] if isinstance(button, dict) and button.get("text"))
    return 0


def count_images(dom: dict[str, Any]) -> int:
    if isinstance(dom.get("images"), list) and dom["images"]:
        return len(dom["images"])
    return int(dom.get("imageCount") or dom.get("html_image_count") or 0)


def product_title_found(dom: dict[str, Any]) -> str:
    for key in ["productTitle", "html_product_title", "title"]:
        value = dom.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def has_login_indicators(dom: dict[str, Any]) -> bool:
    blob = " ".join(str(dom.get(key, "")) for key in ["title", "productTitle", "html_product_title", "bodyTextSample"]).lower()
    patterns = ["enter store using password", "store password", "opening soon", "login", "log in"]
    return any(pattern in blob for pattern in patterns)


FAILURE_KEYS = {
    "desktop_dimensions": "invalid_dimensions",
    "mobile_dimensions": "invalid_dimensions",
    "not_blank_desktop": "blank_screenshot",
    "not_blank_mobile": "blank_screenshot",
    "section_count": "low_section_count",
    "product_title": "missing_product_title",
    "cta_present": "missing_cta",
    "images_present": "missing_product_images",
    "scroll_height": "scroll_height_out_of_range",
    "login_indicators": "login_or_password_page",
}


def record(checks: dict[str, Any], failures: list[str], key: str, payload: dict[str, Any]) -> None:
    checks[key] = payload
    if not payload.get("pass"):
        failure_key = FAILURE_KEYS.get(key, key)
        if failure_key not in failures:
            failures.append(failure_key)


def fail_artifacts(desktop: Path, mobile: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = FAILURES_ROOT / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    for path in [desktop, mobile]:
        if path.exists():
            shutil.copy2(path, out_dir / path.name)
    return out_dir


def main() -> int:
    args = parse_args()
    products = load_products()
    if args.product not in products:
        print(json.dumps({"result": "FAIL", "checks": {}, "failures": ["unknown_product"]}, indent=2))
        return 1

    baseline_dom_path = args.baseline_dom or Path(products[args.product]["baseline_dom"])
    checks: dict[str, Any] = {}
    failures: list[str] = []

    try:
        dom = load_json(args.dom)
        baseline_dom = load_json(baseline_dom_path)
    except Exception as exc:
        print(json.dumps({"result": "FAIL", "checks": {}, "failures": [f"load_error: {exc}"]}, indent=2))
        return 1

    if args.desktop.exists():
        desktop_width, desktop_height, desktop_std = image_metrics(args.desktop)
    else:
        desktop_width, desktop_height, desktop_std = 0, 0, 0.0
    if args.mobile.exists():
        mobile_width, mobile_height, mobile_std = image_metrics(args.mobile)
    else:
        mobile_width, mobile_height, mobile_std = 0, 0, 0.0

    record(checks, failures, "desktop_dimensions", {
        "pass": args.desktop.exists() and desktop_width >= 1400 and desktop_height >= 500,
        "width": desktop_width,
        "height": desktop_height,
    })
    record(checks, failures, "mobile_dimensions", {
        "pass": args.mobile.exists() and mobile_width >= 370 and mobile_height >= 500,
        "width": mobile_width,
        "height": mobile_height,
    })
    record(checks, failures, "not_blank_desktop", {
        "pass": desktop_std > 10,
        "std_dev": round(desktop_std, 2),
    })
    record(checks, failures, "not_blank_mobile", {
        "pass": mobile_std > 10,
        "std_dev": round(mobile_std, 2),
    })

    baseline_sections = int(baseline_dom.get("sectionCount") or len(baseline_dom.get("sections", [])) or 0)
    current_sections = int(dom.get("sectionCount") or len(dom.get("sections", [])) or 0)
    threshold = max(1, int(baseline_sections * 0.8))
    record(checks, failures, "section_count", {
        "pass": current_sections >= threshold,
        "count": current_sections,
        "baseline": baseline_sections,
        "threshold": threshold,
    })

    found_title = product_title_found(dom)
    expected_tokens = [token for token in args.product.lower().split("-") if token]
    if not expected_tokens:
        expected_tokens = [args.product.lower()]
    title_blob = " ".join(
        str(dom.get(key, "")) for key in ["productTitle", "html_product_title", "title", "bodyTextSample"]
    ).lower()
    title_pass = bool(found_title) and any(token in title_blob for token in expected_tokens)
    record(checks, failures, "product_title", {
        "pass": title_pass,
        "found": found_title,
    })

    cta_count = count_buttons(dom)
    record(checks, failures, "cta_present", {
        "pass": cta_count >= 1,
        "count": cta_count,
    })

    image_count = count_images(dom)
    record(checks, failures, "images_present", {
        "pass": image_count >= 1,
        "count": image_count,
    })

    baseline_scroll = float(baseline_dom.get("scrollHeight") or baseline_dom.get("screenshotHeight") or 0)
    current_scroll = float(dom.get("scrollHeight") or desktop_height or 0)
    if baseline_scroll <= 0:
        baseline_scroll = float(desktop_height or 1)
    ratio = current_scroll / baseline_scroll if baseline_scroll else 999.0
    record(checks, failures, "scroll_height", {
        "pass": ratio <= 2.0,
        "ratio": round(ratio, 3),
        "current": current_scroll,
        "baseline": baseline_scroll,
    })
    record(checks, failures, "login_indicators", {
        "pass": not has_login_indicators(dom),
        "found": has_login_indicators(dom),
    })

    result = "PASS" if not failures else "FAIL"
    output: dict[str, Any] = {
        "result": result,
        "checks": checks,
        "failures": failures,
    }

    if result == "FAIL":
        failure_dir = fail_artifacts(args.desktop, args.mobile)
        output["failure_artifacts_dir"] = str(failure_dir)

    print(json.dumps(output, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
