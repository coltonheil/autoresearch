# Ad Creative Loop — Program File

## Purpose

Run an iterative Meta Ads creative loop for Heil Ginseng. Each loop cycle generates one image variant and one copy variant, scores both against rubrics, keeps packages above threshold, discards the rest, and logs every result. Output is a ranked bench of draft creative packages ready for Ben review and Colton approval. Nothing auto-activates.

---

## Platform

- **Primary:** Meta Ads (Facebook + Instagram)
- **Pixel ID:** 1434396548313112
- **Formats:**
  - 1080×1080 (square — Feed, Marketplace)
  - 1080×1350 (portrait — Feed, Explore)
  - 1920×1080 (landscape — Audience Network, in-stream)
- **Placement default:** Square first, then portrait for Feed-priority runs.

---

## Visual Direction — David Protein Standard

David Protein is the benchmark aesthetic. Their creative is:
- **Editorial product-world scenes**: product lives in a purposefully composed environment (not floating on white)
- **Natural or studio-natural lighting**: soft directional light, no harsh flash, no over-processed HDR
- **Earth tones and organic palettes**: browns, greens, creams, muted golds — aligned with ginseng's natural origin
- **Negative space used intentionally**: product has room to breathe; background serves product
- **Clean but not sterile**: visual warmth and texture without clutter
- **No AI-generated humans**: zero exceptions. Product + environment + hands (real or props) only.
- **No stock photo look**: no generic "health wellness" clichés, no white-background supplement shots, no fake-outdoor composite look

Apply this direction to all Heil Ginseng creative. Farm-documentary and clinical supplement aesthetics are penalized.

---

## Asset Sources

Generated images and existing product photography both feed this loop.

### Existing product photography (use first)
```
~/.openclaw/workspace/outputs/ginseng-drive-assets/Capsules/
~/.openclaw/workspace/outputs/ginseng-drive-assets/Roots/
~/.openclaw/workspace/outputs/ginseng-drive-assets/Tea/
~/.openclaw/workspace/outputs/ginseng-drive-assets/Powder/
```

### AI-generated images
- Tool: Nano Banana Pro (`nano-banana-pro` skill)
- Output path: `~/.openclaw/workspace/outputs/autoresearch/ad-creative/<YYYY-MM-DD>/`
- Formats: 1K draft → score → if above threshold → 4K final
- Generation prompt must encode: no humans, David Protein visual direction, product + natural environment

### Enhancement candidates
- Source: existing drive assets
- Enhancement: crop, lighting adjustment, background simplification
- Use when existing photos are strong but need composition refinement

---

## Identity Lock Rules (Non-Negotiable)

These are hard constants for every future Heil ad-creative run. They override aesthetic preference, novelty, and weighted rubric score.

1. **Packaging identity must match real Heil packaging from approved source photos.**
2. **Ginseng roots must look morphologically realistic based on approved source photos.**

### Reference conditioning is mandatory

Every product generation must be conditioned on approved visual references. Each run must provide a `reference_manifest_path` that resolves to a manifest listing the exact approved packshots and root references for that product. The manifest template lives at:

`programs/reference-manifest.example.json`

If the run cannot load approved references, the run is incomplete and production candidates must not be generated.

### Generation mode hierarchy

Use the highest-fidelity mode available, in this exact order:

1. **Image edit / inpaint from a real Heil product photo** — preferred for production candidates.
2. **Multi-reference generation with mandatory packaging lock** — only if edit/inpaint is not viable.
3. **Text-only generation** — forbidden for production candidates. It may be used only for exploratory ideation, and every output from that mode is auto-discard unless later rebuilt with approved references.

### Per-product reference requirements

- **Capsules**
  - Minimum references: 1 approved front packshot and 1 secondary angle.
  - Must preserve: logo mark, bottle geometry, cap color/shape, label architecture, capsule color cues if visible.
- **Roots**
  - Minimum references: 1 approved packaging reference if packaging is shown, plus at least 2 real root morphology references.
  - Must preserve: root branching pattern realism, skin texture, taper, wrinkles, age cues, and any visible retail packaging identity.
