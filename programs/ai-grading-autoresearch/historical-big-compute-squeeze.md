# AI Grading Historical Big-Compute Squeeze

## Source Model

Upstream pattern:
- one mutable surface per experiment loop
- protected evaluator/corpus
- fixed budget
- baseline first
- results.tsv
- keep only metric wins; discard/revert losses

This program is meant to run under a Codex `/goal`, but `/goal` is only the
runtime wrapper. The experiment discipline lives here.

## Run Scope

Run tag: `ai-grading-historical-big-compute-squeeze`
Branch or snapshot policy: work from `/Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch`; do not revert unrelated user work; snapshot mutable config/dataset/model artifacts before each experiment. The run is allowed to make targeted checkpoint commits for its own artifacts only.
Results TSV: `/Users/coltonheil/repos/autoresearch/results/ai-grading-autoresearch/historical-big-compute-squeeze.tsv`
Artifact directory: `~/.openclaw/workspace/outputs/autoresearch/ai-grading-autoresearch/historical-big-compute-squeeze/`

## Baseline

Baseline commands:

```bash
cd /Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch
python3 scripts/validate_grading_source_of_truth.py
python3 scripts/bench/build_historical_scene_manifest.py
python3 scripts/bench/export_historical_detection_dataset.py
python3 scripts/bench/evaluate_detector_against_reviewed_labels.py --config configs/bench/historical_yolo_inference.json
python3 scripts/bench/run_launch_audit.py
```

Metric extraction commands:

```bash
jq -r '.best | [.recall, .precision, .tp, .fp, .fn, .imgsz, .conf] | @tsv' \
  reports/bench-detector-eval/latest.json
tail -n 1 outputs/historical-scene-evaluator/train-runs/historical-yolo11n-mps-v1/results.csv
jq -r '[.software_launch_ok, .promotion_ok] | @tsv' reports/launch-audit/latest.json
```

Baseline artifacts:
- `outputs/historical-scene-evaluator/historical_scene_manifest.json`
- `outputs/historical-scene-evaluator/yolo-root-detector/data.yaml`
- `outputs/historical-scene-evaluator/train-runs/historical-yolo11n-mps-v1/`
- `reports/bench-detector-eval/latest.json`
- `reports/launch-audit/latest.json`

## Objective

Squeeze the existing historical source images before moving to conveyor data
collection. The run should determine whether remaining detector errors are due
to unexploited historical data, weak synthetic data, or genuinely new current
camera/conveyor domain gaps.

## Immutable Inputs

- `inputs/china-sorting/raw/`
- `inputs/staged/*/images/`
- `inputs/china-sorting/training_dataset/`
- `inputs/staged/*/reference-crops/`
- `outputs/historical-scene-evaluator/historical_scene_manifest.json`
- `outputs/historical-scene-evaluator/yolo-root-detector/data.yaml`
- `inputs/bench/reviewed_detection_labels/20260501_indoor_root_test/labels.json`
- `configs/bench/historical_yolo_inference.json`

## Protected Evaluators

These cannot be edited during the autoresearch run:

- `scripts/validate_grading_source_of_truth.py`
- `scripts/bench/build_historical_scene_manifest.py`
- `scripts/bench/export_historical_detection_dataset.py`
- `scripts/bench/evaluate_detector_against_reviewed_labels.py`
- `scripts/bench/evaluate_bakeoff_report_against_reviewed_labels.py`
- `scripts/bench/run_launch_audit.py`
- historical split metadata inside
  `outputs/historical-scene-evaluator/historical_scene_manifest.json`
- reviewed Basler transfer labels in
  `inputs/bench/reviewed_detection_labels/20260501_indoor_root_test/labels.json`

If an evaluator is objectively wrong, stop and report `blocked`; do not mutate
it mid-loop.

## Loop A: Teacher Proposal Audit

Question: can expensive teacher models improve or verify the existing
historical full-frame boxes?

