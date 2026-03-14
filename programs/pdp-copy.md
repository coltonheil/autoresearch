# PDP Copy Optimization Loop

## Purpose

Run one autoresearch iteration for the Heil Ginseng Capsules product page using the upstream karpathy/autoresearch pattern:

```
LOOP:
  1. change ONE element of the copy
  2. score the variant with rubrics/pdp-cro.md
  3. if score > baseline + 2 → KEEP (becomes new baseline)
  4. if score <= baseline + 2 or compliance fails → DISCARD
  5. repeat up to 5 variants per run
```

This program is for draft-generation and evaluation only. It does not publish, sync, or write anything to live Shopify.

---

## Operating mode

**DRAFT ONLY.**

Nothing in this loop may modify the live storefront, Shopify admin, theme files, product data, or third-party apps. The output of each run is a set of markdown drafts plus a keep/discard recommendation.

---

## Target product

- Product: **American Ginseng Capsules 500mg**
- Shopify product ID: **7630033420384**
- Shopify handle: `american-ginseng-capsules-500mg`
- Current price: **$15.99** (compare-at: $19.99)
- Count: **60 capsules** (30 servings at 2 caps/day, or 60 days at 1 cap/day)
- Product URL: <https://heilginseng.com/products/american-ginseng-capsules-500mg>
- Primary keyword: **american ginseng capsules**
- Brand voice: **confident, specific, farm-proud, Wisconsin grit, not clinical, not hype-y**

---

## Current live copy snapshot (as of 2026-03-09)

The live PDP title is "Premium American Ginseng Capsules (500mg, 60ct)". Key content blocks:

- **Hero paragraph:** Opens with historical framing ("has been treasured for centuries"). Product identity is delayed behind backstory.
- **Sourcing Promise section:** Strong — mentions Edgar, WI, glacial soil, 100+ year farm, high ginsenoside levels.
- **Quality You Can Trust section:** Third-party testing for heavy metals, pesticides, purity. No fillers. Good.
- **Trust badge bar:** GBW Certified, Wisconsin Grown (95% of US ginseng), Lab Tested, Family Farm (4 Generations).
- **Supplement Facts panel:** 1,000mg American Ginseng Root Extract per 2-capsule serving.
- **Accordion sections:** How to Use, Ingredients & Testing, Where It Comes From.
- **Subscribe & Save block:** 10% off, flexible cadence, cancel anytime.
- **Guarantee block:** 30-day money-back, even if opened.
- **FAQs (JSON-LD):** 5 questions covering dosage, ingredients, vegan status, bottle duration, timing.
- **FDA disclaimer:** Present in footer of body_html.

**Identified weaknesses for optimization:**
1. Hero opening is historical rather than product-clear. First-time shoppers must read a full paragraph before understanding what is being sold.
2. The trust badge bar is strong but buried mid-page — not above the fold on mobile.
3. "Subscribe & Save" block is informational but not conversion-optimized.
4. CTA support near the buy box is thin — no price anchoring, no urgency, no guarantee visible near the add-to-cart button.
5. Benefit bullets are absent from above-the-fold content. Benefits are prose, not scannable bullets.

---

## Target audience

The primary buyer for Capsules is:

- **Health-conscious adult (35–65)** who wants a daily supplement they can trust
- Curious about traditional/natural wellness but skeptical of supplement hype
- Values origin, purity, and clean ingredients over trend labels
- May have seen ginseng referenced in traditional Asian or indigenous practice and wants an authentic source
- Finds capsule format appealing because it removes prep — no tea brewing, no measuring powder
- Price-sensitive: $15.99 is an accessible entry point, especially with a 60-count bottle
- Likely mobile shopper — first visit often via Meta or Google ads, may return via email

**Secondary buyers:**
- Gift buyers looking for a credible, farm-direct supplement for a family member
- Existing Roots or Tea customers moving to capsule convenience

---

## Ginseng grades context

Heil Ginseng uses the canonical 6 American ginseng root grades. Copy should reference grade quality where it naturally strengthens trust or helps explain capsule sourcing — but never in a way that implies capsules use inferior material.

**Canonical 6 grades (best to smallest):**
1. **Humanoid** — largest, most irregular, most prized; rare
2. **Bullet** — round, dense, premium grade
3. **Standard Large** — common commercial grade, strong ginsenoside profile
4. **Standard Medium** — mid-tier commercial grade
5. **Standard Small** — entry commercial grade
6. **Pencil** — thin, small, least valued

