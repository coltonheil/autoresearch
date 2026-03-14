# Data Chief Pipeline Integrity Rubric

Version: 2.0 | Weights sum: 100

## Scoring Overview

Score each run 0–100 using the weighted dimensions below.
Apply the rubric to both baseline and variant. Delta = `variant_score - baseline_score`.

| Dimension | Weight | Good (full points) | Poor (0 pts) |
|-----------|--------|--------------------|--------------|
| Data integrity and believability | 35% | Hero customers have populated, believable, cross-consistent business data | Core demo records are empty, zeroed, or tell an incoherent story |
| API availability and status | 15% | Every target API returns 200 | Any core target API fails |
| API response structure | 15% | Required keys and non-empty shapes are present | Core shapes are missing or empty |
| Trust narrative completeness | 15% | Both trust narratives (Connector→Librarian→P&L and P&L→Repricing) are fully traceable | Key links in the trust chain are broken or missing |
| Page route availability | 10% | Every target page returns 200 | Any target page fails |
| Error hygiene | 10% | No tested API returns a top-level `error` | Top-level `error` appears on tested route |

**Total weight: 100%**

---

## Dimension Scoring Guides

### 1) Data Integrity and Believability — weight: 35

This is the heaviest dimension because Data Chief only works if a PE operating partner looks at the numbers and believes them. "Records exist" is not enough. The numbers must tell a coherent, believable story for a field service business.

Core checks:

**Connector believability:**
- Connector `total_records` values are greater than 0 for every connector
- Record counts are in a realistic range (hundreds to thousands, not single digits for a field service company)

**Customer population:**
- Customer list returns at least 25 customers
- Hero customers (CUST-1001, CUST-1023, CUST-1037) all appear with non-empty names

**P&L believability:**
- P&L rows exist for all three hero customers
- P&L line items have non-zero dollar amounts
- P&L line items reference named source systems (not null or generic placeholders)
- Revenue and cost figures are in a plausible range for field service ($1K–$500K per customer)

**Repricing justification:**
- Repricing data exists for all three hero customers
- Each repricing recommendation includes a current rate and a recommended rate
- The delta between current and recommended is non-zero

**Librarian activity:**
- Librarian events exist
- At least one event is auto-confirmed
- Events have non-empty explanation text

**Trust and source provenance:**
- Trust source inventory returns positive record counts for every source system
- Source systems have recognizable names (not raw connector IDs)

**Cross-surface consistency:**
- Summary metrics revenue for a hero customer is broadly consistent with that customer's P&L total (within 20%)
- If summary metrics show N jobs, the customer should have P&L entries that plausibly represent N jobs

