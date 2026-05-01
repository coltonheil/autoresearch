# Packaging Visual Autoresearch Loop — Program File

## Purpose

Run an iterative visual autoresearch loop for Heil Ginseng packaging mockups. Each cycle generates mockup variants, scores them through the BTD-grounded persona panel using `rubrics/packaging-visual.md`, keeps top performers, discards the rest, and logs everything to `results/packaging-visual.tsv`. The loop iterates 3 cycles (8 → 4 → 2) to converge on a final brand direction.

Nothing auto-activates. Final direction requires human approval.

## Relationship to Existing Programs

This program extends the text-only brand direction loop in `programs/packaging.md`. That loop narrowed 27 text concepts to a top 5. This loop takes visual mockups (generated from those top directions) through the same autoresearch architecture but with visual scoring.

The scoring rubric is `rubrics/packaging-visual.md` (v1.1) — NOT `rubrics/packaging-brand.md` (which scores text concepts) and NOT `rubrics/ad-creative-visual.md` (which scores Meta ad images).

**v1.1 changes:** Dimension weights rebalanced (Shelf+Mobile now 45%), new Product Visibility Gate and Visual Clutter Gate, persona weights shifted, thumbnail-first evaluation order, score calibration prompts.

## Loop Architecture

```
CYCLE 1: Broad Exploration (8 mockups)
├── Generate 8 mockup images from top brand directions
├── Score each through 6 personas (fresh context)
├── Apply hard gates (Seal, BTD Citation, Cultural Depth)
├── Log all scores to TSV
├── KEEP top 4, DISCARD bottom 4
└── Output: 4 kept mockups with full scorecards

CYCLE 2: Refinement (4 variants)
├── Generate 4 refined variants based on Cycle 1 keeps
│   ├── Variant prompts reference Cycle 1 TSV keep/discard log
│   ├── Each variant addresses specific weaknesses from Cycle 1
│   └── No more than 2 variants per kept direction
├── Score each through 6 personas (fresh context)
├── Apply hard gates
├── Log all scores to TSV
├── KEEP top 2, DISCARD bottom 2
└── Output: 2 finalists with full scorecards

CYCLE 3: Final Polish (2 finalists)
├── Generate 2 polished variants of finalists
│   ├── Address remaining weaknesses from Cycle 2
│   ├── Focus on Shelf Impact and Premium Positioning (weakest dimensions from prior cycles)
│   └── Consider color boldness, seal prominence, typography weight
├── Score each through 6 personas (fresh context)
├── Apply hard gates
├── Log all scores to TSV
├── Final ranking
└── Output: 1 recommended direction + 1 runner-up, both with full scorecards
```

## Generation Rules

### Identity Lock (Non-Negotiable)

1. **Ginseng Board seal must appear on every mockup.** Red ring with eagle emblem. Non-negotiable.
2. **Start from real product photos.** Reference images in `~/repos/heil-ad-intel-pipeline/reference_library/packaging/`
3. **No fabricated packaging.** Every mockup must be recognizably grounded in actual Heil product photography.
4. **Eagle seal cannot have red background.** The seal itself is red ring + eagle. Background behind seal must not be red.
5. **5 SKU families:** roots pouch (clear window), powder pouch (no window), capsules bottle (white, plain cap, tan capsules), tea box (horizontal), combo lineup.

### Mockup Generation Protocol

For each mockup in a cycle:

1. Select brand direction (from top 5 text scores or prior cycle keeps)
2. Select target SKU (rotate through SKU families)
3. Load reference photo from `reference_library/packaging/`
4. Generate mockup using image edit mode (conditioned on real photo)
5. Validate Ginseng Board seal presence before scoring
6. If seal missing or incorrect → regenerate (do not score)
7. Save to `outputs/autoresearch/packaging-visual/<YYYY-MM-DD>/cycle-N/`

### Generation Constraints (v1.1 — HARD RULES)

Every mockup MUST satisfy these constraints. If it doesn't, regenerate before scoring.

1. **Max 5 text blocks per face:**
   - Brand name (required)
   - Product name/type (required)
   - Weight/quantity (required)
   - ONE cultural/origin element (choose: bilingual name OR origin statement OR heritage tagline — not all three)
   - Ginseng Board seal (required, counts as visual element not text)

2. **30% minimum whitespace:** At least 30% of the primary label face must be negative space (no text, no illustration, no pattern). Visual breathing room is not optional.

3. **Typography hierarchy:** Brand name must be at least 2× the point size of the next-largest text element. If the brand name isn't the dominant text, the hierarchy is wrong.

4. **Product visibility (roots/powder/combo only):** A clear transparent window showing the actual product. Window must cover ≥10% of the front face. Not optional for these SKUs.

5. **Seal sizing:** Ginseng Board seal must render at minimum 8% of the label face area. Small enough to be tasteful, large enough for detection.

6. **Max 8 visual elements total** on the primary face. Count everything: seal, logo, illustration, pattern, window, border, icon, text block. If you hit 9, remove something.

### Cycle 1: Broad Exploration

Generate 8 mockups from the top brand directions identified in Phase 0.4:

| # | Brand Direction | SKU | Focus |
|---|----------------|-----|-------|
| 1 | B08 East Meets Midwest | Roots 8oz | Top text scorer, sage green palette |
| 2 | B08 East Meets Midwest | Powder 8oz | Same direction, different SKU |
| 3 | B02 Heritage Polish | Roots 8oz | #2 text scorer, heritage evolution |
| 4 | B02 Heritage Polish | Tea 30ct | Same direction, different SKU |
| 5 | B04 Gift First | Roots 8oz | Gift-focused positioning |
| 6 | C03 Hua Qi Shen | Roots 8oz | Top visual scorer, Chinese market |
| 7 | Modern Farm | Capsules 60ct | Clean minimal direction |
| 8 | B08 East Meets Midwest | Capsules 60ct | Top direction on capsules SKU |

