# R6 Bupa Performance Outputs Closeout

Date: 2026-05-19

## Scope

This file records the generated R6 performance outputs for the corrected Bupa held-out run.

Important interpretation boundary:

- Report `tier` in `data/heldout/bupa/reports/_summary.csv` is the fused product/session quality tier.
- R6 `tier` in `data/heldout/bupa/performance/*.csv` is the tester-performance score tier.
- These are intentionally different outputs. A poor product/session report can still have a Leading tester-performance score if the tester clearly surfaced serious friction.

## Command Run

```bash
python scripts/build_performance_tracking.py \
  --findings-csv data/heldout/bupa/processed/layer3_findings_filtered.csv \
  --assessments-csv data/heldout/bupa/processed/layer3_video_assessments.csv \
  --windows-csv data/heldout/bupa/processed/windows.csv \
  --layer1-flags-csv data/heldout/bupa/processed/layer1_flags.csv \
  --out-dir data/heldout/bupa/performance
```

`layer1_flags.csv` is absent for the Bupa held-out run, so the script ran without Layer 1 duration anomaly inputs.

## Output Paths

- `data/heldout/bupa/performance/per_submission.csv`
- `data/heldout/bupa/performance/per_tester.csv`

## Output Counts

- Per-submission rows: `21`
- Per-tester rows: `21`
- Cross-check lane: `with_overrides` for all 21 submissions.
- Low-evidence submissions: `0`

## Tier Distribution

Per-submission and per-tester distributions are identical because each Bupa tester has one submission:

| R6 tier | Count |
|---|---:|
| Leading | 14 |
| Proficient | 2 |
| Developing | 5 |
| Foundational | 0 |

## Lowest R6 Scores

| Video ID | Score | R6 tier | Cap reason | Top friction types |
|---|---:|---|---|---|
| `deanmills1987__web-health-information-bupa` | 55.0 | Developing | S1 project-level blocker present | F1,F6,F3 |
| `gameoverdan__web-health-information-bupa` | 55.0 | Developing | S1 project-level blocker present | F3,F6,F5 |
| `olekwane__web-health-information-bupa` | 55.0 | Developing | S1 project-level blocker present | F1,F3,F2 |
| `sharelinsonny__web-health-information-bupa` | 55.0 | Developing | S1 project-level blocker present | F1,F2,F6 |
| `jadesharp92__web-health-information-bupa` | 65.0 | Developing | >=2 S2 task-blockers | F3,F2,F1 |

## Highest R6 Scores

| Video ID | Score | R6 tier | Total findings | Top friction types |
|---|---:|---|---:|---|
| `daniellepaigejones07__web-health-information-bupa` | 90.7 | Leading | 59 | F1,F3,F2 |
| `lindarcole__web-health-information-bupa` | 90.5 | Leading | 53 | F6,F1,F2 |
| `margieflint__web-health-information-bupa` | 90.4 | Leading | 67 | F1,F2,F6 |
| `chiomaenenmoh__web-health-information-bupa` | 88.9 | Leading | 47 | F6,F1,F7 |
| `ghum__web-health-information-bupa` | 88.3 | Leading | 49 | F6,F2,F1 |

## Validation

```text
pytest tests/test_performance_model.py
33 passed
```

## Remaining R6 Action

R6 should review these generated outputs and confirm:

- `web-health-information-bupa` remained in `with_overrides`.
- The distinction between report quality tier and R6 tester-performance tier is described correctly.
- The absence of Bupa Layer 1 flags is accepted as a held-out caveat rather than a scoring change.
- No R6 scoring rules, caps, lanes, or tier boundaries were tuned using Bupa outputs.
