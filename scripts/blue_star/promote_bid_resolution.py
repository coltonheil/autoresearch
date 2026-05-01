#!/usr/bin/env python3
import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPO_SLUG = "blue-star"
LOOP_SLUG = "bid-resolution"
OUTPUT_ROOT = Path.home() / ".openclaw" / "workspace" / "outputs" / "autoresearch" / REPO_SLUG / LOOP_SLUG
DEFAULT_BLUE_STAR_ROOT = Path.home() / "repos" / "blue-star"
DECISION_JSON = "autoresearch-bid-resolution-decisions.json"
DECISION_MD = "autoresearch-bid-resolution-decisions.md"
BACKLOG_JSON = "autoresearch-pipeline-improvement-backlog.json"
BACKLOG_MD = "autoresearch-pipeline-improvement-backlog.md"

PARTNER_LEAD_PATTERNS = {
    "genset_service": ["generator service", "genset service", "maintenance", "repair", "inspection", "load bank", "loadbank"],
    "electrical_contractor": ["installation", "install", "wiring", "electrical", "ats", "transfer switch"],
    "rental": ["rental", "temporary generator", "temp generator", "portable generator"],
    "fuel": ["fuel", "diesel delivery", "refuel", "fueling"],
    "civil_site_work": ["pad", "concrete", "civil", "site prep", "bollard", "trenching"],
}

