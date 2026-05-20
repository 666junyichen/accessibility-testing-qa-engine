# Presentation Slide Fact Pack

Use this alongside `demo_script.md` when preparing the final presentation.

## Core Story

The project is a decision-support pipeline for tester-submission review. It
turns transcript evidence into window-level findings, video-level reports,
coaching recommendations, R6 performance tables, and a Streamlit review demo.

## Slide-ready Facts

- Development scope: 55 official dev reports after excluding two transcription
  failure edge cases from the 57 generated development reports.
- Held-out scope: 21 Bupa videos, processed once after freeze.
- Bupa outputs: 1,252 windows, 813 filtered Layer 3 findings, 21 reports, 21 R6
  rows, zero failed reports.
- Streamlit demo: three views, covering Single Video, Tester Trajectory, and
  Cohort Overview.
- Strongest validated Layer 3 agreement: friction type and severity have the
  clearest evaluation support.
- Ablation message: removing Layer 3 collapses the dev55 quality tiers, so
  current final-tier decisions are L3-dependent.
- R6 message: report quality tier and tester-performance tier are different
  constructs and should be narrated separately.

## Demo Path

1. Open the Streamlit app from `app/streamlit_demo.py`.
2. Start with a single dev55 report.
3. Move to the tester trajectory view.
4. End with cohort overview and R6 performance distribution.
5. Close with limitations: L2 is exploratory, Bupa L1/L2 were not regenerated,
   and coaching remains template-based reviewer support.

## Evidence Sources

- `README.md`
- `docs/evaluation_design.md`
- `docs/ablation_study.md`
- `docs/case_studies.md`
- `docs/performance_tracking.md`
- `need/01_final_report/bupa_heldout_fact_pack.md`
- `need/03_final_checking/technical_closeout/FINAL_TECHNICAL_HANDOFF.md`

