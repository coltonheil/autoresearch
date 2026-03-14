# Data Chief Language Quality Loop

## Purpose

Improve operator-facing language across Data Chief using the upstream karpathy/autoresearch keep-or-discard pattern. Data Chief is a demo/MVP for PE-owned field service businesses, and its target user is a PE operating partner or portfolio ops manager who thinks in customers, margins, contracts, and service delivery.

Every string in the app either sounds like a tool built for operators or sounds like a data engineer's internal notes. This loop systematically finds and fixes the latter.

```
LOOP:
  1. identify ONE language defect pattern
  2. score current text with scripts/score_data_chief_language.py
  3. fix the underlying data or display logic
  4. if score improves without hiding the defect → KEEP
  5. if score does not improve or the fix is cosmetic-only → DISCARD
  6. repeat up to 3 variants per run
```

---

## What 100 Looks Like

A score of 100 means every user-facing string in Data Chief reads like it was written for a PE operating partner, not a data engineer. Specifically:

- Zero snake_case identifiers visible anywhere in the UI or API responses consumed by the UI
- Zero pipeline jargon terms (quarantined, normalized value, unmapped columns, schema version, etc.)
- Zero internal seed artifacts (hero_customer_enrichment, demo_mvp_seed, cross_source_aliases_reconciled, etc.)
- Every connector description explains what the system does in business terms
- Every Librarian event explains the conflict and resolution in plain English
- Every P&L line item label is human-readable
- Every repricing recommendation explains the "why" in margin/pricing terms, not data terms
- Every summary metric has a clear label an operator would understand
- No empty descriptions where context is needed
- Text is concise — 1-2 sentences per description, not 3+

**Example of GOOD operator language:**

| Surface | Good | Bad |
|---------|------|-----|
| Connector description | "Syncs invoices, payments, and customer records from your accounting system" | "Extracts pipe-delimited records from embedded JSON payloads" |
| Librarian event | "Two invoices from different systems matched to the same job. Auto-confirmed based on matching customer and date." | "cross_source_aliases_reconciled: normalized value mapping applied to quarantined records" |
| P&L line item | "HVAC maintenance — ServiceTitan work orders" | "source_system: st_work_orders, record_state: resolved" |
| Repricing recommendation | "Current rate $85/hr is 12% below market. Recommend $95/hr to restore target margin." | "downstream economics indicate invoice_density supports rate adjustment" |
| Trust source inventory | "QuickBooks — 1,247 invoice records synced" | "qb_connector: total_records 1247, schema_version_seen: 3" |
| Summary metric label | "Total Revenue" | "revenue_aggregate" |
| Customer list subtitle | "32 active service customers" | "customer_count: 32, record_state: active" |

---

## Target

- Product: **Data Chief**
- Site: <https://data-chief.vercel.app>
- Users: **PE operating partners and portfolio ops managers**
- Core workflow: **Connectors → Librarian → Customers → Customer Detail → Trust**
- App repo: `~/.openclaw/workspace/workstreams/data-chief/app/`
- Supabase project: `qrujdoojqtlcbtwyhqam`

Key pages under language inspection:
- `/connectors` — connector names, descriptions, status labels
- `/librarian` — event summaries, resolution explanations, conflict descriptions
- `/customers` — customer names, list subtitles, column headers
- `/customers/CUST-1001` — P&L labels, metric labels, repricing explanations
- `/trust/CUST-1001` — source system names, inventory labels, provenance descriptions

Key APIs supplying user-facing text:
- `/api/v1/customers` — customer names, descriptions
- `/api/v1/connectors` — connector names, descriptions, source system labels
- `/api/v1/librarian/events` — event summaries, resolution text, conflict descriptions
- `/api/v1/trust/CUST-1001` — source inventory labels, provenance descriptions
- `/api/v1/customers/CUST-1001/pnl` — line item labels, source attribution text
- `/api/v1/customers/CUST-1001/summary-metrics` — metric labels, period labels
- `/api/v1/repricing?customer_id=CUST-1001` — recommendation explanations, rate labels

---

## Tables and Fields That Commonly Leak Internal Text

The scorer checks all API and page text, but these are the known hotspots where internal language tends to survive:

