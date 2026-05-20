# Step 6.2 Coaching Templates

## Overview

This document defines the first-draft coaching templates for Step 6.2.

The current recommendation engine uses Step 5.1-B session-level signals as its top-level coaching taxonomy input:

- `narration_quality`
- `recording_quality`
- `coaching_evidence`

These fields determine three coaching categories:

1. Narration
2. Recording
3. Moderation

The baseline templates are session-level and template-based. The V2 extension adds optional 5.1-A severity-aware support, but does not yet include timestamped evidence, friction-type aggregation, or LLM-based contextual coaching.

---

## Design Scope

This version is a first-stage skeleton for Step 6.2.

It is designed to:

- consume 5.1-B session-level outputs
- generate high-level coaching recommendations
- organise recommendations into three categories:
  - `narration`
  - `recording`
  - `moderation`

It is not yet designed to:

- inject 5.1-A evidence
- cite timestamps
- use F1–F7 as recommendation taxonomy anchors
- generate complex LLM-based contextual coaching
- consume Step 6.1 fused quality report outputs

---

## Design Principles

- Coaching taxonomy is based on Step 5.1-B fields, not directly on F1–F7.
- Recommendations are session-level, not finding-level.
- Recommendations should be actionable, concise, and easy to read.
- Recommendations are generated only when a session-level signal indicates a meaningful issue.
- Signals that indicate acceptable or strong performance may produce no recommendation.

---

## Recommendation Categories

The recommendation engine currently outputs three coaching categories:

### 1. Narration
Driven by:
- `narration_quality`

### 2. Recording
Driven by:
- `recording_quality`

### 3. Moderation
Driven by:
- `coaching_evidence`

---

## 1. Narration Templates

### narration_quality = `none`

**Category**  
`narration`

**Title**  
Narration is insufficient for reliable interpretation

**Summary**  
The participant barely spoke during the session, making it difficult to interpret intent, confusion, or decision-making.

**Advice**
- Set think-aloud expectations clearly before the task begins.
- Use neutral reminders to encourage verbalisation without directing task behaviour.
- Treat detailed behavioural conclusions from this session with caution if low narration persists.

**Trigger**
- `trigger_field = narration_quality`
- `trigger_value = none`

**Priority**
- `4`

**Evidence Note**
- 5.1-B marks narration as effectively absent.

---

### narration_quality = `sparse`

**Category**  
`narration`

**Title**  
Increase participant verbalisation

**Summary**  
The session contains only fragments or very short utterances, which limits the usefulness of downstream interpretation.

**Advice**
- Encourage more continuous think-aloud narration throughout the task.
- Use neutral moderator prompts such as asking what the participant is seeing or trying to do.
- Aim for brief but frequent verbal check-ins rather than long periods of silence.

**Trigger**
- `trigger_field = narration_quality`
- `trigger_value = sparse`

**Priority**
- `3`

**Evidence Note**
- 5.1-B marks narration as sparse at the session level.

---

### narration_quality = `adequate`

**Category**  
`narration`

**Title**  
Narration could be more consistently explicit

**Summary**  
The participant provided enough verbal content for analysis, but the session would benefit from more regular think-aloud narration.

**Advice**
- Encourage the participant to briefly explain what they are noticing while moving through the task.
- Prefer short, regular verbal updates instead of only commenting after an action is completed.
- Use neutral prompts to invite process narration when long silent stretches appear.

**Trigger**
- `trigger_field = narration_quality`
- `trigger_value = adequate`

**Priority**
- `1`

**Evidence Note**
- 5.1-B marks narration as adequate but not rich.

---

### narration_quality = `rich`

**Action**  
No narration recommendation is generated.

**Reason**  
The session already contains sustained and useful verbalisation.

---

## 2. Recording Templates

### recording_quality = `poor`

**Category**  
`recording`

**Title**  
Recording quality limits reliable downstream analysis

**Summary**  
The session recording is broken, incomplete, or substantially degraded, which weakens the reliability of interpretation.

**Advice**
- Treat this session as low-confidence evidence.
- Improve recording setup and audio checks before the next session begins.
- Consider excluding this session from analyses that require detailed behavioural evidence.

**Trigger**
- `trigger_field = recording_quality`
- `trigger_value = poor`

**Priority**
- `5`

