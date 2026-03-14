#!/usr/bin/env python3
"""Render a Shopify PDP baseline or CSS variant on a temporary unpublished theme."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

DEFAULT_STORE = "heil-ginseng.myshopify.com"
DEFAULT_API_VERSION = "2024-01"
PRODUCTS_PATH = Path.home() / "repos/autoresearch/config/products.json"
TOKEN_REFRESH_SCRIPT = Path.home() / "repos/clawd/workstreams/ginseng-retail/refresh_shopify_token.py"
TOKEN_FILE = Path.home() / "repos/clawd/workstreams/ginseng-retail/shopify_token.txt"
DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
MOBILE_VIEWPORT = {"width": 375, "height": 812}
AUTORESEARCH_CSS_KEY = "assets/autoresearch-variant.css"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", required=True, help="Product key from products.json")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--css", help="CSS string to inject into the preview theme")
    group.add_argument("--css-file", type=Path, help="Path to a CSS file to inject")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    parser.add_argument("--store", default=DEFAULT_STORE)
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION)
    return parser.parse_args()


def load_products() -> dict[str, Any]:
    return json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))


def normalize_css(css: str) -> str:
    aliases = {
        "button.btn-add-to-cart": "button.btn-add-to-cart, button.btn-add-cart",
        ".btn-add-to-cart": ".btn-add-to-cart, .btn-add-cart",
    }
    normalized = css
    for src, dest in aliases.items():
        normalized = normalized.replace(src, dest)
    return normalized.strip()


def load_css(args: argparse.Namespace) -> str | None:
    if args.css:
        return normalize_css(args.css)
    if args.css_file:
        return normalize_css(args.css_file.read_text(encoding="utf-8"))
    return None


def refresh_shopify_token() -> str:
    subprocess.run([sys.executable, str(TOKEN_REFRESH_SCRIPT)], check=True)
    token = None
    for line in TOKEN_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("Access Token:"):
            token = line.split(":", 1)[1].strip()
            break
    if not token:
        raise RuntimeError("Unable to parse Shopify access token")
    return token


def shopify_request(method: str, store: str, api_version: str, path: str, token: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"https://{store}/admin/api/{api_version}/{path.lstrip('/')}"
    response = requests.request(
        method,
        url,
        headers={
            "X-Shopify-Access-Token": token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    if response.status_code >= 400:
        detail = response.text.strip() or response.reason
        raise RuntimeError(f"Shopify {method} failed ({response.status_code}) for {path}: {detail}")
    if not response.content:
        return {}
    return response.json()


def get_themes(store: str, api_version: str, token: str) -> list[dict[str, Any]]:
    payload = shopify_request("GET", store, api_version, "themes.json", token)
    themes = payload.get("themes")
    if not isinstance(themes, list):
        raise RuntimeError("Invalid themes response")
    return themes


def get_published_theme(themes: list[dict[str, Any]]) -> dict[str, Any]:
    for theme in themes:
        if theme.get("role") == "main":
            return theme
    raise RuntimeError("Published theme not found")


def ensure_unpublished_capacity(themes: list[dict[str, Any]]) -> None:
    unpublished = [theme for theme in themes if theme.get("role") == "unpublished"]
    if len(unpublished) >= 15:
        raise RuntimeError(f"Store already has {len(unpublished)} unpublished themes (>=15). Abort.")


def duplicate_theme_via_cli(source_theme_id: int, theme_name: str, store: str, token: str) -> dict[str, Any]:
    cmd = [
        "shopify", "theme", "duplicate",
        "--theme", str(source_theme_id),
        "--name", theme_name,
        "--store", store,
        "--password", token,
        "--json", "--force",
    ]
    result = subprocess.run(cmd, text=True, capture_output=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"shopify theme duplicate failed: {(result.stderr or result.stdout).strip()}")
    payload = json.loads(result.stdout)
    theme = payload.get("theme")
    if not isinstance(theme, dict) or not theme.get("id"):
        raise RuntimeError(f"Unexpected theme duplicate payload: {payload}")
    return theme


def wait_for_theme_ready(theme_id: int, store: str, api_version: str, token: str, timeout_s: int = 120) -> None:
    started = time.time()
    while time.time() - started < timeout_s:
        themes = get_themes(store, api_version, token)
        current = next((theme for theme in themes if int(theme.get("id", 0)) == theme_id), None)
        if current and not current.get("processing"):
            return
        time.sleep(2)
    raise RuntimeError(f"Preview theme {theme_id} never finished processing")


def get_asset(theme_id: int, key: str, store: str, api_version: str, token: str) -> str:
    payload = shopify_request("GET", store, api_version, f"themes/{theme_id}/assets.json?asset[key]={key}", token)
    asset = payload.get("asset") or {}
    value = asset.get("value")
    if not isinstance(value, str):
        raise RuntimeError(f"Unable to load asset {key} from theme {theme_id}")
    return value


def put_css_asset(theme_id: int, css: str, store: str, api_version: str, token: str) -> None:
    shopify_request(
        "PUT", store, api_version, f"themes/{theme_id}/assets.json", token,
        {"asset": {"key": AUTORESEARCH_CSS_KEY, "value": f"/* AUTORESEARCH VARIANT START */\n{css}\n/* AUTORESEARCH VARIANT END */\n"}},
    )
    layout = get_asset(theme_id, "layout/theme.liquid", store, api_version, token)
    marker = "{% comment %} AUTORESEARCH_VARIANT_INCLUDE {% endcomment %}"
    include = marker + "\n{{ 'autoresearch-variant.css' | asset_url | stylesheet_tag }}\n"
    updated = layout if marker in layout else layout.replace("</head>", include + "</head>", 1)
    shopify_request(
        "PUT", store, api_version, f"themes/{theme_id}/assets.json", token,
        {"asset": {"key": "layout/theme.liquid", "value": updated}},
    )


def build_preview_url(product_url: str, theme_id: int) -> str:
    sep = "&" if "?" in product_url else "?"
    return f"{product_url}{sep}preview_theme_id={theme_id}"


def wait_for_product_page(page: Any, expected_title: str) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except PlaywrightTimeoutError:
        pass
    selectors = [
        "button[name='add']",
        "form[action*='/cart/add']",
        "[data-jdgm-widget]",
        ".jdgm-widget",
        "main",
    ]
    for selector in selectors:
        try:
            page.wait_for_selector(selector, timeout=8000)
            break
        except PlaywrightTimeoutError:
            continue
    page.wait_for_timeout(2500)
    content = page.content().lower()
    title = (page.title() or "").lower()
    if "password" in page.url.lower() or "login" in page.url.lower():
        raise RuntimeError(f"Preview redirected to auth page: {page.url}")
    expected_tokens = [token for token in expected_title.lower().split("-") if token]
    if not any(token in content or token in title for token in expected_tokens[:3]):
        raise RuntimeError("Preview page loaded but expected product title was not found")


EXTRACT_JS = r"""
() => {
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const isVisible = (el) => {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    if (!style) return false;
    if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity || '1') === 0) return false;
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };
  const sectionType = (el, text) => {
    const attrs = [el.id || '', el.className || '', el.getAttribute('data-section-type') || '', el.getAttribute('aria-label') || '', text].join(' ').toLowerCase();
    if (el.tagName.toLowerCase() === 'header' || /hero|banner/.test(attrs)) return 'hero';
    if (/price|sale|\$|usd|add to cart|buy now/.test(attrs)) return 'price';
    if (/review|rating|stars?/.test(attrs)) return 'reviews';
    if (/faq|question|accordion/.test(attrs)) return 'faq';
    if (/trust|badge|guarantee|certif|shipping|return/.test(attrs)) return 'trust-badges';
    if (/ingredient|supplement facts|nutrition/.test(attrs)) return 'ingredients';
    if (/subscription|subscribe|delivery/.test(attrs)) return 'subscription';
    if (/gallery|image|slider|carousel/.test(attrs)) return 'media-gallery';
    if (/testimonial|social proof/.test(attrs)) return 'social-proof';
    if (/description|details|product info|overview/.test(attrs)) return 'product-info';
    return el.tagName.toLowerCase();
  };
  const collectComponents = (root) => {
    const tags = [
      ['button', 'button'], ['input[type="checkbox"]', 'checkmark/checkbox'], ['details, [aria-expanded]', 'accordion/toggle'],
      ['select', 'select'], ['input[type="radio"]', 'radio'], ['img', 'image'], ['video', 'video'], ['form', 'form'],
      ['[class*="star" i], [aria-label*="star" i]', 'star-rating'], ['[class*="review" i]', 'review-module'],
      ['[class*="badge" i]', 'badge'], ['[class*="subscription" i], [class*="subscribe" i]', 'subscribe-option'],
      ['[class*="qty" i], [name*="quantity" i]', 'quantity-selector'], ['[class*="tabs" i], [role="tablist"]', 'tabs'],
      ['[class*="carousel" i], [class*="slider" i]', 'carousel'], ['[class*="faq" i]', 'faq-module'],
    ];
    const found = [];
    for (const [selector, label] of tags) {
      if (root.querySelector(selector)) found.push(label);
    }
    return found;
  };
  const buttons = Array.from(document.querySelectorAll('button, a, input[type="submit"], input[type="button"]'))
    .filter(isVisible)
    .map((el) => ({ tag: el.tagName.toLowerCase(), text: norm(el.innerText || el.value || el.getAttribute('aria-label') || ''), classes: norm(typeof el.className === 'string' ? el.className : '') }))
    .filter((item) => item.text)
    .slice(0, 100);
  const images = Array.from(document.querySelectorAll('img')).filter(isVisible)
    .map((img) => ({ src: img.currentSrc || img.src || '', alt: norm(img.alt || '') }))
    .slice(0, 100);
  const sections = [];
  const candidates = Array.from(document.querySelectorAll('main section, main article, main div, main aside, section, article, body > div, body > main, body > section'));
  const seen = new Set();
  for (const el of candidates) {
    if (!isVisible(el)) continue;
    const text = norm(el.innerText || '');
    if (!text && !el.querySelector('img')) continue;
    const rect = el.getBoundingClientRect();
    if (rect.height < 40) continue;
    const key = `${Math.round(rect.top)}:${Math.round(rect.left)}:${Math.round(rect.width)}:${Math.round(rect.height)}:${text.slice(0,80)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const sectionImages = Array.from(el.querySelectorAll('img')).filter(isVisible);
    sections.push({
      tag: el.tagName.toLowerCase(), id: el.id || null, classes: norm(typeof el.className === 'string' ? el.className : ''),
      ariaLabel: el.getAttribute('aria-label'), sectionType: sectionType(el, text), top: Math.round(window.scrollY + rect.top),
      text, textPreview: text.slice(0, 500), wordCount: text ? text.split(/\s+/).length : 0, components: collectComponents(el),
      imageCount: sectionImages.length, imageAltTexts: sectionImages.map(img => norm(img.getAttribute('alt') || '')).filter(Boolean).slice(0, 20),
    });
  }
  sections.sort((a, b) => a.top - b.top);
  const titleEl = document.querySelector('h1, [class*="product-title" i], [class*="title" i]');
  const pageImages = Array.from(document.querySelectorAll('img')).filter(isVisible);
  const inventorySet = new Set();
  sections.forEach(section => (section.components || []).forEach(c => inventorySet.add(c)));
  return {
    url: location.href,
    title: document.title,
    productTitle: norm(titleEl?.textContent || ''),
    bodyTextSample: norm(document.body.innerText || '').slice(0, 4000),
    sectionCount: sections.length,
    sections,
    componentInventory: Array.from(inventorySet),
    buttons,
    ctaButtons: buttons.filter((b) => /(add to cart|buy now|purchase|subscribe|checkout|shop pay)/i.test(b.text)),
    images,
    imageAltTexts: images.map(img => img.alt).filter(Boolean).slice(0, 100),
    imageCount: pageImages.length,
    scrollHeight: Math.max(document.documentElement.scrollHeight || 0, document.body.scrollHeight || 0),
  };
}
"""


def capture_preview(preview_url: str, output_dir: Path, expected_title: str) -> dict[str, Any]:
    desktop_path = output_dir / "desktop.png"
    mobile_path = output_dir / "mobile.png"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            desktop_context = browser.new_context(viewport=DESKTOP_VIEWPORT)
            desktop_page = desktop_context.new_page()
            desktop_page.goto(preview_url, wait_until="domcontentloaded")
            wait_for_product_page(desktop_page, expected_title)
            desktop_page.screenshot(path=str(desktop_path), full_page=True)
            dom_extract = desktop_page.evaluate(EXTRACT_JS)
            desktop_context.close()

            mobile_context = browser.new_context(
                viewport=MOBILE_VIEWPORT, is_mobile=True, has_touch=True, device_scale_factor=1,
                user_agent=("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 "
                            "(KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"),
            )
            mobile_page = mobile_context.new_page()
            mobile_page.goto(preview_url, wait_until="domcontentloaded")
            wait_for_product_page(mobile_page, expected_title)
            mobile_page.screenshot(path=str(mobile_path), full_page=True)
            mobile_context.close()
        finally:
            browser.close()
    dom_extract["screenshotPaths"] = {"desktop": str(desktop_path), "mobile": str(mobile_path)}
    return dom_extract


def delete_theme(theme_id: int, store: str, api_version: str, token: str) -> None:
    shopify_request("DELETE", store, api_version, f"themes/{theme_id}.json", token)


def main() -> int:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    products = load_products()
    if args.product not in products:
        raise SystemExit(f"Unknown product {args.product}. Valid keys: {', '.join(sorted(products))}")
    product = products[args.product]
    css = load_css(args)
    token = refresh_shopify_token()
    themes = get_themes(args.store, args.api_version, token)
    main_theme = get_published_theme(themes)
    ensure_unpublished_capacity(themes)
    theme_name = f"AR-Test-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    theme_id: int | None = None
    try:
        theme = duplicate_theme_via_cli(int(main_theme["id"]), theme_name, args.store, token)
        theme_id = int(theme["id"])
        wait_for_theme_ready(theme_id, args.store, args.api_version, token)
        if css:
            put_css_asset(theme_id, css, args.store, args.api_version, token)
        preview_url = build_preview_url(product["url"], theme_id)
        dom_extract = capture_preview(preview_url, args.output, expected_title=product["handle"])
        dom_extract.update({
            "product": args.product,
            "handle": product["handle"],
            "preview_theme_id": theme_id,
            "preview_url": preview_url,
            "capturedAt": datetime.now(timezone.utc).isoformat(),
            "appliedCss": css or "",
        })
        dom_path = args.output / "dom-extract.json"
        dom_path.write_text(json.dumps(dom_extract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({
            "preview_theme_id": theme_id,
            "preview_url": preview_url,
            "desktop": str(args.output / 'desktop.png'),
            "mobile": str(args.output / 'mobile.png'),
            "dom": str(dom_path),
            "cssApplied": bool(css),
        }, indent=2))
        return 0
    finally:
        if theme_id is not None:
            try:
                delete_theme(theme_id, args.store, args.api_version, token)
            except Exception as exc:
                print(f"Warning: failed to delete preview theme {theme_id}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
