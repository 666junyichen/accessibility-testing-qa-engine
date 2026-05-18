# R4 Peiyun - Bupa Held-out Input Sanity Check (Updated)

Date: 2026-05-18

Original R4 review basis: `658190f Add Bupa heldout transcription manifest and status`

Updated review basis: `91a95cb Fix Bupa manyi_tan transcript status`

Update owner: R2/Nix, applying R4's original sanity-check structure to the latest repository state.

## Executive Decision

The Bupa held-out set is now pipeline-ready for R7 evaluation on all 21 videos.

The previous hard blocker, `manyi_tan`, has been resolved in `91a95cb`: the corrected S3 key is now recorded in the manifest, the transcript JSON is present in the repository, and the transcript parses successfully.

## Final Counts

| Check item | Result |
| --- | --- |
| Manifest rows | 21 |
| Transcript JSON files present | 21 |
| Transcript JSON files parseable | 21 |
| Transcript validation failures | 0 |
| Hard blockers for R7 | 0 |
| Videos R7 can process | 21 |

## What Changed Since R4's Original Note

R4's original review correctly found a `20 + 1` state on commit `658190f`: 20 processable videos and 1 unprocessable video, `manyi_tan`.

The repository now contains the correction:

- `manyi_tan` UUID corrected from the missing-key value to `3c9fbbce-ec6b-4f1a-99a7-cdd19fda82a1`.
- `data/heldout/bupa/processed/manifest.csv` now points to the corrected MP4/VTT S3 keys.
- `data/heldout/bupa/processed/transcription_status.csv` now marks `manyi_tan` as `success`.
- `data/heldout/bupa/processed/transcript_validation.csv` now marks `manyi_tan` as `success`.
- `data/heldout/bupa/raw/transcribe-output/web-health-information-bupa/manyi_tan__web-health-information-bupa__transcript.json` is present and parseable.

Current `manyi_tan` validation values:

| Field | Value |
| --- | --- |
| Transcript characters | 2,177 |
| AWS transcript items | 438 |
| Audio segments | 40 |
| Approx. pronunciation-word count | 373 |
| Approx. average confidence | 0.941 |
| Approx. low-confidence word share `<0.5` | 3.8% |

Decision: `manyi_tan` is no longer a blocker. It should be included in R7 as a short-sample caveat, not excluded.

## Sanity Checks Completed

### 1. Manifest and project key

- All 21 Bupa rows use the canonical project key: `web-health-information-bupa`.
- `bupa-uk` remains only as the source scope inside S3 paths, not as the model/project lane key.
- This aligns with R6's compatibility note: `web-health-information-bupa` maps to `with_overrides`; using `bupa-uk` as the project key would silently fall back to `dev_only`.

R7 requirement: every output row in `layer3_video_assessments.csv` and downstream evaluation files must carry `project=web-health-information-bupa`, never `project=bupa-uk`.

### 2. Transcript presence and parseability

- Expected transcript JSON files: 21.
- Found transcript JSON files: 21.
- JSON parse failures: 0.
- Missing transcript JSON files: 0.

The transcript folder checked was:

`data/heldout/bupa/raw/transcribe-output/web-health-information-bupa/`

### 3. Status and validation files

The processed tracking files now agree:

- `manifest.csv`: all 21 rows marked `transcription_status=success`.
- `transcription_status.csv`: all 21 rows marked `success`.
- `transcript_validation.csv`: all 21 rows marked `success`.

There is no remaining `failed` Bupa transcript row in the current repository state.

### 4. Local MP4/VTT availability

The MP4/VTT files are still referenced through S3 paths in the manifest. They are not required to be fully committed as local media files for R7 if the pipeline consumes the transcript JSON and manifest fields.

If any later script requires local video or VTT files, download from the S3 keys listed in `manifest.csv`; do not change the project key.

## Advisory Caveats for R7

These caveats are non-blocking. They should be carried into evaluation notes so that unusual R7 scores are interpretable.

| Video | Caveat | R7 decision |
| --- | --- | --- |
| `manyi_tan` | Very short transcript after correction. It is parseable and has acceptable average confidence, but the sample is much shorter than the rest of the held-out set. | Include; flag as short-sample caveat. |
| `terryaflint17` | Lower transcription confidence than most Bupa files. Approx. average confidence was around 0.802 in R4's original check, with a higher low-confidence share. | Include; flag if R7 outputs look unstable. |
| `deanmills1987` | Moderate transcription-confidence caveat. Approx. average confidence was around 0.849 in R4's original check. | Include; flag if R7 outputs look unstable. |
| `ghum` | Moderate transcription-confidence caveat. Approx. average confidence was around 0.888 in R4's original check. | Include; flag if R7 outputs look unstable. |
| `ripabegum`, `giuliaclemente26`, `gracieha22` | Shorter transcripts compared with most Bupa held-out files. | Include; treat as short-sample cases. |

No advisory caveat above blocks R7.

## R7 Contract

R7 can now proceed with the full Bupa held-out set:

- Input count: 21 videos.
- Expected video IDs: the 21 rows in `data/heldout/bupa/processed/manifest.csv`.
- Expected transcript source: `data/heldout/bupa/raw/transcribe-output/web-health-information-bupa/*.json`.
- Expected project key: `web-health-information-bupa`.
- Expected hard exclusions: none.

If R7 produces fewer than 21 Bupa rows, that should be treated as a pipeline issue, not an input-data exclusion decision.

## Evidence Snapshot

Local checks on 2026-05-18:

```text
git log -1 --oneline
91a95cb Fix Bupa manyi_tan transcript status

transcript JSON count
21

JSON parse check
{ "json_files": 21, "bad": [] }

manyi_tan validation row
manyi_tan,...,success,,2177,438,40
```

## Final Line

R7 can proceed on all 21 videos; there are no blocked Bupa held-out videos in the current repository state.
