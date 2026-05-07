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

## Current Limitations

The current implementation still has several limitations despite the V2 severity-aware extension:

- recommendations remain primarily session-level
- no timestamp-level evidence injection
- only `severity_s` from 5.1-A is currently consumed
- friction-type (`F1–F7`) aggregation is not yet implemented
- no multi-finding coaching synthesis across related friction patterns
- no Step 6.1 fused weighting integration
- no complex contextual recommendation generation with LLM
- no survey-based validator integration

---

## Future Extension

Potential future extensions include:

- friction-type (`F1–F7`) aggregation across multiple findings
- meta-coaching generation using narration + recording combinations
- timestamp-aware recommendation evidence
- top-K finding selection and recommendation compression
- recommendation diversity optimisation across reports
- adaptive recommendation tone based on Step 6.1 fused outputs
- survey-supported validation for complex issue escalation
- more contextual LLM-assisted coaching generation for non-template cases
