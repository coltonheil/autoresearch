# AI Grading Bench Detector Inference Loop

## Source Model

Upstream pattern:
- one mutable surface
- protected evaluator/corpus
- fixed budget
- baseline first
- results.tsv
- keep only metric wins; discard/revert losses

## Run Scope

Run tag: `ai-grading-bench-detector-inference`
Branch or snapshot policy: run from `/Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch`; snapshot the mutable config before each experiment and restore losing variants.
Results TSV: `/Users/coltonheil/repos/autoresearch/results/ai-grading-autoresearch/bench-detector-inference.tsv`
Artifact directory: `~/.openclaw/workspace/outputs/autoresearch/ai-grading-autoresearch/bench-detector-inference/`

## Baseline

Baseline command:

```bash
cd /Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch
python3 scripts/bench/evaluate_detector_against_reviewed_labels.py \
  --config configs/bench/historical_yolo_inference.json
```

Metric extraction command:

```bash
jq -r '.best | [.recall, .precision, .tp, .fp, .fn, .imgsz, .conf] | @tsv' \
  /Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch/reports/bench-detector-eval/latest.json
```

Baseline artifact: `reports/bench-detector-eval/latest.json`

## Hypothesis

Reusable failure mode: the current detector suppresses real thin roots at the default confidence threshold and creates duplicate boxes when threshold is lowered.
Expected improvement: tune inference config or a postprocessing config so recall improves without adding duplicate/false-positive boxes.
Why this should generalize: thin root recall and duplicate suppression are detector behaviors that should apply across current-camera bench frames before larger retraining.

## Variant

Mutable surface: `/Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch/configs/bench/historical_yolo_inference.json`
Allowed edits: `conf`, `imgsz`, and explicitly documented postprocessing fields if the production code already reads them.
Disallowed edits: reviewed labels, raw frames, evaluator code, train/test split, detector weights, launch audit thresholds, or promotion criteria.
Protected evaluator/corpus/rubric:
- `scripts/bench/evaluate_detector_against_reviewed_labels.py`
- `inputs/bench/reviewed_detection_labels/20260501_indoor_root_test/labels.json`
- `inputs/bench/sessions/20260501_indoor_root_test/raw_frames/`
- `rubrics/ai-grading-autoresearch/bench-detector-inference.md`

## Evaluation

Evaluation set: non-excluded reviewed production-geometry frames from `20260501_indoor_root_test`.
Primary metric: `recall - (0.05 * fp)`, with precision and raw `fn`/`fp` as protected gates.
Direction: higher is better.
Keep threshold: keep only if score improves over the current best and `fn` does not increase.
Regression gates:
- `fn` must not increase.
- `fp` must not increase unless recall improves and the score still improves.
- `python3 scripts/validate_grading_source_of_truth.py` must pass.
- `python3 scripts/bench/run_launch_audit.py` must keep software launch passing.
Fixed budget per experiment: 10 minutes or one config variant, whichever comes first.

## Iteration Protocol

1. Inspect current config and latest `results.tsv` entry.
2. State one hypothesis.
3. Change only `configs/bench/historical_yolo_inference.json`.
4. Save the variant artifact under the output directory.
5. Run the fixed evaluator and validation commands.
6. Extract metric and regression checks.
7. Append one TSV row.
8. Keep only if the score improves and gates pass.
9. Restore losing, equal, crashed, or over-complex variants.
10. Continue until interrupted or a stop condition fires.

## Stop Conditions

Timeout: stop after 2 hours unless explicitly extended.
Crash retry limit: stop after 2 evaluator crashes from the same hypothesis class.
External blocker: stop when further improvement requires new reviewed frames, new labels, or training new weights.
Cost or safety limit: no remote GPU spend from this loop.
Human approval boundary: do not promote production if `reports/launch-audit/latest.json` has `promotion_ok=false`.

## Promotion Target

Winning artifact: `configs/bench/historical_yolo_inference.json`
Promotion command:

```bash
cd /Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch
python3 scripts/bench/segment_roots_in_session.py inputs/bench/sessions/20260501_indoor_root_test --models historical_yolo_root_detector
python3 scripts/bench/evaluate_detector_against_reviewed_labels.py --config configs/bench/historical_yolo_inference.json
python3 scripts/bench/run_launch_audit.py
```

Dry-run default: yes; no production promotion unless launch audit passes.
Post-promotion validation: source-of-truth validation, launch audit, pre-shop check.
