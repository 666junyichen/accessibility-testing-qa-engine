# R3 Layer 3 Prompt Design

## 1. Purpose

This document explains the semantic design for Step 5.1 Layer 3 LLM
classification.

Step 5.1 is split into two prompts:

- 5.1-A finding-level classification for friction, severity, sentiment, and
  calibrator audit signals.
- 5.1-B video/session-level assessment for narration quality, recording
  quality, and coaching evidence.

The prompts use the client friction and sentiment framework documented in:

`docs/friction_taxonomy.md`

The source framework comes from the client PDF:

`Friction & Sentiment Classification Framework.pdf`

This prompt design supports:

- Step 5.1 Prompt Design
- Step 5.2 LLM Classification
- Step 5.3 Manual Annotation
- Step 5.4 Agreement Evaluation
- Step 8.3 Case Study

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 2. Input Units

5.1-A uses one transcript window from:

`data/processed/windows.csv`

Each window represents approximately 60 seconds of tester narration. The core
input fields are:

| Field | Source | Purpose |
|---|---|---|
| `window_id` | `windows.csv` | Unique window identifier |
| `project` | `windows.csv` | Project context |
| `video_id` | `windows.csv` | Tester-project identifier |
| `window_text` | `windows.csv` | Main transcript text to classify |
| `task_title` | raw task CSV files | Provides task context |
| `task_instructions` | raw task CSV files | Helps interpret whether behaviour is relevant to the task |

5.1-B uses a full video/session transcript and the same project/task context
where available. It assigns session-level quality signals rather than extracting
individual friction findings.

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 3. Why Task Context Is Included

Window text alone can be ambiguous.

For example, a tester saying "I cannot find it" is difficult to interpret
without knowing what they were asked to find.

Therefore, the prompt includes both:

- transcript text
- task title and task instructions

This allows the LLM to distinguish between:

- real friction that blocks or slows task completion
- normal task exploration
- irrelevant or off-task narration
- successful completion
- content feedback without a task barrier

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 4. Canonical Prompt Modules

The Step 5.1 implementation is split across the canonical Round 5 modules:

| Module | Role |
|---|---|
| `src/layer3/prompts_a.py` | Builds 5.1-A finding-level prompt messages |
| `src/layer3/prompts_b.py` | Builds 5.1-B video/session-level prompt messages |
| `src/layer3/schemas_a.py` | Defines the 5.1-A pydantic output schema |
| `src/layer3/schemas_b.py` | Defines the 5.1-B pydantic output schema |

The prompt modules may embed a JSON-shaped example for LLM instruction, but the
authoritative field structure is the pydantic schema. Documentation should not
define a separate JSON schema or alternate field names.

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 5. Friction Type Boundaries

The friction labels follow `docs/friction_taxonomy.md`.

| Code | Label |
|---|---|
| F1 | Comprehension Friction |
| F2 | Confidence Friction |
| F3 | Accessibility Friction |
| F4 | Unresponsive Interface |
| F5 | Unexpected Behaviour |
| F6 | Content Not Found |
| F7 | Excessive Effort |

Boundary rules:

- Use F1 when the main issue is understanding wording, terminology,
  instructions, or content meaning.
- Use F2 when the tester understands the content but is unsure what will
  happen, what to choose, whether an action is correct, or where to go next.
- Use F3 when the issue involves screen readers, keyboard access, focus,
  headings, labels, zoom, PDF accessibility, or other accessibility/assistive
  technology barriers.
- Use F4 when the tester takes an action but the interface gives no response,
  delayed response, or unclear feedback.
- Use F5 when the interface behaves differently from what the label, design, or
  prior pattern suggested.
- Use F6 when the tester cannot locate information or a pathway needed for the
  task because it is missing, hidden, or placed unexpectedly.
- Use F7 when the task is technically possible but requires too many steps,
  repeated entries, time, scrolling, setup, or cognitive effort.

Important boundary:

- `F7` does not mean "no issue". In the client framework, `F7` means excessive
  effort.
- A no-friction window is represented by an empty `findings` array in 5.1-A, not
  by a special friction label.
- When multiple issues appear in one event, choose the dominant friction type
  and explain secondary issues in `rationale`.

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 6. Severity Boundaries

Severity uses the client S1-S6 framework. Severity is separate from friction
type: the same F-code can appear at different severity levels.

| Source ID | Client Label | Boundary |
|---|---|---|
| S1 | Blocker (Project) | Primary project outcome cannot be achieved independently; abandonment or facilitator intervention is required. |
| S2 | Task Blocker | Overall project may continue, but one assigned task is completely blocked. |
| S3 | Severe Friction | Significant component failure or barrier; tester works around, skips, or proceeds without being able to verify something important. |
| S4 | High Friction | Major difficulty with substantial effort, repeated attempts, workaround, or extended time. |
| S5 | Medium Friction | Noticeable delay, hesitation, or confusion, but completion is not seriously threatened. |
| S6 | Low Friction | Minor issue with negligible impact on task progress. |

Do not use simplified severity labels as prompt output requirements. Manual
annotation and LLM outputs must use the canonical field in `schemas_a.py`.

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 7. Sentiment Boundaries

Sentiment uses the client E1-E5 framework and captures expressed participant
feeling, not the objective severity of the friction.

