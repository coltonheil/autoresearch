# Packaging Brand Direction — Program File

## Purpose

Run an iterative brand direction autoresearch loop for Heil Ginseng packaging. Each loop cycle generates brand direction concepts, evaluates them through a modified taste panel grounded in BTD data, adversarially challenges the top performers, and narrows to a ranked set of finalists. Output is a ranked bench of top 5 brand direction scorecards ready for Phase 0.5 synthesis. Nothing auto-activates.

---

## Pipeline Stages

```
STAGE 1: Concept Generation
  ├── Generate 24–30 Brand Direction Briefs
  ├── Forced distribution: Option A (6–8), Option B (10–12), Option C (8–10)
  ├── Each brief: option, name, positioning, visual language, target segment, shelf hypothesis, gift hypothesis, cost tier, key risk
  └── Output: concept pool with mandatory option representation

STAGE 2: Panel Evaluation — Round 1
  ├── Load 6 modified personas with BTD-grounded weights
  ├── Each persona scores each concept on 6 dimensions (1–10)
  ├── Enforce BTD Citation Gate: every evaluation cites ≥1 BTD entry
  ├── Enforce Cultural Depth Gate: Chinese Diaspora cites ≥5 cultural data points
  ├── Flag unsupported scores [UNSUPPORTED]
  ├── Compute confidence-weighted composites
  └── Output: full evaluation matrix, ranked by composite

STAGE 3: Adversarial Challenge
  ├── Take top 8 concepts from Round 1
  ├── For each: identify strongest counter-argument citing BTD or competitive audit
  ├── Original personas respond to counter-argument
  ├── Adjust scores up or down based on exchange
  ├── Record all arguments and adjustments
  └── Output: adversarial challenge log, adjusted rankings

STAGE 4: Narrowing to Top 5
  ├── Re-rank based on post-adversarial scores
  ├── Select top 5 with mandatory representation:
  │   ├── At least 1 concept from Option A
  │   ├── At least 1 concept from Option B
  │   └── At least 1 concept from Option C
  ├── If forced inclusion needed, replace lowest-ranked concepts
  ├── Produce Direction Scorecard for each finalist
  └── Output: top 5 scorecards, evaluation matrix, TSV log
```

---

## Modified Personas

Each persona is grounded in BTD segments with specific evaluation focus and minimum citation requirements.

| Persona ID | Name | Weight | Focus | BTD Min Citations |
|-----------|------|--------|-------|-------------------|
| `traditional_health` | Traditional Health Buyer | 15% | Heritage, trust, generational messaging | ≥1 per concept |
| `premium_gift` | Premium Gift Buyer | 20% | Premium feel, gifting story, cultural presentation | ≥1 per concept |
| `active_wellness` | Active Wellness Seeker | 15% | Natural, botanical, clean, modern wellness | ≥1 per concept |
| `amazon_discovery` | Amazon Discovery Buyer | 20% | Shelf impact, reviews, price-value, 3-second scan | ≥1 per concept |
| `chinese_diaspora` | Chinese Diaspora Buyer | 20% | Didao, provenance, TCM, gifting culture, root morphology | ≥5 per concept |
| `brand_strategist` | Brand Strategist | 10% | Differentiation, scalability, market fit, cost-feasibility | ≥1 per concept |

### Persona Detail

**Traditional Health Buyer** (15%)
- Grounded in: BTD Traditional segment + Meta "Tom" persona data
- Values: heritage, tradition, proven efficacy, generational knowledge
- Suspicious of: change for change's sake, over-modernization, loss of farm identity
- Key BTD refs: BTD-001, BTD-004, BTD-023, BTD-026, BTD-033, BTD-041, BTD-042
- Special instruction: Must articulate why a rebrand would/wouldn't alienate this buyer

**Premium Gift Buyer** (20%)
- Grounded in: BTD Gift segment + Chinese buyer research
- Values: premium presentation, story worth telling, cultural appropriateness, gift-worthiness
- Suspicious of: generic packaging, budget appearance, anything that "doesn't look like a gift"
- Key BTD refs: BTD-010, BTD-011, BTD-012, BTD-013, BTD-017, BTD-038
- Special instruction: Evaluates gifting presentation across cultural contexts. MUST cite Chinese buyer research.

