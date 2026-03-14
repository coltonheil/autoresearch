#!/usr/bin/env python3
"""Capture a Shopify product snapshot for rollback and diffing."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_STORE = "heil-ginseng.myshopify.com"
DEFAULT_DOMAIN = "pdp-copy"
DEFAULT_API_VERSION = "2024-01"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture the current Shopify product state before a PDP push.",
    )
    parser.add_argument("--product-id", required=True, help="Shopify product ID")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to write snapshot files (default: ~/.openclaw/workspace/outputs/autoresearch/pdp-copy/YYYY-MM-DD/snapshots)",
    )
    parser.add_argument("--store", default=os.getenv("SHOPIFY_STORE", DEFAULT_STORE), help="Shopify store domain")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION, help="Shopify Admin API version")
    return parser.parse_args()


def default_output_dir() -> Path:
    return Path.home() / ".openclaw/workspace/outputs/autoresearch" / DEFAULT_DOMAIN / date.today().isoformat() / "snapshots"


def require_token() -> str:
    token = os.getenv("SHOPIFY_TOKEN")
    if not token:
        raise RuntimeError("SHOPIFY_TOKEN is not set in the environment.")
    return token


def shopify_get(store: str, api_version: str, path: str, token: str) -> dict[str, Any]:
    import requests

    url = f"https://{store}/admin/api/{api_version}/{path.lstrip('/')}"
    response = requests.get(
        url,
        headers={
            "X-Shopify-Access-Token": token,
            "Accept": "application/json",
        },
        timeout=30,
    )
    if response.status_code >= 400:
        detail = response.text.strip() or response.reason
        raise RuntimeError(f"Shopify GET failed ({response.status_code}) for {path}: {detail}")
    return response.json()


def extract_seo_metafields(metafields: list[dict[str, Any]]) -> dict[str, str | None]:
    title_tag = None
    description_tag = None
    for metafield in metafields:
        namespace = metafield.get("namespace")
        key = metafield.get("key")
        value = metafield.get("value")
        if namespace == "global" and key == "title_tag":
            title_tag = value
        if namespace == "global" and key == "description_tag":
            description_tag = value
    return {
        "meta_title": title_tag,
        "meta_description": description_tag,
    }


def build_editable_fields(product: dict[str, Any], seo_fields: dict[str, str | None]) -> dict[str, Any]:
    return {
        "product_id": product.get("id"),
        "handle": product.get("handle"),
        "title": product.get("title"),
        "body_html": product.get("body_html"),
        "meta_title": seo_fields.get("meta_title"),
        "meta_description": seo_fields.get("meta_description"),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        token = require_token()
        product_payload = shopify_get(args.store, args.api_version, f"products/{args.product_id}.json", token)
        product = product_payload.get("product")
        if not isinstance(product, dict):
            raise RuntimeError("Shopify response did not include a product object.")

        metafields_payload = shopify_get(args.store, args.api_version, f"products/{args.product_id}/metafields.json", token)
        metafields = metafields_payload.get("metafields") or []
        if not isinstance(metafields, list):
            raise RuntimeError("Shopify metafields response was not a list.")

        seo_fields = extract_seo_metafields(metafields)
        editable_fields = build_editable_fields(product, seo_fields)

        timestamp = datetime.now(timezone.utc).isoformat()
        full_snapshot = {
            "captured_at_utc": timestamp,
            "store": args.store,
            "api_version": args.api_version,
            "product_id": str(args.product_id),
            "product": product,
            "metafields": metafields,
            "editable_fields": editable_fields,
        }

        full_snapshot_path = output_dir / "pre-push-product.json"
        editable_fields_path = output_dir / "editable-fields.json"
        write_json(full_snapshot_path, full_snapshot)
        write_json(editable_fields_path, editable_fields)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Snapshot saved successfully.")
    print(f"- Product ID: {args.product_id}")
    print(f"- Store: {args.store}")
    print(f"- Full snapshot: {full_snapshot_path}")
    print(f"- Editable fields: {editable_fields_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
