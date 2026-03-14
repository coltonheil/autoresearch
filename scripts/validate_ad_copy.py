#!/usr/bin/env python3
"""Validate draft ad/email/social copy for Tier 2 compliance review."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from openai import OpenAI

DEFAULT_MODEL = "gpt-4o"
FDA_DISCLAIMER = (
    "These statements have not been evaluated by the Food and Drug Administration. "
    "This product is not intended to diagnose, treat, cure, or prevent any disease."
)
PROHIBITED_ACTIONS = [
    "cure", "cures", "cured", "treat", "treats", "treated", "prevent", "prevents", "prevents",
    "diagnose", "diagnoses", "diagnosed", "heal", "heals", "healed", "remedy", "remedies",
    "reverse", "reverses", "eliminate", "eliminates", "erase", "erases",
]
DISEASE_TERMS = [
    "cancer", "tumor", "diabetes", "heart disease", "cardiovascular disease", "stroke", "hypertension",
    "high blood pressure", "alzheimers", "alzheimer's", "dementia", "parkinsons", "parkinson's",
    "arthritis", "depression", "anxiety disorder", "covid", "covid-19", "flu", "influenza", "cold",
    "asthma", "copd", "obesity", "migraine", "insomnia", "erectile dysfunction", "ed", "kidney disease",
    "liver disease", "thyroid disease", "autoimmune disease", "pcos", "osteoporosis", "infection",
]
BORDERLINE_STRUCTURE_FUNCTION_PATTERNS = [
    r"boosts? (your )?(immune system|immunity)",
    r"supports? healthy blood sugar",
    r"lowers? cholesterol",
    r"reduces? inflammation",
    r"detox(ifies|es)?",
    r"balances? hormones",
    r"resets? metabolism",
    r"improves? circulation",
    r"fights? fatigue",
    r"crush(es)? stress",
    r"fix(es)? sleep",
    r"stops? pain",
]
BENEFIT_PATTERNS = [
    r"support(s|ive)?",
    r"wellness",
    r"energy",
    r"focus",
    r"vitality",
    r"immune",
    r"calm",
    r"stress",
    r"recovery",
    r"performance",
    r"sleep",
    r"digestion",
]
TESTIMONIAL_PATTERNS = [
    r'"[^"]+"',
    r"'[^']+'",
    r"\b(review|reviewed|testimonial|testimonials|customer said|customers say|rated \d)",
]
META_PERSONAL_ATTRIBUTES = [
    r"you look tired",
    r"are you overweight",
    r"your wrinkles",
    r"your age",
    r"you need to lose",
    r"struggling with",
    r"suffering from",
]
META_BEFORE_AFTER = [
    r"before and after",
    r"before/after",
    r"after just \d+",
    r"in only \d+ days",
    r"transform(ed|ation)",
]
MISLEADING_SOCIAL = [
    r"guaranteed",
    r"instant results",
    r"overnight",
    r"miracle",
    r"no risk",
    r"everyone",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate draft ad/email/social copy for compliance and brand voice.")
    parser.add_argument("copy_file", type=Path, help="Path to plain text or markdown copy file")
    parser.add_argument("--platform", required=True, choices=["meta", "google", "email", "social"], help="Target platform")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI model to use (default: {DEFAULT_MODEL})")
    return parser.parse_args()


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
    return OpenAI(api_key=api_key)


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Copy file not found: {path}")
    return path.read_text(encoding="utf-8")


def pass_result(details: str, **extra: Any) -> dict[str, Any]:
    return {"status": "PASS", "details": details, **extra}


def warn_result(details: str, **extra: Any) -> dict[str, Any]:
    return {"status": "WARN", "details": details, **extra}


def fail_result(details: str, **extra: Any) -> dict[str, Any]:
    return {"status": "FAIL", "details": details, **extra}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def find_matches(patterns: list[str], text: str) -> list[str]:
    matches: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            found = match.group(0).strip()
            if found and found not in matches:
                matches.append(found)
    return matches


def check_prohibited_disease_claims(text: str) -> dict[str, Any]:
    normalized = normalize(text)
    action_hits = find_matches([rf"\b{re.escape(term)}\b" for term in PROHIBITED_ACTIONS], normalized)
    disease_hits = find_matches([rf"\b{re.escape(term)}\b" for term in DISEASE_TERMS], normalized)
    paired_hits: list[str] = []
    windows = re.split(r"[.!?\n]", normalized)
    for window in windows:
        has_action = any(re.search(rf"\b{re.escape(term)}\b", window) for term in PROHIBITED_ACTIONS)
        has_disease = any(re.search(rf"\b{re.escape(term)}\b", window) for term in DISEASE_TERMS)
        if has_action and has_disease:
            paired_hits.append(window.strip())
    if paired_hits:
        return fail_result(
            "Potential disease-treatment claim detected.",
            action_terms=action_hits,
            disease_terms=disease_hits,
            excerpts=paired_hits[:5],
        )
    if action_hits and disease_hits:
        return warn_result(
            "Prohibited action verbs and disease terms both appear, but not in the same sentence.",
            action_terms=action_hits,
            disease_terms=disease_hits,
        )
    return pass_result("No explicit disease-treatment claim pattern detected.", action_terms=action_hits, disease_terms=disease_hits)


def check_structure_function_claims(client: OpenAI, model: str, text: str, platform: str) -> dict[str, Any]:
    heuristic_hits = find_matches(BORDERLINE_STRUCTURE_FUNCTION_PATTERNS, text)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a conservative FDA/FTC copy reviewer for dietary supplement marketing. "
                    "Flag claims that go beyond acceptable structure-function language. Return JSON only."
                ),
            },
            {
                "role": "user",
                "content": f"""
