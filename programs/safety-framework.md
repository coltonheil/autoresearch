# Universal Safety Framework

## Purpose

This file defines the mandatory safety gates for every Heil Ginseng autoresearch domain.

It exists because a kept variant is not the same thing as a safe variant.

The autoresearch loop is allowed to generate drafts, score them, keep winners, and discard losers. It is not allowed to move a kept variant toward live use unless the safety requirements in this file are satisfied.

This framework preserves the core `karpathy/autoresearch` pattern:

1. change one thing
2. measure the result
3. keep the change if it improves the score
4. discard it if it does not
5. repeat

But for business systems, one more rule is required:

6. never promote a kept variant unless it is safe, auditable, reversible, and approved

This is a universal control layer. It sits between:

- `variant scored as KEEP`
- and `variant promoted toward live use`

## Scope

This framework applies only to autoresearch loop outputs.

It applies to:

- product page copy loops
- SEO metadata loops
- theme and layout loops
- review display loops
- buy box and mobile UX loops
- site performance loops
- technical SEO loops
- ad creative generation loops
- ad copy loops
- email subject and body loops
- social copy loops

It does not apply to:

- one-off manual edits made outside autoresearch
- ordinary human brainstorming
- general strategy discussions
- reporting that does not create or promote a variant

## Core operating principle

A variant may win on proxy score and still be unsafe.

Examples:

- a PDP variant could improve clarity but break Judge.me rendering
- a theme tweak could improve Lighthouse but break mobile layout
- an SEO change could improve metadata quality but remove structured data
- an ad creative package could score well but fail compliance review
- a copy package could be strong but have no rollback trail

Because of that, the autoresearch system must treat promotion as a gated pipeline, not an automatic continuation of scoring.

## Relationship to the broader strategy

This framework follows the architecture in `~/.openclaw/workspace/AUTORESEARCH-STRATEGY.md`.

Compliance must exist in two layers:

- **Layer 1: inside the loop**
  - compliance is part of the scoring system
  - unsafe variants lose points or fail immediately
- **Layer 2: final gate on survivors**
  - Ben reviews every kept customer-facing variant before promotion

This document does not replace that strategy. It operationalizes it.

## Safety tiers

Every autoresearch domain must be classified into one of three safety tiers before the loop is allowed to run.

If a domain touches multiple surfaces, classify it by the highest-risk surface it can affect.

Example:

- a loop that changes both metadata and live PDP copy is **Tier 1**, not Tier 2 or Tier 3
- a loop that only produces ad concepts and image drafts is **Tier 2**
- a loop that only changes script load order and validates Lighthouse is **Tier 3**

## Tier 1 — Live Site Changes

Tier 1 is the highest-risk class.

Use Tier 1 for any autoresearch domain that can modify Shopify, the live storefront, a preview that is intended for promotion to live, or any customer-visible site element whose failure can break purchase flow, trust, layout, or compliance.

### Tier 1 examples

- PDP copy
- SEO metadata when it changes the live storefront or search-facing product page fields
- theme changes
- collection page changes
- review display changes
- buy box changes
- mobile UX changes
- accordion structure or content order changes
- trust badge placement changes
- template or section changes that affect live rendering

### Tier 1 rule

A Tier 1 winner cannot be promoted unless it has:

- pre-push snapshot
- preview render
- visual verification
- dogfood pass on live
- rollback readiness
- human approval

No exceptions.

## Tier 2 — Draft-Only Output

Tier 2 is medium risk.

Use Tier 2 for autoresearch domains that produce review-ready packages but do not directly touch live systems.

### Tier 2 examples

- ad creative images
- ad copy
- email subject lines
- email body copy
- social post copy
- social caption packages
- campaign concept packages

### Tier 2 rule

A Tier 2 winner may be packaged for human review, but it may never be auto-published, auto-activated, auto-scheduled, or sent externally by the autoresearch system.

Tier 2 outputs stop at review-ready package delivery.

## Tier 3 — Technical/Objective

Tier 3 covers objective technical domains where safety is primarily about measurable regression control.

### Tier 3 examples

- site performance
- technical SEO
- structured data fixes
- script ordering changes
- image payload changes
- non-visual performance optimizations that still affect rendered pages

### Tier 3 rule

A Tier 3 winner cannot be promoted unless it passes:

- baseline capture
- automated regression check
- visual regression check
- rollback readiness

If the change affects live pages, treat the live-push mechanics with Tier 1 discipline even if the scoring lane is objective.

## Universal gates

These gates apply to **all** tiers.

A variant that fails any universal gate is not promotable.

### 1. Compliance scan

Every variant must pass compliance twice.

