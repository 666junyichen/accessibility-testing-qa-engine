# Final Technical Handoff

Date: 2026-05-20

## Status

The CS20 project system is technically complete. The development pipeline,
coaching engine, performance tracking, Streamlit demo, Bupa held-out evaluation,
and final verification checks have all been completed.

No further model, prompt, schema, fusion, scoring, postprocess, or coaching
changes should be made from Bupa results. Any remaining work belongs to school
submission packaging, not project-system development.

## Functional Coverage

| Functional area | Final artefacts | Status |
|---|---|---|
| Transcript parsing and windowing | `data/processed/{transcripts,segments,windows}.csv`; `data/heldout/bupa/processed/{transcripts,segments,windows}.csv` | Complete |
| Layer 1 rule detection | `src/features/rule_detector.py`; `data/processed/layer1_flags.csv`; `docs/layer1_design.md` | Complete for dev; Bupa L1 not regenerated and documented as caveat |
| Layer 2 clustering | `src/features/feature_engineering.py`; `src/clustering/cluster_utils.py`; `data/processed/layer2_*`; `docs/cluster_interpretation.md` | Complete as exploratory supporting signal |
| Layer 3 LLM findings | `src/layer3/*`; `data/processed/layer3_findings_filtered.csv`; `data/heldout/bupa/processed/layer3_findings_filtered.csv` | Complete |
| Fusion reports | `src/pipeline/*`; `scripts/run_pipeline.py`; `data/processed/reports/`; `data/heldout/bupa/reports/` | Complete |
| Coaching recommendations | `src/coaching/recommendation_engine.py`; `docs/coaching_templates.md`; report JSON `coaching_recommendations` | Complete |
| Performance tracking | `src/tracking/performance_model.py`; `scripts/build_performance_tracking.py`; `data/processed/performance/`; `data/heldout/bupa/performance/` | Complete |
| Streamlit demo | `app/streamlit_demo.py`; `app/components.py`; `app/styles.py` | Complete for dev55 demo |
| Evaluation governance | `docs/eval_freeze.md`; `docs/evaluation_design.md` | Complete |
| Bupa held-out closeout | `submissions/bupa_corrected_pipeline_run_2026-05-19.md`; `submissions/R8_bupa_evaluation_summary_2026-05-20.md`; `submissions/final_technical_verification_2026-05-20.md` | Complete |

## Final Evidence Files

- `submissions/bupa_corrected_pipeline_run_2026-05-19.md`
- `submissions/R8_bupa_evaluation_summary_2026-05-20.md`
- `submissions/final_technical_verification_2026-05-20.md`
- `README.md`

Supporting member technical notes remain in `submissions/` for traceability.
Internal task briefs, transfer messages, and input packs are coordination
records rather than final handoff evidence.

## Verification Summary

- `pytest`: 155 passed.
- `python scripts/sync_dev55.py --check`: 55/55 files match.
- `python scripts/build_performance_tracking.py`: generated 57 dev
  per-submission rows and 27 dev per-tester rows.
- Bupa held-out integrity: 21 report JSON files, 21 summary rows, 21 manifest
  rows, readable JSON, aligned IDs, zero zero-duration reports.

## Preserved Caveats

- Bupa Layer 1 and Layer 2 artefacts were not regenerated; Bupa conclusions
  rely primarily on Layer 3, fusion reports, R6 submission-level scoring, and
  qualitative case evidence.
- Bupa has one submission per tester, so it does not validate longitudinal
  tester trajectory.
- `manyi_tan__web-health-information-bupa` is included but remains a short
  evidence-density case with limited inference value.
- `sentiment_e`, `calibrator_score_l`, and classifier-generated 5.1-B labels
  should be treated as supporting signals with documented confidence caveats.

## Boundary

Bupa was used only for final external evaluation. It did not change prompts,
schemas, Layer 1 thresholds, Layer 2 settings, 6.1 fusion rules, postprocess
filters, R6 scoring, or coaching logic.
