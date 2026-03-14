#!/usr/bin/env python3
"""Score a PDP copy variant against the fixed rubric."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from openai import OpenAI

DEFAULT_MODEL = "gpt-4o"
DEFAULT_RUBRIC = Path("rubrics/pdp-cro.md")
WEIGHTS = {
    "clarity": 0.20,
    "benefit": 0.20,
    "trust": 0.20,
    "scanability": 0.15,
    "seo": 0.10,
    "cta": 0.05,
    "compliance": 0.10,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score a PDP copy variant using the fixed PDP CRO rubric.",
    )
    parser.add_argument("variant_file", type=Path, help="Path to the markdown variant file")
    parser.add_argument(
        "--rubric",
        type=Path,
        default=DEFAULT_RUBRIC,
        help="Path to rubric markdown file (default: rubrics/pdp-cro.md)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL})",
    )
    return parser.parse_args()


def load_text(path: Path, label: str) -> str:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    return path.read_text(encoding="utf-8")


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
    return OpenAI(api_key=api_key)


def build_prompt(rubric_text: str, variant_text: str) -> tuple[str, str]:
    system = (
        "You are a strict evaluator for supplement product detail page copy. "
        "Score only what is present in the copy. Stay conservative on compliance. "
        "If prohibited claims appear, set compliance to 0 and explain why."
    )
    user = f"""
Score this PDP copy variant using the exact rubric below.

Return JSON only with this shape:
{{
  "clarity": 0,
  "benefit": 0,
  "trust": 0,
  "scanability": 0,
  "seo": 0,
  "cta": 0,
  "compliance": 0,
  "discard_reasons": ["..."],
  "justifications": {{
    "clarity": "brief justification",
    "benefit": "brief justification",
    "trust": "brief justification",
    "scanability": "brief justification",
    "seo": "brief justification",
    "cta": "brief justification",
    "compliance": "brief justification"
  }}
}}

Rules:
- Each score must be an integer from 0 to 100.
- Use the rubric strictly.
- If compliance fails, set compliance to 0 and add at least one discard reason.
- Keep justifications brief.
- Do not include weighted total in the model output.

## Rubric
{rubric_text}

## Variant
{variant_text}
""".strip()
    return system, user


def request_scores(client: OpenAI, model: str, rubric_text: str, variant_text: str) -> dict[str, Any]:
    system, user = build_prompt(rubric_text, variant_text)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    payload = response.choices[0].message.content or ""
    return json.loads(payload)


def clamp_score(value: Any, name: str) -> int:
    if not isinstance(value, (int, float)):
        raise ValueError(f"Model returned non-numeric score for {name}: {value!r}")
    rounded = int(round(float(value)))
    return max(0, min(100, rounded))


def finalize_scores(raw: dict[str, Any]) -> dict[str, Any]:
    scores = {name: clamp_score(raw.get(name), name) for name in WEIGHTS}
    total = sum(scores[name] * weight for name, weight in WEIGHTS.items())
    discard_reasons = raw.get("discard_reasons") or []
    if not isinstance(discard_reasons, list):
        discard_reasons = [str(discard_reasons)]
    discard_reasons = [str(reason).strip() for reason in discard_reasons if str(reason).strip()]
    hard_fail = scores["compliance"] == 0
    if hard_fail and not discard_reasons:
        discard_reasons.append("Compliance score is 0, triggering hard fail.")
    return {
        "total": round(total, 2),
        **scores,
        "hard_fail": hard_fail,
        "discard_reasons": discard_reasons,
    }


def main() -> int:
    args = parse_args()
    try:
        rubric_text = load_text(args.rubric, "Rubric file")
        variant_text = load_text(args.variant_file, "Variant file")
        client = get_client()
        raw = request_scores(client, args.model, rubric_text, variant_text)
        result = finalize_scores(raw)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive API error handling
        print(f"OpenAI API error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
