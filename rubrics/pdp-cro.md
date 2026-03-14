# PDP CRO Scoring Rubric

## Purpose

This is the fixed evaluation harness for Heil Ginseng Capsules product detail page copy experiments.

Use this rubric to score any Capsules PDP copy variant on a 0–100 weighted composite scale. The rubric is stable by design. Agents may apply it, but only humans should edit it.

Primary product: **American Ginseng Capsules 500mg** (Shopify ID: 7630033420384, $15.99)

---

## Scoring process

For every variant:
1. Score each dimension from **0 to 100** using the guidance below
2. Multiply each dimension score by its weight
3. Sum the weighted values to produce the composite score out of 100
4. Apply the compliance hard-fail rule
5. Compare to baseline and apply the keep/discard threshold

### Formula

```
Composite Score =
  (Clarity & Readability × 0.20)
+ (Trust Signals & Social Proof × 0.20)
+ (Benefit-Driven Copy × 0.25)
+ (CTA Effectiveness × 0.15)
+ (Mobile-Friendly Formatting × 0.10)
+ (FDA/Supplement Compliance × 0.10)
```

**Weight check:** 20 + 20 + 25 + 15 + 10 + 10 = **100%** ✓

---

## Keep/discard threshold

A variant is **KEEP** only if BOTH conditions are true:
1. `variant_score - baseline_score >= 2` (minimum 2-point improvement)
2. Compliance dimension does not trigger a hard fail

A variant that scores equal to baseline, within 1.9 points, or lower than baseline is always **DISCARD** — even if it is well-written. The loop requires a meaningful signal, not a tie.

**Why +2 and not +1?** A 1-point delta is within normal scoring noise for subjective rubric evaluation. Two points represents a directional improvement large enough to justify replacing the baseline.

---

## Hard-fail rule

If the variant contains any prohibited claim or compliance violation:
- **FDA/Supplement Compliance = 0**
- Mark variant as **flagged for immediate discard**
- Do not keep the variant even if the composite total would otherwise beat baseline

Hard-fail triggers include: disease claims, "cure/treat/prevent/diagnose" language, unapproved structure-function claims, missing or weakened FDA disclaimer context, clinical overreach.

---

## 1) Clarity & Readability — Weight 20

### Core question
What is this product? Who is it for? Can a first-time shopper understand the offering in 5 seconds?

### How to score

- **90–100:** Immediate comprehension. Within the first sentence or two, the page communicates that this is American ginseng in capsule form, at 500mg per cap, from a Wisconsin farm. No backstory delay.
- **70–89:** Mostly clear, but some value is buried or delayed past the first paragraph.
- **40–69:** Product identity is understandable only after reading a full paragraph or piecing together multiple sections.
- **0–39:** Vague, abstract, confusing, or dominated by brand poetry or generic wellness language.

### High vs low edge cases

- **High:** "Pure Wisconsin-grown American ginseng root powder in a vegetarian capsule. 500mg per cap. 60 count. No fillers." — immediate product signal.
- **High:** Opening line names product format, origin, and key quality signal before any historical narrative.
- **Low:** Opening paragraph spends 3+ sentences on ginseng history before explaining what is being sold.
- **Low:** Current baseline hero: "American ginseng has been treasured for centuries…" — delays product clarity.

---

## 2) Trust Signals & Social Proof Integration — Weight 20

### Core question
Does the copy reduce hesitation with credible, specific trust evidence — and is that evidence placed where the buyer makes the decision?

### How to score

- **90–100:** Origin (Edgar, WI), family-farm credential (4 generations), third-party testing details, GBW certification, and 30-day money-back guarantee are all present, specific, and placed near the buying decision — not buried mid-page or in an accordion.
- **70–89:** Strong trust material exists but some key proof is harder to find (inside accordions, below fold, or stated generically).
- **40–69:** Trust signals are present but generic ("premium quality"), scattered, or disconnected from the buy box.
- **0–39:** Little proof, vague reassurance, or trust claims feel unsubstantiated.

### High vs low edge cases

- **High:** Guarantee, third-party testing summary, and Wisconsin farm origin are all visible above the fold or within 1 scroll of the buy box.
- **High:** "Tested for heavy metals, pesticides, and ginsenoside content by a third-party lab" — specific test list, not just "lab tested."
- **Low:** Badge bar present but buried after 3 paragraphs of prose. Guarantee only visible at page bottom.
- **Low:** "Quality you can trust" without naming what that quality evidence is.

