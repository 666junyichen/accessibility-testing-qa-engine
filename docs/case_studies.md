# R3 Case Studies

## 1. Purpose

This document records selected case studies for Step 8.3.

The case studies are based on manually reviewed transcript windows from:

`data/annotations/r3_manual_annotations_round1.csv`

The goal is to show how R3 semantic analysis can identify meaningful user
experience patterns from transcript windows, including accessibility barriers,
missing or hidden content pathways, comprehension friction, confidence friction,
and excessive effort.

The friction labels follow:

`docs/friction_taxonomy.md`

## 2. Case Selection Criteria

Cases were selected based on:

- clear evidence in the transcript window
- coverage across different official friction types
- relevance to accessibility, missing information, comprehension, confidence, or effort
- usefulness for final reporting and qualitative explanation
- potential to inform Layer 3 LLM classification and future recommendations

## 3. Selected Case Overview

| Case | Window ID | Project | Friction Type | Severity ID | Severity | Sentiment ID | Sentiment |
|---|---|---|---|---|---|---|---|
| Case 1 | `ghum_wa_w029` | Department of Premier and Cabinet WA | F3 Accessibility Friction | S3 | high | E4 | negative |
| Case 2 | `ramazankawish_wa_w075` | Department of Premier and Cabinet WA | F6 Content Not Found | S5 | medium | E4 | negative |
| Case 3 | `Sharelinsonny_uq_w026` | The University of Queensland | F1 Comprehension Friction | S5 | medium | E4 | negative |
| Case 4 | `tianarosie1_wa_w015` | Department of Premier and Cabinet WA | F7 Excessive Effort | S5 | medium | E4 | mixed |

## 4. Case Study 1: Screen Reader Cannot Access PDF Content

### Window

- Project: Department of Premier and Cabinet WA
- Window ID: `ghum_wa_w029`
- Friction Type: F3 Accessibility Friction
- Severity: S3 Severe Friction / high
- Sentiment: E4 Negative / Frustrated

### Evidence

> "I've got no access to the content in here at all"

### What Happened

The tester opened a PDF resource and attempted to access its content using a
screen reader. The transcript shows repeated screen-reader output such as "page
one containing empty group", suggesting that the PDF content was not properly
exposed to assistive technology.

### Interpretation

This is a major accessibility barrier. The user is not simply confused by the
page; they are unable to access the actual content of the resource. Under the
client framework, this maps to F3 because the barrier is caused by assistive
technology compatibility and inaccessible document structure.

### Why This Case Matters

This case is important because content availability is not enough. A resource
can exist on the website but still fail users if the format is inaccessible. For
sensitive public service content, such as coercive control support, inaccessible
PDFs may prevent users from receiving critical information.

### Possible Recommendation

Provide accessible HTML alternatives for PDF resources, ensure PDFs are tagged
correctly, and test downloadable resources with screen readers.

## 5. Case Study 2: Feedback Pathway Cannot Be Found

### Window

- Project: Department of Premier and Cabinet WA
- Window ID: `ramazankawish_wa_w075`
- Friction Type: F6 Content Not Found
- Severity: S5 Medium Friction / medium
- Sentiment: E4 Negative / Frustrated

### Evidence

> "I'm struggling to find the feedback page"

### What Happened

The tester tried to locate a feedback or complaints page but could not easily
find the correct pathway. They searched around headings and page sections,
expecting an option to provide feedback, but the expected route was not visible.

### Interpretation

This is a content-not-found problem. The user has a clear goal, but the pathway
to the required information is hidden, missing, or placed somewhere unexpected.
Under the client framework, this maps to F6 rather than F2 because the main
barrier is locating a needed feedback pathway.

### Why This Case Matters

A feedback pathway is part of service accountability. If users cannot find it,
they may abandon the task or lose confidence in the service. In an NLP pipeline,
this case would likely be detected through phrases such as "struggling to find",
"feedback page", and repeated search/navigation behaviour.

### Possible Recommendation

