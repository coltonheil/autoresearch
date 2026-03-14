# Ad Creative Capsules Branch — 2026-03-12

## Objective

Generate a capsules-only Heil Ginseng ad-creative branch that preserves the real capsules bottle identity under strict validation while exploring premium David Protein style product-world scenes.

This branch is draft-only. Nothing publishes, promotes, or activates.

## Product Scope

- Product: Heil Ginseng Capsules
- SKU identity: locked to the approved capsules bottle references in `programs/reference-manifest.json`
- Output cap: 24 total generated images across pilot + final

## Non-Negotiable Rules

1. The visible bottle must remain unmistakably the real Heil Ginseng capsules SKU.
2. Preserve logo mark, amber bottle silhouette, cap shape/color, label architecture, earthy colorway, and front-label proportions from approved references.
3. Treat the input product photo as an identity anchor, not inspiration.
4. Change environment, lighting, crop, and props only enough to create premium editorial ad creative.
5. No AI humans, faces, bodies, or hands.
6. No generic supplement packaging, blank labels, relabeling, fake logos, duplicate bottles, or packaging simplification.
7. No visible loose roots unless root references are loaded and the root gate passes.
8. If roots are omitted, validation should still pass through packaging fidelity and no-humans gates.
9. Minimum deliverable resolution must satisfy `validate_ad_creative.py` under strict identity.
10. Total generated images for this branch must stay within 1..24 inclusive.

## Reference Requirements

Load the capsules references from `programs/reference-manifest.json`:
- Primary front packshot
- Secondary angle packshot

Use the primary packshot as the edit anchor for generation.
Use both references for validation.

## Pilot Strategy

Run a small capsules-only pilot with multiple environment-only restyles:
- warm stone tabletop
- linen morning light
- dark apothecary shelf
- ceramic capsule dish scene
- restrained flat lay
- walnut editorial surface
- soft window ledge
- low-prop premium ritual setup

Pilot goal: identify which prompts preserve packaging identity best while keeping the bottle large, upright, and label-forward.

## Final Strategy

Promote the strongest prompt patterns from pilot into final generation.
Favor prompt edits that:
- keep the bottle dominant in frame
- explicitly forbid packaging drift
- avoid roots unless references are intentionally loaded
- simplify props and reduce clutter
- maintain premium David Protein editorial lighting

## Validation Gate

Every generated image must receive a matching validation JSON using:

```bash
scripts/validate_ad_creative.py --strict-identity --product-type capsules --reference-image ...
```

Hard discard conditions:
- packaging fidelity FAIL
- AI humans FAIL
- minimum resolution FAIL
- missing validation artifact

## Required Artifacts

Write outputs to:
`~/.openclaw/workspace/outputs/autoresearch/ad-creative/2026-03-12-capsules-branch/`

Required artifacts:
- `scorecard.md`
- `top-8.md`
- `preview/` with top 4 copied images
- `run-summary.json`

## Reporting Metrics

Report at minimum:
- total generated
- identity pass rate
- packaging-fidelity fail count
- no-humans fail count
- kept/discarded
- top failure reasons
- 3 concrete prompt changes that improved capsules fidelity