- **Tea**
  - Minimum references: 1 approved front packshot and 1 secondary angle or lifestyle packshot.
  - Must preserve: tea box/pouch geometry, logo mark, label layout, colorway, sachet/carton architecture if visible.
- **Powder**
  - Minimum references: 1 approved front packshot and 1 secondary angle.
  - Must preserve: pouch/container silhouette, logo mark, label proportions, powder color realism, scoop/product appearance if shown.

### Auto-discard rules

Auto-discard the variant immediately if any of the following are true:

- Packaging identity drifts from the approved references.
- Logo mark changes, softens, disappears, or becomes generic.
- Package geometry changes from the approved SKU.
- Label architecture or colorway changes materially.
- A product requiring visible packaging presents blank, generic, or unreadable pseudo-packaging.
- Roots look synthetic, anatomically implausible, over-smoothed, or otherwise morphologically unrealistic.

A variant that fails either identity constant is a discard even if the composition, lighting, or scroll-stopping score is excellent.

---

## Campaign Brief Template

Each loop run opens with a brief. Fill before running:

```
product: [Capsules | Roots | Tea | Powder]
offer: [e.g., "starter pack", "free shipping >$30", seasonal hook]
angle: [e.g., energy/vitality, heritage/farm-origin, daily ritual, cognitive clarity]
audience: [e.g., health-conscious 35-55, TCM-aware, outdoor/active]
season: [e.g., winter wellness, spring energy, harvest]
max_variants: [integer, default 5]
keep_threshold_visual: 65
keep_threshold_copy: 65
format: [1080x1080 | 1080x1350 | 1920x1080 | all]
reference_manifest_path: [absolute or repo-relative path to approved references]
```

---

## Loop Architecture

```
OUTER LOOP (campaign brief)
  ├── load product brief
  ├── define angle + season + audience
  ├── define keep thresholds and max variants
  ├── load reference manifest for the selected product
  └── run inner loop up to max_variants times

INNER LOOP (autoresearch)
  1. Generate or select image variant using approved references
  2. Run identity lock validation against packaging/root references
  3. If packaging fidelity FAIL or root authenticity FAIL → DISCARD immediately, log, continue
  4. Score image against ad-creative-visual rubric
  5. If visual score < keep_threshold_visual → DISCARD immediately, log, continue
  6. Run compliance pre-scan (no AI humans, no prohibited claims in overlays)
  7. If compliance fail → DISCARD immediately, log reason
  8. Generate copy variant for this image (hook → benefit → CTA pattern)
  9. Score copy against ad-creative-copy rubric
  10. If copy score < keep_threshold_copy → DISCARD copy, log, try copy regen (max 2x)
  11. If copy score >= threshold AND visual score >= threshold AND identity lock PASS → KEEP package
  12. Log all scores and gate outcomes to results/ad-creative.tsv

OUTPUT
  - Ranked creative packages: image path + copy text + angle + format + composite score
  - Compliance pre-scan status per package
  - Identity-lock gate status per package
  - Discard log with reasons

GATES (mandatory, never skipped)
  - Ben reviews all kept variants before any promotion
  - Colton selects what moves forward
  - Nothing auto-activates
```

---

## Copy Framework: Hook → Benefit → CTA

Every ad copy variant follows this pattern:

```
HOOK (1-2 lines, ≤125 chars recommended)
Stop-scroll opener. Specific, not generic. Speaks to the audience's real motivation.
Examples:
  "4 generations of Wisconsin ginseng. One reason people keep coming back."
  "Your 3 PM slump just met its match."
  "Real roots. Tested. No fillers."

BENEFIT (2-4 lines)
One or two primary benefits. Specific > vague. No medical claims.
Examples:
  "American ginseng supports natural energy and mental clarity — the kind that doesn't crash."
  "Harvested on our family farm. Traceable from soil to shelf."

CTA (1 line)
Direct. Low friction.
  "Shop now → free shipping on orders over $30"
  "Get yours at heilginseng.com"
```

---

## Copy Compliance Rules (FDA/FTC Supplement Standards)

