# AI Grading Measurement-Free Optimizer Intelligence Loop

## Run Scope

Run tag: `measurement-free-optimizer-intelligence-20260505`
Runtime target: 6 hours.
Repo: `/Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch`
Results TSV: `/Users/coltonheil/repos/autoresearch/results/ai-grading-autoresearch/measurement-free-optimizer-intelligence-20260505.tsv`
Artifact directory: `~/.openclaw/workspace/outputs/autoresearch/ai-grading-autoresearch/measurement-free-optimizer-intelligence-20260505/`

## Immutable Corpus And Guardrails

Inputs:

- `reports/final-bucket-cut-suitability/20260504T-8h-goal/mixed_lot_root_features.csv`
- `reports/final-bucket-cut-suitability/20260504T-8h-goal/raw_root_final_bucket_suitability.csv`
- `outputs/mixed-lot-clean-grade-crops/20260504T-full-clean-single-root-grade-crops/crops/images/`
- `inputs/china-sorting/training_dataset/`
- `data/final_grade_taxonomy/`
- `reports/premeasurement-optimizer-setup/20260505T-v1/`

Guardrails:

- Do not claim exact grams or centimeters from image proxies.
- Do not mark retail images, generated images, or heuristic outputs as
  optimizer truth.
- Do not create broad human labeling tasks.
- Do not train a production dollar optimizer before closed microbatch outcomes.
- Do not mutate source truth, final grade taxonomy, or reviewed China labels.

## Mutable Surface

Allowed mutable surface:

- scripts and configs that build measurement-free intelligence artifacts under
  `reports/measurement-free-optimizer-intelligence/<timestamp>/`
- optional RunPod/Falcon invocation configs if they write versioned outputs and
  do not alter source truth

Protected surfaces:

- `inputs/china-sorting/training_dataset/`
- `data/final_grade_taxonomy/` except documentation/gate updates explicitly
  required by validation
- prior committed report packets
- evaluator/validator scripts once written for this run

## Required Outputs

The loop should produce:

- `root_morphology_features_v2.csv`
- `root_cluster_assignments.csv`
- `root_embedding_atlas.html`
- `final_bucket_suitability_model_v1.csv`
- `optimizer_uncertainty_sensitivity.md`
- `measurement_priority_queue_v2.csv`
- `readiness_report.md`
- validation summaries and Playwright screenshots where HTML is generated

## Metric

Primary metric: `premeasurement_readiness_score`, higher is better.

Score components:

- artifact completeness
- no fake measurement fields
- cluster coverage across 15k+ clean crops
- lot coverage across BEPLE/beple, 153S, and BEDUB
- China-label anchoring where usable
- uncertainty surfaced rather than hidden
- measurement queue diversity and economic-swing coverage
- Playwright render pass for visual atlas
- repo validators pass

Regression gates:

- `validate_grading_source_of_truth.py` must pass.
- `validate_final_grade_taxonomy.py` must pass if taxonomy-adjacent files are
  touched.
- Any generated HTML must have 0 broken local images under Playwright.
- No output may fill real measurement fields without actual human-provided
  measurements.

## Loop Shape

For every experiment:

1. Propose one concrete artifact improvement.
2. Change only the measurement-free intelligence builder/config.
3. Rebuild the packet.
4. Run the fixed validation/readiness checks.
5. Log one TSV row.
6. Keep the variant only if readiness improves and gates pass; otherwise
   discard or supersede it.

## Stop Conditions

- 6-hour wall clock expires.
- Required output packet is complete and validated.
- Continuing requires real weights, ruler measurements, closed microbatch
  outputs, buyer values, or credentials/access not currently available.
- Repeated crashes occur on the same missing dependency.

## Promotion Target

Promote the best validated packet into:

`reports/measurement-free-optimizer-intelligence/<timestamp>/`

Update `PLAN.md` and `CURRENT_WORK.md` with the active packet, validation
status, and remaining measurement blockers.