| Source ID | Client Label | Boundary |
|---|---|---|
| E1 | Positive / Delighted | Genuine delight, praise, or pleasant surprise. |
| E2 | Positive / Satisfied | Mild positive feeling; things worked as expected. |
| E3 | Neutral / Indifferent | Matter-of-fact verbal expression without clear emotion. |
| E4 | Negative / Frustrated | Annoyance, confusion, disappointment, irritation, or frustration. |
| E5 | Negative / Angry | Strong negative emotion, hostility, or clear intent to abandon or avoid. |

Sentiment discipline:

- `E3` means neutral sentiment was expressed.
- `null` means no emotional evidence was available.
- `E3` and `null` are not interchangeable.
- If the participant makes any verbal expression in the finding, use E1-E5.
- Only use `null` when there is no stated signal and no emotion evidence.

Do not use simplified sentiment labels as prompt output requirements. Manual
annotation and LLM outputs must use the canonical field in `schemas_a.py`.

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 8. Signal Alignment And Calibrator Boundaries

5.1-A findings use a dual-signal interpretation:

- `observed_signal`: what the participant actually did.
- `stated_signal`: what the participant said.
- `signal_alignment`: whether the observed and stated signals agree.

Alignment rules:

- Use `aligned` when observed behaviour and stated experience support the same
  interpretation.
- Use `conflicted` when the participant's statement and behaviour disagree; in
  that case, score to the lower observed behaviour level rather than averaging.
- Use `stated_missing` when the transcript contains no relevant verbal
  statement for the finding.

`calibrator_score_l` is an L1-L5 audit signal from the SMP calibrator prompt. It
coexists with `severity_s` but must not be merged with it or treated as the same
scale.

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 9. Video-Level Quality Boundaries

5.1-B is a video/session-level assessment. It is independent from 5.1-A and
should not list friction findings or severity.

Semantic boundaries:

- `narration_quality` measures whether the participant verbalised enough
  context for analysis, from no useful narration to rich think-aloud evidence.
- `recording_quality` measures whether the transcript/audio is usable for
  downstream analysis. It is not a judgement of production or film quality.
- `coaching_evidence` identifies moderator coaching. Neutral prompts such as
  "what are you thinking?" or "can you describe that?" are not coaching.
  Explicitly telling the participant where to click, naming the target control,
  or giving the answer is coaching.

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 10. Design Rules

The prompts use the following rules:

- Use only evidence from the transcript and task context.
- Use task context to decide whether behaviour is relevant.
- Do not infer personal attributes, unstated motivations, diagnoses, or
  unsupported cohort details.
- Produce one finding per distinct friction event in 5.1-A.
- Return an empty findings array when no friction is present.
- Choose one dominant friction type per finding.
- If multiple issues appear, explain the main one in `rationale`.
- Do not use F7 for no-friction or positive-only windows.
- Use cohort context only in `structural_amplification_note` / `rationale`; do
  not upweight severity or calibrator score because of cohort identity alone.
- Return only valid JSON from the prompt response.

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 11. Relationship To Manual Annotation

Manual annotation must use pydantic canonical fields from:

- `src/layer3/schemas_a.py`
- `src/layer3/schemas_b.py`

The annotation CSV used for agreement should align with the same fields as
`data/annotations/r8_manual_annotations_round1.csv`. Older fields such as
`friction_label`, `severity_id`, simplified `severity`, `sentiment_id`,
simplified `sentiment`, and `primary_evidence` are historical inputs only and
should not be used as the evaluation source for Round 5.

This makes it easier to compare:

- human labels
- LLM labels
- cluster interpretation labels

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 12. Relationship To Cluster Interpretation

The prompt design also uses the semantic patterns identified in:

`docs/cluster_interpretation.md`

For example:

- unclear wording, jargon, or technical/legal terminology maps to F1
- uncertainty about next action, consequence, trust, or wayfinding maps to F2
- inaccessible PDFs, focus issues, labels, headings, screen reader barriers, or
  keyboard barriers map to F3
- no response, delayed response, or missing confirmation after an action maps to
  F4
- surprising system behaviour maps to F5
- missing or hidden information maps to F6
- too many steps, repeated entry, extra setup, or excessive scrolling maps to F7

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 13. Future Use

These prompts support Step 5.2 LLM classification.

5.1-A finding-level messages:

```python
from layer3.prompts_a import build_messages

messages = build_messages(
    window_id=window_id,
    project=project,
    video_id=video_id,
    window_text=window_text,
    task_title=task_title,
    task_instructions=task_instructions,
)
```

5.1-B video/session-level messages:

```python
from layer3.prompts_b import build_messages

messages = build_messages(
    video_id=video_id,
    project=project,
    transcript=transcript,
    task_title=task_title,
    task_instructions=task_instructions,
)
```

These messages can then be sent to an LLM API. Outputs should be validated
against `schemas_a.py` / `schemas_b.py`.

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.

## 14. Current Limitations

- The current prompt modules build messages only; they do not call any LLM API.
- Task context is not yet automatically joined into every production window.
- R3 round-1 annotations still need migration to the Round 5 canonical schema.
- The prompts have not yet been evaluated against a completed two-annotator
  canonical annotation set.

Field schema lives in `src/layer3/schemas_a.py` / `schemas_b.py`; this doc only
explains semantic boundaries.
