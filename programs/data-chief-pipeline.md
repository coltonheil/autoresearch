# Data Chief Pipeline Integrity Loop

## Purpose

Validate and improve Data Chief's operator-facing reliability using the upstream karpathy/autoresearch keep-or-discard pattern. Data Chief is a demo/MVP for PE-owned field service businesses. It reconciles messy operational data from multiple source systems (ERP, CMMS, CRM, invoicing, procurement) into trustworthy customer-level P&L with pricing recommendations.

The two trust narratives this loop protects:

1. **Connectors + Librarian trust loop**: Source systems connect → Librarian reconciles conflicts and duplicates → operator confirms or overrides → clean data flows into P&L
2. **Customer P&L trace + pricing recommendation**: Every P&L line item traces to source records → margin analysis drives repricing recommendations → operator accepts, modifies, or rejects

The target user is a PE operating partner or portfolio ops manager. They think in customers, margins, contracts, and service delivery. Every route, every number, every empty state either builds or destroys their trust. This loop exists to make sure the app earns that trust.

```
LOOP:
  1. test ONE integrity weakness
  2. score the environment with scripts/score_data_chief_pipeline.py
  3. if score improves and no route regresses → KEEP
  4. if score does not improve or any route regresses → DISCARD
  5. repeat up to 3 variants per run
```

---

## What 100 Looks Like

A score of 100 means an operator can click through the entire app without hitting a single dead end, empty state, or broken number. Specifically:

- Every connector shows a positive record count and a recent sync timestamp
- The Librarian page shows reconciliation events with plain-English explanations, including at least one auto-confirmed and one operator-overridden decision
- All three hero customers (CUST-1001, CUST-1023, CUST-1037) load with populated P&L, summary metrics, and repricing recommendations
- P&L line items trace back to named source systems — not just "Source A" but "ServiceTitan" or "QuickBooks"
- Repricing recommendations show current rate, recommended rate, and the margin delta that justifies the change
- Trust pages show source inventory with positive record counts for every connected system
- Summary metrics show non-zero revenue, margin, and job count — numbers that make business sense for a field service company
- No API returns a top-level error object on a success path
- No page returns a non-200 status code
- Zero empty states where demo data should exist

The operator should be able to walk through Connectors → Librarian → pick a customer → see the P&L → understand the repricing recommendation → and never once think "this looks broken."

---

## Target

- Product: **Data Chief**
- Site: <https://data-chief.vercel.app>
- App type: **Next.js operator dashboard on Vercel Hobby**
- Primary users: **PE operating partners and portfolio ops managers**
- Primary workflow: **Connectors → Librarian → Customers → Customer Detail (P&L + Repricing) → Trust**
- Key customer records: **CUST-1001**, **CUST-1023**, **CUST-1037**
- Source systems and data live behind Supabase project `qruj` (`qrujdoojqtlcbtwyhqam`)
- App repo: `~/.openclaw/workspace/workstreams/data-chief/app/`

Primary surfaces under test:

**Pages:**
- `/connectors` — source system connection status and record counts
- `/librarian` — data reconciliation events and decisions
- `/customers` — customer list with summary financials
- `/customers/CUST-1001` — hero customer detail with P&L and repricing
- `/customers/CUST-1023` — second hero customer
- `/customers/CUST-1037` — third hero customer
- `/trust/CUST-1001` — source inventory and data provenance

**APIs:**
- `/api/v1/customers` — customer list
- `/api/v1/connectors` — connector status and record counts
- `/api/v1/librarian/events` — reconciliation event log
- `/api/v1/trust/CUST-1001` — source inventory for trust page
- `/api/v1/customers/CUST-1001/pnl` — customer P&L with traceable line items
- `/api/v1/customers/CUST-1001/summary-metrics` — revenue, margin, job count
- `/api/v1/repricing?customer_id=CUST-1001` — repricing recommendations
- `/api/v1/repricing?customer_id=CUST-1023`
- `/api/v1/repricing?customer_id=CUST-1037`

---

## Iteration Protocol

