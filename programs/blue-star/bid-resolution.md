# Blue Star Bid Resolution Loop

## Purpose

Resolve ambiguous Blue Star bid opportunities into auditable, action-ready
business decisions. This loop is not another bulk classifier. It exists to
separate true opportunity decisions from document-access failures, extraction
failures, drawing/vision gaps, and human clarification needs.

The core question for each opportunity:

```text
Should Blue Star spend effort quoting or pursuing this bid, and what evidence
or blocker justifies that answer?
```

## Target

- Blue Star repo: `~/repos/blue-star`
- Active bid knowledge base: `~/repos/blue-star/bid-intelligence`
- Entry point: `bid-intelligence/wiki/index.md`
- Control-plane artifacts:
  - `bid-intelligence/wiki/bid-quote-action-plan.json`
  - `bid-intelligence/wiki/bid-quote-fact-gap-report.json`
  - `bid-intelligence/wiki/bid-readiness-review-decisions.json`
  - `bid-intelligence/wiki/bid-readiness-burndown-report.json`
  - `bid-intelligence/wiki/current-state-audit.json`
- Result log: `~/repos/autoresearch/results/blue-star/bid-resolution.tsv`
- Scorer: `~/repos/autoresearch/scripts/blue_star/score_bid_resolution.py`
- Artifacts:
  `~/.openclaw/workspace/outputs/autoresearch/blue-star/bid-resolution/<YYYY-MM-DD>/`

## Valid Verdicts

Use only verdicts that change the next action:

- `pursue_quote`: evidence supports quote/pursuit.
- `true_no_fit`: relevant docs were present/readable and direct scope evidence
  supports no-fit.
- `docs_missing_inaccessible`: needed bid docs are absent, pointer-only, gated,
  expired, credential-blocked, or otherwise inaccessible.
- `extraction_failure`: source docs exist, but native text/OCR/extracted JSON is
  missing, weak, truncated, noisy, or does not cover the relevant section.
- `drawing_or_vision_review_needed`: drawings, plans, schedules, equipment tags,
  site layouts, or visual scope may contain the answer and current artifacts do
  not resolve it.
- `human_clarification_needed`: the next action requires business judgment,
  agency/vendor clarification, credentials, paid access, or another human owner.
- `continue_investigation`: one bounded high-information test remains and is
  worth running within this loop.

## Evidence Ladder

Use the graph/wiki as the first retrieval layer, not the truth ceiling.

For each bid:

1. Read the wiki bid pages and JSON sidecars:
   - `bid-intelligence/wiki/<bid_id>/overview.md`
   - `bid-intelligence/wiki/<bid_id>/requirements.md`
   - `bid-intelligence/wiki/<bid_id>/drawings-electrical-generators.md`
   - `bid-intelligence/wiki/<bid_id>/contradictions.md`
   - `bid-intelligence/wiki/<bid_id>/requirement-graph.json`
   - `bid-intelligence/wiki/<bid_id>/evidence-index.json`
   - `bid-intelligence/wiki/<bid_id>/source-map.json`
2. If inconclusive, inspect raw artifacts:
   - `bid-intelligence/raw/<bid_id>/source-manifest.json`
   - `bid-intelligence/raw/<bid_id>/ocr-text/`
   - `bid-intelligence/raw/<bid_id>/drawings/`
   - `bid-intelligence/raw/<bid_id>/extracted-json/`
   - `bid-intelligence/raw/<bid_id>/original-pdfs/`
   - `_supabase-storage.json` pointer records if originals are missing.
3. If source docs exist, inspect the original PDFs, spreadsheets, docs, or
   extracted text directly enough to settle the hypothesis.
4. If source docs exist but extraction is weak, do not infer no-fit. Mark
   `extraction_failure` and name the required GLM OCR, spreadsheet parsing, or
   targeted extraction action.
5. If drawings may contain the answer, do not decide no-fit from text-only
   artifacts. Mark `drawing_or_vision_review_needed` unless selected drawing
   records or original pages settle the issue.

## Direct Evidence Standard

Direct evidence means a cited source artifact with a locator:

