# Site Performance Loop — heilginseng.com

## Purpose

Optimize Core Web Vitals and page payload on heilginseng.com using a keep/discard loop.
One bottleneck per run. Score before and after. Keep only if the proxy score improves without other vitals regressing.

## Target Site

- Store: heilginseng.com (Shopify)
- Platform: Shopify (Liquid theme)
- Priority pages: Home, Capsules PDP, Roots PDP, Tea PDP, Powder PDP, Collections

## Core Web Vitals Targets

| Metric | Good Threshold | Poor Threshold |
|--------|---------------|----------------|
| LCP (Largest Contentful Paint) | < 2.5s | > 4.0s |
| CLS (Cumulative Layout Shift) | < 0.1 | > 0.25 |
| INP (Interaction to Next Paint) | < 200ms | > 500ms |
| TBT (Total Blocking Time) | < 200ms | > 600ms |
| Speed Index | < 3.4s | > 5.8s |

## Iteration Protocol

Each loop run follows this exact sequence:

1. **Identify one bottleneck** — pick the single lowest-scoring dimension from the rubric on the target page
2. **Capture baseline** — run Lighthouse CLI and record all metric values
3. **Implement one fix** — change exactly one thing (see scope below)
4. **Measure** — re-run Lighthouse (minimum 3 runs, median the results)
5. **Score** — apply rubric; calculate delta
6. **Keep or revert**:
   - Keep if: rubric score improves AND no Core Web Vital regresses by more than 5%
   - Revert if: any CWV worsens or score does not improve
7. **Log** — append row to `results/site-performance.tsv`
8. **Post** — summary to #ginseng-autoresearch

## Editable Scope

Builders may modify:

- **Theme Liquid**: section render order, lazy-load attributes, defer/async on script tags, noscript fallbacks
- **Image optimization**: convert to WebP/AVIF, add `width`/`height` attributes, implement `loading="lazy"` on below-fold images, preload hero image
- **Third-party script loading**: defer non-critical scripts (chat widgets, pixels, analytics), move to bottom of body, use `async` where safe
- **CSS**: inline critical CSS, defer non-critical stylesheets, remove unused CSS blocks
- **Font loading**: add `font-display: swap`, preconnect to Google Fonts, subset fonts

Builders may NOT modify:

- Shopify checkout pages (owned by Shopify)
- App-injected scripts without explicit app config access
- Any live theme setting that changes product pricing or inventory display
- Anything requiring Shopify admin → theme → live publish without a verified preview step

## Tools

### Lighthouse CLI (primary)
```bash
# Install if missing
npm install -g lighthouse

# Run against a page (use mobile preset for field CWV correlation)
lighthouse https://heilginseng.com --preset=perf --output=json --output-path=./results/lh-home-$(date +%Y%m%d-%H%M).json

# Useful flags
--form-factor=mobile
--throttling-method=simulate
--only-categories=performance
```

### PageSpeed Insights API
```bash
# Requires PAGESPEED_API_KEY in master.env
source ~/.openclaw/.secrets/master.env

curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://heilginseng.com&strategy=mobile&key=${PAGESPEED_API_KEY}" \
  | jq '.lighthouseResult.categories.performance.score, .lighthouseResult.audits["largest-contentful-paint"].displayValue'
```

### WebPageTest (secondary, for waterfall analysis)
- Use webpagetest.org for waterfall charts when diagnosing render-blocking resources
- Save waterfall screenshots to `outputs/autoresearch/site-performance/<YYYY-MM-DD>/`

## Artifact Storage

- Lighthouse JSON: `outputs/autoresearch/site-performance/<YYYY-MM-DD>/lighthouse-<page>-<before|after>.json`
- Lighthouse HTML: same path, `.html` extension
- Waterfall screenshots: same path, `.png`
- Theme diff: `outputs/autoresearch/site-performance/<YYYY-MM-DD>/theme-diff-<runid>.patch`

## Baseline Capture

Before any run, capture and store:
- Lighthouse mobile score and all metric values for target page
- PageSpeed Insights field data if available (CrUX)
- Page weight breakdown (images, JS, CSS, fonts, HTML)

Store as: `outputs/autoresearch/site-performance/<YYYY-MM-DD>/baseline-<page>.json`

## Keep / Revert Decision

**Keep if ALL of the following:**
- Rubric score delta >= +1 point (0-100 scale)
- LCP does not worsen by more than 5% vs baseline
- CLS does not worsen (absolute increase < 0.01)
- INP does not worsen by more than 5% vs baseline

**Revert if ANY of the following:**
- Rubric score does not improve
- Any Core Web Vital regresses beyond the tolerance above
- Visual regression detected (layout broken, images missing, text obscured)

## Branch Convention

- Branch format: `autoresearch/site-performance-<YYYY-MM-DD>-r<NN>`
- Example: `autoresearch/site-performance-2026-03-09-r01`
- Do not merge automatically. Await Colton review for live theme changes.

## Max Variants Per Run

- 1 fix per run
- Max 3 runs before requiring a human review of the pattern

## Stop Conditions

- Score plateaus at or above Good threshold on all Core Web Vitals
- 3 consecutive runs fail to improve any dimension
- A regression is detected and the revert cannot restore the baseline

## Results Log

Append every run to `results/site-performance.tsv`.
Schema: see AUTORESEARCH-STRATEGY.md §9.3.

## Discord Reporting

Post to `#ginseng-autoresearch` after each run:
- Page tested
- Metric changed (e.g., LCP before → after)
- Keep or revert decision
- Rubric score delta
- Link to Lighthouse report artifact

## Real Metric Audit

- Weekly: check Google Search Console Core Web Vitals report for field data movement
- Monthly: check if performance score improvements correlate with conversion rate or organic session changes
- Log correlation findings in `results/site-performance.tsv` real_metric columns