Each loop run follows this exact sequence:

1. **Identify one integrity bottleneck** — choose the single highest-impact failure from the most recent scorer output. Prioritize data integrity failures over availability failures. A route that returns 200 but shows zeroed revenue is worse than a route that returns 500.
2. **Capture baseline** — run `python3 scripts/score_data_chief_pipeline.py` and save the full JSON output
3. **Implement one fix** — change exactly one narrow code or data issue. The fix must address the root cause, not mask it.
4. **Measure again** — re-run the scorer after the change reaches the preview or deployed target
5. **Score** — compare `pipeline_score`, passed checks, and detailed failures before vs after
6. **Keep or revert**:
   - Keep if: score improves and no previously passing route regresses
   - Revert if: score does not improve, a new error appears, or a previously passing route starts failing
7. **Log** — append one row to `results/data-chief-pipeline.tsv`
8. **Post** — summary to `#data-chief` (`1480348031726653564`)

---

## What "Data Integrity" Means in This Context

Data integrity is not just "records exist." For a PE ops demo, data integrity means **the numbers tell a believable story**. Specifically:

- **Connector record counts should be realistic.** A field service company with 5 source systems should show hundreds to thousands of records per connector, not 1 or 0.
- **P&L numbers should make business sense.** Revenue per customer should be in the thousands to tens of thousands range for field service. A customer with $0.00 revenue and 47 jobs is an integrity failure.
- **Repricing recommendations need justification.** A recommendation to raise prices by 15% only makes sense if the current margin data supports it. A repricing row with null margin or null current rate is broken.
- **Cross-surface consistency matters.** If summary metrics say CUST-1001 has $47K revenue, the P&L line items should add up to roughly $47K. If they don't, the operator loses trust immediately.
- **Source traceability must be real.** P&L line items should reference specific source systems (ServiceTitan, QuickBooks) and specific record types (invoices, work orders). A line item with no source attribution breaks the trust narrative.
- **The Librarian must show actual decisions.** Reconciliation events should show what was in conflict, what the Librarian decided, and why. Events with empty explanations or generic "resolved" status are integrity failures.

---

## Editable Scope

Builders may modify:

- **App code** under `workstreams/data-chief/app/src/`
- **API routes** and page loaders under `workstreams/data-chief/app/src/app/`
- **Query and transform helpers** under `workstreams/data-chief/app/src/lib/`
- **Supabase data and SQL fixes** through the Supabase Management API when a data defect, null shape, bad join, or seed issue is the root cause

Builders may execute SQL changes only through this pattern:

```bash
source ~/.openclaw/.secrets/master.env && curl -s -X POST "https://api.supabase.com/v1/projects/qrujdoojqtlcbtwyhqam/database/query" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"YOUR SQL HERE"}'
```

Builders may NOT modify:

- Vercel project settings or production environment variables
- Authentication behavior or introduce a new auth gate
- The loop scoring script or rubric during an iteration run
- Unrelated product positioning, styling, or marketing copy
- The app merely to hide broken data if the underlying route or source is still wrong
- Seed data in a way that makes numbers less realistic (e.g., setting all revenues to round $10,000)

---

## Tools

### Primary runner

Use **Codex CLI**, not Claude Code.

```bash
codex exec "Follow programs/data-chief-pipeline.md and use rubrics/data-chief-pipeline.md"
```

### Pipeline scoring

```bash
python3 scripts/score_data_chief_pipeline.py
```

### Route smoke checks

```bash
curl -i https://data-chief.vercel.app/api/v1/customers
curl -i https://data-chief.vercel.app/api/v1/connectors
curl -i https://data-chief.vercel.app/api/v1/customers/CUST-1001/pnl
curl -i https://data-chief.vercel.app/api/v1/repricing?customer_id=CUST-1001
curl -i https://data-chief.vercel.app/customers/CUST-1001
```

### Local app context

```bash
cd ~/.openclaw/workspace/workstreams/data-chief/app
```

### Supabase Management API

Use only when the defect is in persisted data rather than app code.

