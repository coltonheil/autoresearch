#!/usr/bin/env python3
"""Restore editable Shopify product fields from a saved snapshot."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

DEFAULT_STORE = "heil-ginseng.myshopify.com"
DEFAULT_API_VERSION = "2024-01"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Restore title/body_html from a Shopify product snapshot.",
    )
    parser.add_argument("--snapshot", type=Path, required=True, help="Path to pre-push-product.json")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be restored without updating Shopify")
    parser.add_argument("--confirm", action="store_true", help="Required to execute a live rollback")
    parser.add_argument("--store", default=os.getenv("SHOPIFY_STORE", DEFAULT_STORE), help="Shopify store domain")
    parser.add_argument("--api-version", default=DEFAULT_API_VERSION, help="Shopify Admin API version")
    return parser.parse_args()


def require_token() -> str:
    token = os.getenv("SHOPIFY_TOKEN")
    if not token:
        raise RuntimeError("SHOPIFY_TOKEN is not set in the environment.")
    return token


def load_snapshot(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Snapshot not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Snapshot payload is not a JSON object.")
    return payload


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


def summarize_changes(before: dict[str, Any], target: dict[str, Any], after: dict[str, Any] | None = None) -> list[str]:
    lines: list[str] = []
    lines.append(f"- title: {before.get('title')!r} -> {target.get('title')!r}")
    lines.append(
        f"- body_html length: {len(before.get('body_html') or '')} -> {len(target.get('body_html') or '')}"
    )
    if after is not None:
        lines.append(f"- final title: {after.get('title')!r}")
        lines.append(f"- final body_html length: {len(after.get('body_html') or '')}")
    return lines


def main() -> int:
    args = parse_args()
    try:
        snapshot = load_snapshot(args.snapshot)
        product = snapshot.get("product") or {}
        editable_fields = snapshot.get("editable_fields") or {}
        product_id = editable_fields.get("product_id") or product.get("id")
        if not product_id:
            raise RuntimeError("Snapshot is missing product ID.")

        restore_payload = {
            "title": editable_fields.get("title", product.get("title")),
            "body_html": editable_fields.get("body_html", product.get("body_html")),
        }
        if restore_payload["title"] is None or restore_payload["body_html"] is None:
            raise RuntimeError("Snapshot is missing title or body_html required for rollback.")

        token = require_token()
        before = shopify_request("GET", args.store, args.api_version, f"products/{product_id}.json", token).get("product")
        if not isinstance(before, dict):
            raise RuntimeError("Unable to fetch current product state before rollback.")

        print("Rollback plan")
        for line in summarize_changes(before, restore_payload):
            print(line)

        if args.dry_run:
            print("Dry run only. No Shopify changes were made.")
            return 0

        if not args.confirm:
            print("Rollback blocked. Re-run with --confirm to execute.", file=sys.stderr)
            return 1

        updated_payload = {"product": {"id": product_id, **restore_payload}}
        result = shopify_request("PUT", args.store, args.api_version, f"products/{product_id}.json", token, updated_payload)
        after = result.get("product")
        if not isinstance(after, dict):
            raise RuntimeError("Shopify rollback response did not include a product object.")

        print("Rollback executed successfully.")
        for line in summarize_changes(before, restore_payload, after):
            print(line)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
