# Packaging Visual Rubric — v1.1

## Purpose

Score 0–100 for packaging mockup images in the visual autoresearch loop. Each mockup is evaluated by 6 BTD-grounded personas scoring independently on 6 dimensions. Final composite = persona-weighted × dimension-weighted × confidence-adjusted average.

This rubric has **four** hard gates that override the weighted score:
- **Ginseng Board Seal Gate**
- **Product Visibility Gate** (NEW in v1.1)
- **BTD Citation Gate**
- **Cultural Depth Gate**
- **Visual Clutter Gate** (NEW in v1.1)

## Hard Gates (Override Weighted Score)

### 1. Ginseng Board Seal Gate — PASS / FAIL

Question: does the mockup show the Wisconsin Ginseng Board seal (red ring with eagle) correctly?

PASS when:
- Seal is visible and legible on the packaging
- Seal uses correct red ring format with eagle emblem
- Seal placement is standard for packaging (bottom-right or bottom-center)
- Seal is not obscured, distorted, or replaced with a generic badge

FAIL when:
- Seal is missing entirely
- Seal is replaced with a different certification mark
- Seal is obscured by other design elements
- Eagle emblem is distorted beyond recognition

Operational rule: If a mockup fails the Ginseng Board Seal Gate, it is marked [EXCLUDED-NO-SEAL] and must be regenerated before scoring.

**Note (v1.1):** Cross-model seal detection is unreliable. If the generation model rendered the seal but the scoring model can't confirm it, flag for manual verification. Colton eyeballs the mockup — if seal is present, mark `[MANUAL-OVERRIDE: PASS]`.

### 2. Product Visibility Gate — PASS / FAIL (NEW v1.1)

Question: does the mockup show a clear/transparent window where the actual product is visible?

**Applicable to:** Roots pouch, powder pouch, combo lineup. NOT applicable to capsules (bottle), tea box (box), or extract (bottle).

PASS when:
- A transparent window is visible on the front of the packaging
- The actual product (roots, powder) is visible through the window
- Window is large enough to assess product quality (≥10% of front face area)
- Window is not obscured by labels, text, or design elements

FAIL when:
- No transparent window on roots/powder/combo SKUs
- Window present but too small to assess product (<10% of front face)
- Window obscured by text or design elements
- Product shown outside the package but not visible through a window (staged photography ≠ product visibility)

Operational rule: If a roots/powder/combo mockup fails the Product Visibility Gate, it is marked [EXCLUDED-NO-WINDOW] and must be regenerated with a clear window before scoring.

### 3. BTD Citation Gate — PASS / FAIL

Question: does every persona evaluation cite at least 1 specific BTD entry when scoring this mockup?

PASS when:
- Every persona scoring this mockup cites ≥1 [BTD-XXX] reference in their evaluation
- Cited BTD entries are relevant to the dimension being scored
- At least 90% of dimension scores across all personas have supporting BTD citations

FAIL when:
- Any persona evaluation has zero BTD citations
- More than 30% of dimension scores lack supporting citations

Operational rule: If a mockup fails, mark [EXCLUDED-NO-CITE]. Raw scores recorded but zero-ranked.

### 4. Cultural Depth Gate — PASS / FAIL

Question: does the Chinese Diaspora persona cite ≥5 distinct cultural data points for this mockup?

PASS when:
- Chinese Diaspora persona references ≥5 distinct cultural observations from BTD
- References span multiple cultural dimensions (gifting, TCM, Didao, color symbolism, number symbolism)
- At least 2 references are specific to Chinese buyer behavior

FAIL when:
- Chinese Diaspora persona cites fewer than 5 cultural data points
- Cultural references are all from the same dimension

Operational rule: If failed, Chinese Diaspora scores de-weighted by 50%.

### 5. Visual Clutter Gate — PASS / FAIL (NEW v1.1)

Question: is the mockup clean enough to work at thumbnail size, or is it overloaded with competing elements?

**Evaluation method:** Scored at thumbnail size (200×200px equivalent).

PASS when:
- ≤6 distinct text blocks on the primary face
- ≤8 total visual elements (seal, logo, illustration, pattern, window, border, icon, text block, etc.) competing for attention
- "Visual breathing room" scores ≥4/10

