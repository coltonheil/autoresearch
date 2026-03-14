# Site Performance Rubric — heilginseng.com

Version: 1.0 | Weights sum: 100

## Scoring Overview

Score each run 0–100 using the weighted dimensions below.
Apply to both baseline and variant. Delta = variant_score − baseline_score.

| Dimension | Weight | Good (full points) | Poor (0 pts) |
|-----------|--------|--------------------|--------------|
| LCP | 30% | < 2.5s | ≥ 4.0s |
| CLS | 20% | < 0.1 | ≥ 0.25 |
| INP | 20% | < 200ms | ≥ 500ms |
| Total Blocking Time (TBT) | 15% | < 200ms | ≥ 600ms |
| Speed Index | 15% | < 3.4s | ≥ 5.8s |

**Total weight: 100%**

---

## Dimension Scoring Guides

### LCP — Largest Contentful Paint (weight: 30)

| LCP Value | Points (out of 30) |
|-----------|-------------------|
| < 1.8s | 30 |
| 1.8s – 2.49s | 24 |
| 2.5s – 3.0s | 18 |
| 3.0s – 3.9s | 10 |
| ≥ 4.0s | 0 |

LCP element should be the hero image or H1 on product pages. Penalize if LCP element is a background image or offscreen resource.

**Bonus (+2, max 30):** Hero image is preloaded with `<link rel="preload">` and served as WebP/AVIF.

---

### CLS — Cumulative Layout Shift (weight: 20)

| CLS Value | Points (out of 20) |
|-----------|-------------------|
| < 0.05 | 20 |
| 0.05 – 0.09 | 17 |
| 0.1 – 0.14 | 12 |
| 0.15 – 0.24 | 6 |
| ≥ 0.25 | 0 |

Common CLS sources on Shopify: images without explicit `width`/`height`, late-loading fonts, app banners injecting above content, sticky headers with dynamic height.

---

### INP — Interaction to Next Paint (weight: 20)

| INP Value | Points (out of 20) |
|-----------|-------------------|
| < 100ms | 20 |
| 100ms – 199ms | 17 |
| 200ms – 299ms | 12 |
| 300ms – 499ms | 6 |
| ≥ 500ms | 0 |

INP measures responsiveness. On Shopify, primary sources of high INP: third-party scripts running on main thread, heavy Liquid section JS, non-deferred app scripts.

---

### Total Blocking Time — TBT (weight: 15)

| TBT Value | Points (out of 15) |
|-----------|-------------------|
| < 100ms | 15 |
| 100ms – 199ms | 13 |
| 200ms – 349ms | 9 |
| 350ms – 599ms | 4 |
| ≥ 600ms | 0 |

TBT correlates directly with INP in lab conditions. Reduce by deferring/asyncing non-critical JS and removing unused app scripts.

---

### Speed Index (weight: 15)

| Speed Index | Points (out of 15) |
|-------------|-------------------|
| < 2.0s | 15 |
| 2.0s – 3.39s | 12 |
| 3.4s – 4.49s | 8 |
| 4.5s – 5.79s | 3 |
| ≥ 5.8s | 0 |

Speed Index reflects visual completeness rate. Improve by inlining critical CSS and optimizing render-blocking resources.

---

## Composite Score Formula

```
score = (lcp_points + cls_points + inp_points + tbt_points + si_points)
```

Maximum score: 100 (plus up to 2 bonus points on LCP, capped at 30).

---

## Keep Threshold

**Keep the change if:**
- `variant_score − baseline_score >= 1` (at minimum 1 point improvement)
- AND no individual Core Web Vital dimension (LCP, CLS, INP) regresses by more than 5% in absolute metric value

**Revert if:**
- Score does not improve by at least 1 point
- OR any CWV regresses: LCP worsens > 0.125s, CLS worsens > 0.01, INP worsens > 10ms

---

## Visual Regression Gate (non-scored, binary pass/fail)

Before logging a keep decision, confirm:
- Hero image still renders correctly
- Product title and price still visible above fold on mobile
- No missing or broken layout sections
- No console errors introduced by the change

A visual regression failure forces a revert regardless of score delta.

---

## Measurement Protocol

- Run Lighthouse CLI with `--preset=perf --form-factor=mobile`
- Run 3 times per measurement; take the median for each metric
- Use PageSpeed Insights API for field CWV correlation (CrUX data) when available
- Record both lab (Lighthouse) and field (CrUX) values in the TSV

---

## Rubric Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-03-09 | Initial rubric. Weights: LCP 30, CLS 20, INP 20, TBT 15, SI 15. |