#### Layer 1: in-loop compliance

The scoring loop must include compliance as a scored dimension or hard-fail rule.

Examples:

- PDP copy gets a compliance safety score
- ad copy gets FDA/FTC screening
- email gets CAN-SPAM and claim review
- social copy gets platform and claim review
- technical SEO gets validation against unsafe or invalid structured data outputs

Unsafe variants should be discarded before they become promotion candidates.

#### Layer 2: Ben gate on kept variants

Every kept customer-facing variant must pass Ben review before promotion.

Status values should be explicit:

- `PENDING_BEN_REVIEW`
- `BEN_PASS`
- `BEN_FAIL`

A kept variant with no Ben decision is not eligible for promotion.

### 2. Audit trail

Every variant must be logged in the domain results TSV with full scoring breakdown.

Minimum requirement:

- run ID
- timestamp
- domain
- variant file or artifact path
- baseline score
- variant score
- score delta
- scoring dimension breakdown
- compliance result
- keep or discard decision
- reviewer status fields
- notes
- branch or commit reference if code or config changed

No silent winners.

If a variant cannot be traced from draft artifact to score to decision, it cannot be promoted.

### 3. Human approval

Colton must explicitly approve before any:

- live push
- external publish
- external activation
- scheduling into a system that will publish later
- paid media activation

Approval must be explicit, not implied.

Valid examples:

- written approval in Discord
- explicit approval in a review channel
- explicit sign-off attached to the run record

Invalid examples:

- "it scored well"
- "it passed Ben"
- "it looks good"
- no objection after a delay

### 4. Rollback plan

Before any state change, the current state must be captured and restorable.

This is mandatory even when the change appears small.

Rollback artifacts must be written to the workspace under:

`~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/rollback/`

Minimum rollback artifact set:

- current-state snapshot or export
- restoration instructions or script reference
- variant identifier tied to the snapshot
- timestamp
- operator or agent identifier

If rollback is not ready, promotion is blocked.

## Artifact paths

All safety artifacts live outside the repo in the workspace outputs tree.

Base path:

`~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/`

Required subdirectories by function:

- snapshots: `~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/snapshots/`
- preview renders: `~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/preview/`
- screenshots: `~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/screenshots/`
- rollback artifacts: `~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/rollback/`
- dogfood artifacts: `~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/dogfood/`
- compliance notes: `~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/compliance/`
- monitoring exports: `~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/monitoring/`

Recommended files:

- `snapshots/pre-push-product.json`
- `snapshots/pre-push-page.json`
- `preview/baseline-preview.png`
- `preview/variant-preview.png`
- `screenshots/baseline-desktop.png`
- `screenshots/baseline-mobile.png`
- `screenshots/variant-desktop.png`
- `screenshots/variant-mobile.png`
- `rollback/restore.json`
- `rollback/restore-instructions.md`
- `dogfood/live-desktop.png`
- `dogfood/live-mobile.png`
- `dogfood/checklist.md`
- `compliance/ben-review.md`
- `monitoring/24h-soak-summary.json`

## Tier 1 gates

These gates are additional requirements for any domain that modifies Shopify or the live website.

### 1. Pre-push snapshot

Before any push, capture the current state via Shopify API or equivalent system API as JSON.

Store it at:

`~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/snapshots/`

The snapshot must contain enough information to fully restore the changed surface.

Examples:

- product title, description, metafields, and SEO fields for PDP copy changes
- section JSON or template config for theme or layout changes
- collection metadata for collection page changes
- structured data payload for schema-related changes

Snapshot rules:

- snapshot must be captured before the variant is pushed
- snapshot filename must include the entity being changed
- snapshot must be tied to the run ID
- snapshot must be readable without external memory or guesswork

### 2. Preview rendering

The variant must be rendered before push.

Allowed preview modes:

- Shopify preview theme
- staging environment
- local HTML approximation when the changed surface can be faithfully rendered
- browser screenshot from a preview URL

At least one preview artifact is required before approval.

Store preview artifacts at:

`~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/preview/`

Minimum preview set for visual surfaces:

- desktop preview screenshot
- mobile preview screenshot
- baseline reference screenshot
- variant reference screenshot

### 3. Visual verification before push

A human must be able to compare baseline versus variant before approving the push.

This can be a side-by-side screenshot review or a documented before/after comparison.

Required storage path:

`~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/screenshots/`

The review must be specific enough to answer:

- what changed
- what stayed the same
- whether the layout remained intact
- whether trust and purchase elements remained visible

### 4. Human approval of the preview

Colton must approve the previewed variant before anything is pushed live.

This approval happens after preview artifacts exist, not before.

