# AI Grading Foundation Measurement-Free Optimizer Intelligence Loop

## Run Scope

Run tag: `foundation-measurement-free-optimizer-intelligence-20260505`
Runtime target: 6 hours.
Repo: `/Volumes/CrucialX10/Colton/dev/repos/ai-grading-autoresearch`
Results TSV: `/Users/coltonheil/repos/autoresearch/results/ai-grading-autoresearch/foundation-measurement-free-optimizer-intelligence-20260505.tsv`
Artifact directory: `~/.openclaw/workspace/outputs/autoresearch/ai-grading-autoresearch/foundation-measurement-free-optimizer-intelligence-20260505/`
Promotion target: `reports/measurement-free-optimizer-intelligence/20260505T-foundation-v2/`

## Baseline

Baseline packet:
`reports/measurement-free-optimizer-intelligence/20260505T-v1/`

Baseline status: local engineered-feature packet, complete and validated. It
uses OpenCV morphology/color/texture features, PCA/KMeans clustering, heuristic
bucket suitability, and coarse value priors. It is useful but not best-in-class
foundation compute.

## Immutable Corpus And Guardrails

Inputs:

- `reports/measurement-free-optimizer-intelligence/20260505T-v1/`
- `reports/final-bucket-cut-suitability/20260504T-8h-goal/mixed_lot_root_features.csv`
- `reports/final-bucket-cut-suitability/20260504T-8h-goal/raw_root_final_bucket_suitability.csv`
- `outputs/mixed-lot-clean-grade-crops/20260504T-full-clean-single-root-grade-crops/crops/images/`
- `inputs/china-sorting/training_dataset/`
- `data/final_grade_taxonomy/`
- `reports/premeasurement-optimizer-setup/20260505T-v1/`

Guardrails:

- Do not claim exact grams or centimeters from image proxies.
- Do not mark retail images, generated images, heuristic outputs, or foundation
  outputs as optimizer truth.
- Do not create broad human labeling tasks.
- Do not train a production dollar optimizer before closed microbatch outcomes.
- Do not mutate source truth, final grade taxonomy, reviewed China labels, or
  prior committed report packets.

## Compute Policy

Use the strongest practical foundation vision stack:

- DINOv3-class embeddings, or the strongest locally/RunPod-available visual
  embedding model if DINOv3 cannot be installed or loaded.
- SAM2/SAM2.1-class segmentation or an equivalent foundation segmenter for mask
  and segmentation disagreement, at full coverage if feasible or representative
  subset coverage if compute/model setup is blocked.
- RunPod/GPU is authorized if local M4 Pro inference is too slow, lacks model
  support, or cannot fit the model.

Every artifact must record model name, checkpoint/version, hardware/runtime,
config, coverage, failures, and fallback reason if any.

## Mutable Surface

Allowed mutable surface:

- scripts/configs that build the foundation v2 packet under
  `reports/measurement-free-optimizer-intelligence/20260505T-foundation-v2/`
- RunPod/Falcon/foundation-model invocation configs and captured metadata
- validation scripts for the foundation v2 packet

Protected surfaces:

- source images and labels
- `data/final_grade_taxonomy/` truth fields
- prior report packets
- source-of-truth validators except if adding non-invasive checks needed for
  this packet

## Required Outputs

- `foundation_embedding_features.csv`
- `foundation_cluster_assignments.csv`
- `foundation_embedding_atlas.html`
- `segmentation_quality_audit.csv`
- `engineered_vs_foundation_disagreement.csv`
- `foundation_final_bucket_suitability.csv`
- `foundation_optimizer_sensitivity.md`
- `measurement_priority_queue_v3.csv`
- `readiness_report.md`
- validation summaries
- Playwright screenshots for generated HTML
- completion audit mapping requirements to evidence

## Metric

Primary metric: `foundation_readiness_score`, higher is better.

Score components:

- foundation embedding coverage across 15k+ clean crops and 1,103 China anchors
- segmentation/foundation mask audit coverage
- cluster diversity and lot coverage
- China-label anchoring and nearest-neighbor evidence
- engineered-vs-foundation disagreement surfaced
- weak final-bucket probability coverage with uncertainty
- v3 measurement queue diversity, uncertainty, and economic-swing coverage
- model/runtime provenance completeness
- Playwright render pass for atlas
- repo validators pass

Regression gates:

- `validate_grading_source_of_truth.py` must pass.
- `validate_final_grade_taxonomy.py` must pass if taxonomy-adjacent files are
  touched.
- Generated HTML must have 0 broken local images under Playwright.
- No output may fill real measurement fields without actual human-provided
  measurements.
- Any fallback from DINOv3/SAM2-class models must be explicit and auditable.

## Loop Shape

For every experiment:

1. Propose one concrete foundation-compute artifact improvement.
2. Change only the foundation v2 builder/config/invocation surface.
3. Rebuild or incrementally extend the v2 packet.
4. Run fixed validation/readiness checks.
5. Log one TSV row.
6. Keep the variant only if foundation readiness improves and gates pass;
   otherwise discard or supersede it.

## Stop Conditions

- 6-hour wall clock expires.
- Required v2 packet is complete and validated.
- Continuing requires real weights, ruler measurements, closed microbatch
  outputs, buyer values, credentials, or unavailable model access.
- Repeated crashes occur on the same missing dependency or GPU/model blocker.

## Promotion Target

Promote the best validated packet into:

`reports/measurement-free-optimizer-intelligence/20260505T-foundation-v2/`

Update `PLAN.md` and `CURRENT_WORK.md` with the active packet, validation
status, model/runtime provenance, fallback notes, and remaining measurement
blockers.