Hard discard triggers (any of these = immediate discard, no regen):
- "cures", "treats", "prevents", "heals" any disease or condition
- Claims about diagnosed conditions (diabetes, ADHD, cancer, anxiety disorder, etc.)
- "clinically proven" without a cited study
- Misleading urgency or fabricated scarcity
- Fake testimonials or implied endorsements without disclosure

Soft flag (note in log, Ben must review):
- "boosts immunity" (overused, FDA-sensitive)
- Comparatives like "stronger than" without substantiation
- Any claim linking ginseng to specific health outcomes that could be read as disease claims

Safe framing:
- "supports natural energy"
- "may support mental clarity"
- "harvested from our family farm"
- "traditional use in herbal wellness"
- "4th-generation Wisconsin ginseng"

---

## Keep / Discard Rules

| Condition | Action |
|---|---|
| Packaging Fidelity Gate = FAIL | Discard immediately, log exact drift reason |
| Root Authenticity Gate = FAIL | Discard immediately, log exact realism issue |
| Visual score >= 65 AND passes compliance AND identity lock gates pass | Keep image, proceed to copy scoring |
| Visual score < 65 | Discard immediately, log score + reason |
| Visual passes, copy score >= 65 | Keep package |
| Visual passes, copy score < 65 | Regen copy up to 2x; if still below threshold, discard package |
| Any compliance hard fail | Discard immediately, log specific violation |
| No AI humans rule violated | Discard immediately |
| Score improvement < 3pts visual vs prior variant of same brief | Flag as marginal; deprioritize in ranking |
| Score improvement < 2pts copy vs prior copy of same brief | Flag as marginal; deprioritize in ranking |

---

## Ranking Output Format

Kept packages are ranked descending by composite score (visual × 0.5 + copy × 0.5).

Output format per package:
```
RANK #1 — Composite: 82.5
  Image: outputs/autoresearch/ad-creative/2026-03-09/capsules-v003.png
  Format: 1080x1080
  Visual score: 84 | Copy score: 81
  Packaging Fidelity Gate: PASS
  Root Authenticity Gate: PASS
  Angle: daily ritual
  Hook: "Your 3 PM slump just met its match."
  Copy: [full copy text]
  CTA: "Shop now → heilginseng.com"
  Compliance: PASS
  Ben review: PENDING
  Colton approval: PENDING
```

---

## Iteration Loop Stops When

- `max_variants` kept packages reached, OR
- 3× consecutive discards on the same product+angle combination (angle likely exhausted), OR
- Manual stop

---

## Logging

Append every run (kept AND discarded) to:
```
~/repos/autoresearch/results/ad-creative.tsv
```

Schema:
```
run_id  timestamp_utc  campaign_name  platform  product_focus  angle  image_path  copy_path  format  baseline_score  variant_score  score_delta  visual_score  brand_fit_score  hook_score  benefit_score  cta_score  compliance_score  compliance_pass  no_ai_humans_pass  keep_decision  ben_review_status  colton_approval_status  ctr_delta  cpc_delta  cpa_delta  roas_delta  notes  rubric_version  commit_sha  branch
```

---

## Rubric Versions

- Visual rubric: `rubrics/ad-creative-visual.md` (current: v1.1)
- Copy rubric: `rubrics/ad-creative-copy.md` (current: v1.0)

Update version tag in TSV rows if rubric changes mid-experiment.

---

## Run Reporting

Write run summaries to the result log and run artifact directory.

Summary format:
```
🎨 Ad Creative Loop — [Product] [Date]
Ran [N] variants. Kept [K]. Discarded [D].
Top package: [angle] — Visual: [score] | Copy: [score] | Composite: [score]
[Image thumbnail if available]
Pending: Ben review before any promotion.
```

---

## Rubric Files
- `rubrics/ad-creative-visual.md`
- `rubrics/ad-creative-copy.md`

## Results File
- `results/ad-creative.tsv`

## Asset Output Path
- `~/.openclaw/workspace/outputs/autoresearch/ad-creative/<YYYY-MM-DD>/`

## Branch Convention
- `autoresearch/ad-creative-<yyyy-mm-dd>-r<nn>`
