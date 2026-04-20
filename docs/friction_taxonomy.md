# R3 Friction Taxonomy

## 1. Purpose

This document defines the F1-F7 friction taxonomy used by R3 NLP semantic
analysis. It is based on the client source document:

`Friction & Sentiment Classification Framework.pdf`

Source document metadata:

- Title: Friction & Sentiment Classification Framework
- Type: Internal Reference Document
- Area: Research & Insights Methodology
- Version: 1.5

The taxonomy supports:

- Step 4.3 cluster interpretation
- Step 5.1 prompt design
- Step 5.3 manual annotation
- Step 5.4 inter-annotator agreement evaluation
- Step 8.3 case study selection

## 2. Source Framework Summary

The client framework separates tester experience into three related but distinct
classification dimensions:

| Dimension | What it captures | R3 use |
|---|---|---|
| Friction type | The nature of the impediment experienced by the user | F1-F7 label |
| Friction severity | How seriously the issue prevents task or project success | S1-S6 or simplified severity |
| Sentiment | How the participant felt about the experience | E1-E5 or simplified sentiment |

The framework defines friction as any impediment to a user achieving their goal
efficiently, effectively, and independently.

## 3. Unit Of Analysis

The R3 unit of analysis is one 60-second transcript window from:

`data/processed/windows.csv`

Each window should be interpreted with:

- `window_id`
- `project`
- `video_id`
- `task_title`
- `task_instructions`
- transcript `text`
- optional neighbouring transcript context

Task context comes from:

`data/raw/<project>/*-tasks.csv`

## 4. Client F1-F7 Friction Types

The F1-F7 labels below are the client source taxonomy. These should be treated
as the authoritative labels for Step 5.1 prompt design and Step 5.3 manual
annotation.

| Code | Friction Type | Definition | Example Signals |
|---|---|---|---|
| F1 | Comprehension Friction | User cannot understand the meaning of content due to jargon, unclear language, complex terminology, or poorly written text. | User does not know what a term means; legal or technical text is incomprehensible; error message has no plain-language explanation. |
| F2 | Confidence Friction | User understands the content but feels uncertain about what to do next, whether their action is correct, what will happen if they proceed, or where to find what they need. Includes wayfinding uncertainty and unclear site structure. | User hesitates at submit; user asks if card details are final; user does not know which menu contains settings; user is unsure where to navigate next. |
| F3 | Accessibility Friction | Content or functionality does not work correctly with the user's assistive technology, input method, or accessibility settings, or fails basic accessibility requirements. Often forces workarounds, external help, or abandonment. | Screen reader announces "clickable" with no context; focus jumps unexpectedly; custom component is not keyboard accessible; PDF cannot be read by assistive technology. |
| F4 | Unresponsive Interface | User takes an action but the interface does not respond as expected, responds slowly, or gives no feedback that anything happened. | Button click produces no visible change; form submits with no confirmation; page appears frozen; user clicks multiple times unsure if the first click registered. |
| F5 | Unexpected Behaviour | Interface responds in a way the user did not anticipate based on design, labels, or prior experience. | Next submits a form instead of advancing; save closes a modal without confirmation; back button loses entered data; option triggers immediate action without warning. |
| F6 | Content Not Found | User cannot locate information needed to make a decision or complete a task because it does not exist, is hidden, or is placed somewhere they would not think to look. | Return policy not visible during checkout; no password requirements until an error; shipping costs hidden until final step; contact information not on the site. |
| F7 | Excessive Effort | Task requires more steps, clicks, time, or cognitive effort than reasonably expected. The issue is not primarily comprehension or uncertainty; it is simply too much work to accomplish something straightforward. | Too many confirmation screens; excessive scrolling; simple task takes many clicks; user must re-enter information already provided. |

## 5. R3 Boundary Rules

These rules help annotators and prompts choose the dominant F-code when multiple
issues appear in the same transcript window.

| If the main issue is... | Use |
|---|---|
| The user does not understand wording, terminology, instructions, or content meaning | F1 |
| The user understands the words but is unsure what will happen, what to choose, or where to go next | F2 |
| The issue involves screen reader, keyboard, focus, headings, labels, PDF accessibility, zoom, or assistive technology compatibility | F3 |
| The user acts but the interface gives no response, slow response, or unclear feedback | F4 |
| The interface does something surprising or different from what the label/design implied | F5 |
| The user needs information that is missing, hidden, or placed somewhere unexpected | F6 |
| The task is possible but takes too many steps, clicks, repeated entries, or too much cognitive work | F7 |

When multiple friction types appear:

- Choose the dominant friction type that best explains the user's main barrier.
- Record secondary friction in notes if needed.
- Use task context to decide whether the issue is relevant to the assigned task.
- Do not infer personal attributes or unstated motivations.

## 6. Severity Framework

The client source framework uses S1-S6 severity levels. Severity is separate
from friction type: the same F-code can appear at any severity.