- document path plus page, section, sheet/cell/range, drawing sheet, bbox, or
  JSON evidence id
- short summary of what the artifact proves
- evidence type: `direct`

Indirect evidence includes titles, filenames, graph absence, previous labels,
heuristics, and partial indexes. Indirect evidence may guide investigation but
must not close `pursue_quote` or `true_no_fit` alone.

## Iteration Protocol

Each run follows this sequence:

1. Capture baseline by running:

   ```bash
   cd ~/repos/autoresearch
   python3 scripts/blue_star/score_bid_resolution.py
   ```

2. Select the next highest-value ambiguous bid from the active control-plane
   artifacts. Prefer bids where a decision would change quote action or reveal
   a systemic document/extraction blocker.

3. Write one JSONL ledger entry per bid under the dated artifact directory:

   ```text
   ~/.openclaw/workspace/outputs/autoresearch/blue-star/bid-resolution/<YYYY-MM-DD>/ledger.jsonl
   ```

4. For each bid, state the leading hypothesis and the smallest disconfirming
   test before reading more files.

5. Run only the next best test from the evidence ladder.

6. Choose one valid verdict or explicitly mark `continue_investigation`.

7. Re-run the scorer and compare against baseline.

8. Keep the run if:
   - score improves,
   - no `pursue_quote` or `true_no_fit` decision lacks direct evidence,
   - no missing-doc/extraction blocker is mislabeled as no-fit,
   - the ledger names the next action and owner.

9. Discard or revise the run if:
   - score does not improve,
   - decisions are unsupported,
   - evidence is only indirect for high-impact verdicts,
   - the loop creates labels that do not change next action.

10. Append one row to `results/blue-star/bid-resolution.tsv`.

## Required Ledger Shape

Each `ledger.jsonl` line must be a JSON object:

```json
{
  "run_id": "bsbr-YYYYMMDD-r01",
  "bid_id": "example-bid-id",
  "previous_state": "ambiguous",
  "decision": "Should Blue Star quote or pursue this bid?",
  "leading_hypothesis": "This may be a true no-fit because...",
  "disconfirming_test": "Inspect scope/spec section and drawings for...",
  "artifacts_inspected": [
    "bid-intelligence/wiki/<bid_id>/requirements.md"
  ],
  "evidence": [
    {
      "type": "direct",
      "source": "bid-intelligence/raw/<bid_id>/original-pdfs/spec.pdf",
      "locator": "p. 14, Scope of Work",
      "summary": "Scope is limited to..."
    }
  ],
  "doc_quality": {
    "docs_present": true,
    "readable": true,
    "extraction_quality": "adequate",
    "blocker": null
  },
  "rejected_hypotheses": [
    "docs_missing_inaccessible"
  ],
  "verdict": "true_no_fit",
  "confidence": "medium",
  "next_action": "Move to no-fit with citation.",
  "owner": "agent"
}
```

## Editable Scope

Agents may create or update:

- the run ledger under `~/.openclaw/workspace/outputs/autoresearch/...`
- result rows in `~/repos/autoresearch/results/blue-star/bid-resolution.tsv`
- narrow bid wiki notes only when preserving source-cited truth

Agents may inspect all active Blue Star bid-intelligence files and original
documents.

## Protected Scope

Do not modify during a run unless explicitly asked:

- this program file
- the rubric
- the scorer
- original raw source documents
- Blue Star connector/source code
- unrelated roadmap or app code

## Stop Conditions

Stop when any condition is met:

- 20 ambiguous bids resolved
- 90 minutes elapsed
- three consecutive bids share the same systemic blocker
- scorer reports unsupported high-impact decisions
- the next action requires credentials, paid access, external portal access, or
  human business judgment

## Recommended `/goal`

```text
Run the Blue Star bid-resolution autoresearch program from
~/repos/autoresearch/programs/blue-star/bid-resolution.md for up to 90 minutes
or 20 ambiguous bids. Follow the rubric and scorer, keep a JSONL ledger, use
the Blue Star document-intelligence evidence ladder, and stop if repeated
systemic blockers or unsupported decisions appear.
```