FAIL when:
- >6 distinct text blocks on the primary face
- >8 total visual elements competing for attention
- "Visual breathing room" scores <4/10
- More than 3 languages/scripts/text hierarchies on a single face (bilingual OK, trilingual or bilingual+tagline+origin+certification = clutter)

**"Visual breathing room" prompt:** "On a scale of 1–10, how much empty/quiet space does this design have relative to the content? 1 = every inch is filled, 10 = mostly negative space."

Operational rule: If a mockup fails the Visual Clutter Gate, it is marked [EXCLUDED-CLUTTERED] and must be redesigned with fewer elements before scoring.

## Scoring Dimensions

Total composite: persona-weighted average across 6 dimensions, each scored 1–10.

| Dimension | Weight (v1.1) | Weight (v1.0) | What It Measures |
|-----------|--------------|---------------|------------------|
| Shelf & Thumbnail Impact | **25%** | 20% | Pops in Amazon grid, Meta feed, Shopify collection page. 3-second recognition test. THIS IS THE PURCHASE MOMENT. |
| Mobile Scannability | **20%** | 15% | Hierarchy reads at thumbnail size. Brand name, product type, weight clear at small scale. |
| Cultural Resonance | 15% | 15% | Works for both domestic premium buyers AND Chinese diaspora. Gifting-appropriate. No appropriation. |
| Premium Positioning | **15%** | 20% | Reads as premium wellness, not commodity supplement. Worth $25-80+. |
| Trust & Authenticity | **15%** | 20% | Ginseng Board seal, origin claims, heritage signals, transparency window. Builds buyer confidence. |
| Brand Memorability | 10% | 10% | Distinctive and ownable. Would you recognize it again? Does it create a mental hook? |

Weights sum: 100%

