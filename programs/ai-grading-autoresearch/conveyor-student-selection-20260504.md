# AI Grading Conveyor Student Selection Loop

## Run Scope

Run tag: `conveyor-student-selection-20260504`
Runtime target: 7 hours.
Repo: `/Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch`
Results TSV: `/Users/coltonheil/repos/autoresearch/results/ai-grading-autoresearch/conveyor-student-selection-20260504.tsv`
Artifact directory: `~/.openclaw/workspace/outputs/autoresearch/ai-grading-autoresearch/conveyor-student-selection-20260504/`

## Immutable Evaluator And Corpus

Evaluator:

```bash
python3 scripts/bench/evaluate_conveyor_student_recipe.py \
  --config configs/conveyor_student/inference_recipe.autoresearch.json
```

Truth inputs:

- `outputs/conveyor-h1-box-truth/20260504T0043Z-H1-sam-rescue-boxes/h1_box_truth.json`
- `outputs/conveyor-active-learning-point-truth/20260503T2330Z-active-point-truth/active_learning_point_truth.json`
- `outputs/conveyor-active-learning-point-truth/20260504T0057Z-active-balanced-point-truth/active_learning_point_truth.json`

The corpus contains 230 reviewed conveyor frames with count truth from H1 and
two active-learning review rounds. These labels, source images, evaluator
script, model weights, and score formula are frozen during the run.

## Mutable Surface

Only this file may change:

```bash
configs/conveyor_student/inference_recipe.autoresearch.json
```

Allowed edits:

- select `single`, `union_nms`, or `r2_plus_r1_rescue`
- select `r1` or `r2` as primary model
- tune model confidence thresholds
- tune NMS IoU and rescue IoU
- tune maximum area fraction

Disallowed edits:

- truth files
- evaluator code
- reviewed frame set
- model weights
- training data
- score formula
- promotion criteria

## Metric

Primary metric: `quality_score`, higher is better.

The fixed evaluator computes:

- count MAE across reviewed frames
- under-count rate
- over-count rate
- empty-belt false-positive rate
- fully missed visible-frame rate
- perfect-count rate

Regression gates:

- empty-belt false-positive rate must remain `0`
- missed visible-frame rate must remain `0`
- under-count rate may not rise by more than `0.01` versus the current best
- keep only strict `quality_score` improvements

## Baseline

Baseline recipe: active-round-1 student, single model, confidence `0.50`,
NMS IoU `0.55`.

Baseline command:

```bash
cd /Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch
python3 scripts/bench/evaluate_conveyor_student_recipe.py \
  --config configs/conveyor_student/inference_recipe.autoresearch.json \
  --run-id baseline-r1-conf050
```

Observed baseline:

- quality score `92.981516`
- count MAE `0.604348`
- under-count rate `0.04558`
- over-count rate `0.050414`
- empty-belt FP rate `0`
- missed visible-frame rate `0`
- perfect-count rate `0.63913`

## Loop Command

```bash
cd /Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch
python3 scripts/bench/run_conveyor_student_recipe_autoresearch.py \
  --duration-hours 7 \
  --max-experiments 2500
```

## Keep Or Discard

For every experiment:

1. Write one candidate recipe to the mutable surface.
2. Run the frozen evaluator.
3. Append one TSV row.
4. Keep only if metric improves and gates pass.
5. Restore the best recipe for all discarded or crashed variants.

## Stop Conditions

- 7-hour wall clock expires.
- 2500 experiments complete.
- evaluator crashes repeatedly on the same class of candidate.
- continuing requires new human labels, new model training, or RunPod/CUDA.

## Promotion Target

The winning recipe remains in:

```bash
configs/conveyor_student/inference_recipe.autoresearch.json
```

It is not production-promoted until side-by-side qualitative review confirms
root boxes/counts are better on unreviewed conveyor flow and the next active
learning queue is generated from the selected recipe.
