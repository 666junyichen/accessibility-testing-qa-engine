# R3 Layer 3 Prompt Design

## 1. Purpose

This document explains the prompt design for Step 5.1 Layer 3 LLM
classification.

The prompt is designed to classify each transcript window using the client
friction and sentiment framework documented in:

`docs/friction_taxonomy.md`

The source framework comes from the client PDF:

`Friction & Sentiment Classification Framework.pdf`

This prompt design supports:

- Step 5.1 Prompt Design
- Step 5.2 LLM Classification
- Step 5.3 Manual Annotation
- Step 5.4 Agreement Evaluation
- Step 8.3 Case Study

## 2. Input Unit

The basic input unit is one transcript window from:

`data/processed/windows.csv`

Each window represents approximately 60 seconds of tester narration.

The core input fields are:

| Field | Source | Purpose |
|---|---|---|
| `window_id` | `windows.csv` | Unique window identifier |
| `project` | `windows.csv` | Project context |
| `video_id` | `windows.csv` | Tester-project identifier |
| `window_text` | `windows.csv` | Main transcript text to classify |
| `task_title` | raw task CSV files | Provides task context |
| `task_instructions` | raw task CSV files | Helps interpret whether behaviour is relevant to the task |

## 3. Why Task Context Is Included

Window text alone can be ambiguous.

For example, a tester saying "I cannot find it" is difficult to interpret
without knowing what they were asked to find.

Therefore, the prompt includes both:

- transcript window text
- task title and task instructions

This allows the LLM to distinguish between:

- real friction that blocks or slows task completion
- normal task exploration
- irrelevant or off-task narration
- successful completion
- content feedback without a task barrier

## 4. Prompt Components

The prompt design is implemented in:

`src/layer3/prompts.py`

It contains:

| Component | Purpose |
|---|---|
| `SYSTEM_PROMPT` | Defines the LLM role and output constraints |
| `TAXONOMY_PROMPT` | Provides friction, severity, sentiment, narration, and boundary definitions |
| `USER_PROMPT_TEMPLATE` | Formats one window and its task context |
| `OUTPUT_SCHEMA` | Defines the required JSON output fields |
| `OUTPUT_EXAMPLE` | Provides an example JSON structure |
| `build_user_prompt()` | Builds the user prompt for one window |
| `build_messages()` | Builds chat-style messages for an LLM client |

## 5. Output JSON Schema

The LLM must return valid JSON only.

Expected output:

```json
{
  "window_id": "string",
  "friction_type": "F1 | F2 | F3 | F4 | F5 | F6 | F7 | none | unclear",
  "friction_label": "string",
  "severity_id": "S1 | S2 | S3 | S4 | S5 | S6 | none | unclear",
  "severity": "none | low | medium | high",
  "sentiment_id": "E1 | E2 | E3 | E4 | E5 | unclear",
  "sentiment": "positive | neutral | negative | mixed | unclear",
  "narration_type": "thinking_aloud | reading_page | navigation | feedback_evaluation | task_response | off_task | unclear",
  "at_context_present": "yes | no | unclear",
  "primary_evidence": "short quote from the transcript window",
  "rationale": "brief explanation of the classification",
  "confidence": "low | medium | high"
}
```

## 6. Field Definitions

| Field | Meaning |
|---|---|
| `window_id` | The transcript window being classified |
| `friction_type` | One client F-code, or `none` / `unclear` |
| `friction_label` | Human-readable name of the selected friction type |
| `severity_id` | Client source severity ID from S1-S6, or `none` / `unclear` |
| `severity` | Simplified severity label used by current R3 annotation files |
| `sentiment_id` | Client source sentiment ID from E1-E5, or `unclear` |
| `sentiment` | Simplified sentiment label used by current R3 annotation files |
| `narration_type` | The main type of narration in the window |
| `at_context_present` | Whether accessibility or assistive technology context is present |
| `primary_evidence` | A short quote supporting the classification |
| `rationale` | Short explanation of why this label was selected |
| `confidence` | Model confidence in the classification |

## 7. Friction Type Mapping

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
| none | No observed friction |
| unclear | Unclear friction evidence |

Important boundary:

- `F7` does not mean "no issue". In the client framework, `F7` means
  excessive effort.
- Use `none` when the window shows positive feedback, normal progress, neutral
  reading, or successful completion without an observed impediment.
- Use `unclear` when the transcript or task context is too ambiguous.

## 8. Severity Mapping

The prompt asks for both the client source severity ID and a simplified severity
label.

| Source ID | Client Label | Simplified Label |
|---|---|---|
| S1 | Blocker (Project) | high |
| S2 | Task Blocker | high |
| S3 | Severe Friction | high |
| S4 | High Friction | medium |
| S5 | Medium Friction | medium |
| S6 | Low Friction | low |
| none | No observed friction | none |
| unclear | Insufficient evidence | choose best simplified value only if evidence allows |

## 9. Sentiment Mapping

The prompt asks for both the client source sentiment ID and a simplified
sentiment label.

| Source ID | Client Label | Simplified Label |
|---|---|---|
| E1 | Positive / Delighted | positive |
| E2 | Positive / Satisfied | positive |
| E3 | Neutral / Indifferent | neutral |
| E4 | Negative / Frustrated | negative |
| E5 | Negative / Angry | negative |
| unclear | Insufficient evidence | unclear |

If both positive and negative sentiment appear in the same window, use simplified
sentiment `mixed` and choose the strongest matching `sentiment_id`.

## 10. Design Rules

The prompt uses the following rules:

- Use evidence from the transcript window.
- Use task context to interpret whether behaviour is relevant.
- Do not infer personal attributes or unstated motivations.
- Choose one dominant friction type.
- If multiple issues appear, explain the main one in `rationale`.
- Return only valid JSON.
- Use `none` when there is no clear friction.
- Do not use F7 for no-friction or positive-only windows.
- Use `unclear` when the transcript is too ambiguous.

## 11. Relationship To Manual Annotation

The prompt output fields align with the manual annotation fields in:

`data/annotations/window_semantic_labels_template.csv`

The current manual annotation CSVs still use a simplified `severity` and
`sentiment` field. The prompt additionally includes `severity_id` and
`sentiment_id` so future agreement evaluation can be closer to the client
source framework.

This makes it easier to compare:

- human labels
- LLM labels
- cluster interpretation labels

## 12. Relationship To Cluster Interpretation

The prompt design also uses the semantic patterns identified in:

`docs/cluster_interpretation.md`

For example:

- unclear wording, jargon, or technical/legal terminology maps to F1
- uncertainty about next action, consequence, or wayfinding maps to F2
- inaccessible PDFs, focus issues, labels, headings, screen reader barriers, or keyboard barriers map to F3
- no response, delayed response, or missing confirmation after an action maps to F4
- surprising system behaviour maps to F5
- missing or hidden information maps to F6
- too many steps, repeated entry, or excessive scrolling maps to F7

## 13. Future Use

This prompt will later support Step 5.2 LLM classification.

A future classifier can import:

```python
from layer3.prompts import build_messages
```

and call:

```python
messages = build_messages(
    window_id=window_id,
    project=project,
    video_id=video_id,
    window_text=window_text,
    task_title=task_title,
    task_instructions=task_instructions,
)
```

These messages can then be sent to an LLM API.

## 14. Current Limitations

- The current prompt does not call any LLM API.
- Task context is not yet automatically joined into every production window.
- The prompt has not yet been evaluated against a completed two-annotator manual annotation set.
- The JSON schema may be refined after Step 5.3 manual annotation and Step 5.4 agreement evaluation.