| Table / API | Fields to Watch | Common Leak Pattern |
|-------------|----------------|---------------------|
| `connectors` | `description`, `name`, `source_type` | Pipeline jargon in descriptions ("extracts pipe-delimited…"), raw source_type values as labels |
| `librarian_events` | `summary`, `description`, `resolution_status`, `conflict_type` | Internal seed language ("cross_source_aliases_reconciled"), raw status enums, technical conflict descriptions |
| `customers` | `description`, `segment`, `notes` | Empty descriptions, snake_case segment values |
| `customer_pnl` (via API) | line item `label`, `source_system`, `category` | Raw field names as labels ("st_work_orders"), internal category codes |
| `repricing` (via API) | `recommendation_text`, `reason`, `basis` | Pipeline jargon ("downstream economics"), empty reason fields |
| `trust` / `source_inventory` | `source_label`, `description` | Schema version references, raw connector IDs as labels |
| `summary_metrics` (via API) | metric keys rendered as labels | snake_case keys shown directly ("revenue_aggregate", "job_count") |

**Display helpers that transform these for the UI:**
- `workstreams/data-chief/app/src/lib/librarian-display.ts` — Librarian event formatting
- `workstreams/data-chief/app/src/lib/format.ts` — general text formatting and label translation

When a bad string appears in the UI, trace it: is it stored bad in the database, or is it stored clean but the display helper isn't translating it? Fix whichever is the root cause.

---

## Iteration Protocol

Each loop run follows this exact sequence:

1. **Identify one language pattern to fix** — pick the single most repeated or highest-severity anti-pattern from the latest scorer output. Prioritize by volume: if 14 fields leak snake_case and 3 have jargon, fix snake_case first.
2. **Capture baseline** — run `python3 scripts/score_data_chief_language.py` and store the JSON output
3. **Trace the source** — determine whether the bad text comes from:
   - Persisted data in Supabase (fix the data)
   - Seed content that was never cleaned up (fix the seed data)
   - Display helpers that pass through raw values (fix the display helper)
   - API route that returns internal field names (fix the API serialization)
4. **Implement one underlying fix** — update the root source. If the bad string is in the database, fix the database. If the display helper should be translating it, fix the display helper. Do not add a UI-only patch that leaves the API still returning jargon.
5. **Measure again** — re-run the scorer
6. **Score** — compare `language_score`, total failing fields, and exact failing strings before vs after
7. **Keep or revert**:
   - Keep if: score improves and the underlying bad text is actually gone from both API and rendered HTML
   - Revert if: score does not improve, a new language defect appears, or the page merely hides raw data while the API still returns it
8. **Log** — append one row to `results/data-chief-language.tsv`
9. **Post** — summary to `#data-chief` (`1480348031726653564`)

---

## Editable Scope

Builders may modify:

- **Persisted database text** through the Supabase Management API when bad labels, descriptions, narratives, or seed content live in the database
- **Display helpers** in:
  - `workstreams/data-chief/app/src/lib/librarian-display.ts`
  - `workstreams/data-chief/app/src/lib/format.ts`
- **API route serialization** in `workstreams/data-chief/app/src/app/api/` when internal field names are being passed through to the response without translation
- Narrow presentation helpers closely tied to operator-safe text normalization

Builders may execute SQL changes only through this pattern:

```bash
source ~/.openclaw/.secrets/master.env && curl -s -X POST "https://api.supabase.com/v1/projects/qrujdoojqtlcbtwyhqam/database/query" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"YOUR SQL HERE"}'
```

Builders may NOT modify:

- The app only to conceal bad strings while leaving the underlying data or API untouched
- Product positioning unrelated to operator clarity
- The scoring script or rubric during a loop run
- User-facing surfaces in a way that drops context the operator genuinely needs
- Language by deleting evidence, removing whole sections, or suppressing fields that should remain visible

**Hard rule:** Do not change the page to hide bad data. Fix the underlying data, the display logic, or the API serialization that turns internal values into operator text.

---

## Tools

### Primary runner

Use **Codex CLI**, not Claude Code.

```bash
codex exec "Follow programs/data-chief-language.md and use rubrics/data-chief-language.md"
```

### Language scoring

```bash
python3 scripts/score_data_chief_language.py
```

### Page text inspection

```bash
curl -s https://data-chief.vercel.app/api/v1/connectors | python3 -m json.tool
curl -s https://data-chief.vercel.app/api/v1/librarian/events | python3 -m json.tool
curl -s https://data-chief.vercel.app/api/v1/customers/CUST-1001/pnl | python3 -m json.tool
curl -s https://data-chief.vercel.app/api/v1/repricing?customer_id=CUST-1001 | python3 -m json.tool
```

