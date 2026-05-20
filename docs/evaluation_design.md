# CS20 Evaluation Design — Unified Methodology

**Owner**: R8 (testing + evaluation)  
**Last updated**: 2026-05-06  
**Related documents**: `docs/eval_freeze.md` · `docs/ablation_study.md` · `docs/case_studies.md`

---

## 1. Overview

This document unifies the evaluation methodology for the CS20 pipeline. It references—but does not repeat—the three specialist documents listed above. The purpose here is to:

1. Define the dual-track evaluation architecture and data governance rules.
2. Specify the inter-rater reliability (Kappa) methodology and all lower-confidence propagation rules.
3. Summarise the ablation and case study sub-studies in the context of the overall evaluation picture.
4. State the held-out Gate 1 ∧ Gate 2 governance policy.
5. Document the project-stratified evaluation used in Step 5.4.

Downstream consumers—Final Report authors, Step 6.2 coaching engine, R6 Performance Tracking—should treat §3.3 and §8 as the single authoritative source for confidence caveats.

---

## 2. Dual-Track Evaluation Architecture

The partition specification—including exact counts, the two transcript-failure exclusions, and the "not included" category—is defined in `docs/eval_freeze.md §一`. Summary:

| Partition | Content | Size | Role |
|---|---|---|---|
| **dev set** | AAMI + UQ + DPC-WA collated | 55 videos (57 − 2) | Prompt tuning, Kappa annotation, ablation, rotating validation |
| **held-out** | Bupa collated | 21 videos | One-time final evaluation completed after Gate 1 ∧ Gate 2 |
| **not included** | Brighton raw + Bupa raw | — | No aligned metadata; excluded from all evaluation |

**Annotation iron rule**: Human annotation for Kappa is restricted to the dev set. Post-hoc qualitative audit of Bupa held-out must not feed back into schema or prompt design.

Within the dev set, **rotating project-wise validation** operates at the Step 6.1 fusion layer (AAMI ↔ UQ rotating; DPC-WA always in fit pool). **Step 5.4 project-stratified evaluation** runs 5.2 inference once across all dev videos and compares distributions across the three projects (details in §7).

---

## 3. Cohen's Kappa Methodology

### 3.1 Raw vs Weighted — Selection Rationale

The choice between raw (unweighted) and weighted Cohen's Kappa depends on whether ordinal proximity matters for the annotation task.

**Raw Kappa** is used for `friction_type` and `sentiment_e`. Both fields are nominal: the categories are not ordered on a severity or magnitude scale. Mistaking F1 for F3 is no more or less serious than mistaking F1 for F7, so weighting the disagreement matrix would impose an unwarranted ordinal structure.

**Weighted Kappa** (linear weights) is used for `severity` and `calibrator_score_l`. Both fields represent ordered intensity. A disagreement between S2 and S3 is meaningfully smaller than a disagreement between S1 and S5. Linear weighting is preferred over quadratic weighting because the severity scale was not designed to have squared-distance semantics, and linear weights are easier to audit.

### 3.2 Dimension Grouping

Two comparisons are tracked. **R3 vs R8** (n=14 shared windows, round-1 canonical) measures human inter-annotator reliability. **LLM V2 vs R8** is the model-vs-human gate check. LC rules in §3.3 cite the more conservative or pipeline-relevant value; footnotes flag where the two diverge significantly.

#### Step 5.1-A — Window-level fields (n=14)

| Field | R3 vs R8 κ | LLM V2 vs R8 κ | Confidence tier | Notes |
|---|---|---|---|---|
| `friction_type` | 0.8293 almost perfect | **0.7407** substantial | high | LLM gate ≥ 0.5 passed; V2 retained |
| `severity_s` (weighted) | **0.6056** substantial | **0.7603** substantial | high | Strong ordinal agreement in both comparisons |
| `sentiment_e` | 0.2222 fair | **0.0** slight | **low** | Humans can differentiate; LLM inflates E3→E4 systematically |
| `calibrator_score_l` (weighted) | **0.9271** almost perfect | **0.4118** fair (n=10) | **medium-low** | Human agreement is excellent; low confidence is LLM-specific |
| `signal_alignment` | N/A — single class | N/A | — | 100% agree both sides; κ undefined |

#### Step 5.1-B — Video-level fields (n=14)

| Field | R3 vs R8 κ | LLM V2 vs R8 κ | Confidence tier | Notes |
|---|---|---|---|---|
| `narration_quality` | **0.5882** moderate | **0.0** slight | **medium** | Humans agree moderately; LLM assigns `rich` to all 14 videos |
| `recording_quality` | **0.0** (92.9% agree) | **0.0118** slight | **low** | R3/R8 κ collapses from class imbalance; LLM assigns `acceptable` to all |
| `coaching_evidence` | N/A — single class | N/A | — | All `none` both sides; κ undefined |

