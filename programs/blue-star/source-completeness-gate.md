# Blue Star Source Completeness Gate

## Definition

This is a Karpathy-style autoresearch program for one reusable improvement:
deciding whether a bid has enough source material to support a quote/no-fit
decision before downstream classification or packet work.

Rows are evaluation examples. The research unit is the source-completeness
gate variant.

## Run Scope

Run tag: `bs-source-completeness-<YYYY-MM-DD>-rNN`

Branch policy: create a fresh `autoresearch/bs-source-completeness-<tag>`
branch in `~/repos/autoresearch` before experiments.

Results TSV:

```text
results/blue-star/source-completeness-gate.tsv
```

Artifacts:

```text
~/.openclaw/workspace/outputs/autoresearch/blue-star/source-completeness-gate/<run-id>/
```

## Baseline

Baseline is the current Blue Star bid-routing behavior on the fixed evaluation
set before the candidate gate is applied.

Required baseline artifact:

```text
~/.openclaw/workspace/outputs/autoresearch/blue-star/source-completeness-gate/<run-id>/eval.jsonl
```

Each row must contain both `baseline` and `candidate` objects for the same bid.
Run the scorer once before changing the mutable surface so the baseline score
is recorded.

```bash
cd ~/repos/autoresearch
python3 scripts/blue_star/score_source_completeness_gate.py \
  --eval ~/.openclaw/workspace/outputs/autoresearch/blue-star/source-completeness-gate/<run-id>/eval.jsonl \
  --out ~/.openclaw/workspace/outputs/autoresearch/blue-star/source-completeness-gate/<run-id>/score-baseline.json
```

## Hypothesis

If the routing system first classifies source completeness using direct
artifact evidence, then unsupported no-fit decisions will fall because missing
docs, inaccessible docs, extraction failures, and drawing/vision gaps will stop
being collapsed into negative business decisions.

## Mutable Surface

Edit only:

```text
programs/blue-star/source-completeness-gate.variant.md
```

That file defines the candidate gate rule an agent applies while producing the
`candidate` side of the eval JSONL. Do not edit the scorer, rubric, eval set,
or Blue Star source artifacts during an active run.

## Protected Surface

Do not edit during a run:

- `rubrics/blue-star/source-completeness-gate.md`
- `scripts/blue_star/score_source_completeness_gate.py`
- the fixed `eval.jsonl`
- Blue Star raw/source/canonical document artifacts
- Blue Star wiki generated fact sheets
- any connector, OCR, GLM, or extraction implementation

## Evaluation Set

Use a fixed, source-backed set with these strata:

- complete docs with generator/electrical scope
- complete docs with true non-generator no-fit
- pointer-only or inaccessible bid docs
- source docs present but extraction weak/truncated/noisy
- drawing/spec cases where visual sheets may decide scope
- cases with possible partner-lead value but no Blue Star quote fit

The eval set must be created from real bid artifacts. Do not create synthetic
truth. Every expected verdict must cite the source artifact and locator used to
label the case.

## Primary Metric

Primary metric: `candidate_score - baseline_score`, higher is better.

The scorer rewards:

- fewer unsupported final verdicts
- fewer blockers mislabeled as no-fit
- direct evidence coverage
- correct source-completeness state
- concrete next owner/action

## Regression Gates

Discard a variant if any gate fails:

- candidate increases unsupported `pursue_quote` or `true_no_fit`
- candidate labels missing/inaccessible/extraction/drawing blockers as no-fit
- candidate reduces direct evidence coverage
- candidate increases false partner-referral positives
- candidate weakens source-citation requirements
- candidate changes the eval set, scorer, or rubric to make itself win

## Keep Threshold

Keep only if:

- candidate score improves by at least `+5.0` points over baseline,
- all regression gates pass,
- the variant is simpler or no more complex than the baseline rule, and
- the winning rule has a clear promotion target in Blue Star routing.

Equal scores are discard unless the candidate is materially simpler and no
regression gate fails.

## Iteration Protocol

1. Confirm git state and create a fresh run branch.
2. Build or select the fixed eval set before editing the mutable surface.
3. Run the scorer to record baseline.
4. Edit only `source-completeness-gate.variant.md`.
5. Apply the candidate rule to the same eval set and write candidate outputs.
6. Run the scorer.
7. Append one TSV row.
8. Keep the variant only if the metric and gates pass.
9. Revert/discard the mutable-surface edit if the candidate loses.
10. Continue until interrupted or a stop condition fires.

## Stop Conditions

- eval set is missing or lacks source-backed labels
- scorer cannot parse the eval file
- candidate requires changing the protected evaluator
- next step requires credentials, paid access, live source mutation, or human
  business approval
- repeated failures show the problem is source acquisition or extraction work,
  not a gate-rule issue

## Promotion Target

A kept variant promotes into the Blue Star bid-routing/source-readiness rule
used before quote/no-fit classification. Promotion is a separate code/doc
change after the scorer returns `keep`.
