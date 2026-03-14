#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

BASE_URL = "https://data-chief.vercel.app"
OUTPUT_DIR = Path.home() / ".openclaw" / "workspace" / "outputs" / "autoresearch" / "data-chief-pipeline"
HERO_CUSTOMERS = ["CUST-1001", "CUST-1023", "CUST-1037"]
TIMEOUT = 30

PAGE_ROUTES = [
    "/connectors",
    "/librarian",
    "/customers",
    "/customers/CUST-1001",
    "/customers/CUST-1023",
    "/customers/CUST-1037",
    "/trust/CUST-1001",
]

API_ROUTES = [
    {"name": "customers", "path": "/api/v1/customers"},
    {"name": "connectors", "path": "/api/v1/connectors"},
    {"name": "librarian_events", "path": "/api/v1/librarian/events"},
    {"name": "trust_CUST_1001", "path": "/api/v1/trust/CUST-1001"},
    {"name": "summary_metrics_CUST_1001", "path": "/api/v1/customers/CUST-1001/summary-metrics"},
]


CATEGORIES = {
    "api_status": {"weight": 15, "label": "API availability and status"},
    "response_structure": {"weight": 15, "label": "API response structure"},
    "data_integrity": {"weight": 35, "label": "Data integrity and believability"},
    "trust_narrative": {"weight": 15, "label": "Trust narrative completeness"},
    "page_status": {"weight": 10, "label": "Page route availability"},
    "error_hygiene": {"weight": 10, "label": "Error hygiene"},
}


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def ensure_output_dir() -> Path:
    day_dir = OUTPUT_DIR / datetime.now().strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    return day_dir


def fetch_json(path: str) -> Dict[str, Any]:
    url = BASE_URL + path
    try:
        response = requests.get(url, timeout=TIMEOUT)
        try:
            payload: Any = response.json()
        except Exception:
            payload = None
        return {
            "url": url,
            "status_code": response.status_code,
            "ok": response.ok,
            "payload": payload,
            "text": response.text,
            "headers": dict(response.headers),
        }
    except requests.RequestException as exc:
        return {
            "url": url,
            "status_code": None,
            "ok": False,
            "payload": None,
            "text": "",
            "headers": {},
            "request_error": str(exc),
        }


def fetch_page(path: str) -> Dict[str, Any]:
    url = BASE_URL + path
    try:
        response = requests.get(url, timeout=TIMEOUT)
        return {
            "url": url,
            "status_code": response.status_code,
            "ok": response.ok,
            "content_type": response.headers.get("content-type", ""),
        }
    except requests.RequestException as exc:
        return {
            "url": url,
            "status_code": None,
            "ok": False,
            "content_type": "",
            "request_error": str(exc),
        }


