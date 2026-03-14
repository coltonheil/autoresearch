#!/usr/bin/env python3
"""Promotion gate for Tier 1 PDP copy variants."""

from __future__ import annotations

import argparse
import difflib
import os
import re
import subprocess
import sys
from datetime import date
from html import unescape
from pathlib import Path
from typing import Any

DEFAULT_STORE = "heil-ginseng.myshopify.com"
DEFAULT_API_VERSION = "2024-01"
DEFAULT_PRODUCT_URL = "https://heilginseng.com/products/american-ginseng-capsules-500mg"
DEFAULT_DOMAIN = "pdp-copy"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Tier 1 promotion gate for a PDP copy variant.",
    )
    parser.add_argument("--variant", type=Path, required=True, help="Path to variant markdown file")
    parser.add_argument("--product-id", required=True, help="Shopify product ID")
    parser.add_argument("--approved", action="store_true", help="Required to apply the variant live")
    parser.add_argument("--dry-run", action="store_true", help="Do not apply changes; snapshot, diff, and dogfood the current live page")
    parser.add_argument("--store", default=os.getenv("SHOPIFY_STORE", DEFAULT_STORE), help="Shopify store domain")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION, help="Shopify Admin API version")
    parser.add_argument("--product-url", default=DEFAULT_PRODUCT_URL, help="Live product URL for dogfood")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Output root (default: ~/.openclaw/workspace/outputs/autoresearch/pdp-copy/YYYY-MM-DD)",
    )
    return parser.parse_args()


def default_output_root() -> Path:
    return Path.home() / ".openclaw/workspace/outputs/autoresearch" / DEFAULT_DOMAIN / date.today().isoformat()


def run_script(script_name: str, script_args: list[str]) -> subprocess.CompletedProcess[str]:
    script_path = Path(__file__).with_name(script_name)
    return subprocess.run([sys.executable, str(script_path), *script_args], text=True, capture_output=True)


def require_token() -> str:
    token = os.getenv("SHOPIFY_TOKEN")
    if not token:
        raise RuntimeError("SHOPIFY_TOKEN is not set in the environment.")
    return token


def shopify_request(method: str, store: str, api_version: str, path: str, token: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    import requests

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
        timeout=30,
    )
    if response.status_code >= 400:
        detail = response.text.strip() or response.reason
        raise RuntimeError(f"Shopify {method} failed ({response.status_code}) for {path}: {detail}")
    return response.json() if response.content else {}


def read_variant(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Variant file not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_section(markdown_text: str, heading: str) -> str:
    pattern = rf"^###\s+{re.escape(heading)}\s*$\n(.*?)(?=^###\s+|^##\s+|\Z)"
    match = re.search(pattern, markdown_text, flags=re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def markdown_to_html(text: str) -> str:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text.strip()) if block.strip()]
    html_blocks: list[str] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if all(line.startswith(("- ", "* ")) for line in lines):
            items = "".join(f"<li>{escape_html(line[2:].strip())}</li>" for line in lines)
            html_blocks.append(f"<ul>{items}</ul>")
        else:
            paragraph = " ".join(escape_html(line) for line in lines)
            html_blocks.append(f"<p>{paragraph}</p>")
    return "\n".join(html_blocks)


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def strip_html(text: str) -> str:
    no_tags = re.sub(r"<[^>]+>", "\n", text or "")
    normalized = re.sub(r"\n{2,}", "\n", unescape(no_tags))
    return normalized.strip()


def print_step(title: str) -> None:
    print(f"\n== {title} ==")


def print_diff(current_body_html: str, proposed_body_html: str) -> None:
    current_lines = strip_html(current_body_html).splitlines() or ["(empty)"]
    proposed_lines = strip_html(proposed_body_html).splitlines() or ["(empty)"]
    diff = difflib.unified_diff(current_lines, proposed_lines, fromfile="current-live", tofile="proposed-variant", lineterm="")
    print("\n".join(diff) or "No body_html diff detected.")


def main() -> int:
    args = parse_args()
    output_root = args.output_root or default_output_root()
    snapshots_dir = output_root / "snapshots"
    dogfood_dir = output_root / "dogfood"

    try:
        variant_text = read_variant(args.variant)
        product_description = extract_section(variant_text, "Product Description")
        if not product_description:
            raise RuntimeError("Variant is missing a '### Product Description' section.")
        proposed_body_html = markdown_to_html(product_description)

        print_step("Step 1: Capture snapshot")
        snapshot_run = run_script(
            "shopify_snapshot.py",
            ["--product-id", str(args.product_id), "--output-dir", str(snapshots_dir), "--store", args.store, "--api-version", args.api_version],
        )
        if snapshot_run.returncode != 0:
            raise RuntimeError(snapshot_run.stderr.strip() or snapshot_run.stdout.strip() or "shopify_snapshot.py failed")
        if snapshot_run.stdout.strip():
            print(snapshot_run.stdout.strip())

        token = require_token()
        current_product = shopify_request("GET", args.store, args.api_version, f"products/{args.product_id}.json", token).get("product")
        if not isinstance(current_product, dict):
            raise RuntimeError("Unable to fetch current product state.")

        print_step("Step 2: Show diff")
        print_diff(current_product.get("body_html") or "", proposed_body_html)

        if args.dry_run:
            print_step("Step 3: Dry run gate")
            print("Dry run enabled. No Shopify write will happen.")
            dogfood_run = run_script("dogfood_pdp.py", ["--url", args.product_url, "--output-dir", str(dogfood_dir)])
            if dogfood_run.stdout.strip():
                print(dogfood_run.stdout.strip())
            if dogfood_run.stderr.strip():
                print(dogfood_run.stderr.strip(), file=sys.stderr)
            return dogfood_run.returncode

        if not args.approved:
            print_step("Step 3: Human approval gate")
            print("PROMOTION BLOCKED — requires human approval")
            print("Re-run with --approved after Colton approves the preview/diff.")
            return 0

        print_step("Step 4: Apply variant body_html")
        update_payload = {"product": {"id": args.product_id, "body_html": proposed_body_html}}
        update_result = shopify_request("PUT", args.store, args.api_version, f"products/{args.product_id}.json", token, update_payload)
        updated_product = update_result.get("product")
        if not isinstance(updated_product, dict):
            raise RuntimeError("Shopify update did not return a product object.")
        print(f"Applied variant to product {args.product_id}. body_html length={len(updated_product.get('body_html') or '')}")

        print_step("Step 5: Run live dogfood")
        dogfood_run = run_script("dogfood_pdp.py", ["--url", args.product_url, "--output-dir", str(dogfood_dir)])
        if dogfood_run.stdout.strip():
            print(dogfood_run.stdout.strip())
        if dogfood_run.returncode == 0:
            print_step("Step 6: Promotion success")
            print("Dogfood passed. Promotion succeeded and 24-hour soak period starts now.")
            return 0

        if dogfood_run.stderr.strip():
            print(dogfood_run.stderr.strip(), file=sys.stderr)

        print_step("Step 6: Dogfood failed, starting rollback")
        snapshot_path = snapshots_dir / "pre-push-product.json"
        rollback_run = run_script(
            "shopify_rollback.py",
            ["--snapshot", str(snapshot_path), "--confirm", "--store", args.store, "--api-version", args.api_version],
        )
        if rollback_run.stdout.strip():
            print(rollback_run.stdout.strip())
        if rollback_run.returncode != 0:
            raise RuntimeError(rollback_run.stderr.strip() or rollback_run.stdout.strip() or "Rollback failed after dogfood failure")
        print("Promotion failed dogfood. Snapshot was restored automatically.")
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
