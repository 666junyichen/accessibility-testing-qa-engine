# R8 Task Brief - Bupa Held-out Evaluation Summary

Date: 2026-05-19

## Goal

Write the Bupa held-out evaluation summary from the corrected pipeline outputs and returned member reviews. This is the final technical synthesis for the held-out run, not the course Final Report prose.

## Files To Use

- `group final/technical_closeout/submissions/bupa_corrected_pipeline_run_2026-05-19.md`
- `group final/technical_closeout/submissions/R6_bupa_performance_outputs_2026-05-19.md`
- `data/heldout/bupa/reports/_summary.csv`
- `data/heldout/bupa/reports/*.json`
- `data/heldout/bupa/performance/per_submission.csv`
- `data/heldout/bupa/performance/per_tester.csv`
- Returned R3 case-study note
- Returned R5 coaching-review note
- Returned R6 performance-review note

## Quantitative Facts To Include

Corrected pipeline:

- Bupa videos: 21
- transcript JSON files: 21
- windows: 1252
- L3 Level B: 21/21 succeeded
- L3 Level A: 1252/1252 succeeded
- filtered L3 findings: 813
- reports: 21/21 generated
- zero-duration reports: 0

Report quality tier distribution:

- acceptable: 14
- poor: 7

R6 tester-performance tier distribution:

- Leading: 14
- Proficient: 2
- Developing: 5
- Foundational: 0

Global L3 finding distribution:

- friction type: F1=233, F2=151, F6=145, F3=115, F5=74, F7=62, F4=33
- severity: S5=569, S4=114, S3=77, S6=43, S2=5, S1=5
- sentiment: E4=682, E3=103, E2=16, E5=11
- calibrator score: L2=560, L3=189, L1=54, L4=6, L5=4

## Required Interpretation Points

1. Bupa was evaluation-only; no tuning was performed from held-out results.
2. The corrected run fixed the earlier zero-duration/report-ID issue.
3. Product/session quality and R6 tester-performance tier are different outputs.
4. Layer 1 and Layer 2 were not regenerated for Bupa, so L1/L2 should be described as a limitation.
5. Case-study and coaching-review conclusions should be attributed to R3/R5 returned notes, not invented if those notes have not returned yet.

## Constraints

- Do not start course Final Report prose.
- Do not write presentation bullets.
- Do not write contribution statements, AI usage statements, or signatures.
- Do not tune or recommend tuning based on Bupa.

## Expected Output

Send back one markdown file or message:

`R8_bupa_evaluation_summary_2026-05-19.md`

Suggested sections:

- Run status
- Dataset and path isolation
- Quantitative results
- Main qualitative patterns
- R6 performance interpretation
- R3/R5 review synthesis
- Limitations
- Final technical readiness judgement