> **5.1-B consumers note:** The confidence tiers reflect inter-annotator reliability. The LLM's systematic default behaviour (§3.3 rules LC-3, LC-4) is an additional reason for caution beyond the tier label alone.

### 3.3 Lower-Confidence Marking Rules

Any downstream consumer reading fields listed below must attach the specified confidence metadata. Rules are normative; the §8 table is a quick-reference summary.

---

**LC-1 — `sentiment_e` → `confidence='low'`**

LLM V2 vs R8 κ = 0.0. The classifier systematically assigns E4 (Frustrated) regardless of actual tester tone; R8 correctly differentiates E2/E3/E4. Note that human annotators *can* distinguish sentiment: R3 vs R8 inter-annotator κ = 0.2222 (Fair). The `low` confidence applies to **LLM-generated** `sentiment_e` values. Aggregations depending primarily on LLM sentiment output should be suppressed or clearly caveated. The field is retained in output JSON as a null signal confirming classification was attempted.

---

**LC-2 — `calibrator_score_l` → `confidence='medium-low'`**

LLM V2 vs R8 weighted κ = 0.4118, n = 10 (4 no-finding windows excluded). Human annotators show near-perfect agreement (R3 vs R8 weighted κ = 0.9271), so the low confidence is **LLM-specific**—the model's L-score assignment diverges from human judgment more than the inter-annotator comparison would suggest. R6 mapping layers consuming L-scores directly must attach this metadata.

---

**LC-3 — `recording_quality` (5.1-B) → `confidence='low'`**

R3 vs R8 κ = 0.0 (92.9% agreement, class imbalance): 13 of 14 annotation windows share the same label, so Cohen's Kappa degrades to zero regardless of annotation quality. LLM V2 vs R8 κ = 0.0118: the LLM assigns `acceptable` to all 14 videos systematically. Both paths independently justify `low`. Downstream uses of `recording_quality` must attach `confidence='low'`; Case 5 (`mgblackwell2001_suncorp`) citations must note this caveat.

---

**LC-4 — `narration_quality` (5.1-B) → `confidence='medium'` (not low)**

R3 vs R8 κ = 0.5882 (Moderate): the confidence tier is set by inter-annotator reliability, which is sound. `narration_quality` is the most reliable 5.1-B field for human-generated values. Downstream steps must attach `confidence='medium'`—not 'low'.

However, LLM V2 vs R8 κ = 0.0: the LLM assigns `rich` to all 14 videos. Where `narration_quality` in a report was produced by the LLM classifier rather than by human annotation, it should be treated as `low` confidence despite the field-level `medium` tier. Final Report authors should check the provenance of each cited value.

---

### 3.4 Reporting Guidance

The lower-confidence rules were treated as interpretation guidance rather than
as a new `QualityReport` schema field. Final analysis should keep
`sentiment_e`, `calibrator_score_l`, and classifier-generated 5.1-B labels as
caveated supporting signals, while using `friction_type`, `severity_s`, report
tier, and case-study evidence as the primary evaluative claims.

---

## 4. Ablation Study

**Full study**: `docs/ablation_study.md` (R4, Peiyun He, 2026-04-28, dev55 official scope).

The study replays `fuse_video()` under four configurations (Full / No-L1 / No-L2 / No-L3) on the 55-video dev set. The result is decisive: removing L1 or L2 causes **zero tier changes**; removing L3 collapses **100% of videos** to `good`. `_compute_overall_quality()` currently consults only `l3_findings` and `l3_assessment`—L1 and L2 are audit-only pass-through signals.

Two implications follow (see `docs/ablation_study.md §5`): L3 is a single point of failure with no deterministic fallback; and L1 `DURATION_ANOMALY` flags capture real session anomalies (e.g. `carlpatrickrobinson_suncorp`, duration_ratio 0.144) that the current fusion logic does not act on. Whether to make `DURATION_ANOMALY` a hard gate is a project-level decision outside R4's scope.

Reproducibility: `python scripts/ablation_study.py` → `data/processed/ablation_summary.csv` (220 rows). `--full-57` adds the two excluded edge-case videos.

---

## 5. Case Studies

**Full study**: `docs/case_studies.md` (R3, Step 8.3, W9 progress report evidence base).

Cases were selected for evidence-pattern coverage, not statistical representativeness. The five patterns targeted: high-volume task-blocking friction; missing public-service support pathways; ESL/multilingual access barriers; L1 anomaly interaction with L3 confidence; poor recording with usable-but-caveated L3 evidence. Full selection criteria: `docs/case_studies.md §2`.