---

## 3) Benefit-Driven Copy vs Feature Listing — Weight 25

### Core question
Does the copy translate product features into tangible benefits for the buyer — or does it just list specifications?

**This is the highest-weighted dimension because it most directly drives conversion intent.**

### How to score

- **90–100:** Benefits are concrete, buyer-relevant, and framed around what the shopper gains. Features (500mg, vegetarian capsule, no fillers) are present but connected to buyer outcomes (daily habit fit, capsule convenience, trusted purity). Bullets separate individual benefits so each can land independently.
- **70–89:** Benefits are solid but some sections drift into feature lists without buyer translation.
- **40–69:** Mostly feature listing. Specs are present without explaining why those specs matter to this shopper.
- **0–39:** Almost entirely spec sheet or vague wellness language. Nothing concrete ties a product feature to a real buyer benefit.

### High vs low edge cases

- **High:** "No fillers, binders, or artificial anything — just the same root we grow and grade on the farm, in a capsule." — feature (no fillers) + benefit framing (same root, farm-direct).
- **High:** "60 capsules = a 1–2 month supply at daily use. Easy to maintain." — count translated to habit value.
- **Low:** "100% American Ginseng Root (Panax quinquefolius) - 500mg per capsule, Vegetarian capsule (plant cellulose)." — pure spec list with no buyer-facing translation.
- **Low:** "An amazing superfood that transforms your routine." — vague benefit, no feature grounding.

### Note on ginseng grades

Where relevant, copy may reference that Capsules use quality-grade Wisconsin root — but only if sourcing data supports the specific claim. Avoid implying Humanoid or Bullet grade specifically without confirmation. Safe framing: "the same roots we grow and grade on our farm."

---

## 4) CTA Effectiveness — Weight 15

### Core question
Does the copy actively support the shopper's decision to add to cart — or does it leave the conversion moment unassisted?

### How to score

- **90–100:** The path to purchase is paved. Guarantee language, price anchoring (compare-at $19.99 visible context), subscribe-and-save offer clarity, and friction-reducing copy are all legible near or at the buy box. The copy gives the shopper a concrete reason to act now rather than defer.
- **70–89:** Generally supportive of conversion, but one or more key reassurance elements are missing near the CTA.
- **40–69:** Some purchase-adjacent copy exists (guarantee mentioned somewhere, Subscribe & Save block present) but does not actively remove hesitation or create urgency.
- **0–39:** Copy ends before supporting the buy decision. Reads like an informational article with no conversion orientation.

### High vs low edge cases

- **High:** Guarantee summary, lab-tested line, and "cancel anytime" subscribe-and-save note are all close to or part of the buy box section — not locked inside accordions.
- **High:** Price context framing: "Retail price $19.99 — yours at $15.99. 30-day guarantee included."
- **Low:** Guarantee block exists but is at the bottom of the page after the FAQ — invisible to most mobile shoppers.
- **Low:** Subscribe & Save block is purely informational ("here is how it works") rather than conversion-oriented ("save 10% starting today").

---

## 5) Mobile-Friendly Formatting — Weight 10

### Core question
Is the copy structure easy to absorb on a phone screen in 10 seconds?

### How to score

- **90–100:** Short paragraphs (2–3 lines max), benefit bullets, clear section headers, no dense prose walls. Key value (origin, test, guarantee, format) is accessible without needing to expand accordions.
- **70–89:** Generally scannable, though a few sections run longer than necessary.
- **40–69:** Mixed structure. Some bullets or headings exist, but important value is trapped in long paragraphs or requires accordion expansion.
- **0–39:** Dense, repetitive, or visually exhausting — relies on scrolling through prose to extract product value.

### High vs low edge cases

- **High:** Core product identity, 3 key benefits, and guarantee are all visible as short bullets within the first 2 screen-heights on mobile.
- **High:** Accordion sections contain supplemental detail (ingredients list, where it comes from), not primary value.
- **Low:** Hero section is a 4-sentence paragraph with no bullet structure. Trust signals buried inside closed accordions.

---

## 6) FDA/Supplement Compliance — Weight 10

### Core question
Is every line of copy safely within supplement advertising boundaries?

### How to score