**How to reference grades in Capsules copy:**
- Safe: "Made from quality-grade American ginseng root powder, sourced from our own Wisconsin farm."
- Safe: "The same roots we grow and grade on the farm — powder-processed for daily convenience."
- Avoid: claiming Capsules use Humanoid or Bullet grade specifically unless sourcing data confirms it.
- Avoid: implying other brands use lower grades without specific evidence.

---

## Goal

Improve conversion-oriented product page copy for the Capsules PDP while preserving compliance and brand trust.

The loop should seek stronger clarity, better benefit framing, tighter scanability, stronger trust signals, and cleaner CTA support without drifting into supplement hype or medical claims.

---

## Editable fields

The agent may propose changes only to these copy surfaces:

- Product description (hero paragraph + section copy)
- Benefit bullets (add/restructure)
- FAQ content
- Trust copy (badge labels, guarantee block text, sourcing copy)
- Meta title
- Meta description

---

## Locked fields

The agent must not change, rewrite, remove, or imply changes to:

- Price
- Images
- Supplement facts
- FDA disclaimer
- Product name

If a draft depends on changing any locked field, discard that variant and generate a different copy-only variant.

---

## Compliance guardrails

Every proposed variant must pass a compliance scan before it can be considered for keeping.

### Hard rules

- No disease claims
- No wording that says or implies the product can **cure, treat, prevent, or diagnose** any disease or condition
- No unapproved structure-function claims
- No clinical overreach, symptom promises, or implied medical outcomes
- Preserve the presence of the FDA disclaimer in the live experience; do not remove or weaken it in draft recommendations
- Follow FDA supplement advertising guidelines and conservative supplement marketing norms

### Examples of prohibited directions

Discard any variant that introduces language like:

- "treats fatigue"
- "prevents illness"
- "cures inflammation"
- "diagnoses nutrient deficiency"
- "clinically proven to fix"
- "rebuilds your immune system"

When in doubt, prefer origin, sourcing, quality, process, convenience, and product-format clarity over physiological promises.

---

## Keep threshold

A variant can only be marked **KEEP** if both conditions are true:

1. **Weighted rubric score is at least 2 points greater than baseline** (score_delta >= 2)
2. **Compliance scan passes**

If the score delta is less than 2 points, is equal to baseline, or is lower than baseline, mark the variant **DISCARD**. A marginal improvement of 0–1.9 points does not justify replacing the baseline — it must be a meaningful step forward.

---

## Max variants per run

- Maximum variants to generate and score in a single run: **5**

Do not brute-force many weak ideas. Fewer, sharper variants are better.

---

## Stop condition

Stop the optimization program when either of these is true:

- The current run reaches the max of 5 variants, or
- There have been **3 consecutive runs with no improvement >= 2 points** over the kept baseline

---

## Baseline and comparison rule

Before generating variants, load the latest kept baseline for this product. On the first run, use the baseline capture stored under the workspace outputs directory:

`~/.openclaw/workspace/outputs/autoresearch/pdp-copy/`

Each new variant must be compared against:

- the current kept baseline copy
- the fixed rubric in `rubrics/pdp-cro.md`
- the compliance rules in this program

Only one candidate should be judged at a time.

---

## One-change discipline

Preserve the upstream loop pattern.

Each variant should make **one primary change** to the copy system, such as:

- rewriting the opening description for faster comprehension
- converting a paragraph into mobile-friendly bullets
- strengthening trust copy near the buy box
- improving FAQ handling for sourcing objections
- tightening meta title and meta description around the primary keyword
- adding explicit benefit bullets above the fold

Do not create omnibus rewrites that alter everything at once. The point is to isolate what changed, why it changed, and whether that change improved the score.

---

## Single-run instructions (what the agent does in one iteration)

A single run of this program executes the following sequence:

### Step 1: Load context

Read:
- this program file
- `rubrics/pdp-cro.md`
- the current kept baseline markdown for Capsules from outputs directory
- `results/pdp-copy.tsv` for run history (to avoid repeating previously failed angles)

### Step 2: Identify the highest-leverage weakness