### Cycle 2: Refinement

After Cycle 1 completes, generate 4 refined variants based on what was kept:

1. Take the top 2 kept directions from Cycle 1
2. For each direction, generate 2 variants:
   - Variant A: addresses the lowest-scoring dimension from Cycle 1
   - Variant B: amplifies the highest-scoring dimension from Cycle 1
3. Variant generation prompt MUST reference Cycle 1 TSV scores (what to fix / what to amplify)
4. But scoring prompt must use FRESH context (no Cycle 1 data in scoring prompt)

### Cycle 3: Final Polish

After Cycle 2 completes:

1. Take the top 2 finalists
2. For each, generate 1 polished variant addressing:
   - Shelf & Thumbnail Impact (historically weakest dimension across cycles)
   - Premium Positioning (second priority if shelf is already strong)
3. Consider: bolder color execution, larger brand name, stronger contrast, seal prominence
4. Score and rank final 2

## Scoring Protocol

### Fresh-Context Enforcement (CRITICAL)

Each persona evaluation is an INDEPENDENT LLM call containing ONLY:

```
[SYSTEM]
You are {persona_name}. {persona_definition}

Relevant buyer data:
{persona_btd_refs}

[USER]
Evaluate this packaging mockup for Heil Ginseng.
Score each dimension 1-10 with 1-sentence justification citing specific BTD data.
Assign confidence (High/Medium/Low) for each score.

Dimensions:
1. Premium Positioning (20%)
2. Trust & Authenticity (20%)
3. Shelf & Thumbnail Impact (20%)
4. Mobile Scannability (15%)
5. Cultural Resonance (15%)
6. Brand Memorability (10%)

[IMAGE: mockup]
```

**What is NOT in the prompt:**
- Cycle number
- Prior scores (own or other personas')
- Keep/discard history
- Other mockups in the cycle
- Generation parameters or prompts

**What IS in the generation prompt (not scoring prompt):**
- Cycle 1 TSV log (for Cycle 2 generation only)
- Specific weaknesses to address
- Prior mockup references (for edit mode)

### Model Selection

| Stage | Model | Rationale |
|-------|-------|-----------|
| Mockup generation | gemini-3.1-flash-image-preview | Fast, cheap, good quality |
| Persona scoring (all cycles) | glm-5.1 (zai/glm-5.1) | Consistent evaluation, good cultural depth |
| Cultural Depth review | glm-5.1 (zai/glm-5.1) | Same model, consistent calibration |

### Token Budget

| Stage | Estimated Tokens | Model |
|-------|-----------------|-------|
| Cycle 1: 8 generations | ~16K input | Flash image |
| Cycle 1: 48 persona scores (8 × 6) | ~24K input | GLM-5.1 |
| Cycle 2: 4 generations | ~8K input | Flash image |
| Cycle 2: 24 persona scores (4 × 6) | ~18K input | GLM-5.1 |
| Cycle 3: 2 generations | ~4K input | Flash image |
| Cycle 3: 12 persona scores (2 × 6) | ~9K input | GLM-5.1 |
| **Total** | **~79K tokens** | GLM-5.1 scoring |

## TSV Logging Format

File: `results/packaging-visual.tsv`

Columns:
```
cycle	mockup_id	brand_direction	sku	persona	dimension	score	confidence	btd_citations	seal_gate	btd_gate	cultural_gate	status	composite	notes	asset_path
```

Example rows:
```
1	PV-001-B08-roots	B08-east-meets-midwest	roots-8oz	premium_wellness	premium_positioning	8	high	BTD-002,BTD-015	PASS	PASS	-	keep	7.6	Strong heritage signals	outputs/autoresearch/packaging-visual/2026-04-07/cycle-1/pv-001.jpg
1	PV-001-B08-roots	B08-east-meets-midwest	roots-8oz	chinese_diaspora	cultural_resonance	9	high	BTD-001,BTD-003,BTD-004,BTD-022,BTD-023	PASS	PASS	PASS	keep	7.6	Didao positioning clear	outputs/autoresearch/packaging-visual/2026-04-07/cycle-1/pv-001.jpg
```

## Hard Gate Enforcement

Before any scoring:

1. Check Ginseng Board Seal Gate — if FAIL, regenerate mockup (do not score)
2. After scoring, check BTD Citation Gate — if FAIL, exclude from ranking
3. After scoring, check Cultural Depth Gate — if FAIL, de-weight Chinese Diaspora 50%
4. Log gate status in TSV for every persona × mockup evaluation

## Output Deliverables

After all 3 cycles complete:

1. **Final Recommendation** — 1 recommended direction + 1 runner-up
2. **Full Scorecards** — every mockup × persona × dimension × cycle
3. **TSV Log** — complete experiment log in `results/packaging-visual.tsv`
4. **Weakness Report** — what dimensions are consistently weakest across cycles
5. **Competitor Comparison** — how finalists compare to Dairyland, Zen, Hsu's composites
6. **Phase 0.5 Decision Package** — ready for Colton review

## Integration with Phase 0

This visual loop feeds into Phase 0.5 (Decision Package). The output:
- Supplements the Phase 0.4 text scores with visual validation
- Provides the missing visual taste panel data
- Creates a ranked visual bench that can be cross-referenced with text scores
- Identifies the final brand direction recommendation

## Program Version Log

| Version | Date | Change |
|---|---|---|
| v1.1 | 2026-04-06 | Generation constraints (5 text blocks max, 30% whitespace, typography hierarchy), v1.1 rubric reference, incremental TSV writes |
| v1.0 | 2026-04-06 | Initial visual autoresearch loop program |
