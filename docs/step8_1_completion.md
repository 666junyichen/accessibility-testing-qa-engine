# Step 8.1 Completion Note

`Step 8.1` is now resolved as a dev-batch reporting step built on the existing processed CSV/JSON artifacts.

## What is completed

- batch report generation entrypoint exists at `scripts/run_pipeline.py`
- per-video report outputs already exist under `data/processed/reports/`
- official dev scope has been resolved from `57` generated rows down to the governance-defined `55` videos
- official scope file:
  - `data/processed/reports/dev55_official_list.csv`
- official filtered summary:
  - `data/processed/reports/_summary_dev55.csv`

## Official Step 8.1 output

- `55` dev Quality Reports
- report directory:
  - `data/processed/reports/`
- official summary:
  - `data/processed/reports/_summary_dev55.csv`

## Scope rule used

- include only the official dev55 set from `docs/eval_freeze.md`
- exclude:
  - `troyparnell_suncorp`
  - `thanoptions_wa`

## Out of scope for this Step 8.1 close-out

- no new API integration
- no raw-video download / rebuild work
- no prompt changes
- no held-out Bupa evaluation
