# Data Chief Autoresearch Audit Changelog

**Date:** 2026-03-13
**Auditor:** Opus subagent (autoresearch audit task)
**Reference style:** `programs/site-performance.md` and `rubrics/site-performance.md`

---

## Summary

All 4 Data Chief autoresearch files were rewritten to be sharper, more specific, and better aligned with the two core trust narratives (Connectors→Librarian→P&L and P&L→Repricing). The rewrites make these files production-quality for autonomous overnight runs by Codex CLI.

---

## programs/data-chief-pipeline.md

| Change | Why |
|--------|-----|
| Added "What 100 Looks Like" section | Agent had no clear definition of done. Now has explicit criteria for every surface in the app. |
| Added "What Data Integrity Means in This Context" section | Original file treated integrity as "records exist." New section defines believability: realistic record counts, plausible revenue ranges, cross-surface consistency, source traceability, and Librarian decision quality. |
| Added trust narrative framing to Purpose | Original purpose was generic "operator-facing reliability." Now explicitly ties to the two PE trust narratives. |
| Expanded editable scope with prohibition on unrealistic data | Prevents seed data fixes that make numbers less believable (e.g., setting all revenues to round $10,000). |
| Enriched results TSV schema | Original was just `commit/score/status/description`. Now includes `run_id`, `timestamp_utc`, `baseline_score`, `variant_score`, `score_delta`, `passed_checks`, `failed_checks`, `bottleneck_targeted`, `artifact_path`, and `rubric_version`. Matches site-performance style. |
| Added cross-surface consistency to keep/revert rules | Original didn't check whether summary metrics and P&L totals diverged. |
| Added prioritization guidance to iteration protocol | "Prioritize data integrity failures over availability failures. A route that returns 200 but shows zeroed revenue is worse than a route that returns 500." |
| Normalized repo paths | Changed `/Users/coltonheil/.openclaw/workspace/` to `~/.openclaw/workspace/` for consistency. |

## rubrics/data-chief-pipeline.md — v1.0 → v2.0

| Change | Why |
|--------|-----|
| Reweighted dimensions: data integrity 30→35 | Trust narrative is the core value prop. The heaviest weight should reflect that. |
| Added new dimension: Trust Narrative Completeness (15%) | Original rubric had no check for whether the two end-to-end trust narratives were traceable. A PE operator needs to follow Connectors→Librarian→P&L and P&L→Repricing. |
| Reduced API availability 20→15 | Route reachability matters but is table stakes, not the primary value signal. |
| Reduced API response structure 20→15 | Same reasoning — structural correctness is necessary but not sufficient. |
| Reduced page route availability 15→10 | Binary availability is the least nuanced check. |
| Reduced error hygiene 15→10 | Important but less critical than data believability. |
| Added cross-surface consistency checks under data integrity | Checks that summary metrics revenue ≈ P&L total, and job count ≈ P&L entries. |
| Added P&L traceability checks | P&L line items must reference named source systems, have non-zero amounts, and be in plausible ranges. |
| Added repricing justification checks | Repricing must include current rate, recommended rate, and non-zero delta. |
| Added believability rule callout | Explicit: "If numbers don't make business sense, it's an integrity failure even if structure is correct." |
| Updated evaluator discipline | Added "Would a PE operating partner trust these numbers?" as the guiding question. |

## programs/data-chief-language.md

| Change | Why |
|--------|-----|
| Added "What 100 Looks Like" section with good/bad examples table | Original had no concrete examples of good operator language. Agent couldn't distinguish "clean enough" from "not there yet." 7-row comparison table covers every surface. |
| Added "Tables and Fields That Commonly Leak Internal Text" section | Original said "fix language" without specifying where leaks come from. New table maps 7 table/API hotspots to their common leak patterns and the display helpers that should be translating them. |
| Added API serialization to editable scope | Original only allowed database fixes and display helpers. Some jargon leaks because the API route passes internal field names through without translation. |
| Added source-tracing step to iteration protocol | Step 3 now requires the builder to determine whether bad text comes from persisted data, seed content, display helpers, or API serialization before fixing. |
| Added prioritization guidance | "Prioritize by volume: if 14 fields leak snake_case and 3 have jargon, fix snake_case first." |
| Enriched results TSV schema | Same expansion as pipeline: added `run_id`, `timestamp_utc`, `baseline_score`, `variant_score`, `score_delta`, `failure_pattern_targeted`, `artifact_path`, `rubric_version`. |
| Added anti-marketing-speak to revert rules | Prevents replacement text that is polished but says nothing useful. |

## rubrics/data-chief-language.md — v1.0 → v2.0

| Change | Why |
|--------|-----|
| Reweighted: content completeness 10→15 | Empty descriptions actively undermine operator trust. A connector with no description forces the operator to guess. This deserves more weight than initial 10%. |
| Reweighted: jargon suppression 25→20 | Still important but original overweighted relative to completeness. |
| Added concrete good/bad examples for operator clarity | Original said "plain, grounded, and operator-friendly" without showing what that looks like. Now has 4 good examples and 4 bad examples with explanations. |
| Added known failure hotspot table for naming hygiene | Maps 7 specific locations to their common snake_case leaks AND what the replacement should say. |
| Added acceptable technical terms list | Prevents over-penalization of legitimate business terms like "reconciliation," "margin," "sync." |
| Added specific surfaces where empty descriptions are failures | Lists the 5 surfaces where empty descriptions are particularly damaging. |
| Added concision targets per surface type | Connector descriptions: 1 sentence. P&L labels: 3-8 words. Repricing rationale: 1-2 sentences with numbers. |
| Updated evaluator discipline | Added severity ordering: empty descriptions > verbose descriptions. Added PE operator perspective test. |

---

## What Was NOT Changed

- File paths — all 4 files kept their original locations
- Scoring scripts — `score_data_chief_pipeline.py` and `score_data_chief_language.py` were not modified (rubric changes may require script updates in a follow-up)
- Discord channel ID — kept `1480348031726653564`
- Supabase project ID — kept `qrujdoojqtlcbtwyhqam`
- Branch convention format — kept as-is
- Max variants per run — kept at 3
- Stop conditions — kept the same thresholds

## Follow-Up Needed

1. **Scoring script updates:** The pipeline scorer (`score_data_chief_pipeline.py`) doesn't currently check the new trust narrative completeness dimension or cross-surface consistency. The rubric defines these checks but the scorer needs corresponding code. Same for the language scorer — it should apply the weighted dimension approach from the rubric rather than raw pass-rate.
2. **Results TSV migration:** Existing TSV rows use the old `commit/score/status/description` schema. New runs will use the expanded schema. Consider adding a header row to existing files.
