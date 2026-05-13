# Blue Star Cat-1 Wiki Recovery

## Definition

This is a Karpathy-style autoresearch program for one reusable improvement:
recovering quote-critical Cat-1 bid variables from Blue Star bid documents
through the active source inventory, GLM/vision routing, and LLM wiki pipeline.

Rows are evaluation examples. The research unit is a reusable production
pipeline variant: source completeness, page routing, vision/GLM coverage, wiki
synthesis, or wiki reader behavior. The loop must not turn into manual bid
cleanup, regex extraction, or fallback pricing.

## Run Scope

Run tag: `bs-cat1-wiki-recovery-<YYYY-MM-DD>-rNN`

Branch policy: create a fresh `autoresearch/bs-cat1-wiki-recovery-<tag>`
branch in `~/repos/autoresearch` before experiments.

Blue Star repo:

```text
/Volumes/CrucialX10/Colton/dev/repos/blue-star
```

Results TSV:

```text
results/blue-star/cat1-wiki-recovery.tsv
```

Artifacts:

```text
~/.openclaw/workspace/outputs/autoresearch/blue-star/cat1-wiki-recovery/<run-id>/
```

## Objective

Produce step-change improvements in resolving the variables required to price
generator bids from cited bid-document evidence and the scraped Blue Star
pricing/configurator data.

The core decision is:

> Can the active pipeline resolve missing Cat-1 quote facts from bid specs,
> schedules, drawings, addenda, tables, and whole-page vision artifacts?

## Immutable Evaluation Corpus

Use the fixed four-bid proof corpus unless a later run explicitly freezes a
larger corpus before baseline:

| Bid | Role | Expected challenge |
| --- | --- | --- |
| `d539f592-0629-4955-8050-f7294d32ab7e` | Protected positive control | Telford must remain fully resolved and packet-ready with caveats. |
| `0c95408c-f512-4207-8b6d-a4f7478acc0c` | Protected positive/control edge | Main Library must keep cited Cat-1 facts and must not use a sizing model as truth. |
| `26e7f6c5-7ef2-4044-958e-19f3de70c78c` | Target recovery case | Replacement Backup currently misses voltage and phase. |
| `3661923d-a564-4c17-8ed6-ecdadf1a6699` | Target recovery case | Twelve Mile currently misses voltage, phase, and may miss ATS facts. |

The eval set must be source-backed. Every expected field, blocker, or unknown
state must cite a wiki/raw artifact, page, vision artifact, or source-manifest
record. Do not create synthetic truth.

## Baseline

Baseline is the current Blue Star wiki synthesis and quote-input behavior on
the immutable corpus before editing the mutable surface.

Required baseline artifacts:

```text
~/.openclaw/workspace/outputs/autoresearch/blue-star/cat1-wiki-recovery/<run-id>/eval.jsonl
~/.openclaw/workspace/outputs/autoresearch/blue-star/cat1-wiki-recovery/<run-id>/score-baseline.json
```

Run the scorer once before changing the mutable surface:

```bash
cd ~/repos/autoresearch
python3 scripts/blue_star/score_cat1_wiki_recovery.py \
  --eval ~/.openclaw/workspace/outputs/autoresearch/blue-star/cat1-wiki-recovery/<run-id>/eval.jsonl \
  --out ~/.openclaw/workspace/outputs/autoresearch/blue-star/cat1-wiki-recovery/<run-id>/score-baseline.json
```

## Mutable Surface

Edit only one of these surfaces per experiment:

```text
programs/blue-star/cat1-wiki-recovery.variant.md
```

or, in the Blue Star repo, one explicitly selected active pipeline surface:

```text
bid-intelligence/wiki/_learning/compiled/synthesis-pack.md
bid-intelligence/wiki/_learning/rubrics/active-bid-reading-rubric.md
apps/internal/scripts/wiki/synthesize.ts
apps/internal/scripts/wiki/prepare.ts
apps/internal/scripts/wiki/page-coverage.ts
apps/internal/scripts/wiki/run-missing-vision.ts
apps/internal/src/lib/opportunities/document-understanding.ts
apps/internal/src/lib/opportunities/packet-health.ts
apps/internal/src/lib/documents/page-inventory.ts
apps/internal/src/lib/documents/pilot-routing.ts
apps/internal/scripts/sync-sam-gov-internal-documents.ts
apps/internal/scripts/sync-planetbids-public-documents.ts
```

