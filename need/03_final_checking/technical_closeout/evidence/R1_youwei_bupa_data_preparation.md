# R1 Bupa Data Preparation Closeout

Date: 2026-05-15

## Scope

Prepared the Bupa held-out collated video transcription set using only:

`s3://usyd-03-2025-cs20-1-proj-assets/USyd-032026-Projects-Assets/collated-videos/bupa-uk/`

No Bupa raw videos or Brighton raw videos were used.

The S3 collated Bupa scope contains 21 tester folders. Each visible tester folder contains one `_final.mp4` and one `_chapters.vtt`. Therefore the held-out set is 21 collated videos; the earlier 42 count corresponds to 21 mp4 files plus 21 vtt files.

## Results

- Bupa collated videos found: 21
- AWS Transcribe jobs completed successfully: 21
- AWS Transcribe failures / unable to process: 0
- Correction: `manyi_tan` initially failed because the manifest used `3c9fbbce-ec6b-4f1a-99a7-ccd19fda82a1`; the live S3 key is `3c9fbbce-ec6b-4f1a-99a7-cdd19fda82a1`. The corrected job completed on 2026-05-16.

All 21 available transcript JSON files were copied into the heldout output folder and validated locally by checking JSON load, `results`, transcript text, and word-level `items`.

## Metadata Coverage

Available locally:

- Survey metadata: `data/raw/bupa-uk/`
- Tester metadata: `data/raw/tester_db.csv`
- Base organisation metadata: `data/raw/organisations-data.csv`

Known metadata gaps:

- `organisations-data.csv` does not contain a Bupa organisation row; processed outputs use `project_key=web-health-information-bupa`.
- Bupa task/scenario CSV was not present locally.
- Assignment/tester mapping was not resolved locally. `data/raw/tester_video_mapping.csv` appears to be a mislabeled Excel/xlsx payload rather than a readable CSV.
- Scoring/reference context was not present locally. S3 screenshots show `scoring-reference/` and `llm-insights-reference/` top-level folders, but those contents were not available in the local workspace during this closeout.

Detailed metadata gap table:

`data/heldout/bupa/processed/metadata_gaps.csv`

## Input Paths

- S3 source videos: `s3://usyd-03-2025-cs20-1-proj-assets/USyd-032026-Projects-Assets/collated-videos/bupa-uk/<tester>/<video_uuid>_final.mp4`
- S3 VTT sidecars: `s3://usyd-03-2025-cs20-1-proj-assets/USyd-032026-Projects-Assets/collated-videos/bupa-uk/<tester>/<video_uuid>_chapters.vtt`
- S3 transcript output: `s3://usyd-03-2025-cs20-1-proj-assets/transcribe-output/web-health-information-bupa/`

## Output Paths

- Manifest: `data/heldout/bupa/processed/manifest.csv`
- Transcription status: `data/heldout/bupa/processed/transcription_status.csv`
- Transcript validation: `data/heldout/bupa/processed/transcript_validation.csv`
- Metadata gaps: `data/heldout/bupa/processed/metadata_gaps.csv`
- Heldout transcript JSON folder: `data/heldout/bupa/raw/transcribe-output/web-health-information-bupa/`

## Notes

The final heldout transcript folder contains 21 transcript JSON files. No Bupa collated transcript is currently missing after the corrected `manyi_tan` run.
