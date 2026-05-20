# Held-out Evaluation Freeze Checklist

This document is the governance record for CS20 held-out evaluation. Any Bupa
held-out run must satisfy both Gate 1 and Gate 2. A run before both gates are
complete is invalid, and the resulting Bupa metrics must not be reported.

Final status on 2026-05-20: Gate 1 and Gate 2 were complete, the corrected
21-video Bupa held-out evaluation was completed, and final technical
verification passed. Bupa results must not feed back into prompts, schemas,
fusion, post-processing, R6 scoring, or coaching logic.

This document was consolidated from the Round 4 evaluation-governance review on
2026-04-20. Any future update must also update the evaluation and data-scope
sections in `README.md`.

---

## 1. Immutable Data Split

| Split | Contents | Size | Purpose |
|---|---|---:|---|
| Development set | Three older collated projects: AAMI 21 + UQ 19 + DPC-WA 17, with two transcription failures excluded from formal reporting | 55 videos | Prompt tuning, schema finalisation, manual Kappa checks, ablation, rotating validation |
| Held-out | Bupa collated videos | 21 videos | Completed once after final freeze |
| Not included | Brighton raw package and Bupa raw package | Brighton raw 105 + Bupa raw 315 | Excluded because raw-only assets cannot be aligned reliably to collated tasks, survey data, or reporting scope |

Annotation rule: the human annotation set used for Kappa is strictly limited to
the development set. Bupa held-out may only receive a small post-hoc qualitative
audit after final freeze, and those findings must not feed back into design.

## 2. Development-Internal Validation

- Rotating unit: `AAMI` and `UQ` form the two project-wise rotating validation
  rounds. DPC-WA remains in the fit pool as a diversity source.
- Rotating layer: validation is placed at Step 6.1 fusion, not a full Step 5.2
  rerun, to avoid doubling token cost.
- Prompt cross-project stability: Step 5.4 performs project-stratified
  evaluation through label distributions, low-confidence rates, and human
  annotation alignment. Step 5.2 runs once on the full development set.
- Split grain: video/tester/project group split, not window split.

## 3. Gate 1 - Objectively Verifiable Code Completion

- [x] Step 6.1 `fusion_*.py` merged to the main branch:
  `src/pipeline/{schemas,fusion}.py`, commit `dfe1b0b` on 2026-04-23.
- [x] Step 6.1 pytest passed, including fusion rule and R6 mapping unit tests:
  133 passed on the 2026-05-04 baseline.
- [x] Step 5.1-A and Step 5.1-B prompts have pinned versions and commit
  hashes: V2 canonical at commit `dfe1b0b`; R3 few-shot injection at commit
  `d015fcf`.
- [x] Step 5.2 classifier completed one full development-set inference pass:
  `data/processed/layer3_findings.csv` (2,219 rows),
  `layer3_findings_filtered.csv` (2,133 rows), and
  `layer3_video_assessments.csv` (57 rows), commit `dfe1b0b`.
- [x] Step 5.4 project-stratified evaluation completed: commits `a2e1e18` and
  `ae42f50` on 2026-04-25. `friction_type` Kappa was 0.7407, above the 0.5
  threshold, so V2 was retained.

Gate 1 status: complete on 2026-05-04.

## 4. Gate 2 - Project-Lead Sign-Off

After Gate 1, the project lead signed off four freeze categories by recording
the commit hash, date, and approval status in Section 5.

### Freeze 1: friction / severity / sentiment field set

- `friction_type in {F1, F2, F3, F4, F5, F6, F7}` from
  `client/s3_snapshot/06-friction-sentiment-framework.md`.
- `severity in {S1, S2, S3, S4, S5, S6}` as the canonical client-aligned
  severity scale, replacing the earlier custom five-level scale.
- `sentiment in {E1, E2, E3, E4, E5}` with E3 neutral excluded from aggregate
  sentiment according to the client framework.
