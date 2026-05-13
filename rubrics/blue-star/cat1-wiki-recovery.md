# Blue Star Cat-1 Wiki Recovery Rubric

Version: 1.0

## Primary Score

`candidate_score - baseline_score`, higher is better.

The scorer grades each baseline and candidate on a 100-point scale:

| Dimension | Weight |
| --- | ---: |
| Cat-1 field resolution accuracy | 36 |
| Direct citation/support quality | 24 |
| Quote-readiness correctness | 15 |
| Document-completeness diagnosis | 10 |
| Configurator boundary discipline | 10 |
| Clear next action | 5 |

## Cat-1 Fields

The Cat-1 variables are:

- `power_kw`
- `fuel_type`
- `voltage`
- `phase`
- `ats_required`
- `ats_amp_rating`

Each field may be:

- `resolved`: normalized value is supplied and directly supported.
- `unresolved`: no value is supplied, with a typed reason.
- `not_required`: the field is explicitly not applicable to this bid.

## Direct Evidence Standard

Direct evidence must include:

- source path, evidence id, or artifact id
- page, sheet, section, range, bbox, or vision artifact locator
- short proof text or visual summary
- support level: `literal_bid_text`, `visual_read`, `semantic_bid_inference`,
  or `product_model_join`

Filenames, old field files, prior packet labels, configurator defaults, and
absence from a partial index are not direct evidence.

## Configurator Boundary

The Blue Star configurator/pricing JSON may be used only after the bid docs
have supplied the required facts. It can map:

- kW/fuel/voltage/phase/ATS facts to product line and model
- selected options to pricing
- downloaded Blue Star product docs to product references

It may not infer missing bid facts.

## Regression Failures

Any of these force discard:

- Telford loses any resolved Cat-1 fact or packet-ready status.
- Main Library loses any resolved Cat-1 fact.
- unsupported recovered facts increase.
- stale field fallback is detected.
- configurator defaults or sizing model fill missing bid facts.
- direct citation coverage decreases.
- candidate changes the scorer, rubric, or eval set during the run.

## Keep/Discard Bands

- `keep`: delta >= 8.0, no regression failure, and at least one target field is
  newly resolved with direct evidence or conclusively proven absent.
- `discard`: delta < 8.0 or any regression failure.
- `crash`: scorer cannot parse or evaluate artifacts.
- `blocked`: source-backed labels or source artifacts are missing.

## Evaluation Rows

Each row should contain:

```json
{
  "case_id": "bid-id-or-short-name",
  "bid_id": "uuid",
  "title": "Bid title",
  "role": "protected_positive|target_recovery|holdout",
  "expected": {
    "fields": {
      "power_kw": {"status": "resolved", "value": "150 kW"},
      "fuel_type": {"status": "resolved", "value": "diesel"}
    },
    "quote_readiness": "packet_ready_with_caveats|needs_more_bid_information|ready_to_price|blocked",
    "required_missing_fields": ["voltage", "phase"]
  },
  "baseline": {
    "fields": {},
    "quote_readiness": "",
    "doc_completeness": {},
    "uses_sizing_model_as_truth": false,
    "uses_configurator_defaults_for_bid_facts": false,
    "next_action": ""
  },
  "candidate": {
    "fields": {},
    "quote_readiness": "",
    "doc_completeness": {},
    "uses_sizing_model_as_truth": false,
    "uses_configurator_defaults_for_bid_facts": false,
    "next_action": ""
  }
}
```
