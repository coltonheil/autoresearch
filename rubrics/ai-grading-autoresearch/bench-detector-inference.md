# AI Grading Bench Detector Inference Rubric

## Primary Score

Metric: `recall - (0.05 * fp)`
Direction: higher is better.
Source artifact: `/Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch/reports/bench-detector-eval/latest.json`

## Dimensions

Direct evidence:
- Greedy IoU matches against reviewed production-geometry bench labels.
- Per-frame `tp`, `fp`, `fn`, matched root ids, and missed root ids.

Unsupported decision penalty:
- Any config variant that improves count but increases unsupported duplicate boxes must be penalized through `fp`.
- Any variant evaluated after editing labels, raw frames, evaluator code, or promotion thresholds is invalid.

Regression checks:
- `fn` cannot increase.
- `python3 scripts/validate_grading_source_of_truth.py` must pass.
- `python3 scripts/bench/run_launch_audit.py` must report `software_launch_ok=True`.

Simplicity cost:
- Prefer the simplest config change that improves the metric.
- Do not add postprocessing fields unless production code already reads them and the evaluator measures their effect.

## Keep/Discard Bands

keep: score improves, `fn` does not increase, protected checks pass, and the variant is a reusable inference setting.
discard: score is flat/lower, `fn` increases, protected checks fail, or the change depends on evaluation leakage.
crash: evaluator, validation, or launch audit fails for tool/runtime reasons.
blocked: no config-only variant can improve the score; next step requires new reviewed frames, teacher labels, or detector retraining.