Make feedback and complaints links more visible and consistently placed across
relevant pages.

## 6. Case Study 3: Formal Legal Language Reduces Readability

### Window

- Project: The University of Queensland
- Window ID: `Sharelinsonny_uq_w026`
- Friction Type: F1 Comprehension Friction
- Severity: S5 Medium Friction / medium
- Sentiment: E4 Negative / Frustrated

### Evidence

> "formal legal language, it's not very user-friendly"

### What Happened

The tester reviewed a section of text related to cookies, analytics,
advertising, marketing activities, and pixel tracking. They described the
content as long, formal, legalistic, and unlikely to be read in detail.

### Interpretation

This is comprehension friction. The problem is not that the information is
missing, but that the wording and presentation make the meaning difficult to
absorb. Under the client framework, this maps to F1 because unclear or complex
language reduces understanding.

### Why This Case Matters

This case shows how R3 semantic analysis can detect readability and
plain-language issues from user narration. It also demonstrates why window text
should be interpreted semantically rather than only through audio or interaction
features.

### Possible Recommendation

Simplify legal or privacy-related explanations, provide summaries, and use
layered disclosure so users can understand key points before reading detailed
policy text.

## 7. Case Study 4: Sensitive Content Creates High Cognitive Effort

### Window

- Project: Department of Premier and Cabinet WA
- Window ID: `tianarosie1_wa_w015`
- Friction Type: F7 Excessive Effort
- Severity: S5 Medium Friction / medium
- Sentiment: E4 Negative / Frustrated, with mixed overall sentiment

### Evidence

> "very full-on to read all of the examples"

### What Happened

The tester read examples of coercive control and found them informative but
emotionally intense. They noted that the examples helped confirm that the
scenario described coercive control, but also described the material as
"full-on" to read.

### Interpretation

This is not a simple content failure. The content is doing important explanatory
work, but it creates a high cognitive and emotional load. Under the client
framework, this is best treated as F7 because the issue is the amount of effort
required to process the information, rather than missing content or unclear
terminology.

### Why This Case Matters

Support and safety information must balance detail with care. Users may need
concrete examples to recognise abuse, but too much intense content at once may
feel overwhelming. This case is a strong candidate for qualitative reporting
because it captures the nuance of sensitive public service communication.

### Possible Recommendation

Use clear content warnings, chunk sensitive examples into manageable sections,
and provide visible support pathways near emotionally heavy content.

## 8. Cross-Case Themes

Across the selected cases, several themes appear:

- Accessibility barriers can completely block access to content, especially when PDFs are not screen-reader friendly.
- Missing or hidden pathways often appear through phrases like "I am struggling to find" or repeated attempts to locate a page.
- Comprehension friction often involves formal language, undefined terms, or dense information.
- Confidence friction appears when users understand the content but do not trust the pathway or feel unsure what will happen next.
- Excessive effort can be caused by repeated steps, added setup work, or heavy content load.
- Positive or no-friction cases are useful as contrast examples, but they should be labelled `none`, not F7.

## 9. Relationship To R3 NLP Work

These case studies support the R3 NLP semantic analysis tasks by showing how
transcript windows can be interpreted beyond surface keywords.

They connect to:

- `docs/friction_taxonomy.md`
- `data/annotations/r3_manual_annotations_round1.csv`
- `docs/cluster_interpretation.md`
- `src/layer3/prompts_a.py` / `prompts_b.py`, `src/layer3/schemas_a.py` / `schemas_b.py`
- `docs/prompt_design.md`

The same examples can later be used to evaluate whether Layer 3 LLM
classification correctly identifies friction type, severity, sentiment,
narration type, and supporting evidence.

## 10. Current Limitations

These case studies are based on selected transcript windows rather than full
video review.

Limitations:

- Some surrounding context may be missing because each case uses a 60-second window.
- The examples are manually selected and should not be treated as statistically representative.
- Final case studies may change after full clustering and LLM classification are available.
- Step 8.3 still needs full pipeline outputs from later project stages before final reporting.
