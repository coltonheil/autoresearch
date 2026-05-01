# Blue Star Bid Resolution Rubric

Version: 1.0 | Weights sum: 100

## Scoring Overview

The loop succeeds when ambiguous bids become auditable business decisions or
clear blocker diagnoses. It fails when it relabels stale graph output, treats
missing evidence as no-fit, or creates categories that do not change action.

| Dimension | Weight | Good | Poor |
|---|---:|---|---|
| Decision validity | 20 | Verdict is valid, specific, and changes next action | Verdict is missing, invalid, or vague |
| Direct evidence and provenance | 25 | Direct artifacts with source and locator support high-impact decisions | No citation, only graph absence, or unsupported no-fit |
| Evidence ladder use | 20 | Agent escalates from graph to evidence index/raw/original docs when needed | Agent stops at graph/wiki despite inconclusive evidence |
| Blocker diagnosis | 15 | Missing docs, extraction failures, drawing gaps, and human blockers are separated | Blockers are collapsed into no-fit or generic uncertainty |
| Hypothesis discipline | 10 | Leading hypothesis, disconfirming test, and rejected hypotheses are explicit | Agent searches broadly without a falsifiable test |
| Operational next action | 10 | Next owner/action is concrete and economically sensible | No owner/action or action does not follow from evidence |

## Verdict Rules

Allowed verdicts:

- `pursue_quote`
- `true_no_fit`
- `docs_missing_inaccessible`
- `extraction_failure`
- `drawing_or_vision_review_needed`
- `human_clarification_needed`
- `continue_investigation`

`pursue_quote` and `true_no_fit` require direct evidence.

`true_no_fit` additionally requires proof that relevant docs were present and
readable enough. Missing graph evidence is never sufficient.

Blocker verdicts require a concrete blocker and a next owner/action.

## Direct Evidence Standard

Direct evidence must include:

- artifact path or source id
- locator such as page, section, sheet/range, drawing sheet, bbox, or evidence id
- summary of what the artifact proves
- evidence type `direct`

Indirect evidence may guide investigation but cannot close a high-impact
decision alone.

## Regression Gates

Discard or revise the run if any gate fails:

- any `pursue_quote` lacks direct evidence
- any `true_no_fit` lacks direct evidence
- any `true_no_fit` lacks docs-present/readable support
- any missing-doc or extraction blocker is labeled no-fit
- the ledger omits next owner/action
- the scorer cannot parse the ledger

## Score Interpretation

- 90-100: Strong. Decisions are source-cited and blockers are action-ready.
- 75-89: Useful. Some entries need stronger citations or owner clarity.
- 50-74: Weak. The loop is still diagnosing but not safely closing decisions.
- 0-49: Unsafe. The run risks repeating stale classification errors.

## Keep Threshold

Keep if:

- total score is at least 75,
- every regression gate passes,
- score improves versus baseline or adds net-new valid entries,
- unresolved blockers are named with owners.

Do not keep a lower score just because more items were processed.

## Promotion Gate

Apply the production overlay only if:

- the scorer returns `keep_candidate`,
- `unsupported_decisions` is 0,
- `pursue_quote` entries have direct source evidence and a production-safe next
  action,
- `true_no_fit` entries have direct source evidence and docs-present/readable
  support,
- blocker entries identify whether the owner is source connector, extraction,
  drawing/vision, or human clarification,
- the dry-run promotion creates both decision and pipeline-improvement artifacts.

Promotion must not rewrite raw documents, generated fact sheets, connector code,
or existing bid decisions directly. It writes overlay artifacts that downstream
Blue Star production flows can consume.
