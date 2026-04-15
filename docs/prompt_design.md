# R3 Layer 3 Prompt Design

## 1. Purpose

This document explains the prompt design for Step 5.1 Layer 3 LLM
classification.

The prompt is designed to classify each transcript window using the R3 friction
taxonomy defined in `docs/friction_taxonomy.md`.

This prompt design supports:

- Step 5.1 Prompt Design
- Step 5.2 LLM Classification
- Step 5.3 Manual Annotation
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

- real navigation friction
- normal task exploration
- irrelevant or off-task narration
- successful completion
- content feedback

## 4. Prompt Components

The prompt design is implemented in:

`src/layer3/prompts.py`

It contains:

| Component | Purpose |
|---|---|
| `SYSTEM_PROMPT` | Defines the LLM role and output constraints |
| `TAXONOMY_PROMPT` | Provides the friction, sentiment, narration, and severity definitions |
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
  "friction_type": "F1 | F2 | F3 | F4 | F5 | F6 | F7",
  "friction_label": "string",
  "severity": "none | low | medium | high",
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
| `friction_type` | One friction category from F1-F7 |
| `friction_label` | Human-readable name of the selected friction type |
| `severity` | Estimated seriousness of the issue |
| `sentiment` | Tester sentiment in the window |
| `narration_type` | The main type of narration in the window |
| `at_context_present` | Whether accessibility or assistive technology context is present |
| `primary_evidence` | A short quote supporting the classification |
| `rationale` | Short explanation of why this label was selected |
| `confidence` | Model confidence in the classification |

## 7. Friction Type Mapping

The friction labels follow `docs/friction_taxonomy.md`.

| Code | Label |
|---|---|
| F1 | Navigation / Findability Issue |
| F2 | Content Clarity Issue |
| F3 | Interaction / Control Issue |
| F4 | Accessibility / Assistive Technology Issue |
| F5 | Task Understanding / Expectation Mismatch |
| F6 | Support / Trust / Safety Concern |
| F7 | No Clear Friction / Positive Feedback |

## 8. Design Rules

The prompt uses the following rules:

- Use evidence from the transcript window.
- Use task context to interpret whether behaviour is relevant.
- Do not infer personal attributes or unstated motivations.
- Choose one dominant friction type.
- If multiple issues appear, explain the main one in `rationale`.
- Return only valid JSON.
- Use F7 when there is no clear friction.
- Use `unclear` when the transcript is too ambiguous.

## 9. Relationship To Manual Annotation

The prompt output fields align with the manual annotation fields in:

`data/annotations/window_semantic_labels_template.csv`

This makes it easier to compare:

- human labels
- LLM labels
- cluster interpretation labels

## 10. Relationship To Cluster Interpretation

The prompt design also uses the semantic patterns identified in:

`docs/cluster_interpretation.md`

For example:

- navigation problems map to F1
- unclear wording or information hierarchy maps to F2
- inaccessible PDFs or screen reader barriers map to F4
- support, safety, or trust concerns map to F6

## 11. Future Use

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

## 12. Current Limitations

- The current prompt does not call any LLM API.
- Task context is not yet automatically joined into each sampled window.
- The prompt has not yet been evaluated against the manual annotation set.
- The JSON schema may be refined after Step 5.3 manual annotation and Step 5.4 agreement evaluation.
