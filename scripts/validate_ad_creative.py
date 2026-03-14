#!/usr/bin/env python3
"""Validate draft ad creative assets for Tier 2 review packaging."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, Sequence

from openai import OpenAI
from PIL import Image, ImageFilter

DEFAULT_MODEL = "gpt-4o"
MIN_WIDTH = 1080
MIN_HEIGHT = 1080
WARN_FILE_SIZE_MB = 10
FAIL_FILE_SIZE_MB = 30
STANDARD_ASPECTS = {
    "1:1 (feed)": 1 / 1,
    "9:16 (story/reel)": 9 / 16,
    "4:5 (feed portrait)": 4 / 5,
    "16:9 (landscape)": 16 / 9,
}
ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}
PRODUCT_TYPES = ("capsules", "roots", "tea", "powder")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a draft ad image before it enters the review package.",
    )
    parser.add_argument("image_path", type=Path, help="Path to PNG/JPG/WebP image")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use for vision checks (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--reference-image",
        dest="reference_images",
        type=Path,
        action="append",
        default=[],
        help="Reference image path. Repeat to provide multiple approved packaging/root references.",
    )
    parser.add_argument(
        "--product-type",
        choices=PRODUCT_TYPES,
        help="Product type for identity validation. Required when --strict-identity is enabled.",
    )
    parser.add_argument(
        "--strict-identity",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Hard fail when packaging/root identity gates fail. Enabled by default.",
    )
    return parser.parse_args()


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
    return OpenAI(api_key=api_key)


def pass_result(details: str, **extra: Any) -> dict[str, Any]:
    return {"status": "PASS", "details": details, **extra}


def warn_result(details: str, **extra: Any) -> dict[str, Any]:
    return {"status": "WARN", "details": details, **extra}


def fail_result(details: str, **extra: Any) -> dict[str, Any]:
    return {"status": "FAIL", "details": details, **extra}


def image_to_data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def vision_json(
    client: OpenAI,
    model: str,
    prompt: str,
    image_paths: Sequence[Path],
    schema_hint: str,
) -> dict[str, Any]:
    content: list[dict[str, Any]] = [
        {"type": "text", "text": prompt + "\n\nReturn JSON only matching this shape:\n" + schema_hint}
    ]
    for image_path in image_paths:
        content.append({"type": "image_url", "image_url": {"url": image_to_data_url(image_path)}})

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict creative safety reviewer for dietary supplement ad drafts. "
                    "Be conservative. Return valid JSON only."
                ),
            },
            {"role": "user", "content": content},
        ],
    )
    payload = response.choices[0].message.content or "{}"
    return json.loads(payload)


def classify_aspect_ratio(width: int, height: int) -> tuple[str, float]:
    ratio = width / height
    best_name = "non-standard"
    best_delta = float("inf")
    for name, target in STANDARD_ASPECTS.items():
        delta = abs(ratio - target)
        if delta < best_delta:
            best_name = name
            best_delta = delta
    if best_delta <= 0.03:
        return best_name, ratio
    return "non-standard", ratio


def estimate_text_coverage(image: Image.Image) -> dict[str, Any]:
    thumbnail = image.copy()
    thumbnail.thumbnail((512, 512))
    gray = thumbnail.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    binary = edges.point(lambda p: 255 if p > 40 else 0)
    buffer = BytesIO()
    binary.save(buffer, format="PNG")
    pixels = list(binary.getdata())
    coverage = sum(1 for p in pixels if p > 0) / max(1, len(pixels))
    return {
        "coverage_estimate": round(coverage, 4),
        "percent_estimate": round(coverage * 100, 2),
    }


def validate_file(image_path: Path) -> tuple[dict[str, Any], Image.Image]:
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    try:
        with Image.open(image_path) as img:
            img.verify()
        image = Image.open(image_path)
        image.load()
    except Exception as exc:
        raise ValueError(f"File is not a valid image: {exc}") from exc

    fmt = (image.format or "").upper()
    if fmt not in ALLOWED_FORMATS:
        raise ValueError(f"Unsupported image format {fmt!r}. Allowed: PNG, JPEG, WEBP")
    return pass_result(f"Opened {fmt} image successfully.", format=fmt), image


def validate_reference_images(reference_images: Sequence[Path]) -> dict[str, Any]:
    missing = [str(path) for path in reference_images if not path.exists()]
    if missing:
        return fail_result("One or more reference images do not exist.", missing_paths=missing)
    if not reference_images:
        return warn_result("No reference images supplied.")
    return pass_result(
        f"Loaded {len(reference_images)} reference image(s).",
        reference_images=[str(path) for path in reference_images],
    )


def evaluate_resolution(width: int, height: int) -> dict[str, Any]:
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return fail_result(
            f"Resolution {width}x{height} is below the minimum {MIN_WIDTH}x{MIN_HEIGHT}.",
            width=width,
            height=height,
        )
    return pass_result(f"Resolution {width}x{height} meets minimum size.", width=width, height=height)


def evaluate_aspect_ratio(width: int, height: int) -> dict[str, Any]:
    classification, ratio = classify_aspect_ratio(width, height)
    rounded = round(ratio, 4)
    if classification == "non-standard":
        return warn_result(
            f"Aspect ratio {rounded} is non-standard for Meta placements.",
            aspect_ratio=rounded,
            classification=classification,
        )
    return pass_result(
        f"Aspect ratio classified as {classification}.",
        aspect_ratio=rounded,
        classification=classification,
    )


def evaluate_file_size(image_path: Path) -> dict[str, Any]:
    size_mb = image_path.stat().st_size / (1024 * 1024)
    if size_mb > FAIL_FILE_SIZE_MB:
        return fail_result(f"File size {size_mb:.2f}MB exceeds Meta's 30MB limit.", size_mb=round(size_mb, 2))
    if size_mb > WARN_FILE_SIZE_MB:
        return warn_result(f"File size {size_mb:.2f}MB is larger than the recommended 10MB.", size_mb=round(size_mb, 2))
    return pass_result(f"File size {size_mb:.2f}MB is within the recommended range.", size_mb=round(size_mb, 2))


def evaluate_ai_humans(client: OpenAI, model: str, image_path: Path) -> dict[str, Any]:
    prompt = (
        "Does this image contain any AI-generated human faces, human bodies, or human figures? "
        "Answer YES or NO and explain briefly. If you are unsure, answer YES. "
        "Return JSON with keys: answer, confidence, explanation."
    )
    result = vision_json(
        client,
        model,
        prompt,
        [image_path],
        '{"answer":"YES or NO","confidence":"high|medium|low","explanation":"brief explanation"}',
    )
    answer = str(result.get("answer", "")).strip().upper()
    explanation = str(result.get("explanation", "")).strip() or "No explanation provided."
    confidence = str(result.get("confidence", "")).strip().lower() or "unknown"
    if answer == "YES":
        return fail_result(
            f"Potential AI-generated human detected: {explanation}",
            answer=answer,
            confidence=confidence,
        )
    if answer != "NO":
        return fail_result(
            f"Vision model returned an invalid AI-human decision: {answer or 'empty'}.",
            raw=result,
        )
    return pass_result(f"No AI-generated humans detected. {explanation}", answer=answer, confidence=confidence)


def evaluate_brand_fit(client: OpenAI, model: str, image_path: Path) -> dict[str, Any]:
    prompt = (
        "Score this draft ad image from 0-100 on: product_prominence, david_protein_editorial_fit, and text_legibility. "
        "The target is a clean, premium, product-world scene. It should not feel farm-documentary or clinical supplement. "
        "Also return overall_score, verdict, and short reasoning."
    )
    result = vision_json(
        client,
        model,
        prompt,
        [image_path],
        '{"product_prominence":0,"david_protein_editorial_fit":0,"text_legibility":0,"overall_score":0,"verdict":"PASS or WARN","reasoning":"brief"}',
    )
    scores = {
        key: max(0, min(100, int(round(float(result.get(key, 0))))))
        for key in ["product_prominence", "david_protein_editorial_fit", "text_legibility", "overall_score"]
    }
    reasoning = str(result.get("reasoning", "")).strip() or "No reasoning provided."
    if scores["overall_score"] < 50:
        return warn_result(
            f"Brand-fit pre-screen scored {scores['overall_score']}/100. {reasoning}",
            **scores,
        )
    return pass_result(f"Brand-fit pre-screen scored {scores['overall_score']}/100. {reasoning}", **scores)


def evaluate_text_overlay(client: OpenAI, model: str, image_path: Path, image: Image.Image) -> dict[str, Any]:
    heuristic = estimate_text_coverage(image)
    prompt = (
        "Estimate what percent of the image area appears to be occupied by text or text overlays. "
        "Return JSON with text_area_percent (0-100), text_heaviness (light|moderate|heavy), and reasoning."
    )
    result = vision_json(
        client,
        model,
        prompt,
        [image_path],
        '{"text_area_percent":0,"text_heaviness":"light|moderate|heavy","reasoning":"brief"}',
    )
    try:
        percent = max(0.0, min(100.0, float(result.get("text_area_percent", 0.0))))
    except (TypeError, ValueError):
        percent = 0.0
    heaviness = str(result.get("text_heaviness", "unknown")).strip().lower() or "unknown"
    reasoning = str(result.get("reasoning", "")).strip() or "No reasoning provided."
    details = (
        f"Vision estimated text coverage at {percent:.1f}% ({heaviness}). "
        f"Heuristic edge-density estimate: {heuristic['percent_estimate']:.1f}%. {reasoning}"
    )
    if percent > 20:
        return warn_result(details, text_area_percent=round(percent, 1), text_heaviness=heaviness, heuristic=heuristic)
    return pass_result(details, text_area_percent=round(percent, 1), text_heaviness=heaviness, heuristic=heuristic)


def evaluate_packaging_fidelity(
    client: OpenAI,
    model: str,
    image_path: Path,
    reference_images: Sequence[Path],
    product_type: str | None,
    strict_identity: bool,
) -> dict[str, Any]:
    if not strict_identity:
        return warn_result("Strict identity disabled; packaging fidelity gate is advisory only.")
    if not product_type:
        return fail_result("--product-type is required when --strict-identity is enabled.")
    if not reference_images:
        return fail_result(
            "Strict identity requires at least one --reference-image for packaging comparison.",
            product_type=product_type,
        )

    prompt = f"""
