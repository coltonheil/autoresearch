#!/usr/bin/env python3
"""Generate a single focused PDP copy variant from a baseline."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from openai import OpenAI

DEFAULT_MODEL = "gpt-4o"
DEFAULT_PROGRAM = Path("programs/pdp-copy.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate one focused PDP copy variant from the current baseline.",
    )
    parser.add_argument("baseline_file", type=Path, help="Path to baseline markdown file")
    parser.add_argument("output_path", type=Path, help="Where to save the generated variant markdown")
    parser.add_argument(
        "--program",
        type=Path,
        default=DEFAULT_PROGRAM,
        help="Path to program markdown file (default: programs/pdp-copy.md)",
    )
    parser.add_argument(
        "--focus",
        default="",
        help="Optional rubric area to improve, such as scanability, trust, or seo",
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


def build_prompt(program_text: str, baseline_text: str, focus: str) -> tuple[str, str]:
    focus_line = f"Requested focus area: {focus}" if focus else "Requested focus area: choose the single highest-leverage improvement yourself."
    system = (
        "You write compliant, conversion-oriented draft product page copy for a supplement brand. "
        "Follow the program exactly. Preserve locked fields. Make one primary change only. "
        "Return markdown only."
    )
    user = f"""
Create one new PDP copy variant from the baseline below.

Requirements:
- Preserve the one-change discipline from the program.
- Rewrite the editable fields as a complete replacement set: description, bullets, FAQ, trust copy, meta title, meta description.
- Keep the variant draft-only and compliant.
- Include a `## Change Summary` section at the top that explains what changed and why.
- Keep locked fields untouched and do not imply changing them.
- Output markdown only, ready to save as the variant file.

{focus_line}

## Program
{program_text}

## Baseline
{baseline_text}
""".strip()
    return system, user


def generate_variant(client: OpenAI, model: str, program_text: str, baseline_text: str, focus: str) -> str:
    system, user = build_prompt(program_text, baseline_text, focus)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise ValueError("Model returned an empty variant.")
    return text + "\n"


def main() -> int:
    args = parse_args()
    try:
        baseline_text = load_text(args.baseline_file, "Baseline file")
        program_text = load_text(args.program, "Program file")
        client = get_client()
        variant = generate_variant(client, args.model, program_text, baseline_text, args.focus)
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text(variant, encoding="utf-8")
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive API error handling
        print(f"OpenAI API error: {exc}", file=sys.stderr)
        return 1

    print(str(args.output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
