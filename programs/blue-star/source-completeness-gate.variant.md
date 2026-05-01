# Source Completeness Gate Variant

## Candidate Rule

Before assigning `pursue_quote` or `true_no_fit`, classify source completeness
from direct artifacts:

- `complete`: relevant bid docs are present, readable, and cover the scope.
- `missing_or_inaccessible`: required docs are absent, pointer-only, gated,
  expired, credential-blocked, or not downloaded.
- `extraction_failed`: docs exist, but native text/OCR/extracted JSON is
  missing, truncated, noisy, or does not cover the relevant section.
- `drawing_review_needed`: drawings, schedules, equipment tags, site layouts,
  or visual sheets may contain the answer and have not been inspected.
- `human_blocked`: decision requires business judgment, agency clarification,
  partner acceptance, credentials, paid access, or live mutation approval.

Only `complete` can support final quote/no-fit decisions. All other states must
route to a typed blocker with owner and next action.

## Blocker Precedence

Apply blocker states before business-fit states:

1. If required bid documents are absent, pointer-only, unavailable, gated, or
   not downloaded, return `docs_missing_inaccessible`.
2. If documents are present but required text/table artifacts are missing,
   permanently failed, truncated, stale, or not covering the quote-critical
   section, return `extraction_failure`.
3. If drawings, one-lines, schedules, equipment tags, site plans, rendered
   pages, or visual sheets may contain the deciding facts and have not been
   inspected, return `drawing_or_vision_review_needed`.
4. If the remaining blocker is approval, credentials, commercial judgment, or
   partner acceptance, return `human_clarification_needed`.
5. Only after the source state is `complete`, decide `pursue_quote` or
   `true_no_fit`.

Never treat missing evidence as evidence against fit. A missing source,
failed extraction, or unreviewed drawing is a blocker state, not a no-fit
decision.

## Evidence Requirement

High-impact decisions require:

- source path or source id
- locator: page, section, sheet/range, drawing sheet, bbox, or evidence id
- short summary of what the artifact proves
- source-completeness state
- next owner/action

Missing evidence is a blocker, not negative evidence.
