# Ad Creative Visual Rubric — v1.1

## Purpose

Score 0–100 for any Meta Ads image variant produced in the ad creative loop. Used to decide keep vs discard before copy generation begins. Lower cost to discard early.

This rubric now has **two hard identity gates outside the weighted score**:
- **Packaging Fidelity Gate**
- **Root Authenticity Gate**

If either gate FAILs, the variant is **DISCARDED regardless of composite score**.

---

## Hard Identity Gates (Override Weighted Score)

These gates are pass/fail production controls. Weighted scoring is only a pre-screen.

### 1. Packaging Fidelity Gate — PASS / FAIL

Question: does the candidate match the exact approved Heil packaging identity for the intended SKU?

**PASS when:**
- Logo mark matches the approved packshot
- Package geometry matches the approved SKU
- Label architecture matches the approved SKU
- Core colorway matches the approved SKU
- Visible packaging reads as real Heil packaging, not generic supplement packaging

**FAIL when:**
- Logo is changed, softened, omitted, or replaced
- Package silhouette or geometry drifts from the real SKU
- Label zones, hierarchy, or proportions are materially different
- Colorway drifts into a new or generic scheme
- Candidate shows blank, fake, or genericized packaging where real packaging should be visible

**Concrete examples**
- **PASS:** Capsules bottle shows the same Heil mark placement, same bottle silhouette, same earthy label banding, and same cap treatment as the approved packshot.
- **FAIL:** Capsules bottle becomes a generic amber jar with a blank cream label and a vaguely herbal look.
- **PASS:** Tea package keeps the real carton/pouch structure and recognizable front label architecture from the approved tea references.
- **FAIL:** Tea candidate uses a different pouch shape, a simplified icon, or a new green palette not present on the real package.

### 2. Root Authenticity Gate — PASS / FAIL

Question: do any visible roots look morphologically realistic for real American ginseng?

**PASS when:**
- Root shape looks naturally irregular, not stylized
- Surface texture shows believable wrinkles, age cues, and organic variation
- Branching and taper feel biologically plausible
- Roots align with approved reference photos where roots are shown

**FAIL when:**
- Roots look plastic, waxy, or over-smoothed
- Branching is anatomically implausible or decorative
- Texture lacks believable wrinkles/fibers
- Roots look cartoonish, synthetic, or like generic fantasy tubers

**Concrete examples**
- **PASS:** Root cluster shows asymmetric branching, rough skin texture, natural taper, and real age cues similar to the approved Heil root photos.
- **FAIL:** Root cluster is too symmetrical, too glossy, too smooth, or shaped like sculpted clay.
- **PASS:** Powder scene includes a few realistic cut root pieces with believable fiber and irregularity.
- **FAIL:** Lifestyle scene includes decorative "ginseng" roots that look like polished ginger props or AI-invented tentacles.

### Operational use of the gates

- Use the weighted 0–100 score as an **operational pre-screen**.
- A variant scoring 80 can still be discarded if either hard gate FAILs.
- A variant scoring 66 can proceed only if both hard gates PASS.
- Final production decision is **PASS/FAIL on the hard gates first, weighted score second**.

---

## Scoring Dimensions

Total: 100 points across 5 dimensions.

| Dimension | Weight | Points |
|---|---|---|
| Composition | 25% | 0–25 |
| Brand Consistency | 20% | 0–20 |
| Product Prominence | 20% | 0–20 |
| Lighting & Color | 15% | 0–15 |
| Scroll-Stopping Potential | 20% | 0–20 |

**Weights sum: 100%**

---

## Dimension Definitions

### 1. Composition (25 pts)

Assess spatial layout, visual balance, and intentional use of negative space.

| Score | Description |
|---|---|
| 22–25 | Strong visual hierarchy. Product has a clear focal point. Negative space used intentionally. Frame is balanced without feeling static. Works at 1080×1080 and 1080×1350. |
| 17–21 | Mostly well-composed. Minor imbalance or slightly tight crop. Focal point is clear but not commanding. |
| 11–16 | Adequate but forgettable. Generic framing, no intentional negative space, slightly cluttered. |
| 6–10 | Poor balance. Multiple competing focal points. Crop creates tension without purpose. |
| 0–5 | Cluttered, disorganized, or unframed. No discernible visual hierarchy. |

### 2. Brand Consistency (20 pts)

Assess alignment with Heil Ginseng's brand identity and David Protein visual benchmark.

| Score | Description |
|---|---|
| 18–20 | Unmistakably Heil Ginseng aesthetic. Earth tones, natural origin, premium-but-approachable. Feels like it could sit next to David Protein in a premium wellness editorial. |
| 14–17 | Mostly on-brand. Warm tones and product focus present, but one brand element is off (e.g., background too generic or lighting too commercial). |
| 9–13 | Partially on-brand. Could be any supplement. Farm origin or natural quality not communicated visually. |
| 4–8 | Off-brand. Clinical supplement look, stock-photo feel, or overly bright commercial styling. |
| 0–3 | Antithetical to brand. Neon, chaotic, or low-trust aesthetic. |

### 3. Product Prominence (20 pts)

Assess whether the product is the clear hero of the image.

