# Email Rubric — Klaviyo / heilginseng.com

Version: 1.0 | Weights sum: 100

## Scoring Overview

Score each email element 0–100 using the weighted dimensions below.
Apply to both baseline and variant. Delta = variant_score − baseline_score.

| Dimension | Weight | Scores |
|-----------|--------|--------|
| Subject line strength | 25% | 0–25 |
| Content relevance | 20% | 0–20 |
| CTA clarity | 20% | 0–20 |
| Mobile formatting | 15% | 0–15 |
| Personalization | 10% | 0–10 |
| Compliance | 10% | 0–10 |

**Total weight: 100%**

---

## Dimension Scoring Guides

### Subject Line Strength (weight: 25)

Score the subject line + preview text together.

| Criteria | Points |
|----------|--------|
| Specific and concrete (not vague or generic) | 0–5 |
| Benefit or curiosity clear in first 40 characters | 0–5 |
| Preview text adds new information (not a repeat) | 0–5 |
| Length appropriate for mobile (35–55 chars for subject) | 0–4 |
| No prohibited health claims or compliance risk | 0–3 |
| No spam trigger patterns (ALL CAPS, excessive punctuation, "FREE!!!") | 0–3 |

**Max: 25 points**

Strong examples:
- "Your ginseng shipped — here's what to expect" (25/25 range)
- "Marathon County to your door: roots now in stock" (22–24 range)

Weak examples:
- "Big News Inside!" (5–8 range)
- "Don't miss out!!!" (2–5 range, spam risk)

---

### Content Relevance (weight: 20)

Score the email body's opening section and primary value proposition.

| Criteria | Points |
|----------|--------|
| Opening sentence directly relevant to subscriber's position in journey | 0–5 |
| Product benefits explained with specificity (not generic supplement copy) | 0–5 |
| Farm/origin story or trust signals present where appropriate | 0–4 |
| Offer or reason to act now is clear | 0–3 |
| No redundant or filler sentences | 0–3 |

**Max: 20 points**

---

### CTA Clarity (weight: 20)

| Criteria | Points |
|----------|--------|
| Primary CTA uses an action verb (not "Click Here" or "Learn More") | 0–5 |
| CTA destination matches the email's primary message | 0–5 |
| Only one primary CTA per email (two max, same destination) | 0–4 |
| CTA is visible without scrolling on mobile (above fold or immediately after hero) | 0–3 |
| CTA button contrast is described as sufficient (readable on mobile) | 0–3 |

**Max: 20 points**

---

### Mobile Formatting (weight: 15)

| Criteria | Points |
|----------|--------|
| Subject renders correctly in ~35 character mobile preview | 0–4 |
| Hero content described for single-column mobile layout | 0–3 |
| Font size described as >= 16px for body, >= 20px for headings | 0–3 |
| CTA button described as tap-safe (min 44px height) | 0–3 |
| No critical content reliant on hover states or desktop-only formatting | 0–2 |

**Max: 15 points**

---

### Personalization (weight: 10)

| Criteria | Points |
|----------|--------|
| First name token used in subject or opening line where natural | 0–3 |
| Product reference matches subscriber's purchase or browse history (for post-purchase/win-back) | 0–3 |
| Timing or context reference personalized (e.g., "It's been 90 days since your last order") | 0–2 |
| Fallback values defined for all personalization tokens | 0–2 |

**Max: 10 points**

Personalization only scores where it is appropriate to the flow. Welcome emails score on first-name + origin framing. Win-back emails score on time-since-purchase and product reference. Skip dimensions that do not apply to the flow type and redistribute those points as neutral.

---

### Compliance (weight: 10)

| Criteria | Points |
|----------|--------|
| No disease treatment/cure claims ("treats," "cures," "prevents disease") | 0–4 |
| Health benefit language uses compliant qualifiers ("may support," "traditionally used to") | 0–3 |
| Discount percentages and offer details are factually accurate as written | 0–2 |
| No deceptive urgency (fake countdown, fake scarcity) | 0–1 |

**Auto-discard triggers (score = 0 for compliance dimension AND flag for Ben review):**
- Any claim that implies FDA approval or disease treatment
- Any false urgency that misrepresents stock or time limits
- Missing unsubscribe reference in draft (note: Klaviyo appends automatically, but draft must not remove blocks)

**Max: 10 points**

---

## Composite Score Formula

```
score = subject_score + content_score + cta_score + mobile_score + personalization_score + compliance_score
```

Maximum: 100 points.

---

## Keep Threshold

**Keep the variant if:**
- `variant_score − baseline_score >= 2` (minimum 2-point improvement)
- AND compliance dimension score >= 6/10 (no auto-discard triggers fired)

**Discard if:**
- Score improvement < 2 points
- OR compliance auto-discard trigger fired
- OR subject line length > 60 characters (too long for most mobile clients)

---

## Compliance Gate

Compliance dimension score < 6 = immediate discard, regardless of total score.

All kept variants with any health-benefit language or discount mention must be routed to Ben for compliance review before Colton review.

---

## Scoring Notes

- Score based on the draft content as written; do not infer what Klaviyo will render
- If a dimension is not applicable to the specific flow type (e.g., personalization in a broadcast), score the dimension at its midpoint and note in the TSV
- Subject line and CTA clarity are the two highest-leverage dimensions; prioritize improvements there first

---

## Rubric Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-03-09 | Initial rubric. Weights: subject 25, content 20, CTA 20, mobile 15, personalization 10, compliance 10. |