Review this {platform} copy for unapproved structure-function or efficacy claims.

Return JSON only with:
{{
  "risk_level": "PASS|WARN|FAIL",
  "flagged_claims": ["..."],
  "reasoning": "brief explanation"
}}

Copy:
{text}
""".strip(),
            },
        ],
    )
    payload = json.loads(response.choices[0].message.content or "{}")
    risk = str(payload.get("risk_level", "WARN")).upper()
    flagged = payload.get("flagged_claims") or []
    if not isinstance(flagged, list):
        flagged = [str(flagged)]
    flagged = [str(item).strip() for item in flagged if str(item).strip()]
    flagged = list(dict.fromkeys(heuristic_hits + flagged))
    reasoning = str(payload.get("reasoning", "")).strip() or "No reasoning provided."
    if risk == "FAIL":
        return fail_result(f"Unapproved claims detected. {reasoning}", flagged_claims=flagged)
    if risk == "WARN" or heuristic_hits:
        return warn_result(f"Borderline structure-function claims may need revision. {reasoning}", flagged_claims=flagged)
    return pass_result(f"No unapproved structure-function claims flagged. {reasoning}", flagged_claims=flagged)


def check_disclaimer(text: str) -> dict[str, Any]:
    normalized = normalize(text)
    benefit_hits = find_matches(BENEFIT_PATTERNS, normalized)
    has_disclaimer = normalize(FDA_DISCLAIMER) in normalized
    if benefit_hits and not has_disclaimer:
        return warn_result(
            "Benefit language appears without the standard FDA disclaimer.",
            benefit_terms=benefit_hits,
            disclaimer_needed=True,
        )
    if benefit_hits and has_disclaimer:
        return pass_result("Benefit language is paired with the FDA disclaimer.", benefit_terms=benefit_hits)
    return pass_result("No obvious health/wellness benefit language requiring disclaimer review detected.", benefit_terms=benefit_hits)


def check_testimonials(text: str) -> dict[str, Any]:
    hits = find_matches(TESTIMONIAL_PATTERNS, text)
    if hits:
        return warn_result(
            "Testimonial-style language detected. Typical-results disclosure may be needed.",
            matches=hits[:10],
        )
    return pass_result("No testimonial-style language detected.")


def check_platform_rules(text: str, platform: str) -> dict[str, Any]:
    if platform == "meta":
        before_after = find_matches(META_BEFORE_AFTER, text)
        personal = find_matches(META_PERSONAL_ATTRIBUTES, text)
        if before_after or personal:
            return fail_result(
                "Meta policy risk detected.",
                before_after=before_after,
                personal_attributes=personal,
            )
        return pass_result("No obvious Meta personal-attribute or before/after violations detected.")
    if platform == "email":
        lower = normalize(text)
        has_unsubscribe = "unsubscribe" in lower or "opt out" in lower
        has_address = bool(re.search(r"\b(road|rd\.?|street|st\.?|avenue|ave\.?|suite|ste\.?|po box|wisconsin|wi\b)\b", lower))
        if not has_unsubscribe or not has_address:
            return warn_result(
                "Email copy may be missing CAN-SPAM elements.",
                unsubscribe_present=has_unsubscribe,
                physical_address_present=has_address,
            )
        return pass_result("Email copy includes basic CAN-SPAM markers.", unsubscribe_present=has_unsubscribe, physical_address_present=has_address)
    if platform == "social":
        misleading = find_matches(MISLEADING_SOCIAL, text)
        if misleading:
            return warn_result("Potentially misleading social claims detected.", matches=misleading)
        return pass_result("No obvious misleading social claims detected.")
    return pass_result("No additional platform-specific rule set configured for this platform.")


def check_brand_voice(client: OpenAI, model: str, text: str, platform: str) -> dict[str, Any]:
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are evaluating Heil Ginseng brand voice. The right tone is confident without hype, "
                    "farm-specific not generic, and Wisconsin grit rather than clinical supplement jargon. Return JSON only."
                ),
            },
            {
                "role": "user",
                "content": f"""