**Evidence Note**
- 5.1-B marks the session as barely usable for analysis.

---

### recording_quality = `acceptable`

**Category**  
`recording`

**Title**  
Recording quality is usable but should be improved

**Summary**  
The session is still usable for analysis, but defects in the recording may reduce confidence in detailed interpretation.

**Advice**
- Check microphone clarity and ambient noise before starting future sessions.
- Reduce clipping, brief audio gaps, or interruptions where possible.
- Mark this session as usable with caution if fine-grained analysis is required.

**Trigger**
- `trigger_field = recording_quality`
- `trigger_value = acceptable`

**Priority**
- `2`

**Evidence Note**
- 5.1-B marks recording quality as acceptable rather than good.

---

### recording_quality = `good`

**Action**  
No recording recommendation is generated.

**Reason**  
The session is sufficiently clean and complete for normal downstream use.

---

## 3. Moderation Templates

### coaching_evidence = `explicit`

**Category**  
`moderation`

**Title**  
Reduce directive moderator coaching

**Summary**  
The moderator appears to have directly guided the participant, which may reduce the naturalness and validity of the observed behaviour.

**Advice**
- Avoid telling the participant exactly where to click or what the answer is.
- Prefer neutral prompts that encourage the participant to explain their own thinking.
- Interpret task success with caution when explicit moderator coaching is present.

**Trigger**
- `trigger_field = coaching_evidence`
- `trigger_value = explicit`

**Priority**
- `4`

**Evidence Note**
- 5.1-B marks moderator coaching as explicit at the session level.

---

### coaching_evidence = `none`

**Action**  
No moderation recommendation is generated.

**Reason**  
No clear directive moderator coaching is detected at the session level.

---

## Output Structure Alignment

The current code implementation outputs recommendation objects with the following fields:

- `category`
- `title`
- `summary`
- `advice`
- `trigger_field`
- `trigger_value`
- `priority`
- `evidence_note`
- `tags`

---

## V2 Severity-aware Expansion

The V2 extension adds optional 5.1-A finding-level severity support while preserving the original 5.1-B session-level recommendation interface.

In addition to the original narration / recording / moderation templates, the recommendation engine can now consume optional finding-level records and use `severity_s` to generate severity-aware coaching recommendations.

Severity handling follows three tiers:

- `S1` / `S2`: generate a high-priority severity recommendation for task-blocking or near-blocking friction.
- `S3` / `S4`: generate a targeted severity recommendation for high-friction moments.
- `S5` / `S6`: do not generate a standalone recommendation unless repeated low-severity findings form a larger pattern.

The severity extension also summarises the finding-level severity distribution and surfaces representative findings in `evidence_note`. This allows coaching recommendations to reflect the seriousness of observed issues without changing the existing public API.

The original call remains valid:

```python
engine.generate(assessment)
```
---

## V3 Friction-aggregation + Meta Expansion

V3 adds two additional builders on top of the V2 severity-aware extension. The single public entrypoint `engine.generate(assessment, findings=...)` is unchanged — V3 only widens the set of categories that may appear in the result list. The legacy single-argument call `engine.generate(assessment)` still produces only the original V1 narration / recording / moderation items.

The internal priority ladder is now:

| Priority | Category | Trigger |
|---|---|---|
| 7 (reserved) | — | held for future high-impact builders |
| 6 | meta | narration ∈ {none, sparse} ∧ recording ∈ {poor, acceptable} |
| 5 | severity | one or more S1 / S2 task-blocking finding |
| 5 | recording | recording_quality = `poor` |
| 4 | severity | highest severity among findings is S3 / S4 |
| 4 | friction-aggregation | total ≥ 8 findings, ≥ 3 distinct friction types, ≥ 2 types each carry an S1–S4 finding, top-type share ≤ 0.70 |
| 4 | moderation | coaching_evidence = `explicit` |
| 4 | narration | narration_quality = `none` |
| 3 | narration | narration_quality = `sparse` |
| 2 | severity | repeated S5 / S6 only (≥ 5 low-severity findings) |
| 2 | recording | recording_quality = `acceptable` |
| 1 | narration | narration_quality = `adequate` |

**Priorities here are an internal ordering signal for displaying the most actionable items first; they are not on the same scale as the R6 0–100 score or the fusion `quality_tier`.**