A Tier 1 promotion with no preview approval is invalid, even if all automated checks passed.

### 5. Dogfood pass after push

After the variant goes live, run a browser-based QA pass on the live page.

This is not optional.

Store dogfood artifacts at:

`~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/dogfood/`

The live-page dogfood checklist must explicitly verify all of the following:

- Judge.me reviews still render at the top of the page with stars and review count
- Judge.me reviews still render at the bottom review block
- accordions still expand and collapse correctly
- trust badges are still visible
- mobile layout is not broken
- structured data JSON-LD is still valid
- add-to-cart button is functional
- Subscribe & Save still works
- FDA disclaimer is still present

Recommended additional checks when relevant:

- sticky add-to-cart behavior on mobile
- quantity selector behavior
- price visibility
- variant selector behavior
- page load with no obvious console-breaking issue

### 6. Critical-failure rollback trigger

If dogfood fails any critical check, rollback must begin immediately using the pre-push snapshot.

Critical checks include:

- Judge.me top stars and count missing
- Judge.me bottom review block missing
- add-to-cart broken
- Subscribe & Save broken
- FDA disclaimer missing
- severe mobile layout break
- invalid or missing structured data when the page previously validated
- key accordion content inaccessible

On critical failure:

1. stop further promotion activity
2. restore from snapshot
3. capture rollback evidence
4. alert Colton
5. log the failure in the results TSV and dogfood report

### 7. Soak period

A Tier 1 promotion does not become a stable winner immediately after dogfood pass.

It enters a 24-hour soak period.

During the soak period:

- monitor conversion rate versus baseline
- monitor add-to-cart rate if available
- monitor error reports if available
- monitor any obvious customer-facing breakage signal

Store monitoring artifacts at:

`~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/monitoring/`

Soak-period rule:

- if conversion rate drops by more than 15% versus baseline, flag for rollback review

This threshold is a review trigger, not an always-auto-rollback trigger. A human reviews context before deciding whether to revert.

## Tier 2 gates

These gates apply to draft-only output domains.

### 1. Asset validation

Assets must be validated before they are packaged for review.

For images, validate:

- required platform format
- dimensions
- file size
- crop safety
- legibility
- product prominence when applicable
- no AI humans in any Heil visual
- brand-fit score above threshold

For copy, validate:

- platform character limits where relevant
- headline and body fit
- URL field or CTA field fit where relevant
- no prohibited claims

### 2. Platform compliance pre-scan

Every Tier 2 package must pass the right pre-scan for its destination.

Examples:

- FDA/FTC review for ads
- CAN-SPAM review for email
- platform Terms of Service review for social
- product claim review for any paid or promotional copy

This pre-scan happens before packaging and before Ben final review.

### 3. Package format

Tier 2 outputs must be delivered as review-ready packages, not as raw loose files.

A package should include:

- image or asset path
- copy draft
- score breakdown
- compliance notes
- angle or hypothesis
- usage recommendation
- file specs if relevant

Store packages at:

`~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/`

Recommended package names:

- `package-v1.md`
- `package-v2.md`
- `package-v3.md`

### 4. Activation block

The autoresearch system cannot activate, publish, or send Tier 2 outputs.

This is a hardcoded safety rule, not a configurable preference.

The system may:

- generate
- score
- rank
- package
- route for review

The system may not:

- publish a social post
- send an email
- activate an ad
- upload and turn on a campaign
- schedule content for automatic publishing

Only a human may perform activation.

## Tier 3 gates

These gates apply to technical and objective domains.

### 1. Baseline capture

Before any change, capture the baseline technical state.

Store baseline artifacts at:

`~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/snapshots/`

Examples:

- Lighthouse JSON report
- Lighthouse HTML report
- Core Web Vitals measurements
- structured data validation result
- before screenshots for visual surfaces
- payload sizes and script counts

### 2. Automated regression check

After the variant is applied, rerun the same technical tests and compare against baseline.

Examples:

- Lighthouse before vs after
- LCP before vs after
- CLS before vs after
- structured data validation before vs after
- image payload before vs after
- JavaScript weight before vs after

The same test conditions must be used where possible so the comparison is meaningful.

### 3. Visual regression

Even technical changes can break rendering.

For any Tier 3 variant that affects a rendered page, take before and after screenshots and compare them for layout shift or broken rendering.

Minimum visual set:

- desktop before
- desktop after
- mobile before
- mobile after

Store them at:

`~/.openclaw/workspace/outputs/autoresearch/<domain>/<YYYY-MM-DD>/screenshots/`

### 4. Rollback on regression

If any core metric degrades by more than 5% versus baseline, auto-rollback.

Core metrics include the metrics the domain was explicitly optimizing.