Score this {platform} copy for Heil brand voice.

Return JSON only with:
{{
  "voice_score": 0,
  "fits_brand": true,
  "reasoning": "brief explanation"
}}

Copy:
{text}
""".strip(),
            },
        ],
    )
    payload = json.loads(response.choices[0].message.content or "{}")
    score = max(0, min(100, int(round(float(payload.get("voice_score", 0))))))
    reasoning = str(payload.get("reasoning", "")).strip() or "No reasoning provided."
    if score < 60:
        return warn_result(f"Brand voice scored {score}/100. {reasoning}", voice_score=score)
    return pass_result(f"Brand voice scored {score}/100. {reasoning}", voice_score=score)


def main() -> int:
    args = parse_args()
    try:
        text = load_text(args.copy_file)
        client = get_client()
        results = {
            "copy_file": str(args.copy_file),
            "platform": args.platform,
            "checks": {
                "prohibited_disease_claims": check_prohibited_disease_claims(text),
                "structure_function_claims": check_structure_function_claims(client, args.model, text, args.platform),
                "required_disclaimer": check_disclaimer(text),
                "testimonial_rules": check_testimonials(text),
                "platform_rules": check_platform_rules(text, args.platform),
                "brand_voice": check_brand_voice(client, args.model, text, args.platform),
            },
        }
    except (FileNotFoundError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"OpenAI API error: {exc}", file=sys.stderr)
        return 1

    statuses = [check["status"] for check in results["checks"].values()]
    results["summary"] = {
        "fail_count": sum(1 for status in statuses if status == "FAIL"),
        "warn_count": sum(1 for status in statuses if status == "WARN"),
        "pass_count": sum(1 for status in statuses if status == "PASS"),
        "overall_status": "FAIL" if "FAIL" in statuses else ("WARN" if "WARN" in statuses else "PASS"),
    }
    print(json.dumps(results, indent=2))
    return 1 if results["summary"]["fail_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
