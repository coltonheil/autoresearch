#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import requests

BASE_URL = "https://data-chief.vercel.app"
OUTPUT_DIR = Path.home() / ".openclaw" / "workspace" / "outputs" / "autoresearch" / "data-chief-language"
TIMEOUT = 30
MIN_TEXT_LENGTH = 3

API_PATHS = [
    "/api/v1/customers",
    "/api/v1/connectors",
    "/api/v1/librarian/events",
    "/api/v1/trust/CUST-1001",
    "/api/v1/customers/CUST-1001/pnl",
    "/api/v1/customers/CUST-1001/summary-metrics",
    "/api/v1/repricing?customer_id=CUST-1001",
]

PAGE_PATHS = [
    "/connectors",
    "/librarian",
    "/customers",
    "/customers/CUST-1001",
    "/trust/CUST-1001",
]

SNAKE_CASE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+)+\b")
ACCEPTABLE_TECHNICAL_TERMS = {
    "servicetitan",
    "quickbooks",
    "salesforce",
    "auto-confirmed",
    "reconciliation",
    "margin",
    "rate",
    "p&l",
    "sync",
    "synced",
}
PIPELINE_JARGON = [
    "quarantined",
    "quarantine",
    "normalized value",
    "unmapped columns",
    "pipe-delimited",
    "embedded json",
    "schema version",
    "schema versions",
    "downstream economics",
    "record_state",
    "pnl_impact",
]
INTERNAL_ARTIFACTS = [
    "hero_customer_enrichment",
    "demo_mvp_seed",
    "cross_source_aliases_reconciled",
    "firmware_rev",
    "telemetry_interval_ms",
]
MARKETING_SPEAK = [
    "operator-grade synergy",
    "leveraging downstream economics",
]
DESCRIPTION_HINTS = {"description", "summary", "detail", "details", "reason", "explanation", "note", "label", "title", "headline", "caption", "notes"}
CONTEXT_REQUIRED_HINTS = {"description", "summary", "detail", "details", "reason", "explanation", "note", "notes"}
OPERATOR_TERMS = {
    "customer",
    "revenue",
    "margin",
    "rate",
    "contract",
    "invoice",
    "payment",
    "service",
    "work order",
    "labor",
    "price",
    "renewal",
    "records",
    "profit",
    "cost",
    "source system",
    "sync",
    "job",
    "hours",
    "recommend",
    "recommended",
    "auto-confirmed",
}
INTERNAL_SIGNAL_TERMS = {
    "json",
    "payload",
    "schema",
    "firmware",
    "telemetry",
    "downstream",
    "record_state",
    "pnl_impact",
    "source_system",
    "pipe-delimited",
    "embedded",
}