Audit the baseline against the rubric. Name the single biggest bottleneck. Examples:
- the hero description is too historical and not product-clear
- benefits are buried in paragraphs instead of bullets
- trust proof is present but not front-loaded
- CTA support near buy box is weak (no guarantee visible, no value framing)
- FAQ does not handle the sourcing objection clearly

### Step 3: Generate one focused variant

Create one draft that attacks the selected weakness while keeping the rest of the page stable.

For each variant, explicitly note:
- Variant ID and date
- Baseline file used
- Hypothesis
- Single primary change
- Edited fields
- Draft copy by section
- Compliance scan result
- Rubric sub-scores
- Weighted total
- Score delta vs baseline
- Keep or discard decision
- Brief reasoning

### Step 4: Score the variant

Score the draft with the fixed rubric in `rubrics/pdp-cro.md`.
- Score each dimension from 0 to 100
- Apply the dimension weights
- Compute the weighted total out of 100
- Apply the compliance hard-fail rule if prohibited claims appear

### Step 5: Make the keep/discard decision

- If score > baseline + 2 AND compliance passes: **KEEP** (this variant becomes the new baseline)
- Otherwise: **DISCARD** (revert to prior kept baseline, test a different single change)

### Step 6: Repeat up to 5 variants

Continue the loop, one variant at a time, until max variants or stop condition is reached.

---

## Output location and file format

Save every variant as a markdown file under:

`~/.openclaw/workspace/outputs/autoresearch/pdp-copy/<date>/`

Recommended filename pattern:
- `capsules-baseline.md`
- `capsules-v1-hero-clarity.md`
- `capsules-v2-benefit-bullets.md`
- `capsules-v3-trust-copy.md`

## Required markdown structure for each variant file

```md
# Capsules PDP Variant - V1

- Date: YYYY-MM-DD
- Product: American Ginseng Capsules 500mg
- Shopify Product ID: 7630033420384
- Price: $15.99
- URL: https://heilginseng.com/products/american-ginseng-capsules-500mg
- Baseline Compared Against: <file>
- Hypothesis: <one sentence>
- Primary Change: <one sentence>
- Edited Fields: <list>

## Draft Copy
### Meta Title
...

### Meta Description
...

### Product Description
...

### Benefit Bullets
...

### Trust Copy
...

### FAQ
...

## Compliance Scan
- Result: PASS or FAIL
- Notes: ...

## Rubric Scores
- Clarity & Readability: x/100
- Trust Signals & Social Proof: x/100
- Benefit-Driven Copy: x/100
- CTA Effectiveness: x/100
- Mobile-Friendly Formatting: x/100
- FDA/Supplement Compliance: x/100
- Weighted Total: x/100

## Decision
- Baseline Score: x/100
- Variant Score: x/100
- Score Delta: +/- x
- Threshold Met (>=2): YES or NO
- KEEP or DISCARD
- Reasoning: ...
```

---

## Decision hygiene

When scoring, stay strict.

Do not keep variants because they are more poetic, more elaborate, or more modern-sounding. Keep them only if they outperform baseline by 2+ points on the rubric and remain safely compliant.

Strong copy for this product should usually emphasize:
- what the product is in plain English (capsule format, 500mg, 60ct)
- capsule convenience and daily habit fit
- Wisconsin-grown origin (Edgar, WI; Marathon County)
- 4-generation family-farm credibility
- third-party testing and purity
- clean ingredients (no fillers, vegetarian capsule)
- $15.99 accessible entry point
- 30-day money-back guarantee

---

## What good variants usually look like

Good variants for this product are likely to:
- explain the product faster (format, origin, quality signal within first sentence)
- move concrete proof higher on the page
- convert dense paragraphs into scannable bullets
- reduce buyer hesitation without hype
- make the guarantee visible near the buy decision
- reference farm credentials specifically (not generically)

## What weak variants usually look like

Weak variants usually:
- wander into wellness clichés
- over-index on history instead of present-day product value
- sound clinical or sterile
- promise outcomes the brand cannot safely claim
- add fluff without improving scanability or trust
- require changes to locked assets or layout elements

---

## Final rule

This program is an instruction file, not an automation script.

It exists to guide future agents through a disciplined, repeatable, compliance-safe PDP copy optimization loop for Capsules using the original autoresearch principle:

**one change, one score, keep if score_delta >= 2 and compliance passes, discard otherwise, repeat.**