| Condition | Points (out of 35) |
|-----------|--------------------|
| All integrity and believability checks pass | 35 |
| 1–2 checks fail (minor gaps) | 26 |
| 3–4 checks fail (noticeable holes in the story) | 17 |
| 5–6 checks fail (operators would question the data) | 8 |
| 7+ checks fail (the data doesn't tell a believable story) | 0 |

**Believability rule:** If a route technically returns data but the numbers don't make business sense (all customers with identical revenue, $0 margin on every line item, record counts of 1), treat it as an integrity failure even if the structure is correct.

---

### 2) API Availability and Status — weight: 15

Target APIs:
- `/api/v1/customers`
- `/api/v1/connectors`
- `/api/v1/librarian/events`
- `/api/v1/trust/CUST-1001`
- `/api/v1/customers/CUST-1001/pnl`
- `/api/v1/customers/CUST-1001/summary-metrics`
- `/api/v1/repricing?customer_id=CUST-1001`
- `/api/v1/repricing?customer_id=CUST-1023`
- `/api/v1/repricing?customer_id=CUST-1037`

| Condition | Points (out of 15) |
|-----------|--------------------|
| All target APIs return 200 | 15 |
| 1 target API fails | 10 |
| 2 target APIs fail | 6 |
| 3 target APIs fail | 2 |
| 4+ target APIs fail | 0 |

This dimension is about reachability and route health, not business-value completeness.

---

### 3) API Response Structure — weight: 15

Core expectations:
- `/api/v1/customers` returns `data` as a non-empty array
- `/api/v1/connectors` returns `data` as a non-empty array
- `/api/v1/librarian/events` returns `data` as a non-empty array
- `/api/v1/customers/CUST-1001/pnl` returns `data.rows` with at least one row
- `/api/v1/trust/CUST-1001` returns `source_inventory` with at least one row
- `/api/v1/customers/CUST-1001/summary-metrics` returns `data` as a non-empty object
- Repricing endpoints return non-empty `data` arrays for all hero customers

| Condition | Points (out of 15) |
|-----------|--------------------|
| All structure checks pass | 15 |
| 1 structure check fails | 10 |
| 2 structure checks fail | 6 |
| 3 structure checks fail | 2 |
| 4+ structure checks fail | 0 |

A structurally valid API that returns empty business data should not receive full credit here. But the primary penalty for empty-but-structured responses lives in the data integrity dimension.

---

### 4) Trust Narrative Completeness — weight: 15

This dimension checks whether the two core trust narratives are actually traceable end-to-end:

**Narrative 1: Connectors → Librarian → P&L**
- Connectors show named source systems with positive record counts
- Librarian events reference specific source systems and conflicts
- P&L line items trace back to named source systems
- The chain from "data entered the system" to "data appears in the P&L" is followable

**Narrative 2: P&L → Repricing**
- P&L shows current margin data
- Repricing recommendations reference that margin data
- The chain from "here's what the customer costs" to "here's why we recommend this price" is followable

| Condition | Points (out of 15) |
|-----------|--------------------|
| Both narratives are fully traceable end-to-end | 15 |
| One narrative is complete, the other has minor gaps | 11 |
| Both narratives have gaps but are partially followable | 7 |
| One narrative is broken, the other is partial | 3 |
| Neither narrative is traceable | 0 |

---

### 5) Page Route Availability — weight: 10

Target pages:
- `/connectors`
- `/librarian`
- `/customers`
- `/customers/CUST-1001`
- `/customers/CUST-1023`
- `/customers/CUST-1037`
- `/trust/CUST-1001`

| Condition | Points (out of 10) |
|-----------|--------------------|
| All target pages return 200 | 10 |
| 1 page fails | 7 |
| 2 pages fail | 4 |
| 3+ pages fail | 0 |

Page checks are binary and focus on route health, not deep UI behavior.

---

### 6) Error Hygiene — weight: 10

Do the tested APIs avoid returning a top-level `error` object or value in normal success paths?

| Condition | Points (out of 10) |
|-----------|--------------------|
| No tested successful response contains top-level `error` | 10 |
| 1 route includes top-level `error` | 5 |
| 2 routes include top-level `error` | 2 |
| 3+ routes include top-level `error` | 0 |

A 200 response that still exposes a top-level `error` in a normal flow should lose points. A non-200 route is already penalized under API availability.

---

## Composite Score Formula

```text
pipeline_score =
  data_integrity_points
+ api_status_points
+ response_structure_points
+ trust_narrative_points
+ page_status_points
+ error_hygiene_points
```

Maximum score: **100**

---

## Keep Threshold

**Keep the change if:**
- `variant_score > baseline_score`
- AND no previously passing target route regresses
- AND no new top-level `error` appears
- AND cross-surface consistency is maintained or improved

**Revert if:**
- Score does not improve
- OR any previously passing target route fails after the change
- OR the change improves one route by hollowing out required business data somewhere else
- OR numbers become less believable after the change

---

## Interpretation Bands

- **95–100:** Demo-ready. An operator could walk through the full workflow and trust the numbers at every step.
- **85–94:** Strong. Minor data gaps or traceability issues remain, but the core story holds.
- **70–84:** Usable but risky. Operators will hit confusing gaps or unbelievable numbers in important flows.
- **50–69:** Weak. Too many routes or datasets are failing to support the trust narrative.
- **Below 50:** Broken. Do not present this as a working demo to anyone.

---

## Measurement Protocol

- Run `python3 scripts/score_data_chief_pipeline.py`
- Use the scorer's fixed route list and fixed checks
- Save the full JSON output for both baseline and variant
- Compare the score delta AND the specific failing checks, not just the headline score
- For trust narrative scoring, manually verify end-to-end traceability if automated checks are ambiguous

---

## Evaluator Discipline

- Score the environment that exists, not the intended architecture
- Do not award points for routes that return placeholder shells without believable data
- Treat zero-heavy demo responses as integrity failures when seeded data should exist
- Check cross-surface consistency: if summary metrics say $47K revenue, the P&L should roughly add up to $47K
- Favor operator trust over technical elegance
- A passing score must reflect an app someone could actually click through without hitting obvious dead ends or numbers that don't add up
- When in doubt, ask: "Would a PE operating partner look at this and say 'I trust these numbers'?"

---

## Rubric Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-03-13 | Initial rubric for Data Chief pipeline integrity loop. |
| 2.0 | 2026-03-13 | Reweighted: data integrity 30→35, added trust narrative completeness (15), reduced API status 20→15, response structure 20→15, page status 15→10, error hygiene 15→10. Added cross-surface consistency checks, believability rule, P&L traceability checks. |