**Active Wellness Seeker** (15%)
- Grounded in: BTD Wellness segment + Meta "Wendy" data
- Values: modern wellness aesthetic, ingredient transparency, ritual integration, Instagram-worthy
- Suspicious of: dated aesthetics, clinical supplement look, heritage-heavy (wants modern heritage)
- Key BTD refs: BTD-002, BTD-015, BTD-027, BTD-029, BTD-035, BTD-042
- Special instruction: Compares to Ritual/AG1 aesthetic standard from competitive audit

**Amazon Discovery Buyer** (20%)
- Grounded in: BTD Amazon segment + Helium10 data
- Values: 3-second shelf impact, clear differentiation, review-friendly presentation, price-value signal
- Suspicious of: anything that blends into the grid, unclear product identity, premium pricing without visual justification
- Key BTD refs: BTD-048, BTD-050, BTD-051, BTD-052, BTD-053, BTD-055, BTD-058
- Special instruction: Evaluates purely from Amazon search grid perspective. "Would this stand out next to Zen and Dairyland?"

**Chinese Diaspora Buyer** (20%)
- Grounded in: BTD Chinese Diaspora segment (all 4 sub-segments)
- Values: Didao authenticity (BTD-003), GBW seal (BTD-005), root morphology knowledge (BTD-006), Wisconsin provenance (BTD-004, BTD-009), gifting cultural norms (BTD-010-013), TCM literacy (BTD-001, BTD-022)
- Suspicious of: cultural appropriation, decorative Chinese characters without meaning, ignorance of gifting norms, any direction that treats Chinese culture as exotic aesthetic
- Key BTD refs: BTD-003, BTD-004, BTD-005, BTD-006, BTD-009, BTD-010, BTD-011, BTD-012, BTD-013, BTD-018, BTD-019, BTD-020, BTD-022, BTD-023
- Special instruction: MUST reference ≥5 distinct cultural data points per concept evaluation. Evaluates across all 4 sub-segments (recent immigrants, 1.5-2nd gen, international students, cross-cultural gift buyers).

**Brand Strategist** (10%)
- Grounded in: Competitive audit + cost-benefit analysis
- Values: strategic coherence, market differentiation, cost-feasibility alignment, long-term scalability
- Suspicious of: short-term thinking, aesthetic novelty without strategic foundation, scope creep potential
- Key BTD refs: BTD-051, BTD-052 (market sizing) + competitive audit whitespace + cost-benefit analysis
- Special instruction: Evaluates whether the direction creates a defensible brand position, not just a nice aesthetic

---

## Concept Generation Template

Each Brand Direction Brief follows this format:

```
concept_id: [unique ID, e.g., "A-01", "B-07", "C-04"]
option: [A | B | C]
concept_name: [descriptive name, e.g., "Heritage Refined", "Wisconsin Modern"]
positioning_statement: [1 sentence defining the brand's market position]
visual_language:
  colors: [primary palette description]
  typography: [type style description]
  imagery: [imagery approach description]
  mood: [3-5 adjectives describing the feel]
target_primary_segment: [primary buyer segment from BTD]
target_secondary_segments: [other segments with moderate appeal]
amazon_shelf_hypothesis: [how this performs in Amazon search grid, citing competitive audit]
chinese_gift_hypothesis: [how this performs for Chinese gift market, citing BTD cultural data]
cost_tier: [low | medium | high — from Phase 0.3 analysis]
key_risk: [1-2 sentences on the primary risk of this direction]
differentiation_mechanism: [what specifically makes this different from every competitor]
```

---

## Loop Architecture