**v1.1 Rationale:** Shelf + Mobile rise from 35% to 45% — these are the dimensions that catch busy/cluttered designs. Trust + Premium drop from 40% to 30% — seal is now a hard gate (doesn't need weight), premium double-counted less. Cultural stays at 15%.

## Persona Set (Fixed)

Each persona scores independently with FRESH context. No cross-persona contamination. No prior cycle data.

| Persona | Weight (v1.1) | Weight (v1.0) | BTD Min Citations | Focus |
|---------|--------------|---------------|-------------------|-------|
| Mobile Speed Shopper | **20%** | 15% | ≥1 | 3-second scan, hierarchy, Amazon thumbnail legibility |
| Skeptical First-Timer | **20%** | 15% | ≥1 | Trust signals, clarity, risk reduction, "is this real?" test, CLUTTER PENALTY |
| Premium Wellness Buyer | **15%** | 20% | ≥1 | Premium value, story, quality justification, craftsmanship signals |
| Chinese Diaspora Buyer | **15%** | 20% | ≥5 | Didao provenance, TCM context, gifting culture, color/number symbolism |
| Premium Gift Buyer | 15% | 15% | ≥1 | Giftability, presentation, cultural gifting norms |
| Brand Strategist | 15% | 15% | ≥1 | Differentiation, scalability, competitive whitespace |

**v1.1 Rationale:** Skeptical First-Timer and Mobile Speed Shopper gain 5% each — these personas penalize clutter and reward clean hierarchy. Chinese Diaspora and Premium Wellness each drop 5%.

### Persona Detail

**Mobile Speed Shopper** (20%)
- Values: instant recognition, clear product name, readable weight/price, bold hierarchy, clean layout
- Sensitive to: small text, complex illustrations, low contrast, busy layouts, too many competing elements
- BTD refs: BTD-048, BTD-050, BTD-051, BTD-052
- Lens: "I'm scrolling Amazon on my phone. Do I stop?"
- **v1.1 emphasis:** This persona is the primary advocate against visual clutter. If a design is busy, this persona will penalize it hard.

**Skeptical First-Timer** (20%)
- Values: clear product identity, origin proof, certification seals, unambiguous labeling, clean uncluttered design
- Sensitive to: vague branding, missing weight/origin, clutter that creates doubt, overwhelming information
- BTD refs: BTD-004, BTD-023, BTD-026, BTD-033
- Lens: "I've never bought ginseng. Do I trust this enough to try it?"
- **v1.1 emphasis:** Clutter creates doubt. More text ≠ more trust for first-time buyers. Clean, confident design signals quality.

**Premium Wellness Buyer** (15%)
- Values: premium materials, heritage story, farm credibility, elevated design, restrained elegance
- Sensitive to: cheap-looking materials, generic layouts, weak typography, visual overload
- BTD refs: BTD-002, BTD-015, BTD-027, BTD-029, BTD-035
- Lens: "Would I pay $55 for this and feel good about it?"

**Chinese Diaspora Buyer** (15%)
- Values: Didao (Wisconsin provenance as gold standard), TCM positioning, correct cultural symbolism, gifting norms
- Sensitive to: cultural appropriation, wrong colors for gifting (white/black), sets of 4, generic "Eastern" motifs without depth
- BTD refs: BTD-001, BTD-003, BTD-004, BTD-005, BTD-006, BTD-009, BTD-010, BTD-011, BTD-012, BTD-013, BTD-018, BTD-019, BTD-020, BTD-022, BTD-023
- MUST cite ≥5 distinct cultural data points per mockup
- Lens: "Does this honor the tradition, or just use it as decoration?"

**Premium Gift Buyer** (15%)
- Values: beautiful presentation, story worth telling, cultural appropriateness, perceived value
- Sensitive to: budget appearance, generic packaging, cultural tone-deafness
- BTD refs: BTD-010, BTD-011, BTD-012, BTD-013, BTD-017, BTD-038
- Lens: "Would I be proud to gift this to someone important?"

**Brand Strategist** (15%)
- Values: differentiation from Dairyland/Zen/Hsu's, scalability across SKUs, ownable visual identity
- Sensitive to: me-too design, trends that won't age, single-SKU thinking
- BTD refs: BTD-051, BTD-052
- Lens: "Can this brand own a visual territory for the next decade?"

## Dimension Definitions

### 1. Shelf & Thumbnail Impact (25% — was 20%)

| Score | Description |
|---|---|
| 9–10 | Immediately arresting. Would stop a scrolling thumb and stand out in Amazon grid. Distinctive color, shape, or composition. Recognizable at 200px wide. |
| 7–8 | Strong presence. Would slow a scrolling thumb. Clear brand read at distance. |
| 5–6 | Average presence. Would be noticed by someone already searching for ginseng. Blends somewhat with competitors. |
| 3–4 | Blends in. Indistinguishable from competitors in a grid. |
| 1–2 | Invisible. Would scroll past without registering. |

### 2. Mobile Scannability (20% — was 15%)

| Score | Description |
|---|---|
| 9–10 | Perfect hierarchy at thumbnail. Brand name, product type, and weight all readable instantly. Works at 200px wide. |
| 7–8 | Good hierarchy. Most info readable at thumbnail. One element may need a beat to register. |
| 5–6 | **Mediocre.** Brand name barely readable, everything else is lost. A 5–6 means this design is NOT ready for mobile commerce. This score should feel like a penalty. |
| 3–4 | Poor. Key info illegible at small size. Too much visual complexity. |
| 1–2 | Unscannable. Nothing reads at mobile size. |

**v1.1 Evaluation order:** Score Mobile Scannability FIRST on a thumbnail-sized image (200px wide), BEFORE seeing the full-resolution image. Then score Shelf & Thumbnail Impact on the same thumbnail. Only after both are scored should the evaluator see the full-size image for remaining dimensions.

### 3. Cultural Resonance (15% — unchanged)

| Score | Description |
|---|---|
| 9–10 | Deeply culturally informed. Nuanced understanding of gifting norms, TCM context, Didao provenance. Works for domestic AND Chinese diaspora without compromise. No appropriation. |
| 7–8 | Culturally respectful and informed. Understands major norms. Minor gaps in TCM nuance but nothing offensive. |
| 5–6 | Culturally neutral. Doesn't violate norms but doesn't demonstrate depth either. |
| 3–4 | Culturally superficial. Uses "Eastern" motifs without depth or inadvertently violates a norm. |
| 1–2 | Culturally insensitive or appropriative. |

### 4. Premium Positioning (15% — was 20%)

| Score | Description |
|---|---|
| 9–10 | Unmistakably premium. Could sit alongside Ritual, David Protein, Fly By Jing. Materials, typography, and layout all signal quality-first. Justifies $55+ pricing without question. |
| 7–8 | Strongly premium. Most elements communicate quality. One or two may read mid-market but overall impression is aspirational. |
| 5–6 | Adequately premium. "Nice supplement" rather than "premium wellness." Risk of blending with mid-tier. Pricing ceiling limited. |
| 3–4 | Weakly premium. Reads commodity or generic. |
| 1–2 | Anti-premium. Budget, mass-market, or clinical. |

### 5. Trust & Authenticity (15% — was 20%)

| Score | Description |
|---|---|
| 9–10 | Ironclad trust through few, powerful signals. Seal prominent and legible. Origin communicated clearly in 1–2 elements, not scattered across the label. Trust comes from confidence, not from proving everything at once. Transparency window shows actual product. |
| 7–8 | Strong trust. Seal present, origin communicated, one trust element could be stronger. |
| 5–6 | Moderate trust. Some signals present but gaps. Seal too small, origin buried, or transparency missing. |
| 3–4 | Weak trust. Minimal proof signals. Buyer would wonder "is this real?" |
| 1–2 | No trust signals. Generic packaging with no authenticity markers. |

**v1.1 change:** 9–10 anchor redefined. Trust is about confidence and restraint, not piling on verification layers. The Ginseng Board seal + clear window + one origin statement = enough. More isn't better.

### 6. Brand Memorability (10% — unchanged)

| Score | Description |
|---|---|
| 9–10 | Highly memorable and ownable. Creates a distinct visual territory that no competitor occupies. Would recognize it again instantly. |
| 7–8 | Memorable with strong identity. One distinctive element that sticks. |
| 5–6 | Moderately memorable. Professional but doesn't create a mental hook. |
| 3–4 | Forgettable. Looks like many other brands. |
| 1–2 | Generic. No distinguishing features. |

## Keep / Discard Threshold

| Decision | Condition |
|---|---|
| KEEP | Composite ≥ 6.5 AND ALL hard gates PASS (Seal, Product Visibility, BTD Citation, Cultural Depth, Visual Clutter) |
| DISCARD | Composite < 6.5 OR any hard gate FAIL |
| Marginal flag | Composite 6.5–7.0 — keep but deprioritize |
| Top candidate | Composite ≥ 8.0 — advance to next cycle with priority |

## Fresh-Context Protocol (CRITICAL)

To prevent persona contamination between evaluations and cycles:

1. **Each persona evaluation is an independent LLM call.** The prompt contains ONLY: persona definition + relevant BTD citations + the mockup image. It does NOT contain prior scores, other persona scores, cycle number, or generation history.

2. **No cross-persona visibility.** Persona A cannot see Persona B's scores or reasoning. Each scores in isolation.

3. **No cross-cycle memory.** Cycle 2 evaluations do NOT see Cycle 1 scores. The generation prompt for Cycle 2 may reference Cycle 1's keep/discard log (to know what to refine), but the scoring prompt is always fresh.

4. **BTD citations are injected per persona.** Each persona receives only their relevant BTD refs (listed above). This prevents citation fishing — personas can't cite data outside their domain.

5. **Confidence levels are mandatory.** Every score includes High/Medium/Low confidence based on data density. Low confidence scores are de-weighted 30%.

## Scoring Protocol

### v1.1: Thumbnail-First Evaluation (NEW)

For each mockup × persona:

1. **Pass 1 — Thumbnail evaluation (200px wide image only):**
   - Score Mobile Scannability (20%)
   - Score Shelf & Thumbnail Impact (25%)
   - Score Visual Clutter Gate (text blocks, visual elements, breathing room)
   - These two dimensions + clutter gate = 45% of composite, evaluated at the size buyers actually see

2. **Pass 2 — Full-resolution evaluation:**
   - Score Premium Positioning (15%)
   - Score Trust & Authenticity (15%)
   - Score Cultural Resonance (15%)
   - Score Brand Memorability (10%)
   - Check remaining gates (Seal, Product Visibility, BTD Citation, Cultural Depth)

This means **2 LLM calls per persona × mockup** instead of 1. The extra cost is justified because thumbnail performance was the #1 gap in Cycle 1.

### Scoring Calibration (NEW v1.1)

Add to every scoring prompt:

> "Use the full 1–10 scale. A score of 5 means 'mediocre — would not purchase.' A score of 7 means 'good but with clear weaknesses.' Reserve 9–10 for designs that are genuinely best-in-class. Do not default to 6–7."

After scoring, if more than 60% of a persona's scores across mockups fall in the 6–7 range, flag the evaluation as [UNDER-DIFFERENTIATED] and re-run with explicit instructions to spread scores.

### Scoring Protocol (Per Dimension)

For each dimension:

1. Persona identifies ≥1 BTD citation informing their evaluation
2. Persona scores dimension 1–10 with 1-sentence justification citing BTD
3. Persona assigns confidence (High/Medium/Low)
4. Scores without citations flagged [UNSUPPORTED]
5. Aggregation: persona-weighted × dimension-weighted × confidence-adjusted

### Aggregation Formula

composite = Σ(persona_weight × dimension_weight × score × confidence_multiplier) / normalization_factor

Where:
- High confidence: × 1.0
- Medium confidence: × 0.85
- Low confidence: × 0.70
- Normalization ensures composite is on 1–10 scale

## Anti-Patterns (Penalize)

- Generic supplement look: white bottle, clinical labeling
- Stock-photo heritage: generic farm imagery, amber grain fields
- Cultural appropriation: decorative Chinese motifs without authentic connection
- Ginseng Board seal too small or obscured
- Overcrowded label: too many elements competing for space
- Illegible at thumbnail: fine details that don't scale
- Dated aesthetics: 1990s clip-art feel, heavy borders, script overload
- **Information dump (v1.1):** More than 3 languages/scripts/text hierarchies on a single face. Bilingual is fine. Trilingual or bilingual+tagline+origin+certification is clutter.
- **Seal collision (v1.1):** Ginseng Board seal overlapping or competing with other badges, certifications, or decorative elements.
- **Cultural overload (v1.1):** Attempting to signal TCM, Didao, gifting, heritage, and modern wellness all on one label. Pick 2–3 cultural threads, not all 5.
- **Calligraphy as wallpaper (v1.1):** Using Chinese calligraphy as a background texture or decorative fill rather than as readable, meaningful text.
- **No product window on roots/powder (v1.1):** Opaque packaging for roots or powder SKUs where buyers need to see the product.

## Rewarded Patterns

- Clean hierarchy: brand → product → weight readable in 2 seconds
- Data-grounded scoring: every strength claim cites specific BTD entry
- Shelf standout: would visually separate from Dairyland, Zen, Hsu's in Amazon grid
- Premium material cues: matte finishes, foil accents, textured substrates
- Ginseng Board seal prominent and correct
- **Product visibility (v1.1):** Clear window showing actual product through packaging (roots, powder)
- Cross-cultural appeal: works for American premium AND Chinese diaspora
- **Visual breathing room (v1.1):** 30%+ whitespace on the primary label face
- **Typography hierarchy (v1.1):** Brand name is the dominant text element (2× point size of next-largest)
- Authenticity window: shows actual product through packaging

## Competitor Reference (for Brand Strategist persona)

| Brand | Composite Avg | Strengths | Weaknesses |
|-------|--------------|-----------|------------|
| Dairyland | 6.4 | Consistent system, strong shelf | Dated, weak premium, "Dairyland" confusion |
| Zen | 6.6 | Chinese-primary, gold accents, flag motif | Blends with category, weak mobile |
| Hsu's | 6.2 | Strong trust, bilingual | Busy layout, poor mobile, generic |
| Heil Current (Option A) | 4.8 | — | Below all competitors on every metric |

## Rubric Version Log

| Version | Date | Change |
|---|---|---|
| v1.1 | 2026-04-06 | Weight rebalance (Shelf+Mobile 35→45%, Trust+Premium 40→30%), Product Visibility Gate, Visual Clutter Gate, persona weight shifts (Skeptical+Mobile +5% each, Diaspora+Wellness -5% each), thumbnail-first evaluation, score calibration, anti-patterns expanded, Trust anchor redefined |
| v1.0 | 2026-04-06 | Initial packaging visual rubric for autoresearch visual loop |