If a run edits Blue Star code, it must name the one file as the mutable surface
before the experiment starts. Do not edit multiple surfaces in one experiment.
If a missing-document hypothesis requires downloading or routing source
artifacts, the experiment must write a typed source-completeness artifact and
must not directly edit `fields/*.json`.

## Protected Surface

Do not edit during a run:

- `rubrics/blue-star/cat1-wiki-recovery.md`
- `scripts/blue_star/score_cat1_wiki_recovery.py`
- the fixed `eval.jsonl`
- bid source documents, raw downloaded PDFs, source manifests, or evidence labels
- existing field JSON by hand
- Blue Star pricing/configurator scraped JSON
- old synthetic/demo packet surfaces

## Disallowed Patterns

Discard any variant that:

- uses regex/string matching as the final source of truth
- manually edits `fields/*.json`
- hardcodes bid-specific answers
- fills missing bid facts from configurator defaults
- uses a sizing model to infer quote facts that should come from bid docs
- treats absence from a partial wiki/evidence index as proof the source document
  lacks the fact
- treats missing evidence as a negative business decision
- weakens citation/support-level requirements
- changes the evaluator, rubric, or eval set to make itself win

## Primary Metric

Primary metric: `candidate_score - baseline_score`, higher is better.

The scorer rewards:

- cited recovery of Cat-1 fields: `power_kw`, `fuel_type`, `voltage`, `phase`,
  `ats_required`, `ats_amp_rating`
- direct evidence from page text, tables/schedules, addenda, drawings, or
  whole-page vision artifacts
- correct separation of unresolved document facts from configurator/pricing
  mapping
- quote-readiness correctness
- preservation of protected positive controls

The scorer penalizes:

- unsupported recovered facts
- stale-field fallback
- configurator defaults filling missing bid facts
- sizing-model truth
- regressions on Telford or Main Library

## Keep Threshold

Keep only if:

- candidate score improves by at least `+8.0` points over baseline,
- all regression gates pass,
- at least one target missing field is newly recovered with cited evidence or
  conclusively proven absent from downloaded docs,
- Telford and Main Library do not regress, and
- the winning change has a clear promotion target in the Blue Star repo.

Equal scores are discard unless the variant materially simplifies the real
pipeline and no regression gate fails.

## Iteration Protocol

1. Confirm git state and create a fresh run branch.
2. Freeze the eval set before editing the mutable surface.
3. Run the scorer to record baseline.
4. State one hypothesis and the disconfirming test.
5. Edit exactly one mutable surface.
6. Rerun only the fixed corpus through the required Blue Star pipeline stages.
   For source-completeness variants, this includes source inventory audit,
   document acquisition/routing if available, page-level GLM for every page,
   whole-page vision for any page that may contain tables/drawings/schedules or
   ambiguous electrical data, and wiki synthesis.
7. Write candidate outputs into the same eval JSONL shape.
8. Run the scorer.
9. Append one TSV row.
10. Keep the variant only if the metric and gates pass.
11. Revert/discard losing variants.
12. Continue until interrupted, seven hours expire, or a stop condition fires.

## Stop Conditions

- the eval set lacks source-backed labels
- the scorer cannot parse or evaluate artifacts
- the next useful experiment requires changing the evaluator/rubric
- a real source is unavailable after the source inventory has proved the bid
  portal/document set was checked and typed the missing artifact
- paid access, credentials, live source mutation, or human business approval is
  required
- no metric improvement after five valid experiments
- seven-hour runtime expires

## Promotion Target

A kept variant promotes into the active Blue Star wiki pipeline only after the
scorer returns `keep` and protected checks pass. If the winning change replaces
an old path, delete the old path instead of preserving a compatibility fallback.
