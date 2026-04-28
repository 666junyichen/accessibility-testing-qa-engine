# Step 8.1 Dev55 Scope

This note resolves the official `Step 8.1` input scope using the current repository outputs and the project governance docs.

## Official target

- `docs/eval_freeze.md` defines the dev set as:
  - old 3 projects collated
  - AAMI/Suncorp `21` + UQ `19` + DPC-WA `17`
  - actual `57` including `2` transcription failures
  - official evaluation scope = `55` videos

## Current batch output

- `data/processed/reports/_summary.csv` currently contains `57` report rows.
- That means the existing batch run includes the two failed/near-empty cases and therefore is broader than the official `dev55` scope.

## Excluded from official dev55

The following two rows should be excluded from formal `Step 8.1` reporting:

1. `troyparnell_suncorp`
   - documented in `README.md` as a retained transcript failure / near-empty-file edge case
   - raw AWS Transcribe JSON size is only `2,857` bytes
   - current batch output shows only `1` window and `0` L3 findings

2. `thanoptions_wa`
   - raw AWS Transcribe JSON size is only `10,787` bytes
   - current batch output shows only `2` windows and `0` L3 findings
   - this matches the project note that the dev total `57` contains `2` transcription failures and should be reduced to `55`

## Official dev55 file

- The resolved official list is stored in:
  - `data/processed/reports/dev55_official_list.csv`
- The official filtered batch summary is stored in:
  - `data/processed/reports/_summary_dev55.csv`

## Project counts after exclusion

- `department-of-premier-and-cabinet-wa`: `16`
- `suncorp-insurance`: `20`
- `the-university-of-queensland`: `19`
- total: `55`

## Sync discipline

`data/processed/reports/dev55/` is the **official dev55 physical whitelist**:
a byte-level subset of the current `data/processed/reports/` main directory,
restricted to the 55 video IDs listed in `dev55_official_list.csv`.

Whenever the main `data/processed/reports/` directory is regenerated, for example
after fusion changes, prompt revisions, classifier reruns, or full pipeline
reruns, the `dev55/` subset must be re-synced from the new main reports to
avoid content drift between the two locations.

Check for drift before syncing:

```powershell
python scripts/sync_dev55.py --check
```

Rebuild the physical dev55 subset from the current main reports:

```powershell
python scripts/sync_dev55.py
```
