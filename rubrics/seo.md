# SEO Rubric — heilginseng.com

Version: 1.0 | Weights sum: 100
Baseline: Traditional SEO 85% | AI/GEO readiness 30%

## Scoring Overview

Score each page or element 0–100 using the weighted dimensions below.
Apply to both baseline and variant. Delta = variant_score − baseline_score.

| Dimension | Weight | Scores |
|-----------|--------|--------|
| On-page optimization | 25% | 0–25 |
| Content quality | 25% | 0–25 |
| Technical SEO | 20% | 0–20 |
| Schema / structured data | 15% | 0–15 |
| AI/GEO readiness | 15% | 0–15 |

**Total weight: 100%**

---

## Dimension Scoring Guides

### On-Page Optimization (weight: 25)

Score the meta title, meta description, H1, H2 structure, and keyword presence.

| Criteria | Points |
|----------|--------|
| Primary keyword in `<title>`, within first 40 characters | 0–5 |
| Title length 50–60 characters, ends with "| Heil Ginseng" | 0–4 |
| Meta description 140–160 characters, includes primary keyword and CTA/trust signal | 0–4 |
| H1 matches primary search intent; only one H1 per page | 0–4 |
| H2s create logical content sections; at least 2 H2s on PDPs | 0–3 |
| Primary keyword appears in first 100 words of body copy naturally | 0–3 |
| Internal links present with descriptive anchor text (not "click here") | 0–2 |

**Max: 25 points**

---

### Content Quality (weight: 25)

Score the depth, clarity, and search intent coverage of the page content.

| Criteria | Points |
|----------|--------|
| Content directly answers the primary search intent (transactional, informational, or navigational) | 0–6 |
| Product/topic benefits explained with specificity (not generic filler) | 0–5 |
| Farm-origin, Wisconsin/Marathon County, and Panax quinquefolius entity signals present where appropriate | 0–4 |
| FAQ section present with natural-language questions and complete-sentence answers | 0–4 |
| Content length appropriate for the page type (PDP: 300+ words; blog: 800+ words; collection: 200+ words) | 0–3 |
| No keyword stuffing; reading naturally at <= 2% keyword density | 0–3 |

**Max: 25 points**

---

### Technical SEO (weight: 20)

Score technical hygiene elements.

| Criteria | Points |
|----------|--------|
| Canonical tag present and pointing to correct URL | 0–4 |
| Page is indexable (no noindex meta tag or X-Robots-Tag) | 0–4 |
| Image alt text present on all product images; descriptive, not empty or "image" | 0–4 |
| Page load score >= 70 on Lighthouse mobile (from site-performance rubric) | 0–3 |
| Mobile-friendly layout confirmed (Shopify responsive theme baseline pass) | 0–3 |
| No broken internal links on the page | 0–2 |

**Max: 20 points**

---

### Schema / Structured Data (weight: 15)

Score JSON-LD implementation quality and completeness.

| Criteria | Points |
|----------|--------|
| `Product` schema present on PDP pages with: `name`, `description`, `brand`, `offers` (price, priceCurrency, availability) | 0–4 |
| `FAQPage` schema present on pages with FAQ sections; answers visible on-page | 0–3 |
| `BreadcrumbList` schema present and accurate | 0–2 |
| `Organization` schema on home page with `sameAs` links to social profiles | 0–2 |
| Schema validates with no errors in Google Rich Results Test | 0–2 |
| No schema errors flagged in Google Search Console (if field data available) | 0–2 |

**Max: 15 points**

PDPs that are missing Product schema score 0/4 on that criteria. FAQPage schema on pages without a visible FAQ section also scores 0 (schema must reflect visible content).

---

### AI/GEO Readiness (weight: 15)

Score the page's readiness to be cited by AI Overviews, Perplexity, ChatGPT, and other generative search engines.

| Criteria | Points |
|----------|--------|
| Content uses complete, self-contained answer sentences (not just fragments or bullets) | 0–3 |
| Named entities used consistently: "American ginseng (Panax quinquefolius)," "Marathon County, Wisconsin," "4th-generation family farm" | 0–3 |
| FAQ section formatted as direct question + complete answer (cited-snippet-ready format) | 0–3 |
| Schema data provides AI-parseable structured context (Product, FAQPage, Organization) | 0–3 |
| Content written in authoritative, factual tone (not promotional hype) appropriate for AI citation | 0–3 |

**Max: 15 points**

The AI/GEO baseline for heilginseng.com is 30%. This rubric dimension should be the primary growth target for loop runs until the score reaches 60%+.

Entity optimization tips for ginseng:
- Use "American ginseng" not just "ginseng" (disambiguate from Asian ginseng)
- Include "Panax quinquefolius" at least once per page
- Reference geographic specificity: Marathon County, Wisconsin, Edgar Wisconsin
- Reference farm history when appropriate: "family-grown since 1904," "4th generation"

---

## Composite Score Formula

```
score = onpage_score + content_score + technical_score + schema_score + aigeo_score
```

Maximum: 100 points.

---

## Keep Threshold

**Keep the variant if:**
- `variant_score − baseline_score >= 2` (minimum 2-point improvement)
- AND compliance language is clean (no disease treatment claims in updated content)

**Discard if:**
- Score improvement < 2 points
- OR schema validation fails (Rich Results Test error introduced)
- OR health claim compliance issue introduced

---

## Compliance Gate

Any content change that introduces health claims must be reviewed:
- Compliant qualifiers required: "traditionally used to," "may support," "associated with"
- Prohibited: "treats," "cures," "prevents," "FDA approved," "clinically proven"
- Schema `description` fields follow the same rules as on-page copy

A compliance violation in any kept variant triggers a Ben review before the change can be implemented live.

---

## Validation Protocol

For schema changes:
1. Test JSON-LD against: https://search.google.com/test/rich-results
2. Record pass/fail in `results/seo.tsv` field `rich_results_test_pass`
3. If fail: discard regardless of rubric score improvement

For meta/copy changes:
1. Preview in SERP simulator (describe character counts and truncation risk)
2. Confirm no orphaned keywords or awkward truncation at 60 chars (title) or 160 chars (description)

---

## Priority Scoring Notes

- AI/GEO readiness (15%) is the highest-priority growth dimension given the 30% baseline; weight all loop runs toward improving this dimension first
- Schema/structured data (15%) is the fastest path to AI/GEO improvement; prioritize FAQPage and Product schema
- On-page optimization (25%) is already at 85% traditional SEO baseline; marginal gains here compound with AI/GEO improvements

---

## Rubric Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-03-09 | Initial rubric. Weights: on-page 25, content 25, technical 20, schema 15, AI/GEO 15. Baseline: Traditional 85%, AI/GEO 30%. |