You are evaluating packaging fidelity for a Heil Ginseng production candidate.
Image order:
1) Candidate ad image
2+) Approved reference images for the same product

Product type: {product_type}
Task:
- Determine whether visible Heil packaging in the candidate preserves the real approved identity from the references.
- Focus on logo mark, package geometry, label architecture, colorway, cap/lid/bag form, and whether the package reads as the same real SKU.
- If product packaging is visible but genericized, blank, relabeled, wrong colorway, wrong proportions, or different geometry, FAIL.
- If the product type normally requires visible packaging in this concept and the candidate hides or blanks it, FAIL.
- WARN only for minor ambiguity such as glare or partial occlusion that does not clearly change identity.
- PASS only when brand identity alignment is exact enough for production.
Return JSON with keys:
status: PASS|WARN|FAIL
visible_packaging: yes|no
score: 0-100
reason: brief explanation
fail_conditions: array of triggered fail conditions or empty array
must_preserve_elements: array of concrete identity elements seen in the references
""".strip()
    result = vision_json(
        client,
        model,
        prompt,
        [image_path, *reference_images],
        '{"status":"PASS|WARN|FAIL","visible_packaging":"yes|no","score":0,"reason":"brief","fail_conditions":[],"must_preserve_elements":[]}',
    )
    status = normalize_status(result.get("status"))
    score = clamp_score(result.get("score"))
    reason = str(result.get("reason", "")).strip() or "No explanation provided."
    visible_packaging = str(result.get("visible_packaging", "unknown")).strip().lower() or "unknown"
    fail_conditions = normalize_string_list(result.get("fail_conditions"))
    must_preserve_elements = normalize_string_list(result.get("must_preserve_elements"))

    details = f"Packaging fidelity {status} at {score}/100. {reason}"
    payload = {
        "score": score,
        "visible_packaging": visible_packaging,
        "fail_conditions": fail_conditions,
        "must_preserve_elements": must_preserve_elements,
        "product_type": product_type,
        "reference_images": [str(path) for path in reference_images],
    }
    if status == "FAIL":
        return fail_result(details, **payload)
    if status == "WARN":
        return warn_result(details, **payload)
    return pass_result(details, **payload)


def evaluate_root_authenticity(
    client: OpenAI,
    model: str,
    image_path: Path,
    reference_images: Sequence[Path],
    product_type: str | None,
    strict_identity: bool,
) -> dict[str, Any]:
    if not strict_identity:
        return warn_result("Strict identity disabled; root authenticity gate is advisory only.")
    if not product_type:
        return fail_result("--product-type is required when --strict-identity is enabled.")

    prompt = f"""
