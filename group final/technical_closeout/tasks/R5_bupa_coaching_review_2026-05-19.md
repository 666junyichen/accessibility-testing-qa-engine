# R5 Task Brief - Bupa Coaching Recommendation Review

Date: 2026-05-19

## Goal

Review the generated Bupa coaching recommendations for plausibility and caveats. This is a qualitative review task, not a recommendation-engine rewrite.

## Files To Use

- `data/heldout/bupa/reports/*.json`
- `data/heldout/bupa/reports/_summary.csv`
- `data/heldout/bupa/processed/layer3_findings_filtered.csv`
- `docs/coaching_templates.md`
- `docs/r5_coaching_engine_observations_and_extensions.md`
- `group final/technical_closeout/submissions/bupa_corrected_pipeline_run_2026-05-19.md`

## Current Bupa Coaching Summary

Generated recommendation count:

- total recommendations: 50
- severity: 20
- friction-aggregation: 17
- recording: 12
- narration: 1

Priority distribution:

- priority 5: 7
- priority 4: 30
- priority 2: 12
- priority 1: 1

Videos with recording recommendations:

- `allenabegum123__web-health-information-bupa`
- `deanmills1987__web-health-information-bupa`
- `ghum__web-health-information-bupa`
- `giuliaclemente26__web-health-information-bupa`
- `gracieha22__web-health-information-bupa`
- `iakhtar1__web-health-information-bupa`
- `lydia_2222__web-health-information-bupa`
- `manyi_tan__web-health-information-bupa`
- `matthew_mayston__web-health-information-bupa`
- `ripabegum__web-health-information-bupa`
- `sharelinsonny__web-health-information-bupa`
- `terryaflint17__web-health-information-bupa`

## Required Checks

1. Pick 5-8 representative videos and inspect their `coaching_recommendations`.
2. Confirm whether severity and friction-aggregation recommendations match the underlying top findings.
3. Check whether recording/narration recommendations are reasonable given `narration_quality` and `recording_quality`.
4. Flag any recommendation that is too generic, misleading, or not sufficiently grounded.
5. Note that R5 must remain decoupled from R6 performance scoring and calibrator mismatch flags.

## Constraints

- Do not modify coaching templates or code for Bupa.
- Do not tune recommendation priority using Bupa.
- Do not start Final Report prose, presentation bullets, contribution statements, AI usage statements, or signatures.

## Expected Output

Send back one markdown file or message:

`R5_bupa_coaching_review_2026-05-19.md`

Include:

- pass / caveat / fail overall judgement
- videos reviewed
- 3-5 examples of good recommendations
- any caveats R8 should include
- any future-work notes
