# SEO Loop — heilginseng.com

## Purpose

Optimize on-page SEO and AI/GEO readiness for heilginseng.com using a keep/discard loop.
One page or one element per run. Score before and after. Keep only if rubric score improves by >= 2 points.

## Baseline

- Traditional SEO score: **85%** (strong on-page fundamentals; room for structured data and content depth)
- AI/GEO readiness score: **30%** (significant gap; priority growth area for AI Overview, Perplexity, ChatGPT citations)

## Focus Areas

| Area | Priority | Opportunity |
|------|----------|-------------|
| Product page meta (title, description, H1) | High | Higher CTR from SERP |
| Collection page descriptions | High | Topical authority, collection SEO |
| Blog content optimization | High | Informational intent capture, assisted revenue |
| Schema markup (Product, FAQ, BreadcrumbList, Organization) | Critical | AI/GEO lift, rich results eligibility |
| Internal linking | Medium | Link equity distribution, crawlability |
| Alt text optimization | Medium | Image search, accessibility |
| Entity optimization | High (AI/GEO) | Named entity clarity for AI indexing |

## AI/GEO Opportunity (30% → 60%+ target)

AI/GEO (Generative Engine Optimization) is the primary growth lever. Heilginseng.com is likely underrepresented in AI Overview, Perplexity, and ChatGPT search because:
- Structured data is incomplete or missing on key product pages
- FAQ schema is not implemented on product or blog pages
- Entity signals for "American ginseng," "Wisconsin ginseng," "Marathon County ginseng" are weak
- Content does not follow the conversational Q&A structure AI models prefer to cite

### AI/GEO Actions (prioritize these):
1. Add `FAQPage` schema to all 4 product PDPs
2. Add `Product` schema with `brand`, `manufacturer`, `countryOfOrigin`, `offers` fields
3. Add `Organization` schema to home page with `sameAs` links to social profiles
4. Write FAQ sections using natural-language questions and complete-sentence answers
5. Use entity-rich language: "American ginseng (Panax quinquefolius)," "Marathon County, Wisconsin," "4th-generation family farm"
6. Add `BreadcrumbList` schema site-wide
7. Optimize for featured snippet eligibility: lead with the direct answer, then expand

## Iteration Protocol

Each loop run follows this exact sequence:

1. **Select target page** — pick from priority table or explicit run instruction
2. **Identify one optimization element** — meta title, meta description, H1, FAQ schema, Product schema, alt text, internal link, or blog section
3. **Capture baseline** — score current page using the SEO rubric; note any existing rankings in Google Search Console if available
4. **Draft variant** — write exactly one optimized version of the element
5. **Score variant** — apply rubric; calculate delta
6. **Keep or revert**:
   - Keep if: rubric score delta >= +2 points
   - Revert if: score does not improve by 2 points
7. **Validate** — run structured data through Google's Rich Results Test (for schema changes)
8. **Log** — append row to `results/seo.tsv`
9. **Output** — save draft to `outputs/autoresearch/seo/<YYYY-MM-DD>/`
10. **Post** — summary to #ginseng-autoresearch

## Editable Scope

Builders may optimize:

- **Product page meta**: `<title>`, `<meta name="description">`, H1, H2 structure
- **Collection descriptions**: intro paragraph, buyer-guide text, FAQ block
- **Blog content**: heading structure, intro paragraph, internal links, meta fields, FAQ schema block
- **Schema markup**: JSON-LD blocks for Product, FAQPage, BreadcrumbList, Organization
- **Alt text**: product image and lifestyle image alt attributes
- **Internal links**: anchor text and link target selection within blog and product content

Builders may NOT modify:

- Live theme files without a preview-tested diff
- Shopify's auto-generated canonical tags (Shopify controls these)
- Anything requiring Shopify admin → theme → live publish without a verified preview step
- Robots.txt or sitemap.xml without explicit approval

## Meta Title Formula

```
[Primary Keyword] — [Brand Differentiator] | Heil Ginseng
```

Examples:
- "American Ginseng Capsules — Wisconsin Farm-Grown | Heil Ginseng"
- "Buy American Ginseng Root — Marathon County, Wisconsin | Heil Ginseng"
- "American Ginseng Tea — 30 or 120 Count | Heil Ginseng"

Constraints:
- 50–60 characters (Google truncates at ~60)
- Include primary keyword in first 40 characters
- Always end with "| Heil Ginseng"

## Meta Description Formula

```
[Primary benefit] + [differentiator] + [CTA]. [Trust signal].
```

Examples:
- "4th-generation Wisconsin-grown ginseng capsules. No fillers, no additives. Order today — ships from Marathon County. Family-grown since 1904."
- "Premium American ginseng roots harvested in Marathon County, Wisconsin. Buy direct from the farm. 30-day satisfaction guarantee."

Constraints:
- 140–160 characters
- Include primary keyword naturally
- End with an action or trust signal

## FAQ Schema Template (JSON-LD)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is American ginseng used for?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "American ginseng (Panax quinquefolius) has been traditionally used to support energy, mental clarity, and overall well-being. It is not intended to treat, cure, or prevent any disease."
      }
    }
  ]
}
```

Rules:
- Questions must match natural-language searches
- Answers must be complete sentences with compliant health language
- Minimum 3 Q&A pairs per FAQPage block; maximum 10
- All answers must be visible on the page (not hidden in schema only)

## Compliance (SEO-specific)

- Meta descriptions: no disease treatment claims
- FAQ answers: use compliant qualifiers ("traditionally used to," "may support," "associated with")
- Schema `description` fields: same rules as on-page copy
- No "approved by FDA" or "clinically proven" language anywhere

## Artifact Storage

- Draft copy: `outputs/autoresearch/seo/<YYYY-MM-DD>/<page-handle>-<element>-v<NN>.md`
- Schema JSON: same path, `.json` extension
- Results log: `results/seo.tsv`

## Results Log Schema (TSV)

```
run_id  timestamp_utc  page_type  page_url  element_changed  baseline_score  variant_score  score_delta  onpage_score  content_score  technical_score  schema_score  aigeo_score  compliance_pass  keep_decision  draft_path  rich_results_test_pass  real_metric_window_start  real_metric_window_end  impressions_delta  clicks_delta  avg_position_delta  notes  rubric_version
```

## Max Variants Per Run

- 1 element per run
- Max 3 variants per element per page before moving on
- Revisit after 30 days with real metric data

## Keep Threshold

Rubric score delta >= +2 points (0–100 scale).

## Stop Conditions

- All rubric dimensions score above 80/100 for a given page
- 3 consecutive variants fail to improve by 2 points
- Real metric data shows no organic impression/click movement after 4 weeks

## Discord Reporting

Post to `#ginseng-autoresearch` after each run:
- Page and element optimized
- Baseline score vs variant score
- Keep or discard decision
- Any schema validation results
- Draft path if kept

## Real Metric Audit

- Weekly: Google Search Console → check impressions and CTR for optimized pages
- Monthly: Organic session trend from GA4 for optimized pages
- Monthly: Check AI Overview appearances in GSC (Search Appearance → AI Overviews)
- Log correlation findings in `results/seo.tsv` real_metric columns
