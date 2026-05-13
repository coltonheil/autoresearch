# Cat-1 Wiki Recovery Variant

## Candidate Reader Rule

Read the active Blue Star wiki as a bid analyst. Resolve Cat-1 variables only
from cited bid-document evidence:

- `power_kw`
- `fuel_type`
- `voltage`
- `phase`
- `ats_required`
- `ats_amp_rating`

Use the full available wiki context:

- prepared page transcripts
- source map and document inventory
- evidence index
- requirement graph
- whole-page vision analyses
- drawing analyses
- correction intents and validation reports
- source manifests and page coverage ledgers

## Evidence Ladder

Prefer evidence in this order:

1. explicit equipment schedules, generator schedules, ATS schedules, bid forms,
   and addenda corrections
2. drawing callouts, one-lines, risers, site/electrical sheets, and visual
   schedules from whole-page vision
3. generator/ATS specification sections and scope paragraphs
4. semantically strong fuel-system language when no contrary fuel evidence
   exists
5. configurator/pricing JSON only for mapping already-cited bid facts to Blue
   Star model/options/pricing

## Strict Boundaries

- Do not use configurator defaults to fill missing bid facts.
- Do not use a sizing model as truth for kW, voltage, phase, fuel, or ATS.
- Do not use regex/string matching as final truth.
- Do not hardcode answers for the four-bid corpus.
- Do not manually edit field rollups.
- If a field is unresolved, state whether the likely failure is missing source
  document, missing GLM/vision artifact, context-selection loss, synthesis loss,
  verifier rejection, or true absence from downloaded docs.

## Shorthand Semantics

Accept common electrical shorthand when cited in context:

- `3Ø`, `3PH`, `3 phase`, `3-phase`, `3 phase 4 wire`, and `wye 4wire` can
  support `phase = three_phase`.
- `480Y/277`, `480/277`, `480/277VAC`, and `277/480V` can support matching
  voltage values when generator/ATS context is clear.
- `208Y/120`, `208/120`, and `120/208V` can support matching voltage values
  when generator/ATS context is clear.
- ATS-adjacent amp tokens such as `150A automatic transfer switch`, `400A ATS`,
  `600A service rated ATS`, or `ATS 600 amps` can support `ats_amp_rating`.
- Fuel tanks, day tanks, belly/sub-base tanks, diesel fuel oil, fuel fill,
  refueling, and DF-2 fuel language can support `fuel_type = diesel` when no
  gaseous-fuel service evidence contradicts it.

## Output Discipline

Each recovered field must include:

- field name
- normalized value
- support level
- source path or evidence id
- page/sheet/locator
- quoted or summarized evidence
- contradiction search summary
- whether the fact came from text/table/schedule/drawing/vision/configurator

Configurator output may map cited facts to Blue Star product line, model,
option, and price. It may not create bid facts.