- **90–100:** Conservative, clean, and clearly compliant. No disease claims, no prohibited verbs, no unapproved health promises. FDA disclaimer context is preserved. Copy focuses on origin, purity, testing, and format.
- **70–89:** Safe overall, with a few phrases that are slightly aggressive but still within accepted supplement marketing norms.
- **40–69:** Borderline phrasing or ambiguous implication that needs revision before production use.
- **0–39:** Non-compliant or materially risky language present.

### Hard-fail trigger

Any prohibited claim sets this dimension to **0** and flags the variant for immediate discard regardless of composite total.

### High vs low edge cases

- **High:** "Pure Wisconsin-grown American ginseng root powder. Third-party tested. No fillers." — origin and quality, no health claims.
- **High:** Focus on convenience, daily habit, and farm-direct sourcing rather than physiological outcomes.
- **Low:** "Supports immunity, focus, and energy" — without appropriate qualification, this is borderline.
- **Immediate discard:** "Treats fatigue," "prevents illness," "boosts your immune system" — automatic hard fail.

---

## Interpretation bands

- **90–100:** Exceptional. Clear candidate to keep if compliant and score delta >= 2.
- **80–89:** Strong. Usually worth keeping if it beats baseline by 2+.
- **70–79:** Serviceable but not compelling. Likely needs another iteration.
- **60–69:** Weak conversion support. Usually discard.
- **Below 60:** Poor or risky. Discard.

---

## Example baseline scoring (current live copy — 2026-03-09)

The following scores represent the current live Capsules PDP copy against this rubric. This is the **baseline** all variants must beat by 2+ points.

**Product title:** "Premium American Ginseng Capsules (500mg, 60ct)"

| Dimension | Score | Weight | Weighted |
|---|---|---|---|
| Clarity & Readability | 62 | 0.20 | 12.4 |
| Trust Signals & Social Proof | 74 | 0.20 | 14.8 |
| Benefit-Driven Copy | 55 | 0.25 | 13.75 |
| CTA Effectiveness | 52 | 0.15 | 7.8 |
| Mobile-Friendly Formatting | 60 | 0.10 | 6.0 |
| FDA/Supplement Compliance | 88 | 0.10 | 8.8 |
| **Weighted Total** | | | **63.55** |

**Baseline composite score: 63.55 / 100**

**Score to beat for KEEP: 65.55 or higher** (baseline + 2)

### Scoring rationale for baseline

- **Clarity (62):** Hero paragraph leads with historical context ("has been treasured for centuries") rather than product clarity. A first-time shopper must read 2–3 sentences before understanding what they're buying. Deducted for delayed product identity.
- **Trust (74):** GBW Certified, Wisconsin Grown, Lab Tested, Family Farm badges are present. Third-party testing is specific (heavy metals, pesticides, ginsenoside content). Guarantee is visible. Score held back because trust signals are mid-page, not near the buy box.
- **Benefit-Driven Copy (55):** Ingredients section is mostly a spec list (500mg, vegetarian capsule, no fillers) without buyer-facing translation. History and process content fills copy space that could carry benefit framing. Benefit bullets above the fold are absent.
- **CTA Effectiveness (52):** Guarantee block exists at page bottom. Subscribe & Save block is informational. No price anchoring near buy box. No friction-removing copy adjacent to the add-to-cart button. Low score reflects weak CTA support architecture.
- **Mobile-Friendly Formatting (60):** Accordion structure helps, but hero is a prose paragraph. Key trust signals and benefits are inside closed accordions on mobile. Subscribe & Save and Guarantee blocks require significant scrolling.
- **FDA/Supplement Compliance (88):** Copy is generally conservative. FDA disclaimer is present. A few borderline phrases ("Ginseng has traditionally been used to support natural energy") score slightly below 100 but do not trigger hard fail.

---

## Evaluator discipline

- Score what is on the page, not what you imagine the layout might do.
- Do not award points for claims that are unsupported by visible copy.
- Do not inflate scores for length, polish, or brand romance alone.
- Penalize fluff, vagueness, and buried proof.
- Stay strict on compliance. A clever line is not worth a risky claim.

## Quick evaluator checklist

Before finalizing a score, ask:

- Can a first-time shopper tell what this is in 5 seconds?
- Are benefits framed for the buyer, not just listed as specs?
- Is trust established early with real, specific proof?
- Is the copy easy to scan in bullets and short paragraphs on mobile?
- Does the copy help the shopper buy now — is the path to purchase clear?
- Is every line safe for supplement marketing?

If any answer is clearly no, the total should reflect it.
