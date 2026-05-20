# Final Report Source Index

Use this index to locate repository evidence while writing the Final Report.
Do not paste raw internal task messages into the report; use the consolidated
project-facing files listed here.

## System Overview

| Report need | Source |
|---|---|
| End-to-end system summary and final status | `README.md` |
| Final technical completion statement | `need/03_final_checking/technical_closeout/FINAL_TECHNICAL_HANDOFF.md` |
| Data split and evaluation governance | `docs/eval_freeze.md` |
| Bupa held-out final result | `need/03_final_checking/technical_closeout/evidence/bupa_evaluation_summary_2026-05-20.md` |

## Methodology

| Topic | Source |
|---|---|
| Transcript parsing and windowing | `src/data/transcript_parser.py`, `src/preprocessing/window_splitter.py`, `README.md` |
| Layer 1 rule detector | `src/layer1/rule_detector.py`, `docs/layer1_design.md` |
| Layer 2 feature engineering and clustering | `src/layer2/`, `docs/cluster_interpretation.md` |
| Layer 3 schemas, prompts, and taxonomy | `src/layer3/`, `docs/l3_design.md` |
| Fusion and QualityReport generation | `src/pipeline/fusion.py`, `scripts/run_pipeline.py` |
| Coaching recommendation engine | `src/coaching/recommendation_engine.py`, `docs/coaching_templates.md` |
| Performance tracking | `src/tracking/performance_model.py`, `scripts/build_performance_tracking.py`, `docs/performance_tracking.md` |
| Demo interface | `app/streamlit_demo.py`, `app/components.py`, `app/styles.py` |

## Evaluation Evidence

| Topic | Source |
|---|---|
| Evaluation method and caveats | `docs/evaluation_design.md` |
| Inter-rater agreement / kappa | `need/01_final_report/research_notebooks/04_kappa_agreement.ipynb`, `docs/evaluation_design.md` |
| Ablation study | `docs/ablation_study.md`, `data/processed/ablation_summary.csv` |
| Case studies | `docs/case_studies.md` |
| Bupa held-out fact pack | `need/01_final_report/bupa_heldout_fact_pack.md` |
| Bupa supporting review synthesis | `need/03_final_checking/technical_closeout/evidence/bupa_supporting_review_summary_2026-05-20.md` |

## Figures and Analysis Materials

| Topic | Source |
|---|---|
| Transcript and structured EDA | `need/01_final_report/research_notebooks/eda_report.md` |
| EDA figures | `need/01_final_report/research_notebooks/figures/` |
| Notebook archive | `need/01_final_report/research_notebooks/` |

## Limitations / Future Work

| Limitation | Source |
|---|---|
| Bupa Layer 1 / Layer 2 not regenerated | `need/03_final_checking/technical_closeout/evidence/bupa_evaluation_summary_2026-05-20.md` |
| LLM confidence caveats | `docs/evaluation_design.md` |
| Layer 2 tester-dominance caveat | `docs/cluster_interpretation.md` |
| R6 heuristic-v1 and trajectory caveat | `docs/performance_tracking.md` |
| Coaching specificity and timestamp grounding limitations | `need/01_final_report/coaching_limitations_summary.md` |