| Score | Description |
|---|---|
| 18–20 | Product is unambiguously the hero. Clear, sharp, properly sized for thumb-view. No competing elements diminish it. |
| 14–17 | Product is prominent but slightly overshadowed by environment or props. |
| 9–13 | Product is present but gets lost in the scene. Environment competes equally with the product. |
| 4–8 | Product is a supporting element, not the hero. Hard to identify in thumbnail. |
| 0–3 | Product barely visible or absent. |

### 4. Lighting & Color (15 pts)

Assess light quality, color temperature, and palette coherence.

| Score | Description |
|---|---|
| 13–15 | Natural or studio-natural lighting. Soft directional light. Color palette is warm, coherent, on-brand (earth tones, muted golds, organic greens). |
| 10–12 | Mostly good lighting. Minor issues — slightly flat, minor color inconsistency, or warm palette partially broken by one element. |
| 6–9 | Adequate lighting but generic — no mood, no warmth, no editorial feel. |
| 2–5 | Harsh lighting, over-processed, or cold/sterile palette inconsistent with brand. |
| 0–1 | Poor lighting — blown highlights, heavy shadows with no purpose, or obviously AI-artifact lighting. |

### 5. Scroll-Stopping Potential (20 pts)

Assess thumb-stop power on a mobile feed at a glance.

| Score | Description |
|---|---|
| 18–20 | Immediately arresting. Distinctive composition, visual tension, or textural detail that makes a thumb pause. Would stop scroll in a competitive feed. |
| 14–17 | Likely to slow the thumb. Interesting but not commanding. Requires a beat to register. |
| 9–13 | Would be scrolled past by most users. Interesting only to someone already searching for this product. |
| 4–8 | Blends in completely. Indistinguishable from generic content. |
| 0–3 | Actively repels attention — confusing, amateurish, or visually cluttered. |

---

## Hard Discard Rules (Auto-0, Skip Scoring)

Any of these triggers an immediate DISCARD before scoring. Log reason.

| Rule | Discard Trigger |
|---|---|
| **Packaging Fidelity Gate FAIL** | Packaging identity drifts from the approved Heil reference images. |
| **Root Authenticity Gate FAIL** | Visible roots are morphologically unrealistic or synthetic-looking. |
| **No AI-generated humans** | Any image containing AI-generated human faces, bodies, or human figures — even partially visible. Hands/props are acceptable. Real-person photos are acceptable. AI-generated people: zero exceptions. |
| **No stock photo look** | Image is identifiably sourced from stock or has the compositional hallmarks of a staged stock shoot (perfect white background + product, fake-outdoor compositing, anonymous lifestyle models). |
| **No cluttered compositions** | More than 3 distinct visual elements competing for attention simultaneously. |
| **Compliance: no prohibited overlay text** | Any text overlay containing medical claims, disease references, or FTC-prohibited language. |

---

## Keep / Discard Threshold

| Decision | Condition |
|---|---|
| **KEEP** | Score ≥ 65 AND all hard discard rules pass |
| **DISCARD** | Score < 65 OR any hard discard rule triggered |
| **Marginal flag** | Score 65–69 — keep but deprioritize in ranking |
| **Improvement gate** | New variant scores ≥ 3 pts higher than previous kept variant on same brief/angle — worthwhile; otherwise note as marginal |

---

## Anti-Patterns Reference

Penalize these in scoring, especially under Brand Consistency and Scroll-Stopping Potential:

- **Stock photo look**: generic, anonymous, could be any health brand
- **Clinical supplement aesthetic**: white lab backdrop, sterile props, cold blue/white palette
- **Cluttered compositions**: too many props, too much text, product buried in noise
- **AI-generated humans**: zero tolerance. Automatic discard.
- **Over-processed HDR or heavy saturation**: loses the natural, farm-origin feel
- **Floating product on white**: fine for e-commerce PDP, not for Meta creative
- **Generic "wellness" visual clichés**: yoga mats, green smoothies, anonymous hands holding supplements
- **Packaging drift**: new labels, softened marks, fake containers, or made-up SKUs
- **Synthetic roots**: polished, symmetrical, or fantasy-looking ginseng forms

---

## Rewarded Patterns

Give bonus consideration (within scoring ranges) for:

- **Editorial product-world scenes**: product staged in its natural habitat — wooden surfaces, forest floor, farmland light, stone, linen, dried botanicals
- **Natural material textures**: wood grain, soil, bark, unbleached linen, ceramic — communicates authenticity
- **Intentional negative space**: deliberate emptiness that focuses the eye
- **Warm earth tones**: the palette of a Wisconsin ginseng farm — Browns, greens, golds, cream
- **Soft directional natural light**: morning or late-afternoon light quality, real or studio-simulated
- **Minimalist product staging**: product as sculpture, not product as commodity
- **Reference-true packaging**: unmistakably the real Heil SKU from approved packshots
- **Botanically believable roots**: texture and branching that read as real American ginseng

---

## Rubric Version Log

| Version | Date | Change |
|---|---|---|
| v1.1 | 2026-03-12 | Added Packaging Fidelity Gate and Root Authenticity Gate as hard PASS/FAIL overrides with examples and operational guidance |
| v1.0 | 2026-03-09 | Initial rubric |