```bash
source ~/.openclaw/.secrets/master.env && curl -s -X POST "https://api.supabase.com/v1/projects/qrujdoojqtlcbtwyhqam/database/query" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"YOUR SQL HERE"}'
```

---

## Artifact Storage

Store all generated artifacts under:

`~/.openclaw/workspace/outputs/autoresearch/data-chief-pipeline/<YYYY-MM-DD>/`

Expected artifacts per run:
- scorer baseline JSON (`baseline.json`)
- scorer after JSON (`after.json`)
- failing-route snapshots if needed
- curl captures for broken routes if needed
- diff or patch excerpt for kept changes
- run notes (`run-r<NN>-notes.md`)

---

## Keep / Revert Decision Rules

**Keep if ALL of the following are true:**
- `pipeline_score` improves versus baseline
- No previously passing route regresses
- No API under test returns a top-level `error`
- Hero customer routes still return non-empty, believable business data after the change
- Cross-surface consistency is maintained or improved (e.g., summary metrics and P&L totals don't diverge)

**Revert if ANY of the following are true:**
- Score does not improve
- Any page route drops from 200 to non-200
- Any API route drops from 200 to non-200
- A route starts returning structurally valid JSON but empty business data where live demo data should exist
- A fix masks a defect instead of repairing the underlying route, query, or seed data
- Numbers become less believable (e.g., all customers suddenly show identical revenue)

---

## Branch Convention

- Branch format: `autoresearch/data-chief-pipeline-<YYYY-MM-DD>-r<NN>`
- Example: `autoresearch/data-chief-pipeline-2026-03-13-r01`

Do not merge automatically. Await human review after a kept run.

---

## Max Variants Per Run

- 1 bottleneck per variant
- Maximum 3 variants per run

This loop should stay surgical. Do not bundle several integrity fixes into one unscored change.

---

## Stop Conditions

Stop the run when any of these is true:
- `pipeline_score` reaches **100**
- 3 consecutive variants fail to improve score
- A regression appears that cannot be cleanly isolated within the current run
- The next needed fix requires a larger architectural rewrite that should be handled as separate scoped work

---

## Results Log Format

Append every run to `results/data-chief-pipeline.tsv`

Header:

```text
run_id	timestamp_utc	commit	baseline_score	variant_score	score_delta	passed_checks	failed_checks	status	bottleneck_targeted	description	artifact_path	rubric_version
```

Status should be one of:
- `KEEP`
- `REVERT`
- `HOLD`

Description should be brief and specific, for example:
- `Fixed trust route source inventory counts for hero customer`
- `Reverted customer detail variant because repricing data disappeared for CUST-1023`
- `Populated P&L source system labels — line items now reference ServiceTitan and QuickBooks`

---

## Discord Reporting

Post to `#data-chief` (`1480348031726653564`) after each run:
- Bottleneck targeted
- `pipeline_score` before → after
- Pass/fail count before → after
- Keep or revert decision
- Top remaining failures (max 3)
- Artifact path under `outputs/autoresearch/data-chief-pipeline/`

---

## What This Loop Optimizes

This loop rewards operator-grade reliability and data believability:
- Every page loads without errors
- Every API route resolves with the correct structure
- Connector record counts are realistic and positive
- Customer P&L has traceable, non-zero line items
- Repricing recommendations have clear margin justification
- The Librarian shows real reconciliation decisions with explanations
- Summary metrics and P&L totals are cross-consistent
- Trust pages show complete source provenance
- No 500s, no empty states where demo data should exist
- Numbers tell a story a PE operating partner would believe

This loop does **not** reward:
- Cosmetic changes that don't fix real integrity issues
- Hiding broken data behind UI changes
- Making numbers look pretty without fixing the source

---

## Final Rule

This program is an instruction file for a disciplined Data Chief reliability loop.

The standard is simple:

**One integrity fix, one score, keep only if the environment becomes more trustworthy — meaning the numbers are more believable, the routes are more reliable, and an operator would trust the app more than before the change.**
