# Meta Cross-Channel Handoff Contract

This contract lets `#ginseng-autoresearch` hand winning creative packages to `#ginseng-retail`, then receive performance feedback back against the same stable `asset_id` values.

## Files

- `contracts/meta-handoff.schema.json` — outbound packet contract from autoresearch to retail
- `contracts/meta-feedback.schema.json` — return packet contract from retail to autoresearch
- `templates/meta-handoff-template.json` — starter handoff payload
- `templates/meta-feedback-template.json` — starter feedback payload
- `scripts/build_meta_handoff.py` — builder/validator for production handoff packets

## Guardrail

- Never auto-activate campaigns.
- All packets are draft-only.
- Human operator activation in Meta Ads Manager is required.

## Autoresearch -> Retail handoff process

1. Run the creative branch and keep only assets that pass packaging, roots, and no-humans gates.
2. Build the handoff packet:
   - `python3 scripts/build_meta_handoff.py --source-run <run-folder> --output <handoff.json>`
3. Validate the output against `contracts/meta-handoff.schema.json`.
4. Post the resulting JSON packet and referenced image assets into `#ginseng-retail`.
5. Retail uses `asset_id` as the durable join key in naming, tracking sheets, and Meta ad naming.
6. Retail may adapt campaign/ad set structure, but must preserve `asset_id` exactly.

## Retail -> Autoresearch feedback return process

1. After testing, export or compile performance metrics per `asset_id`.
2. Fill `templates/meta-feedback-template.json` or generate the same shape from a reporting script.
3. Validate feedback against `contracts/meta-feedback.schema.json`.
4. Return the feedback packet to `#ginseng-autoresearch`.
5. Autoresearch joins performance results back to source prompts and validation artifacts by `asset_id`.

## Required retail discipline

- One result row per `asset_id`
- Keep Meta IDs for campaign, ad set, and ad
- Return exact test window via `date_start` and `date_end`
- Populate verdict as `win`, `hold`, or `kill`
- Use `notes` for context like audience, placement mix, landing page changes, or operator observations

## Example commands

```bash
python3 scripts/build_meta_handoff.py \
  --source-run ~/.openclaw/workspace/outputs/autoresearch/ad-creative/2026-03-12-capsules-branch \
  --output ~/.openclaw/workspace/outputs/autoresearch/handoffs/2026-03-12-capsules-batch-01.json
```

```bash
python3 - <<'PY'
import json
from pathlib import Path
from jsonschema import validate
schema = json.loads(Path('contracts/meta-feedback.schema.json').read_text())
payload = json.loads(Path('templates/meta-feedback-template.json').read_text())
validate(payload, schema)
print('feedback template valid')
PY
```