### Friction-aggregation builder (priority 4)

Triggers when a session shows multi-pattern friction across several friction types — issuing one parallel recommendation per type would duplicate coaching effort.

**All four guard rails must be satisfied (V3.1, following peer review feedback — earlier V3 rule was 3-rail and over-triggered on dev57):**

1. `total findings (with valid friction_type AND severity_s) >= 8` — tightened from 5 to suppress generic multi-label noise on small samples
2. `>= 3 distinct friction types` among those valid findings
3. `>= 2 distinct friction types each carry at least one S1-S4 finding` — a single non-trivial type plus several low-severity types is not multi-pattern
4. `top type share <= 0.70` — when one friction type dominates (e.g. `F1=20, F2=1, F6=1`), that's a single-pattern session, not a multi-pattern one

**Output:**

- `category = "friction-aggregation"`
- `trigger_field = "friction_type_distribution"`
- `trigger_value` is the comma-joined list of friction-type codes ordered by count desc, F-code asc on ties — e.g. `"F1,F6,F2"`
- `evidence_note` summarises the count distribution: `5.1-A: total=12 findings across 4 distinct friction types (F1=5, F2=4, F6=2, F7=1)`
- advice begins with an explicit cross-reference to the severity item ("After addressing any severity-priority recommendation first, use this aggregation to group the remaining coaching themes — do not treat the two as parallel"), then anchors coaching on the dominant friction type and names the secondary types using their short labels (Comprehension / Confidence / Accessibility / Unresponsive / Unexpected / Not Found / Excessive Effort). The cross-reference avoids reviewer-side perceived duplication when severity and friction-aggregation co-occur (≈ 65% of dev57 sessions).

Findings with missing or unknown `friction_type` / `severity_s` are skipped silently — the builder will not crash on partially populated input.

### Meta builder (priority 6)

Triggers on the 5.1-B combination `narration_quality ∈ {none, sparse}` ∧ `recording_quality ∈ {poor, acceptable}`. When recording is degraded, the narration signal is also degraded; coaching the participant on think-aloud cadence before fixing the recording channel is unlikely to land.

When this builder fires, `generate()` **suppresses** the isolated `narration` and `recording` items in favour of one combined meta item. Moderation, severity, and friction-aggregation are independent and still emit normally — only the two builders driven by the same 5.1-B signals are suppressed.

**Output:**

- `category = "meta"`
- `trigger_field = "narration_recording_combo"`
- `trigger_value` = e.g. `"sparse+acceptable"` or `"none+poor"`
- `evidence_note` flags the suppression: `5.1-B narration=sparse ∧ recording=acceptable; isolated narration / recording recommendations are suppressed in favour of this meta item.`

When narration is `adequate` / `rich`, or recording is `good`, the meta builder is silent and the original narration / recording items emit as in V1.

### Eval-freeze posture

Per `docs/eval_freeze.md §六`, the only-once trigger list covers prompts, 4.2 parameters, 5.x JSON schema, 6.1 fusion rules / weights, R6 mapping, and post-processing thresholds. Step 6.2 coaching content is **not** in that list. The V3 expansion only adds items to `QualityReport.coaching_recommendations` and does not alter any frozen surface, so it does not invalidate Bupa held-out.

---

## Current Limitations

After V2 + V3, residual limitations are:

- recommendations remain session-level — no per-window or timestamp evidence
- finding-level inputs only consume `severity_s` and `friction_type`; `sentiment_e` and `calibrator_score_l` are not yet routed to coaching
- friction-aggregation uses count-only stable ordering — it does not weight types by severity
- meta builder is binary (suppress or not); it does not soften individual narration / recording wording inside the meta item
- no Step 6.1 fused weighting integration
- no complex contextual recommendation generation with LLM
- no survey-based validator integration

---

## Future Extension

Potential future extensions include:

- timestamp-aware recommendation evidence (per-window grounding)
- top-K finding selection and recommendation compression for very dense sessions
- weighting friction-aggregation ordering by severity instead of raw count
- adaptive recommendation tone based on Step 6.1 fused outputs
- consuming `sentiment_e` and `calibrator_score_l` for tone calibration
- survey-supported validation for complex issue escalation
- more contextual LLM-assisted coaching generation for non-template cases