Mutable surface: teacher proposal/acceptance config only.
Allowed edits:
- teacher model list
- teacher prompt/config files
- proposal confidence thresholds
- explicit acceptance-rule config

Disallowed edits:
- historical ground-truth boxes
- reviewed Basler labels
- evaluator scripts
- training scripts

Primary metric:
- disagreement yield with direct evidence, not proposal volume.

Keep rule:
- keep only if the variant produces a smaller, higher-quality review queue or
  identifies true missing/duplicate/loose boxes with evidence.

Required outputs:
- teacher proposals under a versioned output path
- disagreement report
- review queue with raw-frame provenance
- keep/discard row in results TSV

RunPod teacher execution requirement:
- Use a standard RunPod PyTorch/Jupyter CUDA pod as the first reliable
  execution path. The Mac stays the control plane; the pod runs expensive
  teacher inference only.
- Bootstrap the pod with
  `/Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch/remote_gpu/bootstrap_teacher_jupyter.sh`.
- Prefer the official Falcon Perception `/v1/predictions` endpoint when it
  starts cleanly. If the official endpoint fails, record a `crash` or
  `blocked` row with logs and try the repo-local `/infer` worker only as the
  next explicit teacher experiment.
- Do not fall back to local Mac teacher inference for Falcon/SAM-class models;
  local Mac results are allowed only for already wired lightweight comparison
  teachers such as GroundingDINO/OWLv2/Florence.
- Do not switch to student YOLO training until at least one Loop A teacher pass
  has produced a proposal/disagreement artifact or the teacher path is
  explicitly logged as blocked.
- RunPod proof artifacts must include pod id, GPU model, CUDA check,
  endpoint health response, endpoint URL protocol, and stop confirmation.

## Loop B: Synthetic Scene Recipe

Question: can synthetic full-frame scenes generated from the 1,103 crops and
staged reference crops improve detector generalization?

Mutable surface: synthetic generation recipe/config only.
Allowed edits:
- background mix
- scale/rotation/spacing distributions
- overlap and shadow settings
- synthetic/real mix ratio

Disallowed edits:
- evaluator scripts
- reviewed labels
- historical split
- detector training code, unless the loop is explicitly switched to Loop C

Primary metric:
- fast student detector score on fixed historical held-out split, with Basler
  transfer score as protected regression.

Keep rule:
- keep only if the synthetic recipe improves the fixed metric and does not
  worsen Basler transfer `fn` or `fp`.

Required outputs:
- versioned synthetic dataset manifest
- exact recipe/config
- sample contact sheet
- model/eval comparison showing keep/discard

## Loop C: Fast Student Training Recipe

Question: can GPU-backed student training beat `historical-yolo11n-mps-v1`
without hurting current Basler transfer?

Mutable surface: training config only.
Allowed edits:
- model size
- image size
- epochs/patience
- batch size
- augmentations
- real/synthetic/teacher-labeled data mix

Disallowed edits:
- evaluator scripts
- reviewed labels
- launch audit criteria
- manual promotion docs unless the candidate wins

Primary metric:
- historical held-out detector metric, with Basler reviewed-label metric as
  protected regression.

Protected gates:
- `python3 scripts/validate_grading_source_of_truth.py` passes
- `python3 scripts/bench/run_launch_audit.py` reports `software_launch_ok=true`
- Basler reviewed-label `fn` cannot increase
- Basler reviewed-label `fp` cannot increase unless historical metric improves
  materially and the run is explicitly marked as a non-promotion research win

Promotion rule:
- a candidate can become the active fast detector only after it beats the
  current baseline and passes protected gates.
- production promotion still requires launch audit `promotion_ok=true`.

## Evaluation

Primary score:

```text
historical_detector_score_with_basler_regression
```

For logged rows, record:
- historical mAP50
- historical mAP50-95
- Basler precision
- Basler recall
- Basler TP/FP/FN
- launch audit software/promotion status

Direction: higher is better, but protected gates dominate the scalar score.