CATEGORIES = {
    "operator_clarity": {"weight": 30, "label": "Operator clarity"},
    "jargon_suppression": {"weight": 20, "label": "Internal jargon suppression"},
    "naming_hygiene": {"weight": 20, "label": "Naming hygiene"},
    "content_completeness": {"weight": 15, "label": "Content completeness"},
    "concision": {"weight": 15, "label": "Concision and readability"},
}


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: List[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            cleaned = " ".join(data.split())
            if cleaned:
                self.parts.append(cleaned)


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def ensure_output_dir() -> Path:
    day_dir = OUTPUT_DIR / datetime.now().strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    return day_dir


def fetch_json(path: str) -> Any:
    response = requests.get(BASE_URL + path, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_html(path: str) -> str:
    response = requests.get(BASE_URL + path, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text


def sentence_count(text: str) -> int:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return len([part for part in parts if part])


def looks_empty(text: str) -> bool:
    normalized = text.strip().lower()
    return normalized in {"", "—", "n/a", "na", "null", "none", "unknown", "tbd", "placeholder"}


def normalize(text: str) -> str:
    return " ".join(text.split())


def should_expect_description(path_parts: Iterable[str]) -> bool:
    parts = [str(part).lower() for part in path_parts]
    return any(any(hint in part for hint in DESCRIPTION_HINTS) for part in parts)


def context_required(path_parts: Iterable[str]) -> bool:
    parts = [str(part).lower() for part in path_parts]
    return any(any(hint in part for hint in CONTEXT_REQUIRED_HINTS) for part in parts)


def extract_strings(value: Any, prefix: str = "root", path_parts: Tuple[str, ...] = ()) -> List[Tuple[str, str, bool, bool]]:
    results: List[Tuple[str, str, bool, bool]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            next_prefix = f"{prefix}.{key}"
            next_parts = path_parts + (str(key),)
            results.extend(extract_strings(child, next_prefix, next_parts))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            next_prefix = f"{prefix}[{index}]"
            results.extend(extract_strings(child, next_prefix, path_parts + (str(index),)))
    elif isinstance(value, str):
        cleaned = normalize(value)
        if len(cleaned) >= MIN_TEXT_LENGTH:
            results.append((prefix, cleaned, should_expect_description(path_parts), context_required(path_parts)))
    elif value is None and should_expect_description(path_parts):
        results.append((prefix, "", True, context_required(path_parts)))
    return results


def parse_visible_text(html: str) -> List[str]:
    parser = VisibleTextParser()
    parser.feed(html)
    seen = set()
    results: List[str] = []
    for part in parser.parts:
        cleaned = part.strip()
        if len(cleaned) >= MIN_TEXT_LENGTH and cleaned not in seen:
            seen.add(cleaned)
            results.append(cleaned)
    return results


def has_operator_anchor(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in OPERATOR_TERMS)


def internal_signal_count(text: str) -> int:
    lower = text.lower()
    return sum(1 for term in INTERNAL_SIGNAL_TERMS if term in lower)


def analyze_text(text: str, field_path: str, source: str, expects_description: bool = False, requires_context: bool = False) -> Dict[str, Any]:
    normalized = normalize(text)
    lower = normalized.lower()

    jargon_hits = [term for term in PIPELINE_JARGON if term in lower]
    artifact_hits = [term for term in INTERNAL_ARTIFACTS if term in lower]
    marketing_hits = [term for term in MARKETING_SPEAK if term in lower]

    snake_case_hits = []
    for match in SNAKE_CASE_RE.findall(normalized):
        if match.lower() not in ACCEPTABLE_TECHNICAL_TERMS:
            snake_case_hits.append(match)

    empty_expected_description = expects_description and looks_empty(normalized)
    too_long = sentence_count(normalized) > 3 or len(normalized) > 240
    operator_clarity_issue = internal_signal_count(normalized) > 0 or (len(normalized) > 0 and not has_operator_anchor(normalized) and (bool(jargon_hits) or bool(snake_case_hits)))
    weak_context = requires_context and (looks_empty(normalized) or len(normalized) < 12)

    category_passes = {
        "operator_clarity": not (operator_clarity_issue or jargon_hits or artifact_hits or marketing_hits),
        "jargon_suppression": not (jargon_hits or artifact_hits),
        "naming_hygiene": not snake_case_hits,
        "content_completeness": not (empty_expected_description or weak_context),
        "concision": not too_long,
    }

    failures: List[str] = []
    if not category_passes["operator_clarity"]:
        failures.append("operator_clarity")
    if not category_passes["jargon_suppression"]:
        failures.append("jargon_suppression")
    if not category_passes["naming_hygiene"]:
        failures.append("naming_hygiene")
    if not category_passes["content_completeness"]:
        failures.append("content_completeness")
    if not category_passes["concision"]:
        failures.append("concision")

    return {
        "source": source,
        "field": field_path,
        "text": normalized,
        "passed": len(failures) == 0,
        "failures": failures,
        "category_passes": category_passes,
        "signals": {
            "jargon_hits": jargon_hits,
            "artifact_hits": artifact_hits,
            "marketing_hits": marketing_hits,
            "snake_case_hits": snake_case_hits,
            "empty_expected_description": empty_expected_description,
            "weak_context": weak_context,
            "too_long": too_long,
        },
    }


def summarize_dimension(details: List[Dict[str, Any]], category: str) -> Dict[str, Any]:
    total = len(details)
    passed = sum(1 for entry in details if entry["category_passes"][category])
    failed = total - passed
    ratio = (passed / total) if total else 0.0

    weight = CATEGORIES[category]["weight"]
    if category == "operator_clarity":
        if ratio >= 0.95:
            points = 30
        elif ratio >= 0.80:
            points = 22
        elif ratio >= 0.60:
            points = 14
        elif ratio >= 0.35:
            points = 6
        else:
            points = 0
    elif category == "jargon_suppression":
        if failed == 0:
            points = 20
        elif failed <= 2:
            points = 15
        elif ratio >= 0.80:
            points = 8
        elif ratio >= 0.60:
            points = 3
        else:
            points = 0
    elif category == "naming_hygiene":
        if failed == 0:
            points = 20
        elif failed <= 2:
            points = 14
        elif ratio >= 0.80:
            points = 8
        elif ratio >= 0.60:
            points = 3
        else:
            points = 0
    elif category == "content_completeness":
        if ratio >= 0.95:
            points = 15
        elif ratio >= 0.85:
            points = 11
        elif ratio >= 0.70:
            points = 7
        elif ratio >= 0.50:
            points = 3
        else:
            points = 0
    elif category == "concision":
        if ratio >= 0.95:
            points = 15
        elif ratio >= 0.85:
            points = 11
        elif ratio >= 0.70:
            points = 7
        elif ratio >= 0.50:
            points = 3
        else:
            points = 0
    else:
        points = 0

    return {
        "label": CATEGORIES[category]["label"],
        "weight": weight,
        "points": points,
        "max_points": weight,
        "passed": passed,
        "total": total,
        "failed": failed,
        "pass_rate": round(ratio, 4),
    }


def run() -> Dict[str, Any]:
    details: List[Dict[str, Any]] = []

    for path in API_PATHS:
        payload = fetch_json(path)
        for field_path, text, expects_description, requires_context in extract_strings(payload):
            details.append(analyze_text(text, field_path, f"api:{path}", expects_description, requires_context))

    for path in PAGE_PATHS:
        html = fetch_html(path)
        for index, text in enumerate(parse_visible_text(html)):
            details.append(analyze_text(text, f"visible_text[{index}]", f"page:{path}", False, False))

    category_scores = {
        category: summarize_dimension(details, category)
        for category in CATEGORIES
    }

    total_checks = len(details)
    passed_checks = sum(1 for entry in details if entry["passed"])
    failed_checks = total_checks - passed_checks
    score = round(sum(item["points"] for item in category_scores.values()), 2)

    failure_buckets: Dict[str, int] = {}
    for entry in details:
        for failure in entry["failures"]:
            failure_buckets[failure] = failure_buckets.get(failure, 0) + 1

    return {
        "score": score,
        "language_score": score,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "category_scores": category_scores,
        "failure_buckets": failure_buckets,
        "details": details,
        "base_url": BASE_URL,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    summary = run()
    output_dir = ensure_output_dir()
    output_path = output_dir / f"language-score-{now_stamp()}.json"
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