| Case | Video | Project | Evidence Pattern | Tier |
|---|---|---|---|---|
| 1 | `ghum_uq` | UQ | 93 findings, S1; authentication + search blockers | poor |
| 2 | `margieflint_wa` | DPC-WA | 79 findings, S2; missing actionable support pathways | poor |
| 3 | `giuliaclemente26_wa` | DPC-WA | 91 findings, S3; multilingual access, external workarounds | acceptable |
| 4 | `jenniferparry7_uq` | UQ | L1 DURATION_ANOMALY + LOW_AUDIO_QUALITY alongside S1 barrier | poor |
| 5 | `mgblackwell2001_suncorp` | AAMI | Poor recording (LC-3 rule); 15 findings usable as low-confidence evidence | poor |

Case 4 shows the correct posture when L1 quality flags co-exist with a severe L3 finding: retain the finding, attach the confidence caveat, do not discard. Case 5 directly operationalises Rule LC-3 (§3.3). Cross-case themes and limitations: `docs/case_studies.md §10–12`.

---

## 6. Held-out Gate 1 ∧ Gate 2 Governance

**Full specification**: `docs/eval_freeze.md` (R4 + R2, 2026-04-20).

### Why "Only Once"

The Bupa held-out set's validity as a final benchmark depends on the guarantee that no pipeline design decision was informed by its contents—even informally. The "only-once" rule is operationalised through six invalidation triggers in `docs/eval_freeze.md §六`: any post-run change to prompts (5.1-A/B, 5.2, 5.3, 5.4), 4.2 clustering parameters, 5.x JSON schema, 6.1 fusion rules or weights, R6 mapping rules, or post-processing thresholds voids the Bupa numbers and requires re-running from Gate 1.

### Four Freeze Categories (Gate 2)

Gate 2 required Nix's explicit sign-off before the held-out run. Final status (see `docs/eval_freeze.md §四–五`):

- **Freeze 1** — `friction_type / severity / sentiment / score_L` definitions: signed off by Nix on 2026-05-07.
- **Freeze 2** — `narration_quality / recording_quality / coaching_evidence` enumerations: signed off by Nix on 2026-05-07.
- **Freeze 3** — Step 6.1 fusion I/O schema: signed off by Nix on 2026-05-07.
- **Freeze 4** — R6 mapping rules: signed off by Nix on 2026-05-07.

**Held-out status as of 2026-05-20: ✅ completed.** The corrected Bupa evaluation processed 21 collated videos with 21/21 reports, 813 filtered L3 findings, and zero failed reports. The Bupa outputs were used only for evaluation and were not used to tune prompts, schemas, fusion, post-processing, R6 scoring, or coaching logic. See `group final/technical_closeout/submissions/R8_bupa_evaluation_summary_2026-05-20.md` and `final_technical_verification_2026-05-20.md`.

---

## 7. Step 5.4 Project-Stratified Evaluation

### Purpose and Method

Step 5.4 addresses whether the Step 5.2 classifier generalises across the three client projects, or systematically over/under-classifies in AAMI versus UQ versus DPC-WA sessions.

The full 5.2 classifier runs once across all 55 dev-set videos. Outputs are sliced by project and compared on: `friction_type` distribution (F1–F7 proportions), `severity` distribution, low-confidence finding rate, and human-annotation alignment. The single-run constraint is intentional: project-level differences in outputs reflect distributional or classifier sensitivity differences, not prompt variation between runs.

### Annotation Sample

Inter-annotator agreement is computed on **14 shared windows** (R3 and R8 independent blind annotation, round-1 canonical schema). Project breakdown: **UQ ×6, AAMI ×5, DPC-WA ×3** — all three dev projects are represented (note: AAMI project files use `_suncorp` filename suffix for historical reasons; see §7 Limitations for sample-size caveats).

The 14 windows are: `Sharelinsonny_uq_w026`, `fjone7_uq_w066`, `gameoverdan_suncorp_w040`, `ghum_wa_w029`, `giuliaclemente26_uq_w004`, `giuliaclemente26_uq_w050`, `margieflint_suncorp_w007`, `marychaunguyen_suncorp_w011`, `oliviamitchell22_suncorp_w007`, `oliviamitchell22_suncorp_w017`, `ramazankawish_wa_w075`, `reneerussell99_uq_w009`, `thanoptions_uq_w008`, `tianarosie1_wa_w015`.

### Kappa Results Summary

#### R3 vs R8 inter-annotator (n=14)