Examples:

- Lighthouse performance score
- LCP
- CLS
- structured data validation pass state
- key payload metrics

If the regression threshold is breached:

1. restore the previous state
2. save rollback evidence
3. log the regression in the results TSV
4. mark the variant as failed promotion

## Promotion pipeline

The keep/discard loop and the promotion pipeline are separate.

A kept variant enters promotion review. It does not skip straight to live use.

### Tier 1 promotion pipeline

1. Variant scores `KEEP` in the loop.
2. Ben compliance review returns `PASS`.
3. Pre-push snapshot is captured.
4. Rollback artifacts are written and verified.
5. Variant is applied to preview or staging.
6. Preview screenshot is captured.
7. Baseline screenshot and variant screenshot are compared.
8. Colton approves the preview.
9. Variant is pushed to live.
10. Dogfood pass runs on the live page.
11. Dogfood explicitly checks Judge.me top stars/count, Judge.me bottom review block, accordions, trust badges, mobile layout, structured data, add-to-cart, Subscribe & Save, and FDA disclaimer.
12. If dogfood fails any critical check, auto-rollback from snapshot and alert Colton.
13. If dogfood passes, enter 24-hour soak period.
14. If soak monitoring shows more than 15% conversion drop versus baseline, flag for rollback review.
15. Record final status in results TSV and artifact folders.

### Tier 2 promotion pipeline

1. Variant scores `KEEP` in the loop.
2. Ben compliance review returns `PASS`.
3. Asset validation returns `PASS`.
4. Platform compliance pre-scan returns `PASS`.
5. Review-ready package is assembled.
6. Colton approves the package.
7. Human manually publishes or activates it.

### Tier 3 promotion pipeline

1. Variant scores `KEEP` in the loop.
2. Ben review is required if customer-facing copy or compliance-sensitive outputs are involved.
3. Baseline technical state is captured.
4. Rollback artifacts are prepared.
5. Variant is applied in the testable environment.
6. Automated regression suite is rerun.
7. Before/after screenshots are compared for visual regression.
8. If any core metric degrades by more than 5%, auto-rollback.
9. If checks pass, promote according to the domain's deployment method.
10. Log the final status and evidence.

## Required dogfood checklist for Tier 1

The following checklist must appear verbatim or near-verbatim in the live QA artifact for Tier 1 pages.

- [ ] Judge.me top stars and review count render near the buy box
- [ ] Judge.me bottom review block renders
- [ ] Accordions expand and collapse correctly
- [ ] Trust badges are visible
- [ ] Mobile layout is not broken
- [ ] Structured data JSON-LD validates
- [ ] Add-to-cart button functions
- [ ] Subscribe & Save functions
- [ ] FDA disclaimer is present

If any box is unchecked, the variant is not safely promoted.

## Minimum logging requirements

Every promoted or promotion-attempted variant must leave enough evidence for audit.

At minimum, keep:

- variant markdown or asset package
- score breakdown
- Ben review note
- approval note
- snapshot path
- preview screenshot path
- live dogfood checklist path when applicable
- rollback artifact path when applicable
- monitoring path when applicable
- final status

Recommended final status values:

- `DISCARDED_IN_LOOP`
- `KEPT_PENDING_BEN`
- `BLOCKED_BY_BEN`
- `PENDING_PREVIEW_APPROVAL`
- `APPROVED_FOR_PUSH`
- `LIVE_PENDING_DOGFOOD`
- `ROLLED_BACK_AFTER_DOGFOOD`
- `LIVE_SOAKING`
- `FLAGGED_FOR_ROLLBACK_REVIEW`
- `PROMOTION_COMPLETE`

## Failure handling

Do not hide failed promotions.

If a promotion attempt fails, the system should preserve:

- the failed artifact
- the failed check
- the rollback action taken
- the time of failure
- the reviewer or agent involved
- the next-step recommendation

A failed promotion is still useful institutional knowledge.

## What this framework does not do

This framework does not replace human judgment on:

- brand voice
- positioning
- offer strategy
- campaign strategy
- whether a good variant is worth launching now

This framework does not:

- auto-publish anything
- auto-activate anything externally
- guarantee business results
- override human review
- apply to one-off manual edits outside autoresearch

What it does guarantee is narrower and more important:

- safety gates exist
- promotion is auditable
- rollback is prepared
- visual verification happens before live risk
- live QA happens after push

## Final rule

The autoresearch system is allowed to optimize.

It is not allowed to be reckless.

A kept variant is only promotable when it is:

- compliant
- logged
- approved
- reversible
- previewed when required
- dogfooded when required
- monitored when required

That is the universal safety framework.
