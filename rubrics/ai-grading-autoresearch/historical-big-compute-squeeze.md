# AI Grading Historical Big-Compute Squeeze Rubric

## Primary Score

Metric: historical detector improvement with Basler transfer regression gates.
Direction: higher is better.
Source artifacts:
- `outputs/historical-scene-evaluator/train-runs/*/results.csv`
- `reports/bench-detector-eval/latest.json`
- `reports/launch-audit/latest.json`

## Required Logged Metrics

Each experiment row must include or point to:

- historical mAP50
- historical mAP50-95
- Basler precision
- Basler recall
- Basler TP
- Basler FP
- Basler FN
- software launch status
- production promotion status
- artifact path
- checkpoint commit hash or explicit `no_commit_large_artifact_manifest`
- decision: keep, discard, crash, or blocked

## Evidence Dimensions

Direct evidence:
- raw frame provenance for every teacher proposal
- dataset manifest for every synthetic dataset
- training command/config for every student candidate
- fixed evaluator outputs for every candidate

Unsupported-decision penalty:
- proposal volume without reviewed disagreement evidence is not improvement
- synthetic image volume without held-out detector improvement is not
  improvement
- training more epochs/models without a fixed metric is not improvement
- any result after editing protected evaluators is invalid

Regression checks:
- `python3 scripts/validate_grading_source_of_truth.py` passes
- `python3 scripts/bench/run_launch_audit.py` reports `software_launch_ok=true`
- Basler transfer `fn` must not increase
- Basler transfer `fp` must not increase unless explicitly marked
  non-promotion research and justified by a material historical win
- production promotion requires launch audit `promotion_ok=true`
- after each experiment, the result ledger and run note are checkpointed with a
  targeted commit or a committed manifest records why the artifact itself was
  not committed

Simplicity cost:
- prefer smaller/faster student models when metrics are tied
- prefer synthetic/teacher recipes that are explainable and reproducible
- reject variants that require preserving confusing fallback paths

## Keep/Discard Bands

keep:
- improves the active loop metric
- passes protected gates
- writes complete artifacts
- has a plausible downstream use for conveyor readiness

discard:
- metric is flat/lower
- protected gates fail
- artifacts are incomplete
- change is too broad to attribute improvement to one surface

crash:
- command/runtime failure
- missing dependency
- unusable output
- GPU provisioning failure
- missed checkpoint commit because of git state or artifact write failure

blocked:
- requires new physical conveyor data
- requires user budget approval
- evaluator/source-of-truth inconsistency found
- no clean mutable surface remains for the current loop