```
OUTER LOOP (brand direction evaluation)
  ├── Load BTD, competitive audit, cost-benefit analysis
  ├── Load panel config (personas, dimensions, weights, gates)
  ├── Generate concept pool (24–30 briefs, forced distribution)
  └── Run inner stages sequentially

STAGE 2 (panel evaluation)
  For each concept:
    For each persona:
      1. Read Brand Direction Brief
      2. Identify ≥1 BTD citation informing evaluation
      3. Score each dimension 1–10 with justification
      4. Assign confidence level per score
      5. Chinese Diaspora: verify ≥5 cultural citations
    Compute confidence-weighted composite
    Check BTD Citation Gate (PASS/FAIL)
    Check Cultural Depth Gate (PASS/FAIL)
    If either gate FAIL → exclude from ranking, mark [EXCLUDED]
  Rank all concepts by composite score

STAGE 3 (adversarial challenge)
  For top 8 concepts:
    1. Adversarial Reviewer identifies strongest counter-argument
    2. Counter-argument cites BTD or competitive audit data
    3. Original personas respond to counter-argument
    4. Scores may adjust up or down (max ±1.5 per dimension)
    5. Record all arguments and adjustments in adversarial log
  Re-rank based on adjusted scores

STAGE 4 (narrowing)
  1. Select top 5 by post-adversarial composite
  2. Verify mandatory representation:
     - At least 1 from Option A
     - At least 1 from Option B
     - At least 1 from Option C
  3. If any option unrepresented:
     - Force-include highest-scoring concept from missing option
     - Replace lowest-ranked concepts (4th/5th position)
  4. Produce Direction Scorecard for each finalist
  5. Log all results to TSV

OUTPUT
  - Full evaluation matrix (all concepts × all personas × all dimensions)
  - Top 5 direction scorecards with adversarial challenge summary
  - Adversarial challenge log
  - Option distribution analysis
  - Results TSV log
```

---

## Scoring Dimensions

| Dimension ID | Name | Weight |
|-------------|------|--------|
| `premium_positioning` | Premium Positioning Credibility | 20% |
| `buyer_resonance` | Buyer Segment Resonance | 25% |
| `competitive_diff` | Competitive Differentiation | 15% |
| `cross_channel` | Cross-Channel Versatility | 10% |
| `cultural` | Cultural Appropriateness | 15% |
| `feasibility` | Implementation Feasibility | 15% |

Reference: `rubrics/heil-ginseng/packaging-brand.md` (current: v1.0)

---

## Keep / Discard Rules

| Condition | Action |
|---|---|
| BTD Citation Gate FAIL | Exclude from ranking, mark `[EXCLUDED-NO-CITE]`, log raw scores |
| Cultural Depth Gate FAIL | De-weight Chinese Diaspora scores by 50%, flag `[LOW-CULTURAL-DEPTH]` |
| Composite ≥ 8.0 AND both gates PASS | Top candidate — advance to adversarial challenge |
| Composite 6.5–7.9 AND both gates PASS | Keep — rank in pool |
| Composite < 6.5 | Discard — log with reason |
| After adversarial, composite drops below 6.5 | Discard from top pool |
| Forced representation needed | Replace 4th/5th ranked with highest from unrepresented option |

---

## Logging

Append every concept evaluation (kept AND excluded) to:
```
~/repos/autoresearch/results/heil-ginseng/packaging-brand.tsv
```

Schema:
```
run_id	timestamp_utc	concept_id	option	category	concept_name	panel_composite	premium_positioning_score	buyer_resonance_score	competitive_diff_score	cross_channel_score	cultural_score	feasibility_score	btd_citation_gate	cultural_depth_gate	adversarial_challenged	adversarial_adjustment	final_rank	top_5	status	notes	rubric_version	commit_sha	branch
```

---

## Run Reporting

Write run summaries to the result log and run artifact directory.

Summary format:
```
Brand Direction Autoresearch - Phase 0.4 [Date]
Generated [N] concepts (A:[a] | B:[b] | C:[c]).
Round 1 panel: [K] kept, [D] discarded, [E] excluded (gate fail).
Top 8 adversarially challenged.
Top 5: [list concept names with option tags]
Mandatory representation: Option A ✅ | Option B ✅ | Option C ✅
Pending: Phase 0.5 synthesis before Colton review.
```

---

## Rubric File
- `rubrics/heil-ginseng/packaging-brand.md`

## Results File
- `results/heil-ginseng/packaging-brand.tsv`

## Output Path
- `~/.openclaw/workspace/outputs/taste-panel-program/phase-0/`

## Branch Convention
- `autoresearch/packaging-brand-<yyyy-mm-dd>-r<nn>`
