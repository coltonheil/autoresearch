# Data Chief Language Quality Rubric

Version: 2.0 | Weights sum: 100

## Scoring Overview

Score each run 0–100 using the weighted dimensions below.
Apply the rubric to both baseline and variant. Delta = `variant_score - baseline_score`.

| Dimension | Weight | Good (full points) | Poor (0 pts) |
|-----------|--------|--------------------|--------------|
| Operator clarity | 30% | Text reads like a decision tool for PE ops managers | Text reads like internal pipeline output |
| Internal jargon suppression | 20% | No pipeline jargon or seed artifacts leak through | Jargon and internal artifacts are visible |
| Naming hygiene | 20% | No snake_case or raw internal identifiers in UI text | Raw identifiers are common |
| Content completeness | 15% | Expected descriptions are populated and useful | Empty or null descriptions remain |
| Concision and readability | 15% | Descriptions are tight and easy to scan | Descriptions are long, technical, or bloated |

**Total weight: 100%**

---

## Dimension Scoring Guides

### 1) Operator Clarity — weight: 30

Core question: Does the text help a PE operating partner understand what happened, why it matters, and what to do next?

**Examples of GOOD operator clarity:**

| Surface | Good Text | Why It's Good |
|---------|-----------|---------------|
| Connector card | "Syncs invoices, payments, and customer records from your accounting system. 1,247 records." | States what the system does and how much data it has. No jargon. |
| Librarian event | "Two invoices from ServiceTitan and QuickBooks matched to the same job for Acme HVAC. Auto-confirmed — amounts match within $0.12." | Explains the conflict, the resolution, and why it was safe to auto-confirm. |
| P&L line item | "Quarterly maintenance contract — ServiceTitan" | Clear service type and source system. |
| Repricing row | "Current rate $85/hr is 12% below comparable customers. Recommend $95/hr to restore 28% target margin." | Specific numbers, clear rationale, actionable. |
| Trust inventory | "QuickBooks — 1,247 invoice records synced. Last sync: 2 hours ago." | Named system, record count, recency. |
| Summary metric | "Total Revenue: $47,200 (last 12 months)" | Clear label, clear period, clear number. |

**Examples of BAD operator clarity:**

| Surface | Bad Text | Why It's Bad |
|---------|----------|--------------|
| Connector card | "Extracts pipe-delimited records from embedded JSON payloads via firmware_rev connector" | Pipeline implementation detail. Operator doesn't know or care about JSON payloads. |
| Librarian event | "cross_source_aliases_reconciled: normalized value mapping applied" | Completely opaque to a non-technical user. |
| P&L line item | "source_system: st_work_orders, pnl_impact: positive" | Raw field names, no business meaning. |
| Repricing row | "downstream economics indicate invoice_density supports rate adjustment" | Jargon-heavy, no specific numbers, not actionable. |

| Condition | Points (out of 30) |
|-----------|--------------------|
| Nearly every tested text field is plain, grounded, and operator-friendly | 30 |
| A few fields still sound internal or overly technical | 22 |
| Mixed quality: operator-friendly in places, internal elsewhere | 14 |
| Most text still reads like raw system output | 6 |
| Text is broadly confusing or unusable for a non-technical user | 0 |

---

### 2) Internal Jargon Suppression — weight: 20

Penalize visible phrases or patterns such as:

**Pipeline jargon (from data engineering):**
- `quarantined` / `quarantine`
- `normalized value`
- `unmapped columns`
- `pipe-delimited`
- `embedded JSON`
- `schema version` / `schema versions`
- `downstream economics`
- `record_state`
- `pnl_impact`

**Internal seed artifacts (from demo scaffolding):**
- `hero_customer_enrichment`
- `demo_mvp_seed`
- `cross_source_aliases_reconciled`
- `firmware_rev`
- `telemetry_interval_ms`

**Acceptable technical terms that should NOT be penalized:**
- Source system names (ServiceTitan, QuickBooks, Salesforce) — these are real business terms
- "Auto-confirmed" — operators understand this concept
- "Reconciliation" — standard business term
- "Margin" / "rate" / "P&L" — operator vocabulary
- "Sync" / "synced" — common enough for non-technical users

| Condition | Points (out of 20) |
|-----------|--------------------|
| No meaningful jargon or seed artifacts appear | 20 |
| 1–2 isolated jargon leaks | 15 |
| Several jargon leaks across tested surfaces | 8 |
| Jargon is frequent and obvious | 3 |
| The product still reads like an internal demo scaffold | 0 |

This dimension is about translation quality, not censorship. Useful technical meaning should stay if it is rewritten in operator language.

---

### 3) Naming Hygiene — weight: 20

Core question: Do user-facing strings avoid snake_case, raw field names, and internal identifiers?

**Known failure hotspots:**