| ID | Severity | Definition | Example |
|---|---|---|---|
| S1 | Blocker (Project) | User could not independently achieve the primary project outcome. Task was abandoned or required facilitator intervention. | Blind user could not complete flight booking because the date picker was entirely inaccessible to screen readers. |
| S2 | Task Blocker | Participant achieved the overall outcome but was completely blocked for one task. The blocked task may have material consequences. | User booked the flight but could not perceive the confirmation email content and did not know their booking details. |
| S3 | Severe Friction | Significant component failure or barrier, even though the overall task was not abandoned. Something clearly broken or inaccessible was worked around or skipped. | User completed checkout but order summary was unreadable at their magnification level and they proceeded without verifying totals. |
| S4 | High Friction | Major difficulty requiring substantial effort, workaround, multiple failed attempts, extended time, or persistence. Would likely cause abandonment without persistence. | User eventually found "Contact Us" after searching multiple pages because it was buried in low-contrast footer text. |
| S5 | Medium Friction | Noticeable impediment causing delay, hesitation, or confusion. Completion was never in doubt but experience was degraded. | User paused at a proceed button, unsure whether it would submit or show a preview, and clicked tentatively. |
| S6 | Low Friction | Minor impediment with negligible impact. User noticed an issue but completed the task with minimal disruption. | User commented the font felt small but read it without zooming. |

### Simplified Severity For Current R3 Annotation

Some current R3 files use a simplified `severity` field:

| Simplified label | Source mapping |
|---|---|
| none | No observed friction |
| low | S6 |
| medium | S4-S5 |
| high | S1-S3 |

Future work should preserve the source `S1-S6` level where possible, especially
for Step 5.4 evaluation and Step 8.3 case study write-up.

## 7. Sentiment Framework

Sentiment captures how participants felt about their experience. This is
distinct from friction: a user may complete a low-friction task while still
feeling frustrated, or encounter friction while remaining patient.

| ID | Category | Sentiment | Meaning | Typical Expressions |
|---|---|---|---|---|
| E1 | Positive | Delighted | Participant expresses genuine delight, praise, or pleasant surprise. | "This is really well designed"; "That was much easier than I expected"; "I wish more sites worked like this." |
| E2 | Positive | Satisfied | Participant expresses contentment; things worked as expected with no complaints. | "That was fine"; "It worked well"; "No problems there." |
| E3 | Neutral | Indifferent | Participant expresses neither positive nor negative feeling; matter-of-fact. Excluded from aggregate sentiment calculations in the client framework. | "Okay, done"; "It works"; no emotional commentary. |
| E4 | Negative | Frustrated | Participant expresses annoyance, irritation, or disappointment. | "This is really frustrating"; "Why is this so complicated?"; "That was harder than it should be." |
| E5 | Negative | Angry | Participant expresses strong negative emotion, hostility, or intent to abandon or avoid. | "This is unacceptable"; "I would never use this again"; "They clearly do not care about their users." |

### Simplified Sentiment For Current R3 Annotation

Some current R3 files use a simplified `sentiment` field:

| Simplified label | Source mapping |
|---|---|
| positive | E1-E2 |
| neutral | E3 |
| negative | E4-E5 |
| mixed | Positive and negative reactions appear in the same window |
| unclear | Sentiment cannot be confidently inferred |

## 8. Narration Type

Narration type is an R3 helper dimension. It is not part of the client F1-F7
taxonomy, but it helps interpret transcript windows and design prompts.

| Label | Definition |
|---|---|
| thinking_aloud | Tester explains thoughts, expectations, decisions, or reasoning. |
| reading_page | Tester mainly reads page content aloud. |
| navigation | Tester describes moving through pages, links, search results, or menus. |
| feedback_evaluation | Tester evaluates whether the page is clear, useful, accessible, or trustworthy. |
| task_response | Tester directly answers the task prompt or summarizes findings. |
| off_task | Content is not relevant to the assigned task. |
| unclear | Window is too ambiguous to classify. |

## 9. Recommended Annotation Fields

Recommended fields for manual annotation:

| Field | Meaning |
|---|---|
| window_id | ID from `windows.csv` |
| project | Project name |
| video_id | Tester-project ID |
| task_title | Task title from `tasks.csv` |
| task_instructions | Task instructions from `tasks.csv` |
| text | Transcript window text |
| narration_type | R3 narration type |
| at_context_present | yes / no / unclear |
| friction_type | One F1-F7 source code, or `none` / `unclear` for non-friction cases |
| friction_label | Human-readable friction label |
| severity_id | Optional source severity ID S1-S6 |
| severity | Simplified severity label if required |
| sentiment_id | Optional source sentiment ID E1-E5 |
| sentiment | Simplified sentiment label if required |
| confidence | low / medium / high annotation confidence |
| primary_evidence | Short quote supporting the label |
| secondary_friction_type | Optional secondary F-code |
| notes | Short explanation and boundary decision |
| annotator | Annotator ID |

## 10. Relationship To Downstream Steps

- Step 5.1 should use this taxonomy as the authoritative F1-F7 prompt schema.
- Step 5.3 should use this taxonomy as the manual annotation guide.
- Step 5.4 should compare R3 and R8 labels using the same F1-F7 definitions.
- Step 8.3 should use these categories to select and explain case studies.

## 11. Current Status

Completed:

- Client source PDF identified and reviewed.
- F1-F7 friction types transcribed and adapted for R3 window-level analysis.
- S1-S6 severity framework documented.
- E1-E5 sentiment framework documented.
- R3 boundary rules and annotation fields documented.
- `src/layer3/prompts.py` aligned with the client F1-F7 labels.
- `docs/prompt_design.md` aligned with the client F1-F7, S1-S6, and E1-E5 framework.
- R3 round 1 manual annotation labels updated to use official client codes.

Pending:

- Review final wording with Nix/R8 before Step 5.1 prompt schema is frozen.
- Ask R8 to complete blind annotation using the same official taxonomy before Step 5.4 agreement evaluation.
