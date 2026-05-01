# Email Loop — Klaviyo / heilginseng.com

## Purpose

Optimize Klaviyo flow emails for Heil Ginseng using a keep/discard loop.
One element per iteration. Score before and after. Keep only if the rubric score improves by >= 2 points.

**CRITICAL: DRAFT ONLY. Never auto-send. Never modify a live flow without explicit Colton approval. All output is drafts for human review.**

## Platform

- Email provider: Klaviyo
- Sender: colton@heilginseng.com
- Active flows: 14

## Priority Flows (optimize in this order)

| Flow | Why It Matters |
|------|---------------|
| Welcome Series | First impression; sets brand tone; drives first purchase |
| Abandoned Cart | Highest revenue-recovery opportunity |
| Post-Purchase | Repeat purchase trigger; review solicitation |
| Win-Back | Re-engage lapsed customers (90+ days no purchase) |
| Browse Abandonment | Mid-funnel recovery |
| Post-Purchase (Day 30) | Replenishment reminder for Capsules and Tea |

## Editable Elements (one per run)

Builders may optimize:

- **Subject line** — clarity, curiosity, specificity, length
- **Preview text** — complements subject; adds urgency or benefit
- **Hero copy** — opening sentence or headline above the fold
- **CTA button text** — action clarity and urgency
- **CTA placement** — above vs below product image, sticky vs static
- **Send timing** — time-of-day or day-of-week within the flow delay settings
- **Offer framing** — how a discount or free shipping threshold is presented
- **Personalization tokens** — first name, product purchased, days since purchase

Builders may NOT modify:

- Live flow step settings without Colton approval
- Email design template HTML (use Klaviyo's block editor descriptions only)
- Subscriber list membership rules
- Flow trigger conditions
- Anything that would auto-send to live subscribers

## Iteration Protocol

Each loop run follows this exact sequence:

1. **Select target flow and target email step** — pick based on priority table above or explicit run instruction
2. **Identify one editable element** — pick the single element with the lowest rubric dimension score
3. **Capture baseline** — score the current version using the email rubric; note open rate and click rate if available from Klaviyo analytics
4. **Draft variant** — write exactly one new version of the element
5. **Score variant** — apply rubric; calculate delta
6. **Keep or discard**:
   - Keep if: rubric score delta >= +2 points
   - Discard if: score does not improve by 2 points
7. **Log** — append row to `results/email.tsv`
8. **Output** — save draft to `outputs/autoresearch/email/<YYYY-MM-DD>/`
9. **Report** — write summary to the result log and run artifact directory

## Compliance Rules (non-negotiable)

- No health claims that imply disease treatment or cure (FDA/FTC)
- No "boost immunity," "treat," "cure," "prevent disease" language
- Allowed: "support," "promote," "may help," "traditional use"
- All discount amounts must be factually accurate
- Unsubscribe link must be present in every email (do not remove from templates)
- CAN-SPAM: physical address footer must remain intact

Draft variants are subject to compliance scoring in the rubric. Low compliance score = immediate discard.

## Subject Line Guidelines

Strong subject lines for Heil Ginseng:
- Lead with specificity, not hype ("Your ginseng order arrived 3 weeks ago — here's what to expect")
- Farm-origin trust ("Straight from Marathon County, Wisconsin")
- Curiosity without clickbait ("One thing most ginseng buyers miss")
- Social proof when available ("Why 400+ customers reorder every quarter")
- Length: 35–50 characters for mobile preview

Avoid:
- ALL CAPS
- Excessive punctuation (!!!)
- Emoji overuse (max 1 per subject line)
- Vague teases ("You won't believe this")
- Prohibited health claim language

## Preview Text Guidelines

- 85–110 characters
- Should add information not already in the subject line
- Never repeat the subject line verbatim
- Use to reinforce benefit, urgency, or offer

## CTA Guidelines

- One primary CTA per email (two max, same destination)
- Action verbs: "Shop Now," "Claim Your Discount," "See the Farm Story," "Try Capsules"
- Avoid passive: "Click Here," "Learn More"
- Button must be tappable on mobile (min 44px height — note in draft description)

## Send Timing Reference

Best-performing times for DTC supplement brands (use as starting hypothesis):
- Welcome email 1: immediately on signup
- Cart abandonment: 1 hour, then 24 hours
- Post-purchase: 3 days after delivery (estimated)
- Win-back: 90 days, then 120 days
- Time of day: 9–11am or 6–8pm local subscriber time

## Artifact Storage

- Draft variants: `outputs/autoresearch/email/<YYYY-MM-DD>/<flow>-<step>-<element>-v<NN>.md`
- Scoring JSON: same path, `.json` extension
- Results log: `results/email.tsv`

## Max Variants Per Run

- 1 element variant per run
- Max 3 variants per element before moving to the next element
- Max 5 elements per flow per loop cycle (then reassess with real metric data)

## Keep Threshold

Rubric score delta >= +2 points (0–100 scale).

## Stop Conditions

- All rubric dimensions score above 80/100 for a given flow step
- 3 consecutive variants fail to improve by 2 points
- Real metric data (open rate, click rate) shows no uplift after 3 kept variants

## Results Log

Append every run to `results/email.tsv`.

Schema (TSV):
```
run_id  timestamp_utc  flow_name  step_number  element_changed  baseline_score  variant_score  score_delta  subject_score  content_score  cta_score  mobile_score  personalization_score  compliance_score  compliance_pass  keep_decision  draft_path  real_metric_window_start  real_metric_window_end  open_rate_delta  click_rate_delta  revenue_per_email_delta  notes  rubric_version
```

## Run Reporting

Record after each run:
- Flow and step tested
- Element changed
- Baseline score vs variant score
- Keep or discard decision
- Draft path (if kept)
- Any compliance flags

## Real Metric Audit

- After 2 weeks: compare open rate and click rate for any kept variants that were implemented
- Monthly: check placed-order rate for flow steps where variants were kept
- Log correlation findings in `results/email.tsv` real_metric columns

## Approval Gate

Before any kept draft can be implemented in a live Klaviyo flow:
1. Colton reviews the draft (ALWAYS — no exceptions)
2. If the email makes health claims or mentions discounts, Ben reviews for compliance
3. Colton explicitly approves implementation in writing (#exec-approvals)

**DRAFT ONLY. The loop outputs drafts. Humans implement.**
