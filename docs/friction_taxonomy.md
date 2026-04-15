# R3 Friction Taxonomy

## 1. Purpose

This document defines the semantic labels used by R3 NLP analysis for transcript windows.
The taxonomy will support:
- 4.3 cluster interpretation
- 5.1 prompt design
- 5.3 manual annotation
- 8.3 case study selection

## 2. Unit of Analysis

The basic unit is one 60-second transcript window from `data/processed/windows.csv`.

Each window should be interpreted together with:
- project
- task title
- task instructions
- window text
- optional neighbouring transcript context

## 3. Input Data

Primary input:
- `data/processed/windows.csv`

Task context:
- `data/raw/*/*-tasks.csv`

Optional context:
- `data/processed/transcripts.csv`
- `data/processed/segments.csv`
- `data/processed/layer1_flags.csv`

## 4. Friction Types

| Code | Label | Definition | Example Evidence |
|---|---|---|---|
| F1 | Navigation / Findability Issue | The tester cannot find where to go, which link to click, or how to reach the needed information. | "I can't find...", "where is...", "I would expect..." |
| F2 | Content Clarity Issue | The tester finds the wording, explanation, information hierarchy, or page content unclear. | "This is confusing", "I don't understand what this means" |
| F3 | Interaction / Control Issue | The tester has trouble interacting with a button, link, form, menu, filter, translation tool, or page component. | "Nothing happens when I click", "this button..." |
| F4 | Accessibility / Assistive Technology Issue | The tester mentions screen reader, zoom, headings, labels, keyboard access, readability, or accessibility tool behaviour. | "heading level", "screen reader", "zoom", "label" |
| F5 | Task Understanding / Expectation Mismatch | The tester's expectation of the task or page does not match what they see. | "I expected...", "I thought this would..." |
| F6 | Support / Trust / Safety Concern | The tester discusses trust, safety, sensitive help-seeking, emergency support, quick exit, helplines, or confidence in information. | "I would trust this", "quick exit", "support service" |
| F7 | No Clear Friction / Positive Feedback | The window contains neutral narration, successful task progress, reading content aloud, or positive feedback without a clear problem. | "This is clear", "this is helpful" |

## 5. Sentiment Labels

| Label | Definition |
|---|---|
| positive | The tester expresses approval, confidence, usefulness, or satisfaction. |
| neutral | The tester mainly describes, reads, or narrates without strong judgement. |
| negative | The tester expresses confusion, frustration, concern, dissatisfaction, or failure. |
| mixed | The tester gives both positive and negative feedback in the same window. |
| unclear | Sentiment cannot be confidently inferred. |

## 6. Narration Type

| Label | Definition |
|---|---|
| thinking_aloud | The tester explains thoughts, expectations, decisions, or reasoning. |
| reading_page | The tester mainly reads page content aloud. |
| navigation | The tester describes moving through pages, links, search results, or menus. |
| feedback_evaluation | The tester evaluates whether the page is clear, useful, accessible, or trustworthy. |
| task_response | The tester directly answers the task prompt or summarizes findings. |
| off_task | The content is not relevant to the assigned task. |
| unclear | The window is too ambiguous to classify. |

## 7. Severity

| Label | Definition |
|---|---|
| none | No friction is visible. |
| low | Minor hesitation or small improvement suggestion, but task still progresses. |
| medium | Noticeable confusion, repeated effort, unclear content, or interaction issue. |
| high | Serious blocker, safety concern, major accessibility barrier, or inability to complete the task. |

## 8. Annotation Fields

Recommended fields for manual annotation:

| Field | Meaning |
|---|---|
| window_id | ID from windows.csv |
| project | Project name |
| video_id | Tester-project ID |
| task_title | Task title from tasks.csv |
| text | Transcript window text |
| narration_type | One narration type label |
| at_context_present | yes / no / unclear |
| friction_type | F1-F7 |
| severity | none / low / medium / high |
| sentiment | positive / neutral / negative / mixed / unclear |
| confidence | low / medium / high |
| notes | Short explanation and evidence |

## 9. Annotation Rules

- Assign the label based on evidence in the window text, not assumptions about the tester.
- Use task description to interpret whether a comment is relevant friction.
- If multiple frictions appear, choose the dominant one and mention secondary issues in notes.
- If the tester is only reading page text, use `reading_page` and usually `F7` unless they also evaluate or express difficulty.
- If accessibility tools or page structure are explicitly discussed, consider `F4`.
- If safety, helplines, quick exit, or trust in support information is discussed, consider `F6`.
- Use `unclear` when the transcript is too ambiguous or lacks enough context.
