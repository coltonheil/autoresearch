#!/usr/bin/env python3
"""Run a browser-based dogfood checklist against a live PDP."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

DEFAULT_URL = "https://heilginseng.com/products/american-ginseng-capsules-500mg"
DEFAULT_DOMAIN = "pdp-copy"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Tier 1 PDP dogfood QA checklist and save artifacts.",
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="Live PDP URL to verify")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to write dogfood artifacts (default: ~/.openclaw/workspace/outputs/autoresearch/pdp-copy/YYYY-MM-DD/dogfood)",
    )
    parser.add_argument("--timeout", type=int, default=30000, help="Page timeout in milliseconds (default: 30000)")
    return parser.parse_args()


def default_output_dir() -> Path:
    return Path.home() / ".openclaw/workspace/outputs/autoresearch" / DEFAULT_DOMAIN / date.today().isoformat() / "dogfood"


def result(name: str, passed: bool, details: str, critical: bool = True) -> dict[str, Any]:
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "critical": critical,
        "details": details,
    }


def flatten_json_ld(payload: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        items.append(payload)
        graph = payload.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                items.extend(flatten_json_ld(item))
    elif isinstance(payload, list):
        for item in payload:
            items.extend(flatten_json_ld(item))
    return items


def print_table(checks: list[dict[str, Any]]) -> None:
    name_width = max(len(check["name"]) for check in checks)
    status_width = 4
    print(f"{'STATUS'.ljust(status_width)} | {'CHECK'.ljust(name_width)} | DETAILS")
    print(f"{'-' * status_width}-+-{'-' * name_width}-+-{'-' * 40}")
    for check in checks:
        print(f"{check['status'].ljust(status_width)} | {check['name'].ljust(name_width)} | {check['details']}")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    desktop_path = output_dir / "live-desktop.png"
    mobile_path = output_dir / "live-mobile.png"
    checklist_path = output_dir / "checklist.json"

    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(f"Error: Playwright is not available: {exc}", file=sys.stderr)
        return 1

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            desktop = browser.new_page(viewport={"width": 1440, "height": 1800})
            desktop.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout)
            desktop.wait_for_timeout(4000)
            desktop.screenshot(path=str(desktop_path), full_page=True)

            body_text = desktop.locator("body").inner_text(timeout=args.timeout)
            title_text = desktop.title()
            meta_description = desktop.locator("meta[name='description']").first.get_attribute("content") or ""

            top_stars_text = desktop.locator(".jdgm-preview-badge, .jdgm-widget.jdgm-preview-badge, [data-average-rating]").first.inner_text(timeout=5000)
            top_stars_ok = bool(top_stars_text and any(char.isdigit() for char in top_stars_text) and ("star" in top_stars_text.lower() or "review" in top_stars_text.lower()))

            bottom_widget_text = desktop.locator(".jdgm-review-widget, .jdgm-rev, #judgeme_product_reviews, .jdgm-all-reviews-widget").first.inner_text(timeout=5000)
            bottom_widget_ok = len(bottom_widget_text.strip()) > 20

            accordion_selectors = [
                "details",
                "summary",
                "button[aria-expanded]",
                ".accordion__title",
                ".collapsible-trigger",
                ".accordion",
            ]
            accordion_selector = ", ".join(accordion_selectors)
            accordion_count = desktop.locator(accordion_selector).count()
            accordion_ok = accordion_count > 0
            accordion_details = f"Found {accordion_count} accordion/collapsible elements."
            if accordion_ok:
                try:
                    expand_target = desktop.locator("details, button[aria-expanded='false'], .accordion__title, .collapsible-trigger, summary").first
                    before_state = expand_target.get_attribute("aria-expanded") or ""
                    expand_target.click(timeout=5000)
                    desktop.wait_for_timeout(500)
                    after_state = expand_target.get_attribute("aria-expanded") or ""
                    accordion_details = f"Found {accordion_count} accordion/collapsible elements and clicked one ({before_state!r} -> {after_state!r})."
                except Exception:
                    accordion_details = f"Found {accordion_count} accordion/collapsible elements; click interaction was attempted but not confirmed."

            badge_terms = ["GBW Certified", "Wisconsin Grown", "Lab Tested", "Family Farm"]
            found_badges = [term for term in badge_terms if term.lower() in body_text.lower()]
            trust_badges_ok = len(found_badges) >= 3

            add_to_cart = desktop.get_by_role("button", name="Add to Cart")
            if add_to_cart.count() == 0:
                add_to_cart = desktop.get_by_role("button", name="Add to cart")
            add_to_cart_ok = add_to_cart.count() > 0 and add_to_cart.first.is_visible()

            subscribe_terms = ["subscribe & save", "subscribe and save", "selling plan", "subscription"]
            subscribe_found = next((term for term in subscribe_terms if term in body_text.lower()), None)
            subscribe_ok = subscribe_found is not None

            fda_phrase = "These statements have not been evaluated"
            fda_ok = fda_phrase.lower() in body_text.lower()

            scripts = desktop.locator("script[type='application/ld+json']")
            product_schema = None
            parsed_payloads = 0
            for idx in range(scripts.count()):
                raw = scripts.nth(idx).inner_text().strip()
                if not raw:
                    continue
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                parsed_payloads += 1
                for item in flatten_json_ld(payload):
                    schema_type = item.get("@type")
                    if schema_type == "Product" or (isinstance(schema_type, list) and "Product" in schema_type):
                        product_schema = item
                        break
                if product_schema:
                    break

            offers = product_schema.get("offers") if isinstance(product_schema, dict) else None
            if isinstance(offers, list):
                offer = offers[0] if offers else {}
            elif isinstance(offers, dict):
                offer = offers
            else:
                offer = {}
            structured_ok = bool(
                isinstance(product_schema, dict)
                and product_schema.get("name")
                and (offer.get("price") or product_schema.get("price"))
                and (offer.get("availability") or product_schema.get("availability"))
            )

            mobile = browser.new_page(viewport={"width": 375, "height": 812}, user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 "
                "Mobile/15E148 Safari/604.1"
            ))
            mobile.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout)
            mobile.wait_for_timeout(4000)
            mobile.screenshot(path=str(mobile_path), full_page=True)
            mobile_metrics = mobile.evaluate(
                """
                () => ({
                  innerWidth: window.innerWidth,
                  scrollWidth: document.documentElement.scrollWidth,
                  titleVisible: !!document.querySelector('h1, .product__title, .product-title'),
                  addToCartVisible: Array.from(document.querySelectorAll('button, input[type="submit"]')).some(el => /add to cart/i.test((el.innerText || el.value || '').trim()) && el.offsetParent !== null)
                })
                """
            )
            mobile_ok = (
                mobile_metrics.get("scrollWidth", 0) <= mobile_metrics.get("innerWidth", 0) + 4
                and bool(mobile_metrics.get("titleVisible"))
                and bool(mobile_metrics.get("addToCartVisible"))
            )

            checks = [
                result("Judge.me top stars", top_stars_ok, top_stars_text.strip() or "Top review badge not found."),
                result("Judge.me bottom review block", bottom_widget_ok, bottom_widget_text.strip()[:200] or "Bottom review block not found."),
                result("Accordions", accordion_ok, accordion_details),
                result("Trust badges", trust_badges_ok, f"Found badges: {', '.join(found_badges) if found_badges else 'none'}"),
                result("Mobile layout", mobile_ok, f"metrics={mobile_metrics}"),
                result(
                    "Structured data",
                    structured_ok,
                    f"Parsed {parsed_payloads} JSON-LD blocks; product schema found={bool(product_schema)}; name={bool(product_schema and product_schema.get('name'))}; price={bool(offer.get('price') or (product_schema or {}).get('price'))}; availability={bool(offer.get('availability') or (product_schema or {}).get('availability'))}",
                ),
                result("Add-to-cart button", add_to_cart_ok, "Visible add-to-cart button found." if add_to_cart_ok else "Add-to-cart button not visible."),
                result("Subscribe & Save", subscribe_ok, f"Matched term: {subscribe_found or 'none'}"),
                result("FDA disclaimer", fda_ok, "FDA disclaimer text present." if fda_ok else "FDA disclaimer text missing."),
                result("Meta title", bool(title_text.strip()), title_text.strip() or "Empty <title> tag."),
                result("Meta description", bool(meta_description.strip()), meta_description.strip() or "Empty meta description."),
            ]

            payload = {
                "url": args.url,
                "desktop_screenshot": str(desktop_path),
                "mobile_screenshot": str(mobile_path),
                "checks": checks,
                "all_passed": all(check["status"] == "PASS" for check in checks),
            }
            checklist_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            browser.close()

        print_table(checks)
        print(f"Checklist JSON: {checklist_path}")
        print(f"Desktop screenshot: {desktop_path}")
        print(f"Mobile screenshot: {mobile_path}")
        return 0 if payload["all_passed"] else 1
    except PlaywrightTimeoutError as exc:
        print(f"Error: Timed out while loading or inspecting the page: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