You are evaluating American ginseng root authenticity for a Heil Ginseng production candidate.
Image order:
1) Candidate ad image
2+) Approved reference images, which may include real roots and/or packaging

Product type: {product_type}
Task:
- First decide whether roots are visibly present in the candidate.
- If product_type is roots, evaluate root authenticity regardless.
- If visible roots are present for any product type, evaluate realism of morphology, surface texture, branching, taper, wrinkles, age cues, and overall natural believability.
- PASS only if the roots look morphologically realistic and consistent with real American ginseng.
- FAIL if roots look plastic, overly smooth, anatomically implausible, wrongly branched, cartoonish, or otherwise synthetic.
- If no roots are visible and product_type is not roots, return PASS with roots_visible=no and note that the gate was not applicable.
Return JSON with keys:
status: PASS|WARN|FAIL
roots_visible: yes|no
score: 0-100
reason: brief explanation
fail_conditions: array
observed_traits: array
""".strip()
    result = vision_json(
        client,
        model,
        prompt,
        [image_path, *reference_images],
        '{"status":"PASS|WARN|FAIL","roots_visible":"yes|no","score":0,"reason":"brief","fail_conditions":[],"observed_traits":[]}',
    )
    status = normalize_status(result.get("status"))
    score = clamp_score(result.get("score"))
    reason = str(result.get("reason", "")).strip() or "No explanation provided."
    roots_visible = str(result.get("roots_visible", "unknown")).strip().lower() or "unknown"
    fail_conditions = normalize_string_list(result.get("fail_conditions"))
    observed_traits = normalize_string_list(result.get("observed_traits"))

    if product_type != "roots" and roots_visible == "no" and status == "PASS":
        reason = f"{reason} Gate not applicable because no roots are visible in the candidate."

    details = f"Root authenticity {status} at {score}/100. {reason}"
    payload = {
        "score": score,
        "roots_visible": roots_visible,
        "fail_conditions": fail_conditions,
        "observed_traits": observed_traits,
        "product_type": product_type,
        "reference_images": [str(path) for path in reference_images],
    }
    if status == "FAIL":
        return fail_result(details, **payload)
    if status == "WARN":
        return warn_result(details, **payload)
    return pass_result(details, **payload)


def normalize_status(value: Any) -> str:
    status = str(value or "").strip().upper()
    return status if status in {"PASS", "WARN", "FAIL"} else "FAIL"


def clamp_score(value: Any) -> int:
    try:
        return max(0, min(100, int(round(float(value)))))
    except (TypeError, ValueError):
        return 0


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned = []
    for item in value:
        text = str(item).strip()
        if text:
            cleaned.append(text)
    return cleaned


def main() -> int:
    args = parse_args()
    try:
        if args.strict_identity and not args.product_type:
            raise ValueError("--product-type is required when --strict-identity is enabled.")
        if args.product_type and args.product_type not in PRODUCT_TYPES:
            raise ValueError(f"Unsupported --product-type {args.product_type!r}.")

        client = get_client()
        file_check, image = validate_file(args.image_path)
        reference_file_check = validate_reference_images(args.reference_images)
        width, height = image.size
        results = {
            "image_path": str(args.image_path),
            "product_type": args.product_type,
            "strict_identity": args.strict_identity,
            "reference_images": [str(path) for path in args.reference_images],
            "checks": {
                "file_valid": file_check,
                "reference_images": reference_file_check,
                "minimum_resolution": evaluate_resolution(width, height),
                "aspect_ratio": evaluate_aspect_ratio(width, height),
                "file_size": evaluate_file_size(args.image_path),
                "ai_humans": evaluate_ai_humans(client, args.model, args.image_path),
                "brand_fit": evaluate_brand_fit(client, args.model, args.image_path),
                "packaging_fidelity": evaluate_packaging_fidelity(
                    client,
                    args.model,
                    args.image_path,
                    args.reference_images,
                    args.product_type,
                    args.strict_identity,
                ),
                "root_authenticity": evaluate_root_authenticity(
                    client,
                    args.model,
                    args.image_path,
                    args.reference_images,
                    args.product_type,
                    args.strict_identity,
                ),
                "text_overlay": evaluate_text_overlay(client, args.model, args.image_path, image),
            },
        }
    except (FileNotFoundError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"OpenAI API error: {exc}", file=sys.stderr)
        return 1

    statuses = [check["status"] for check in results["checks"].values()]
    hard_identity_fails = [
        name
        for name in ("packaging_fidelity", "root_authenticity")
        if results["checks"][name]["status"] == "FAIL"
    ]
    overall_status = "FAIL" if "FAIL" in statuses else ("WARN" if "WARN" in statuses else "PASS")
    if args.strict_identity and hard_identity_fails:
        overall_status = "FAIL"

    results["summary"] = {
        "fail_count": sum(1 for status in statuses if status == "FAIL"),
        "warn_count": sum(1 for status in statuses if status == "WARN"),
        "pass_count": sum(1 for status in statuses if status == "PASS"),
        "strict_identity": args.strict_identity,
        "identity_fail_checks": hard_identity_fails,
        "overall_status": overall_status,
    }
    print(json.dumps(results, indent=2))
    return 1 if overall_status == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
