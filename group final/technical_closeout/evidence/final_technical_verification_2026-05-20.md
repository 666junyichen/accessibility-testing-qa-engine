# Final Technical Verification

Date: 2026-05-20

## Status

Project technical closeout passed.

The Bupa held-out evaluation is complete and ready to be referenced as external validation evidence in Final Report / presentation materials, with documented caveats.

## Checks Run

### Pytest

```text
pytest
155 passed, 1 warning
```

The warning came from `joblib/loky` physical-core detection and did not affect test results.

### Dev55 sync

```text
python scripts/sync_dev55.py --check
dev55 drift check passed: 55/55 files match.
```

### Dev performance table build

```text
python scripts/build_performance_tracking.py
wrote 57 submission rows and 27 tester rows to data/processed/performance
```

No tracked performance-table drift was produced by this rerun.

### Bupa report readability and ID alignment

Checked:

- `data/heldout/bupa/reports/*.json`
- `data/heldout/bupa/reports/_summary.csv`
- `data/heldout/bupa/processed/manifest.csv`

Result:

```text
reports_json 21
summary_rows 21
manifest_rows 21
bad_reports []
ids_aligned True
zero_duration 0
```

## Evaluation Summary Review

Reviewed file:

`group final/technical_closeout/evidence/bupa_evaluation_summary_2026-05-20.md`

Review result:

- Key run counts match Bupa CSV/JSON outputs.
- Report quality tier distribution matches `_summary.csv`: acceptable=14, poor=7.
- R6 tester-performance tier distribution matches performance CSVs: Leading=14, Proficient=2, Developing=5, Foundational=0.
- Bupa `cross_check_lane` is `with_overrides` for all 21 performance rows.
- The evaluation summary correctly preserves the distinction between report quality tier and R6 tester-performance tier.
- The evaluation summary correctly preserves Bupa limitations: Layer 1 / Layer 2 not regenerated, no longitudinal trajectory interpretation, no tuning from Bupa.

Small review correction applied:

- Friction-type labels in the qualitative pattern section were aligned with canonical taxonomy:
  - F1 Comprehension Friction
  - F2 Confidence Friction
  - F3 Accessibility Friction
  - F4 Unresponsive Interface
  - F5 Unexpected Behaviour
  - F6 Content Not Found
  - F7 Excessive Effort
- Calibrator-score wording was revised from "confidence range" to calibrator-strength / repair-concern language.

## Streamlit Demo Check

No new Streamlit code was changed during final verification. The Streamlit dev55 demo had already passed:

- Single Video view
- Tester Trajectory view
- Cohort Overview view

This final verification therefore relies on the previous demo sanity check for UI status.

## Final Technical Caveats To Preserve

- Bupa Layer 1 / Layer 2 artifacts were not regenerated, so Bupa reports show `l1_total=0` and `l2_coverage=0.0`.
- Bupa has one submission per tester, so trajectory fields are not meaningful for longitudinal validation.
- `manyi_tan__web-health-information-bupa` is valid in the corrected run but remains a short evidence-density case: 6 windows and 2 findings.
- Bupa results were not used to tune prompts, schemas, fusion, postprocess filters, R6 scoring, or coaching logic.

## Final Judgement

The project-system technical closeout is complete. The remaining work is no longer pipeline/model development; it is school submission packaging:

- Final Report
- final project status/demo checking form
- presentation slides and video
- contribution statement and signatures
- AI acknowledgement
- client handover link and Q&A preparation