def record_check(
    details: List[Dict[str, Any]],
    name: str,
    passed: bool,
    category: str,
    message: str,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    entry: Dict[str, Any] = {
        "name": name,
        "category": category,
        "passed": passed,
        "message": message,
    }
    if extra:
        entry.update(extra)
    details.append(entry)


def top_level_has_error(payload: Any) -> bool:
    return isinstance(payload, dict) and "error" in payload


def is_non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def positive_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except Exception:
        return False


def safe_len(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def repricing_path(customer_id: str) -> str:
    return f"/api/v1/repricing?customer_id={customer_id}"


def pnl_path(customer_id: str) -> str:
    return f"/api/v1/customers/{customer_id}/pnl"


def get_hero_customer_rows(customers_payload: Any) -> Dict[str, Dict[str, Any]]:
    rows = customers_payload.get("data", []) if isinstance(customers_payload, dict) else []
    index: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict):
            customer_id = row.get("customer_id")
            if customer_id in HERO_CUSTOMERS:
                index[customer_id] = row
    return index


def count_failed(details: List[Dict[str, Any]], category: str) -> int:
    return sum(1 for entry in details if entry["category"] == category and not entry["passed"])


def score_band(failures: int, mapping: List[tuple[int, int]]) -> int:
    for max_failures, points in mapping:
        if failures <= max_failures:
            return points
    return mapping[-1][1]


def run() -> Dict[str, Any]:
    details: List[Dict[str, Any]] = []

    api_results: Dict[str, Dict[str, Any]] = {route["name"]: fetch_json(route["path"]) for route in API_ROUTES}
    hero_pnl_results = {customer_id: fetch_json(pnl_path(customer_id)) for customer_id in HERO_CUSTOMERS}
    hero_repricing_results = {customer_id: fetch_json(repricing_path(customer_id)) for customer_id in HERO_CUSTOMERS}
    page_results = {path: fetch_page(path) for path in PAGE_ROUTES}

    # API availability and status checks
    for route in API_ROUTES:
        result = api_results[route["name"]]
        status_code = result.get("status_code")
        record_check(
            details,
            f"api_status:{route['path']}",
            status_code == 200,
            "api_status",
            f"Expected 200, got {status_code}.",
            {"path": route["path"], "status_code": status_code, "request_error": result.get("request_error")},
        )

    for customer_id, result in hero_pnl_results.items():
        status_code = result.get("status_code")
        record_check(
            details,
            f"api_status:{pnl_path(customer_id)}",
            status_code == 200,
            "api_status",
            f"Expected 200, got {status_code}.",
            {"path": pnl_path(customer_id), "status_code": status_code, "request_error": result.get("request_error")},
        )

    for customer_id, result in hero_repricing_results.items():
        status_code = result.get("status_code")
        record_check(
            details,
            f"api_status:{repricing_path(customer_id)}",
            status_code == 200,
            "api_status",
            f"Expected 200, got {status_code}.",
            {"path": repricing_path(customer_id), "status_code": status_code, "request_error": result.get("request_error")},
        )

    # API response structure checks
    customers_payload = api_results["customers"].get("payload")
    customers_data = customers_payload.get("data") if isinstance(customers_payload, dict) else None
    record_check(
        details,
        "structure:customers_data_non_empty_array",
        is_non_empty_list(customers_data),
        "response_structure",
        "Customers response should expose data as a non-empty array.",
    )

    connectors_payload = api_results["connectors"].get("payload")
    connectors = connectors_payload.get("data") if isinstance(connectors_payload, dict) else None
    record_check(
        details,
        "structure:connectors_data_non_empty_array",
        is_non_empty_list(connectors),
        "response_structure",
        "Connectors response should expose data as a non-empty array.",
    )

    librarian_payload = api_results["librarian_events"].get("payload")
    librarian_rows = librarian_payload.get("data") if isinstance(librarian_payload, dict) else None
    record_check(
        details,
        "structure:librarian_data_non_empty_array",
        is_non_empty_list(librarian_rows),
        "response_structure",
        "Librarian events response should expose data as a non-empty array.",
    )

    trust_payload = api_results["trust_CUST_1001"].get("payload")
    source_inventory = trust_payload.get("source_inventory") if isinstance(trust_payload, dict) else None
    record_check(
        details,
        "structure:trust_source_inventory_non_empty_array",
        is_non_empty_list(source_inventory),
        "response_structure",
        "Trust response should expose source_inventory as a non-empty array.",
    )

    summary_payload = api_results["summary_metrics_CUST_1001"].get("payload")
    summary_data = summary_payload.get("data") if isinstance(summary_payload, dict) else None
    record_check(
        details,
        "structure:summary_metrics_data_non_empty_object",
        isinstance(summary_data, dict) and len(summary_data) > 0,
        "response_structure",
        "Summary metrics should expose data as a non-empty object.",
    )

    for customer_id, result in hero_pnl_results.items():
        payload = result.get("payload")
        rows = ((payload or {}).get("data") or {}).get("rows") if isinstance(payload, dict) else None
        record_check(
            details,
            f"structure:pnl_rows_non_empty:{customer_id}",
            is_non_empty_list(rows),
            "response_structure",
            f"P&L response for {customer_id} should expose non-empty data.rows.",
            {"row_count": safe_len(rows)},
        )

    for customer_id, result in hero_repricing_results.items():
        payload = result.get("payload")
        data = payload.get("data") if isinstance(payload, dict) else None
        record_check(
            details,
            f"structure:repricing_data_non_empty:{customer_id}",
            is_non_empty_list(data),
            "response_structure",
            f"Repricing response for {customer_id} should expose a non-empty data array.",
            {"row_count": safe_len(data)},
        )

    # Data integrity and believability checks
    hero_customer_rows = get_hero_customer_rows(customers_payload)
    connectors = connectors if isinstance(connectors, list) else []
    librarian_rows = librarian_rows if isinstance(librarian_rows, list) else []
    source_inventory = source_inventory if isinstance(source_inventory, list) else []
    summary_data = summary_data if isinstance(summary_data, dict) else {}

    all_connector_counts_positive = bool(connectors) and all(
        positive_number((item or {}).get("total_records")) for item in connectors if isinstance(item, dict)
    )
    record_check(
        details,
        "integrity:connectors_total_records_positive",
        all_connector_counts_positive,
        "data_integrity",
        "Every connector should report total_records > 0.",
        {"connector_count": len(connectors)},
    )

    realistic_connectors = [
        item for item in connectors if isinstance(item, dict) and 100 <= float(item.get("total_records", 0) or 0) <= 10000
    ]
    record_check(
        details,
        "integrity:connectors_record_counts_realistic",
        bool(connectors) and len(realistic_connectors) == len(connectors),
        "data_integrity",
        "Connector record counts should sit in a believable hundreds-to-thousands range.",
        {"realistic_connectors": len(realistic_connectors), "connector_count": len(connectors)},
    )

    customer_count = safe_len(customers_data)
    record_check(
        details,
        "integrity:customers_count_at_least_25",
        customer_count >= 25,
        "data_integrity",
        f"Expected at least 25 customers, found {customer_count}.",
        {"customer_count": customer_count},
    )

    for customer_id in HERO_CUSTOMERS:
        row = hero_customer_rows.get(customer_id)
        has_name = isinstance(row, dict) and bool(str(row.get("customer_name") or "").strip())
        record_check(
            details,
            f"integrity:hero_customer_present:{customer_id}",
            has_name,
            "data_integrity",
            f"Hero customer {customer_id} should appear in customers with a non-empty name.",
        )

    auto_confirmed_count = 0
    explanation_count = 0
    for row in librarian_rows:
        if not isinstance(row, dict):
            continue
        if bool(str(row.get("explanation") or "").strip()):
            explanation_count += 1
        if row.get("auto_confirmed") is True:
            auto_confirmed_count += 1
            continue
        status = str(row.get("resolution_status") or row.get("status") or "").lower()
        operator_status = str(row.get("operator_status") or "").lower()
        if ("auto" in status and "confirm" in status) or ("auto" in operator_status and "confirm" in operator_status):
            auto_confirmed_count += 1
    record_check(
        details,
        "integrity:librarian_events_exist",
        len(librarian_rows) > 0,
        "data_integrity",
        f"Expected librarian events, found {len(librarian_rows)} rows.",
        {"event_count": len(librarian_rows)},
    )
    record_check(
        details,
        "integrity:librarian_auto_confirmed_present",
        auto_confirmed_count > 0,
        "data_integrity",
        f"Expected at least one auto-confirmed librarian event, found {auto_confirmed_count}.",
        {"auto_confirmed_count": auto_confirmed_count},
    )
    record_check(
        details,
        "integrity:librarian_explanations_present",
        explanation_count > 0,
        "data_integrity",
        f"Expected non-empty librarian explanations, found {explanation_count} populated rows.",
        {"explanation_count": explanation_count},
    )

    valid_source_inventory_rows = [item for item in source_inventory if isinstance(item, dict)]
    positive_inventory_rows = 0
    named_inventory_rows = 0
    for item in valid_source_inventory_rows:
        candidate_values = [
            item.get("record_count"),
            item.get("records"),
            item.get("total_records"),
            item.get("source_record_count"),
        ]
        if any(positive_number(value) for value in candidate_values):
            positive_inventory_rows += 1
        source_name = str(item.get("source_name") or item.get("connector_name") or "").strip()
        if source_name and "-" not in source_name.replace(" ", ""):
            named_inventory_rows += 1
    record_check(
        details,
        "integrity:trust_source_inventory_positive_counts",
        len(valid_source_inventory_rows) > 0 and positive_inventory_rows == len(valid_source_inventory_rows),
        "data_integrity",
        "Every trust source inventory row should expose a positive record count.",
        {"source_inventory_count": len(valid_source_inventory_rows), "positive_count_rows": positive_inventory_rows},
    )
    record_check(
        details,
        "integrity:trust_source_inventory_named_sources",
        len(valid_source_inventory_rows) > 0 and named_inventory_rows == len(valid_source_inventory_rows),
        "data_integrity",
        "Trust source inventory should use recognizable source names, not raw IDs.",
        {"source_inventory_count": len(valid_source_inventory_rows), "named_source_rows": named_inventory_rows},
    )

    for customer_id, result in hero_pnl_results.items():
        payload = result.get("payload")
        rows = ((payload or {}).get("data") or {}).get("rows") if isinstance(payload, dict) else []
        rows = rows if isinstance(rows, list) else []
        record_check(
            details,
            f"integrity:pnl_rows_exist:{customer_id}",
            len(rows) > 0,
            "data_integrity",
            f"Expected non-empty P&L rows for {customer_id}.",
            {"row_count": len(rows)},
        )
        has_non_zero_amounts = any(
            positive_number((row or {}).get("total_revenue")) and positive_number((row or {}).get("gross_margin_amount"))
            for row in rows
            if isinstance(row, dict)
        )
        record_check(
            details,
            f"integrity:pnl_non_zero_amounts:{customer_id}",
            has_non_zero_amounts,
            "data_integrity",
            f"P&L rows for {customer_id} should include non-zero revenue and margin amounts.",
        )
        plausible_rows = [
            row for row in rows
            if isinstance(row, dict) and 1000 <= float(row.get("total_revenue", 0) or 0) <= 500000
        ]
        record_check(
            details,
            f"integrity:pnl_plausible_revenue_range:{customer_id}",
            len(rows) > 0 and len(plausible_rows) == len(rows),
            "data_integrity",
            f"P&L revenue for {customer_id} should stay in a plausible field-service range.",
            {"plausible_rows": len(plausible_rows), "row_count": len(rows)},
        )

    for customer_id, result in hero_repricing_results.items():
        payload = result.get("payload")
        data = payload.get("data") if isinstance(payload, dict) else []
        data = data if isinstance(data, list) else []
        row = data[0] if data and isinstance(data[0], dict) else {}
        record_check(
            details,
            f"integrity:repricing_exists:{customer_id}",
            len(data) > 0,
            "data_integrity",
            f"Expected repricing data for {customer_id}.",
            {"row_count": len(data)},
        )
        has_prices = positive_number(row.get("current_price")) and positive_number(row.get("target_price") or row.get("recommended_rate"))
        record_check(
            details,
            f"integrity:repricing_current_and_target_present:{customer_id}",
            has_prices,
            "data_integrity",
            f"Repricing data for {customer_id} should include current and recommended pricing values.",
        )
        current_price = row.get("current_price")
        target_price = row.get("target_price") or row.get("recommended_rate")
        non_zero_delta = False
        try:
            non_zero_delta = abs(float(target_price) - float(current_price)) > 0.0001
        except Exception:
            non_zero_delta = False
        record_check(
            details,
            f"integrity:repricing_non_zero_delta:{customer_id}",
            non_zero_delta,
            "data_integrity",
            f"Repricing data for {customer_id} should include a non-zero delta between current and recommended pricing.",
        )

    record_check(
        details,
        "integrity:summary_metrics_non_empty",
        isinstance(summary_data, dict) and any(value not in (None, "", [], {}) for value in summary_data.values()),
        "data_integrity",
        "Hero customer summary metrics should not collapse into an empty shell.",
    )

    # Trust narrative completeness
    connector_names = {
        str(item.get("connector_id") or "").strip().lower(): item
        for item in connectors
        if isinstance(item, dict) and str(item.get("connector_id") or "").strip()
    }
    inventory_names = {
        str(item.get("connector_id") or item.get("source_name") or item.get("source_key") or "").strip().lower(): item
        for item in source_inventory
        if isinstance(item, dict)
    }

    connector_chain_ok = len(connectors) > 0
    librarian_reference_ok = False
    for row in librarian_rows:
        if not isinstance(row, dict):
            continue
        connector_id = str(row.get("connector_id") or "").strip().lower()
        if connector_id and (connector_id in connector_names or connector_id in inventory_names):
            librarian_reference_ok = True
            break
    record_check(
        details,
        "trust:connectors_to_librarian_referenceable",
        connector_chain_ok and librarian_reference_ok,
        "trust_narrative",
        "Connectors should be non-empty and librarian events should reference recognizable source systems.",
        {"connector_count": len(connectors), "librarian_event_count": len(librarian_rows)},
    )

    pnl_named_source_trace = False
    for item in source_inventory:
        if not isinstance(item, dict):
            continue
        source_name = str(item.get("source_name") or item.get("connector_name") or "").strip()
        if source_name and positive_number(item.get("record_count") or item.get("total_records") or item.get("records")):
            pnl_named_source_trace = True
            break
    record_check(
        details,
        "trust:librarian_to_pnl_named_source_trace",
        pnl_named_source_trace and all(
            safe_len((((hero_pnl_results[cid].get("payload") or {}).get("data") or {}).get("rows"))) > 0 for cid in HERO_CUSTOMERS
        ),
        "trust_narrative",
        "The chain from source systems through librarian activity into hero-customer P&L should be followable.",
    )

    repricing_chain_results = []
    for customer_id in HERO_CUSTOMERS:
        pnl_rows = (((hero_pnl_results[customer_id].get("payload") or {}).get("data") or {}).get("rows") or [])
        repricing_rows = ((hero_repricing_results[customer_id].get("payload") or {}).get("data") or [])
        repricing_row = repricing_rows[0] if repricing_rows and isinstance(repricing_rows[0], dict) else {}
        try:
            current_price = float(repricing_row.get("current_price"))
            target_price = float(repricing_row.get("target_price") or repricing_row.get("recommended_rate"))
            delta_ok = abs(target_price - current_price) > 0.0001
        except Exception:
            delta_ok = False
        repricing_chain_results.append(len(pnl_rows) > 0 and bool(repricing_row) and delta_ok)
    record_check(
        details,
        "trust:pnl_to_repricing_traceable",
        all(repricing_chain_results),
        "trust_narrative",
        "Hero customers should show a followable chain from P&L to repricing with current and recommended values plus a non-zero delta.",
        {"per_customer": dict(zip(HERO_CUSTOMERS, repricing_chain_results))},
    )

    pnl_total_revenue = 0.0
    pnl_rows_cust_1001 = (((hero_pnl_results["CUST-1001"].get("payload") or {}).get("data") or {}).get("rows") or [])
    if isinstance(pnl_rows_cust_1001, list):
        pnl_total_revenue = sum(float((row or {}).get("total_revenue") or 0) for row in pnl_rows_cust_1001 if isinstance(row, dict))
    summary_revenue = summary_data.get("ttm_revenue") if isinstance(summary_data, dict) else None
    within_10_pct = False
    variance_pct = None
    try:
        pnl_total = float(pnl_total_revenue)
        summary_total = float(summary_revenue)
        baseline = max(abs(pnl_total), 1.0)
        variance_pct = abs(summary_total - pnl_total) / baseline
        within_10_pct = variance_pct <= 0.10
    except Exception:
        within_10_pct = False
    record_check(
        details,
        "trust:summary_metrics_matches_pnl_within_10pct",
        within_10_pct,
        "trust_narrative",
        "Summary-metrics revenue should stay within 10% of the P&L total revenue for the hero customer.",
        {"summary_ttm_revenue": summary_revenue, "pnl_total_revenue": round(pnl_total_revenue, 2), "variance_pct": round(variance_pct, 4) if variance_pct is not None else None},
    )

    # Page route status
    for path, result in page_results.items():
        status_code = result.get("status_code")
        record_check(
            details,
            f"page_status:{path}",
            status_code == 200,
            "page_status",
            f"Expected 200, got {status_code}.",
            {"path": path, "status_code": status_code, "request_error": result.get("request_error")},
        )

    # Error hygiene
    for route in API_ROUTES:
        payload = api_results[route["name"]].get("payload")
        record_check(
            details,
            f"error_hygiene:{route['path']}",
            not top_level_has_error(payload),
            "error_hygiene",
            "Successful API responses should not expose a top-level error key.",
        )
    for customer_id, result in hero_pnl_results.items():
        record_check(
            details,
            f"error_hygiene:{pnl_path(customer_id)}",
            not top_level_has_error(result.get("payload")),
            "error_hygiene",
            "Successful P&L responses should not expose a top-level error key.",
        )
    for customer_id, result in hero_repricing_results.items():
        record_check(
            details,
            f"error_hygiene:{repricing_path(customer_id)}",
            not top_level_has_error(result.get("payload")),
            "error_hygiene",
            "Successful repricing responses should not expose a top-level error key.",
        )

    category_scores: Dict[str, Dict[str, Any]] = {}

    api_failures = count_failed(details, "api_status")
    api_points = score_band(api_failures, [(0, 15), (1, 10), (2, 6), (3, 2), (9999, 0)])
    api_checks = [entry for entry in details if entry["category"] == "api_status"]
    category_scores["api_status"] = {
        "label": CATEGORIES["api_status"]["label"],
        "weight": CATEGORIES["api_status"]["weight"],
        "points": api_points,
        "max_points": CATEGORIES["api_status"]["weight"],
        "passed": sum(1 for entry in api_checks if entry["passed"]),
        "total": len(api_checks),
        "failed": api_failures,
    }

    structure_failures = count_failed(details, "response_structure")
    structure_points = score_band(structure_failures, [(0, 15), (1, 10), (2, 6), (3, 2), (9999, 0)])
    structure_checks = [entry for entry in details if entry["category"] == "response_structure"]
    category_scores["response_structure"] = {
        "label": CATEGORIES["response_structure"]["label"],
        "weight": CATEGORIES["response_structure"]["weight"],
        "points": structure_points,
        "max_points": CATEGORIES["response_structure"]["weight"],
        "passed": sum(1 for entry in structure_checks if entry["passed"]),
        "total": len(structure_checks),
        "failed": structure_failures,
    }

    integrity_failures = count_failed(details, "data_integrity")
    integrity_points = score_band(integrity_failures, [(0, 35), (2, 26), (4, 17), (6, 8), (9999, 0)])
    integrity_checks = [entry for entry in details if entry["category"] == "data_integrity"]
    category_scores["data_integrity"] = {
        "label": CATEGORIES["data_integrity"]["label"],
        "weight": CATEGORIES["data_integrity"]["weight"],
        "points": integrity_points,
        "max_points": CATEGORIES["data_integrity"]["weight"],
        "passed": sum(1 for entry in integrity_checks if entry["passed"]),
        "total": len(integrity_checks),
        "failed": integrity_failures,
    }

    trust_checks = [entry for entry in details if entry["category"] == "trust_narrative"]
    trust_failures = sum(1 for entry in trust_checks if not entry["passed"])
    connector_chain_pass = next((entry["passed"] for entry in trust_checks if entry["name"] == "trust:connectors_to_librarian_referenceable"), False)
    librarian_to_pnl_pass = next((entry["passed"] for entry in trust_checks if entry["name"] == "trust:librarian_to_pnl_named_source_trace"), False)
    pnl_to_repricing_pass = next((entry["passed"] for entry in trust_checks if entry["name"] == "trust:pnl_to_repricing_traceable"), False)
    cross_surface_pass = next((entry["passed"] for entry in trust_checks if entry["name"] == "trust:summary_metrics_matches_pnl_within_10pct"), False)

    narrative_one_complete = connector_chain_pass and librarian_to_pnl_pass
    narrative_one_partial = connector_chain_pass or librarian_to_pnl_pass
    narrative_two_complete = pnl_to_repricing_pass
    narrative_two_partial = False
    narrative_two_entry = next((entry for entry in trust_checks if entry["name"] == "trust:pnl_to_repricing_traceable"), None)
    if narrative_two_entry and isinstance(narrative_two_entry.get("per_customer"), dict):
        results = list(narrative_two_entry["per_customer"].values())
        narrative_two_partial = any(results)
    if narrative_one_complete and narrative_two_complete and cross_surface_pass:
        trust_points = 15
    elif ((narrative_one_complete and (narrative_two_complete or narrative_two_partial)) or ((narrative_one_complete or narrative_one_partial) and narrative_two_complete)) and not (not cross_surface_pass and not narrative_two_complete):
        trust_points = 11
    elif (narrative_one_partial and narrative_two_partial) or (trust_failures <= 2 and (narrative_one_partial or narrative_two_partial)):
        trust_points = 7
    elif narrative_one_complete or narrative_two_partial or narrative_one_partial:
        trust_points = 3
    else:
        trust_points = 0
    category_scores["trust_narrative"] = {
        "label": CATEGORIES["trust_narrative"]["label"],
        "weight": CATEGORIES["trust_narrative"]["weight"],
        "points": trust_points,
        "max_points": CATEGORIES["trust_narrative"]["weight"],
        "passed": sum(1 for entry in trust_checks if entry["passed"]),
        "total": len(trust_checks),
        "failed": trust_failures,
    }

    page_failures = count_failed(details, "page_status")
    page_points = score_band(page_failures, [(0, 10), (1, 7), (2, 4), (9999, 0)])
    page_checks = [entry for entry in details if entry["category"] == "page_status"]
    category_scores["page_status"] = {
        "label": CATEGORIES["page_status"]["label"],
        "weight": CATEGORIES["page_status"]["weight"],
        "points": page_points,
        "max_points": CATEGORIES["page_status"]["weight"],
        "passed": sum(1 for entry in page_checks if entry["passed"]),
        "total": len(page_checks),
        "failed": page_failures,
    }

    error_failures = count_failed(details, "error_hygiene")
    error_points = score_band(error_failures, [(0, 10), (1, 5), (2, 2), (9999, 0)])
    error_checks = [entry for entry in details if entry["category"] == "error_hygiene"]
    category_scores["error_hygiene"] = {
        "label": CATEGORIES["error_hygiene"]["label"],
        "weight": CATEGORIES["error_hygiene"]["weight"],
        "points": error_points,
        "max_points": CATEGORIES["error_hygiene"]["weight"],
        "passed": sum(1 for entry in error_checks if entry["passed"]),
        "total": len(error_checks),
        "failed": error_failures,
    }

    total_checks = len(details)
    passed_checks = sum(1 for entry in details if entry["passed"])
    failed_checks = total_checks - passed_checks
    score = round(sum(item["points"] for item in category_scores.values()), 2)

    return {
        "score": score,
        "pipeline_score": score,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "category_scores": category_scores,
        "details": details,
        "base_url": BASE_URL,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    summary = run()
    output_dir = ensure_output_dir()
    output_path = output_dir / f"pipeline-score-{now_stamp()}.json"
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