| Field | κ | Level |
|---|---|---|
| `friction_type` | **0.8293** | Almost perfect |
| `severity_s` (weighted) | **0.6056** | Substantial |
| `severity_s` (nominal) | 0.3378 | Fair |
| `sentiment_e` | 0.2222 | Fair |
| `calibrator_score_l` (weighted) | **0.9271** | Almost perfect |
| `narration_quality` | **0.5882** | Moderate |
| `recording_quality` | 0.0 (92.9% agree) | Class imbalance |

#### LLM V2 vs R8 (n=14 / n=10 for calibrator)

| Field | κ | Level | Verdict |
|---|---|---|---|
| `friction_type` | **0.7407** | Substantial | ✅ Gate passed |
| `severity_s` (weighted) | **0.7603** | Substantial | ✅ Strong ordinal agreement |
| `sentiment_e` | **0.0** | Slight | ⚠️ Systematic E3→E4 inflation |
| `calibrator_score_l` (weighted) | **0.4118** | Fair | ⚠️ LLM gap; human agreement excellent |
| `narration_quality` | **0.0** | Slight | ⚠️ LLM assigns `rich` to all videos |
| `recording_quality` | **0.0118** | Slight | ⚠️ LLM assigns `acceptable` to all videos |

### Key Error Patterns

`friction_type` disagreements (LLM vs R8): 3 windows — `giuliaclemente26_uq_w050` (R8=F7, LLM=F1), `marychaunguyen_suncorp_w011` (R8=F3, LLM=F7), `giuliaclemente26_uq_w004` (R8=F5, LLM=F7). All are borderline multi-friction windows where the dominant type is genuinely ambiguous; the 3-window disagreement rate is consistent with the κ = 0.7407 result. The inter-annotator sample shows 2 disagreements (R3 vs R8): `giuliaclemente26_uq_w004` (R3=F2, R8=F5) and `tianarosie1_wa_w015` (R3=F7, R8=none).

`sentiment_e` (LLM): systematic E4 assignment regardless of tester tone. Does not trigger a V3 revision but should be addressed with E3 calibration examples if sentiment accuracy becomes a downstream requirement.

5.1-B video-level defaults (LLM): the model assigns `rich` to all `narration_quality` and `acceptable` to all `recording_quality` across the entire 14-window sample. This is a V2 prompt calibration gap in the 5.1-B assessment, separate from the finding-level friction verdict. See LC-3 and LC-4 in §3.3 for the downstream handling rules.

### Results Summary (Project Distribution)

Project-stratified inference completed in commits `a2e1e18` / `ae42f50` (2026-04-25). The UQ/DPC-WA contrast is visible in the label distribution:

UQ sessions concentrate F4/F5 (authentication and form barriers) with a higher S1/S2 rate, reflecting course-discovery and account-access task structures. DPC-WA sessions are dominated by F6 (content not found / missing pathways) in the S3–S5 range. AAMI distribution falls between the two; full breakdowns are in the commit artefacts.

### Limitations

- The 14-window sample is small and unevenly distributed across projects (UQ ×6, AAMI ×5, DPC-WA ×3). Per-project κ stratification is therefore not pursued; combined-κ values are the primary inter-annotator metric. Whether project-specific friction patterns are uniformly recognised cannot be tightly validated at this sample size.
- The 5.1-B LLM default bias means that video-level quality labels in the production pipeline should not be treated as standalone classifier-generated assessments. They are retained as known-lower-confidence supporting fields, not as primary final claims.

---

## 8. Summary: Confidence Propagation Rules (Quick Reference)

For Final Report authors and downstream pipeline consumers. All κ values from n=14 shared annotation windows (calibrator: n=10).

| Field | Scope | R3 vs R8 κ | LLM V2 vs R8 κ | Confidence to attach | Driving comparison |
|---|---|---|---|---|---|
| `friction_type` | 5.1-A | 0.8293 | 0.7407 (raw) | *(none required)* | Both clear ≥ 0.5 gate |
| `severity_s` | 5.1-A | 0.6056 (weighted) | 0.7603 (weighted) | *(none required)* | Both substantial |
| `sentiment_e` | 5.1-A | 0.2222 (raw) | 0.0 (raw) | **`low`** | LLM (LC-1) |
| `calibrator_score_l` | 5.1-A | 0.9271 (weighted) | 0.4118 (weighted) | **`medium-low`** | LLM (LC-2) |
| `narration_quality` | 5.1-B | 0.5882 (raw) | 0.0 (raw) | `medium` for human / `low` for LLM-generated | Inter-annotator (LC-4); see provenance note |
| `recording_quality` | 5.1-B | 0.0 (92.9% agree) | 0.0118 (raw) | **`low`** | Both (LC-3) |

Rules LC-1 through LC-4 in §3.3 are the normative definitions. This table is a reference summary only. Where R3 vs R8 and LLM vs R8 diverge, the "Driving comparison" column identifies which value sets the confidence tier.