HARD_JUNK_NO_FIT_PATTERNS = [
    "propellant actuated",
    "cad pad",
    "cad-pad",
    "ordnance",
    "cartridge",
    "explosive",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def find_latest_ledger() -> Optional[Path]:
    ledgers = sorted(OUTPUT_ROOT.glob("*/ledger.jsonl"), key=lambda path: path.stat().st_mtime)
    return ledgers[-1] if ledgers else None


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        payload = json.loads(stripped)
        if not isinstance(payload, dict):
            raise ValueError(f"{path}:{line_number} is not a JSON object")
        payload["_line"] = line_number
        entries.append(payload)
    return entries


def load_existing(path: Path, key: str) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    values = data.get(key, [])
    if not isinstance(values, list):
        raise ValueError(f"{path} field {key} must be a list")
    return [item for item in values if isinstance(item, dict)]


def compact_evidence(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    evidence = entry.get("evidence", [])
    compact: List[Dict[str, Any]] = []
    if not isinstance(evidence, list):
        return compact
    for item in evidence:
        if not isinstance(item, dict):
            continue
        compact.append({
            "type": item.get("type"),
            "source": item.get("source"),
            "locator": item.get("locator"),
            "summary": item.get("summary"),
        })
    return compact


def searchable_text(entry: Dict[str, Any]) -> str:
    title = str(entry.get("title") or entry.get("decision") or "")
    next_action = str(entry.get("next_action") or "")
    blocker = ""
    if isinstance(entry.get("doc_quality"), dict):
        blocker = str(entry["doc_quality"].get("blocker") or "")
    return " ".join([title, next_action, blocker, json.dumps(compact_evidence(entry))]).lower()


def production_mapping(entry: Dict[str, Any]) -> Tuple[str, str, bool]:
    verdict = entry.get("verdict")
    if verdict == "pursue_quote":
        return "packet_candidate", "queue_packet_or_asset_review", True
    if verdict == "true_no_fit":
        return "no_fit", "suppress_quote_and_record_no_fit_rule", True
    if verdict == "docs_missing_inaccessible":
        return "source_blocked", "queue_source_acquisition_or_connector_fix", False
    if verdict == "extraction_failure":
        return "extraction_blocked", "queue_targeted_extraction_or_ocr_rerun", False
    if verdict == "drawing_or_vision_review_needed":
        return "vision_blocked", "queue_drawing_or_vision_review", False
    if verdict == "human_clarification_needed":
        return "human_blocked", "queue_human_clarification", False
    return "investigation", "continue_investigation", False


def secondary_disposition(entry: Dict[str, Any]) -> Dict[str, Any]:
    verdict = entry.get("verdict")
    provided = entry.get("secondary_disposition")
    if isinstance(provided, dict):
        route = provided.get("commercial_route")
        if isinstance(route, str) and route:
            return {
                "blueStarFit": False if route != "blue_star_quote" else True,
                "commercialRoute": route,
                "referralEligible": provided.get("referral_eligible") is True,
                "referralCategory": provided.get("referral_category"),
                "territory": provided.get("territory") or entry.get("territory"),
                "rationale": provided.get("rationale") or "Secondary disposition supplied by the scored ledger.",
            }

    text = searchable_text(entry)
    normalized_text = text.replace("-", " ")

    if verdict == "pursue_quote":
        return {
            "blueStarFit": True,
            "commercialRoute": "blue_star_quote",
            "referralEligible": False,
            "referralCategory": None,
            "territory": entry.get("territory"),
            "rationale": "Primary route is Blue Star quote or packet review.",
        }

    if verdict in {"docs_missing_inaccessible", "extraction_failure", "drawing_or_vision_review_needed", "human_clarification_needed", "continue_investigation"}:
        return {
            "blueStarFit": None,
            "commercialRoute": "not_enough_info",
            "referralEligible": False,
            "referralCategory": None,
            "territory": entry.get("territory"),
            "rationale": "Do not monetize or suppress until source evidence resolves the bid.",
        }

    if verdict == "true_no_fit":
        if any(pattern in normalized_text for pattern in HARD_JUNK_NO_FIT_PATTERNS):
            return {
                "blueStarFit": False,
                "commercialRoute": "junk_no_fit",
                "referralEligible": False,
                "referralCategory": "junk",
                "territory": entry.get("territory"),
                "rationale": "Direct evidence points to a non-genset or non-commercial-lead no-fit.",
            }

        for category, patterns in PARTNER_LEAD_PATTERNS.items():
            if any(pattern in normalized_text for pattern in patterns):
                return {
                    "blueStarFit": False,
                    "commercialRoute": "partner_lead_candidate",
                    "referralEligible": True,
                    "referralCategory": category,
                    "territory": entry.get("territory"),
                    "rationale": "No fit for Blue Star direct quote, but evidence suggests a potentially valuable partner lead.",
                }

        return {
            "blueStarFit": False,
            "commercialRoute": "unqualified_no_fit_reviewable",
            "referralEligible": False,
            "referralCategory": None,
            "territory": entry.get("territory"),
            "rationale": "No fit for Blue Star, but not enough partner-lead evidence to monetize automatically.",
        }

    return {
        "blueStarFit": None,
        "commercialRoute": "investigation",
        "referralEligible": False,
        "referralCategory": None,
        "territory": entry.get("territory"),
        "rationale": "Unhandled verdict requires investigation.",
    }


def infer_pipeline_items(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    bid_id = str(entry.get("bid_id") or "")
    verdict = entry.get("verdict")
    text = searchable_text(entry)
    normalized_text = text.replace("-", " ")
    items: List[Dict[str, Any]] = []
    secondary = secondary_disposition(entry)

    if verdict == "true_no_fit" and "propellant actuated" in text:
        items.append({
            "type": "no_fit_rule",
            "priority": "high",
            "bidId": bid_id,
            "pattern": "gas pressure propellant actuated generator / CAD-PAD ordnance",
            "recommendation": "Treat this wording as ordnance/CAD-PAD no-fit unless electrical generator, kW/kVA, ATS, voltage, or standby-power evidence is present.",
        })

    if secondary["commercialRoute"] == "partner_lead_candidate":
        items.append({
            "type": "partner_referral_candidate",
            "priority": "medium",
            "bidId": bid_id,
            "pattern": f"Blue Star no-fit with partner lead category: {secondary['referralCategory']}",
            "recommendation": "Preserve as a source-cited referral candidate; do not sell or send until freshness, territory, contactability, and partner acceptance criteria are reviewed.",
        })

    if verdict == "pursue_quote" and "reverse auction" in normalized_text:
        items.append({
            "type": "routing_rule",
            "priority": "medium",
            "bidId": bid_id,
            "pattern": "reverse auction with real generator line items",
            "recommendation": "Route to packet candidate plus human event-mechanics review; do not suppress as no-fit solely due to reverse-auction mechanics.",
        })

    if verdict == "pursue_quote" and "split" in text and "line" in text and "generator" in text:
        items.append({
            "type": "routing_rule",
            "priority": "medium",
            "bidId": bid_id,
            "pattern": "multi-line generator package",
            "recommendation": "Split generator line items into asset/package-level quote records before selecting products or generating a packet.",
        })

    if verdict == "pursue_quote" and ("ats" in text or "asset decomposition" in text or "multi-asset" in text):
        items.append({
            "type": "routing_rule",
            "priority": "medium",
            "bidId": bid_id,
            "pattern": "generator plus ATS / multi-asset construction scope",
            "recommendation": "Route to asset/package decomposition and packet-with-caveats rather than single-value fact promotion.",
        })

    if verdict == "docs_missing_inaccessible":
        items.append({
            "type": "source_connector_task",
            "priority": "high",
            "bidId": bid_id,
            "pattern": "source reports current document but no downloaded/trusted/ready artifact",
            "recommendation": "Treat as source acquisition or connector work, not no-fit and not OCR/GLM rerun.",
        })

    if verdict == "extraction_failure":
        items.append({
            "type": "extraction_task",
            "priority": "high",
            "bidId": bid_id,
            "pattern": "source document exists but extracted artifact is inadequate",
            "recommendation": "Queue targeted GLM/OCR/spreadsheet/drawing extraction based on doc_quality.blocker.",
        })

    return items


def decision_record(entry: Dict[str, Any], ledger: Path) -> Dict[str, Any]:
    lane, action, promotion_safe = production_mapping(entry)
    owner_and_action = f"{entry.get('owner', '')} {entry.get('next_action', '')}".lower()
    human_gate = "human" in owner_and_action or "confirm" in owner_and_action
    quote_promotion_allowed = promotion_safe and entry.get("verdict") == "pursue_quote" and not human_gate
    return {
        "bidId": entry.get("bid_id"),
        "runId": entry.get("run_id"),
        "ledger": str(ledger),
        "ledgerLine": entry.get("_line"),
        "previousState": entry.get("previous_state"),
        "verdict": entry.get("verdict"),
        "confidence": entry.get("confidence"),
        "productionLane": lane,
        "productionAction": action,
        "quotePromotionAllowed": quote_promotion_allowed,
        "promotionSafe": promotion_safe,
        "secondaryDisposition": secondary_disposition(entry),
        "decision": entry.get("decision"),
        "leadingHypothesis": entry.get("leading_hypothesis"),
        "disconfirmingTest": entry.get("disconfirming_test"),
        "docQuality": entry.get("doc_quality"),
        "evidence": compact_evidence(entry),
        "rejectedHypotheses": entry.get("rejected_hypotheses", []),
        "nextAction": entry.get("next_action"),
        "owner": entry.get("owner"),
        "pipelineItems": infer_pipeline_items(entry),
        "generatedAt": now_iso(),
    }


def merge_by_bid(existing: List[Dict[str, Any]], incoming: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for item in existing:
        bid_id = item.get("bidId")
        if bid_id:
            merged[str(bid_id)] = item
    for item in incoming:
        bid_id = item.get("bidId")
        if bid_id:
            merged[str(bid_id)] = item
    return [merged[key] for key in sorted(merged)]


def build_decision_artifact(existing: List[Dict[str, Any]], incoming: List[Dict[str, Any]], ledger: Path) -> Dict[str, Any]:
    decisions = merge_by_bid(existing, incoming)
    counts = Counter(str(item.get("verdict")) for item in decisions)
    lanes = Counter(str(item.get("productionLane")) for item in decisions)
    return {
        "artifactVersion": "blue-star.autoresearch-bid-resolution-decisions.v1",
        "generatedAt": now_iso(),
        "inputLedger": str(ledger),
        "summary": {
            "decisionCount": len(decisions),
            "byVerdict": [{"name": key, "count": counts[key]} for key in sorted(counts)],
            "byProductionLane": [{"name": key, "count": lanes[key]} for key in sorted(lanes)],
        },
        "decisions": decisions,
    }


def build_backlog_artifact(existing: List[Dict[str, Any]], decisions: List[Dict[str, Any]], ledger: Path) -> Dict[str, Any]:
    incoming: List[Dict[str, Any]] = []
    replacement_bids = {str(decision.get("bidId")) for decision in decisions if decision.get("bidId")}
    replacement_runs = {str(decision.get("runId")) for decision in decisions if decision.get("runId")}
    for decision in decisions:
        for item in decision.get("pipelineItems", []):
            if isinstance(item, dict):
                item = dict(item)
                item["runId"] = decision.get("runId")
                item["sourceDecisionBidId"] = decision.get("bidId")
                item["sourceVerdict"] = decision.get("verdict")
                item["generatedAt"] = now_iso()
                incoming.append(item)

    incoming.append({
        "type": "roadmap_item",
        "priority": "medium",
        "pattern": "partner referral lane for Blue Star no-fit opportunities",
        "recommendation": "Design a secondary disposition lane that preserves source-cited Blue Star no-fits with commercial value for possible regional genset service, electrical, rental, fuel, or civil partners.",
        "generatedAt": now_iso(),
    })

    merged: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for item in existing:
        item_bid = str(item.get("sourceDecisionBidId") or item.get("bidId") or "")
        item_run = str(item.get("runId") or "")
        if item_bid in replacement_bids and item_run in replacement_runs:
            continue
        key = (str(item.get("type")), str(item.get("pattern")), str(item.get("bidId") or item.get("sourceDecisionBidId")))
        merged[key] = item
    for item in incoming:
        key = (str(item.get("type")), str(item.get("pattern")), str(item.get("bidId") or item.get("sourceDecisionBidId")))
        merged[key] = item
    backlog = [merged[key] for key in sorted(merged)]
    counts = Counter(str(item.get("type")) for item in backlog)
    return {
        "artifactVersion": "blue-star.autoresearch-pipeline-improvement-backlog.v1",
        "generatedAt": now_iso(),
        "inputLedger": str(ledger),
        "summary": {
            "itemCount": len(backlog),
            "byType": [{"name": key, "count": counts[key]} for key in sorted(counts)],
        },
        "items": backlog,
    }


def render_decision_md(artifact: Dict[str, Any]) -> str:
    lines = [
        "# Autoresearch Bid Resolution Decisions",
        "",
        f"Generated: {artifact['generatedAt']}",
        f"Input ledger: `{artifact['inputLedger']}`",
        "",
        "## Summary",
        "",
    ]
    for item in artifact["summary"]["byVerdict"]:
        lines.append(f"- {item['name']}: {item['count']}")
    lines.extend(["", "## Decisions", ""])
    for decision in artifact["decisions"]:
        secondary = decision.get("secondaryDisposition") if isinstance(decision.get("secondaryDisposition"), dict) else {}
        lines.extend([
            f"### {decision['bidId']}",
            "",
            f"- Verdict: `{decision['verdict']}`",
            f"- Production lane: `{decision['productionLane']}`",
            f"- Production action: `{decision['productionAction']}`",
            f"- Secondary commercial route: `{secondary.get('commercialRoute')}`",
            f"- Referral eligible: `{str(secondary.get('referralEligible')).lower()}`",
            f"- Confidence: `{decision['confidence']}`",
            f"- Quote promotion allowed: `{str(decision['quotePromotionAllowed']).lower()}`",
            f"- Next action: {decision.get('nextAction')}",
            f"- Owner: `{decision.get('owner')}`",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def render_backlog_md(artifact: Dict[str, Any]) -> str:
    lines = [
        "# Autoresearch Pipeline Improvement Backlog",
        "",
        f"Generated: {artifact['generatedAt']}",
        f"Input ledger: `{artifact['inputLedger']}`",
        "",
        "## Summary",
        "",
    ]
    for item in artifact["summary"]["byType"]:
        lines.append(f"- {item['name']}: {item['count']}")
    lines.extend(["", "## Items", ""])
    for item in artifact["items"]:
        lines.extend([
            f"### {item.get('type')} - {item.get('pattern')}",
            "",
            f"- Priority: `{item.get('priority')}`",
            f"- Bid: `{item.get('bidId') or item.get('sourceDecisionBidId')}`",
            f"- Recommendation: {item.get('recommendation')}",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def backup_if_exists(path: Path, backup_dir: Path) -> Optional[Path]:
    if not path.exists():
        return None
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"{path.name}.bak-{now_stamp()}"
    backup.write_bytes(path.read_bytes())
    return backup


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote Blue Star bid-resolution ledger decisions into production overlay artifacts.")
    parser.add_argument("--ledger", type=Path, help="Ledger JSONL path. Defaults to latest ledger.")
    parser.add_argument("--blue-star-root", type=Path, default=DEFAULT_BLUE_STAR_ROOT)
    parser.add_argument("--apply", action="store_true", help="Write artifacts into the Blue Star bid-intelligence wiki.")
    parser.add_argument("--out-dir", type=Path, help="Dry-run output dir. Defaults next to the ledger.")
    args = parser.parse_args()

    ledger = args.ledger or find_latest_ledger()
    if ledger is None:
        raise SystemExit(f"No ledger found under {OUTPUT_ROOT}")
    entries = read_jsonl(ledger)
    incoming = [decision_record(entry, ledger) for entry in entries]

    wiki_root = args.blue_star_root / "bid-intelligence" / "wiki"
    decision_path = wiki_root / DECISION_JSON
    backlog_path = wiki_root / BACKLOG_JSON
    existing_decisions = load_existing(decision_path, "decisions")
    decision_artifact = build_decision_artifact(existing_decisions, incoming, ledger)
    existing_backlog = load_existing(backlog_path, "items")
    backlog_artifact = build_backlog_artifact(existing_backlog, decision_artifact["decisions"], ledger)

    if args.apply:
        targets = {
            decision_path: decision_artifact,
            backlog_path: backlog_artifact,
        }
        backup_dir = ledger.parent / "promotion-backups"
        backups = [str(path) for path in (backup_if_exists(path, backup_dir) for path in targets) if path]
        write_json(decision_path, decision_artifact)
        (wiki_root / DECISION_MD).write_text(render_decision_md(decision_artifact), encoding="utf-8")
        write_json(backlog_path, backlog_artifact)
        (wiki_root / BACKLOG_MD).write_text(render_backlog_md(backlog_artifact), encoding="utf-8")
        result = {
            "mode": "apply",
            "ledger": str(ledger),
            "written": [str(wiki_root / name) for name in [DECISION_JSON, DECISION_MD, BACKLOG_JSON, BACKLOG_MD]],
            "backups": backups,
            "decisionSummary": decision_artifact["summary"],
            "backlogSummary": backlog_artifact["summary"],
        }
    else:
        out_dir = args.out_dir or ledger.parent / "promotion-dry-run"
        out_dir.mkdir(parents=True, exist_ok=True)
        write_json(out_dir / DECISION_JSON, decision_artifact)
        (out_dir / DECISION_MD).write_text(render_decision_md(decision_artifact), encoding="utf-8")
        write_json(out_dir / BACKLOG_JSON, backlog_artifact)
        (out_dir / BACKLOG_MD).write_text(render_backlog_md(backlog_artifact), encoding="utf-8")
        result = {
            "mode": "dry_run",
            "ledger": str(ledger),
            "written": [str(out_dir / name) for name in [DECISION_JSON, DECISION_MD, BACKLOG_JSON, BACKLOG_MD]],
            "decisionSummary": decision_artifact["summary"],
            "backlogSummary": backlog_artifact["summary"],
            "applyCommand": f"python3 scripts/blue_star/promote_bid_resolution.py --ledger {ledger} --apply",
        }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