### Source files

```bash
cd ~/.openclaw/workspace/workstreams/data-chief/app
```

### Supabase Management API

```bash
source ~/.openclaw/.secrets/master.env && curl -s -X POST "https://api.supabase.com/v1/projects/qrujdoojqtlcbtwyhqam/database/query" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"YOUR SQL HERE"}'
```

---

## Artifact Storage

Store all generated artifacts under:

`~/.openclaw/workspace/outputs/autoresearch/data-chief-language/<YYYY-MM-DD>/`

Expected artifacts per run:
- baseline scorer JSON (`baseline.json`)
- after scorer JSON (`after.json`)
- failing text inventory (`failing-fields.json`)
- raw API snippets for repeated offenders
- run notes (`run-r<NN>-notes.md`)

---

## Keep / Revert Decision Rules

**Keep if ALL of the following are true:**
- `language_score` improves
- The failing text count decreases
- The removed anti-pattern no longer appears in both the source API response AND the rendered HTML
- The change preserves operator meaning while improving readability

**Revert if ANY of the following are true:**
- Score does not improve
- A fix removes useful meaning instead of translating it into operator language
- Snake case, seed tags, or technical jargon are still visible in another user-facing surface after the change
- The change only masks the defect on one page while it persists in the API or shared data
- The replacement text is vague marketing-speak that sounds polished but says nothing useful

---

## Branch Convention

- Branch format: `autoresearch/data-chief-language-<YYYY-MM-DD>-r<NN>`
- Example: `autoresearch/data-chief-language-2026-03-13-r01`

Do not merge automatically. Await human review after a kept run.

---

## Max Variants Per Run

- 1 language pattern per variant
- Maximum 3 variants per run

Examples of valid single-pattern targets:
- All snake_case field names leaking through connector descriptions
- Internal seed artifact names in Librarian event summaries
- Pipeline jargon in repricing recommendation text
- Empty descriptions on connectors where source system context is needed
- Raw status enum values displayed as-is instead of translated labels

---

## Stop Conditions

Stop the run when any of these is true:
- `language_score` reaches **100**
- 3 consecutive variants fail to improve score
- The remaining defects require a broader content strategy change rather than targeted cleanup
- The next change would alter business meaning instead of improving wording clarity

---

## Results Log Format

Append every run to `results/data-chief-language.tsv`

Header:

```text
run_id	timestamp_utc	commit	baseline_score	variant_score	score_delta	passed_checks	failed_checks	failure_pattern_targeted	status	description	artifact_path	rubric_version
```

Status should be one of:
- `KEEP`
- `REVERT`
- `HOLD`

Description should be brief and specific, for example:
- `Replaced internal seed tags in librarian summaries with operator-safe explanations`
- `Reverted variant because snake_case fields still leaked through trust API narrative`
- `Fixed connector descriptions — now explain business function instead of data format`

---

## Discord Reporting

Post to `#data-chief` (`1480348031726653564`) after each run:
- Language pattern targeted
- `language_score` before → after
- Failing text count before → after
- Keep or revert decision
- Top 3 remaining bad strings (exact text + source)
- Artifact path under `outputs/autoresearch/data-chief-language/`

---

## What This Loop Rewards

This loop rewards language that:
- Sounds like a product built for PE operating partners, not a data pipeline
- Uses plain English labels a non-technical person understands instantly
- Explains reconciliation decisions in business terms ("matched invoice to work order based on customer and date")
- Keeps source detail when operators need it, but translates it cleanly ("ServiceTitan — 847 work orders" not "st_connector: total_records 847")
- Describes repricing rationale in margin and rate terms, not data terms
- Stays concise: 1-2 sentences per description, not 3+
- Fills in context where operators need it (no empty descriptions on key surfaces)

This loop penalizes:
- snake_case identifiers anywhere in UI or operator-facing API text
- Raw internal seed artifacts and demo scaffold language
- Pipeline jargon (quarantined, normalized value, unmapped columns, schema version, etc.)
- Marketing-speak that sounds impressive but says nothing useful to an operator
- Empty descriptions where context is expected
- Long technical explanations that bury the business point
- Display-only fixes that leave the API still returning jargon

---

## Final Rule

This program is an instruction file for a disciplined Data Chief language loop.

The standard is simple:

**One language defect, one score, keep only if the app reads more clearly for operators because the underlying source — database, display helper, or API serialization — actually got better.**