- `score_L in {L1, L2, L3, L4, L5}` from
  `client/s3_snapshot/07-friction-score-calibrator-prompt.md`; it remains
  separate from S1-S6 and is not mapped into severity.

### Freeze 2: narration / recording quality field set

- `narration_quality` enum and definitions.
- `recording_quality` enum and definitions.
- `coaching_evidence` enum and definitions.

### Freeze 3: Step 6.1 fusion input/output schema

- Input: Step 5.2 classifier output per window plus Step 5.1-B video-level
  tester-behaviour fields.
- Output: per-tester x per-task quality judgement, coaching recommendation
  seed, and confidence.
- Fusion rule: consensus rules across Layer 1 rules, Layer 2 clustering, and
  Layer 3 classification, including weights, conflict handling, and fallbacks.

### Freeze 4: R6 mapping rules

- Mapping from Step 5.x / Step 6.1 outputs to R6 Performance Tracking fields.
- Normalisation rules across testers and projects.

## 5. Freeze Sign-Off Record

| Freeze category | Commit hash | Date | Sign-off | Notes |
|---|---|---|---|---|
| Freeze 1 - friction/severity/sentiment | `dfe1b0b` | 2026-05-07 | Lead approved | Round 5 canonical V2 prompt and `schemas_a/b`; Step 5.4 `friction_type` Kappa 0.7407 >= 0.5, V2 retained |
| Freeze 2 - narration/recording quality | `dfe1b0b` | 2026-05-07 | Lead approved | Step 5.1-B schema canonical; `coaching_evidence` remains binary: `none` or `explicit` |
| Freeze 3 - Step 6.1 fusion I/O schema | `dfe1b0b` | 2026-05-07 | Lead approved | `src/pipeline/{schemas,fusion}.py`; seven `quality_tier` rules plus `DURATION_ANOMALY` cap locked |
| Freeze 4 - R6 mapping rules | `ee8d5ce` | 2026-05-07 | Lead approved | `src/tracking/performance_model.py`; weights 0.50 / 0.35 / 0.15, four cap rules, tier-gap mismatch flag, stable band, and calibrator audit-only rule |

## 6. Only-Once Rule

After the Bupa held-out run, changes to any of the following surfaces invalidate
the Bupa metrics and require Gate 1 and Gate 2 to be repeated:

1. Prompts: Step 5.1-A, 5.1-B, 5.2, 5.3, or 5.4.
2. Step 4.2 clustering parameters: `final_k`, `min_samples`, `eps`, or feature
   set.
3. Step 5.x JSON schema fields.
4. Step 6.1 fusion rules or weights.
5. R6 mapping rules.
6. Post-processing rules, including confidence thresholds and low-confidence
   filtering.

## 7. Permitted Bupa Actions Before Freeze

Before both gates are complete, Bupa collated data may only be used for:

- Coverage statistics: video count, tester count, task count, and duration
  distribution.
- Structured-data distribution comparison, such as survey-label distribution
  versus the development set.

Before freeze, Bupa collated data must not be used for LLM prompt calls,
classifier inference, human annotation, or schema/prompt feedback.

## 8. Bupa Held-Out Result Status on 2026-05-20

- Corrected Bupa scope: 21 collated videos.
- Corrected run: 21 transcripts, 1,252 windows, Level B 21/21, Level A
  1,252/1,252, 813 filtered findings, 21/21 reports, and zero zero-duration
  reports.
- Downstream reviews: R3, R5, R6, and R8 reviews were returned and archived.
- Final verification: pytest 155 passed, dev55 sync 55/55 passed, and Bupa
  reports were readable and ID-aligned.
- Documented caveats: Bupa Layer 1 and Layer 2 were not rerun; the one
  submission per tester structure does not support longitudinal trajectory
  validation; `manyi_tan` is a short evidence-density case.

Owner: project lead. Last updated: 2026-05-20. Related records: `README.md`,
`docs/evaluation_design.md`, and `data/heldout/bupa/`.