Fixed budget per experiment:
- Loop A: one teacher configuration or 2 GPU-hours, whichever comes first.
  The first six-hour run should spend its first valid GPU experiment on
  Falcon/SAM-class teacher proposals and disagreement mining, not plain
  student training.
- Loop B: one synthetic recipe plus one student train/eval cycle.
- Loop C: one training config plus one train/eval cycle.

Total first-run budget:
- 6 hours wall time from goal launch.
- Stop before 6 hours if a program stop condition fires.
- Do not exceed the user-approved spend envelope without asking.

## Checkpoint And Commit Policy

The run must not lose progress if it hits the six-hour deadline. Use targeted
commits and artifact snapshots:

- Create or reuse a run id such as
  `historical-big-compute-squeeze-YYYYMMDDTHHMMSSZ`.
- Before the first experiment, commit the program/rubric/results launch files
  in `~/repos/autoresearch` if they are still uncommitted.
- After baseline and after every experiment, append a results TSV row and write
  a run note under the artifact directory.
- Commit only the loop-owned files needed to preserve progress:
  - `/Users/coltonheil/repos/autoresearch/results/ai-grading-autoresearch/historical-big-compute-squeeze.tsv`
  - relevant run notes/manifests/configs under this repo or the artifact root
  - versioned dataset/model comparison reports produced by the run
- Do not stage or commit unrelated dirty work in the repo.
- If a model artifact is too large for git, write its path, checksum, and
  metrics into a committed manifest instead of committing the weight file.
- Every commit message must start with
  `autoresearch historical squeeze:` and describe the checkpoint.
- If the run reaches the deadline mid-experiment, stop the experiment safely,
  write a `blocked` or `crash` row if needed, commit the latest ledger/notes,
  and produce a final status memo.

## Iteration Protocol

1. Inspect current git/worktree and latest results TSV entry.
2. Restate the active loop: A, B, or C.
3. Record baseline/current-best metrics before changing anything.
4. State one hypothesis.
5. Change only the mutable surface for that loop.
6. Run fixed commands and save logs/artifacts.
7. Extract metrics and protected gate results.
8. Append one TSV row.
9. Commit the checkpoint artifacts according to the checkpoint policy.
10. Keep only if the metric improves and gates pass.
11. Revert/discard losing, equal, crashed, or over-complex variants.
12. Stop and report if further improvement requires conveyor-domain data.

For the next launch, start with Loop A unless the RunPod teacher endpoint is
blocked after the setup cap. The first Loop A hypothesis should be:

```text
Falcon/SAM-class GPU teachers can reduce human labeling work by finding
historical missing/duplicate/loose boxes and hard negatives that local
teachers or YOLO missed.
```

The first Loop A metric is not model accuracy. It is evidence-backed
disagreement yield: true suspicious boxes per reviewed proposal, with raw-frame
provenance and no changes to source truth.

## Stop Conditions

Stop when any is true:
- Six hours of wall time have elapsed.
- A best historical student candidate is documented and remaining failures are
  clearly current-camera/conveyor-domain gaps.
- Three consecutive valid variants fail to improve the current best.
- Further progress requires new physical conveyor data.
- Remote GPU spend would exceed the user-approved budget.
- Docker/RunPod/GPU provisioning fails twice in the same way.
- A protected evaluator or source-of-truth inconsistency is discovered.

## Promotion Target

Winning artifacts:
- versioned teacher proposal/disagreement artifacts
- versioned synthetic dataset manifest
- versioned fast student weights
- model comparison report
- source-of-truth/doc updates only for promoted artifacts

Promotion command set:

```bash
cd /Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch
python3 scripts/validate_grading_source_of_truth.py
python3 scripts/bench/evaluate_detector_against_reviewed_labels.py --config configs/bench/historical_yolo_inference.json
python3 scripts/bench/run_launch_audit.py
```

Dry-run default: yes. Do not overwrite the current active model or mark the
goal complete unless the completion audit shows every requirement is satisfied.