| Location | Common Leak | What It Should Say Instead |
|----------|-------------|---------------------------|
| Connector descriptions | `source_type: erp_connector` | "ERP System" or the actual product name |
| Librarian events | `conflict_type: duplicate_record` | "Duplicate record found" |
| P&L labels | `st_work_orders` | "ServiceTitan Work Orders" |
| Summary metric labels | `revenue_aggregate` | "Total Revenue" |
| Repricing fields | `invoice_density` | "Invoice Volume" or "Billing Frequency" |
| Customer segments | `high_value_commercial` | "High-Value Commercial" |
| Trust page | `schema_version_seen` | Remove entirely or "Data Format Version" |

| Condition | Points (out of 20) |
|-----------|--------------------|
| No visible raw identifiers in tested user-facing text | 20 |
| 1–2 identifier leaks remain | 14 |
| Several identifier leaks remain | 8 |
| Raw field names are common | 3 |
| Naming hygiene is broadly broken | 0 |

---

### 4) Content Completeness — weight: 15

Core question: Where the app expects descriptive language, is something useful actually present?

This dimension matters more than initial weighting suggested because empty descriptions actively undermine operator trust. A connector with no description forces the operator to guess what it does. A Librarian event with no explanation makes the reconciliation opaque.

**Surfaces where empty descriptions are failures:**
- Connector cards — must explain what the source system does
- Librarian events — must explain what was reconciled and why
- Customer descriptions — should provide business context
- Repricing recommendations — must explain the rationale
- Trust source inventory — must label what each source provides

| Condition | Points (out of 15) |
|-----------|--------------------|
| Expected descriptions are populated and useful | 15 |
| 1–2 expected descriptions are empty or placeholder-like | 11 |
| Several expected descriptions are empty or weak | 7 |
| Many expected descriptions are missing | 3 |
| The product regularly omits context where operators need it | 0 |

---

### 5) Concision and Readability — weight: 15

Core question: Are text fields short enough for operators to scan without wading through system prose?

**Good concision targets:**
- Connector descriptions: 1 sentence
- Librarian event summaries: 1–2 sentences
- P&L line item labels: 3–8 words
- Repricing rationale: 1–2 sentences with specific numbers
- Summary metric labels: 2–4 words

**Primary penalty cases:**
- Descriptions longer than 3 sentences when 1–2 would do
- Bloated narrative wrappers around a simple point
- Technical phrasing that makes the operator parse structure before meaning
- Repetitive explanations that say the same thing twice in different words

| Condition | Points (out of 15) |
|-----------|--------------------|
| Text is consistently concise and easy to scan | 15 |
| A few fields run long | 11 |
| Mixed readability; several fields are too dense | 7 |
| Many fields are long and technical | 3 |
| Readability is poor across the product | 0 |

---

## Composite Score Formula

```text
language_score =
  operator_clarity_points
+ jargon_suppression_points
+ naming_hygiene_points
+ completeness_points
+ concision_points
```

Maximum score: **100**

---

## Keep Threshold

**Keep the change if:**
- `variant_score > baseline_score`
- AND the targeted bad strings are actually removed from BOTH the source API response AND the rendered HTML
- AND the change preserves business meaning instead of hiding the problem

**Revert if:**
- Score does not improve
- OR bad strings are only hidden on one surface but persist in shared data, helpers, or APIs
- OR the text becomes vaguer while technically avoiding the forbidden phrase
- OR the replacement is marketing-speak that sounds polished but provides no useful information to an operator

---

## Interpretation Bands

- **95–100:** Reads like a polished operator tool. Clean, clear, and business-first throughout.
- **85–94:** Strong. Only minor language residue remains. An operator wouldn't notice the gaps.
- **70–84:** Usable, but operators will still see occasional internal leakage or empty spots.
- **50–69:** Weak. Too much of the product still sounds like internal scaffolding.
- **Below 50:** Broken language layer. The app is not speaking to operators clearly enough to build trust.

---

## Measurement Protocol

- Run `python3 scripts/score_data_chief_language.py`
- The scorer inspects both API text (from JSON responses) and rendered page text (from HTML)
- The score is driven by the percentage of tested text fields that pass all anti-pattern checks
- Save failing field inventories so repeated offenders are visible across runs
- For operator clarity scoring, evaluate against the good/bad examples in this rubric

---

## Evaluator Discipline

- Score visible user language, not hidden implementation details
- Do not give credit for removing context operators still need
- Prefer grounded business wording over vague polished prose
- Penalize marketing-speak that sounds impressive but says little ("leveraging downstream economics")
- The goal is not less text. The goal is clearer text.
- When scoring operator clarity, ask: "Would a PE operating partner read this and immediately understand what it means and what to do?"
- When scoring jargon, distinguish between pipeline jargon (always bad) and business-technical terms like "reconciliation" or "margin" (acceptable)
- Empty descriptions should be treated as more severe than slightly wordy descriptions — missing context is worse than verbose context

---

## Rubric Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-03-13 | Initial rubric for Data Chief language quality loop. |
| 2.0 | 2026-03-13 | Reweighted: content completeness 10→15, jargon suppression 25→20, concision 15→15 (unchanged). Added concrete good/bad examples for operator clarity. Added known failure hotspot table for naming hygiene. Added acceptable technical terms list. Added specific surfaces where empty descriptions are failures. |
