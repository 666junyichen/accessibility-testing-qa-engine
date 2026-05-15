# R1 Bupa Data Preparation Closeout

Date: 2026-05-15

## Scope

Prepared the Bupa held-out collated video transcription set using only:

`s3://usyd-03-2025-cs20-1-proj-assets/USyd-032026-Projects-Assets/collated-videos/bupa-uk/`

No Bupa raw videos or Brighton raw videos were used.

The S3 collated Bupa scope contains 21 tester folders. Each visible tester folder contains one `_final.mp4` and one `_chapters.vtt`. Therefore the held-out set is 21 collated videos; the earlier 42 count corresponds to 21 mp4 files plus 21 vtt files.

## Results

- Bupa collated videos found: 21
- AWS Transcribe jobs completed successfully: 20
- AWS Transcribe failures / unable to process: 1
- Failed tester/video: `manyi_tan`
- Failure reason: AWS Transcribe submission reported that the configured source S3 URI did not point to an existing S3 object. This was left as unable to process per R1 decision.

All 20 available transcript JSON files were copied into the heldout output folder and validated locally by checking JSON load, `results`, transcript text, and word-level `items`.

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
- Original local synced transcript JSON folder: `data/raw/transcribe-output/web-health-information-bupa/`

## Notes

The final heldout transcript folder contains 20 transcript JSON files. The missing transcript is `manyi_tan`, recorded explicitly as failed in both `manifest.csv` and `transcription_status.csv`.
