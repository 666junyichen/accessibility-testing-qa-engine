# R3 Case Studies

## 1. Purpose

This document records selected case studies for Step 8.3.

The case studies are based on manually reviewed transcript windows from:

`data/annotations/r3_manual_annotations_round1.csv`

The goal is to show how R3 semantic analysis can identify meaningful user experience patterns from transcript windows, including accessibility barriers, navigation problems, content clarity issues, and trust or safety concerns.

## 2. Case Selection Criteria

Cases were selected based on:

- clear evidence in the transcript window
- coverage across different friction types
- relevance to accessibility, navigation, content clarity, or trust/safety
- usefulness for final reporting and qualitative explanation
- potential to inform Layer 3 LLM classification and future recommendations

## 3. Selected Case Overview

| Case | Window ID | Project | Friction Type | Severity | Sentiment |
|---|---|---|---|---|---|
| Case 1 | `ghum_wa_w029` | Department of Premier and Cabinet WA | F4 Accessibility / Assistive Technology Issue | high | negative |
| Case 2 | `ramazankawish_wa_w075` | Department of Premier and Cabinet WA | F1 Navigation / Findability Issue | medium | negative |
| Case 3 | `Sharelinsonny_uq_w026` | The University of Queensland | F2 Content Clarity Issue | medium | negative |
| Case 4 | `tianarosie1_wa_w015` | Department of Premier and Cabinet WA | F6 Support / Trust / Safety Concern | medium | mixed |

## 4. Case Study 1: Screen Reader Cannot Access PDF Content

### Window

- Project: Department of Premier and Cabinet WA
- Window ID: `ghum_wa_w029`
- Friction Type: F4 Accessibility / Assistive Technology Issue
- Severity: high
- Sentiment: negative

### Evidence

> "I've got no access to the content in here at all"

### What Happened

The tester opened a PDF resource and attempted to access its content using a screen reader. The transcript shows repeated screen-reader output such as "page one containing empty group", suggesting that the PDF content was not properly exposed to assistive technology.

### Interpretation

This is a major accessibility barrier. The user is not simply confused by the page; they are unable to access the actual content of the resource. This means the resource may be unusable for screen-reader users unless an accessible version or OCR-readable structure is provided.

### Why This Case Matters

This case is important because it shows that content availability is not enough. A resource can exist on the website but still fail users if the format is inaccessible. For sensitive public service content, such as coercive control support, inaccessible PDFs may prevent users from receiving critical information.

### Possible Recommendation

Provide accessible HTML alternatives for PDF resources, ensure PDFs are tagged correctly, and test downloadable resources with screen readers.

## 5. Case Study 2: Feedback Page Findability Issue

### Window

- Project: Department of Premier and Cabinet WA
- Window ID: `ramazankawish_wa_w075`
- Friction Type: F1 Navigation / Findability Issue
- Severity: medium
- Sentiment: negative

### Evidence

> "I'm struggling to find the feedback page"

### What Happened

The tester tried to locate a feedback or complaints page but could not easily find the correct pathway. They searched around headings and page sections, expecting an option to provide feedback, but the expected route was not visible.

### Interpretation

This is a navigation and findability problem. The user has a clear goal, but the information architecture does not make the path obvious. This type of issue is especially important for government or support websites, where feedback and complaints pathways should be easy to locate.

### Why This Case Matters

A feedback pathway is part of service accountability. If users cannot find it, they may abandon the task or lose confidence in the service. In an NLP pipeline, this case would likely be detected through phrases such as "struggling to find", "feedback page", and repeated search/navigation behaviour.

### Possible Recommendation

Make feedback and complaints links more visible and consistently placed across relevant pages.

## 6. Case Study 3: Formal Legal Language Reduces Readability

### Window

- Project: The University of Queensland
- Window ID: `Sharelinsonny_uq_w026`
- Friction Type: F2 Content Clarity Issue
- Severity: medium
- Sentiment: negative

### Evidence

> "formal legal language, it's not very user-friendly"

### What Happened

The tester reviewed a section of text related to cookies, analytics, advertising, marketing activities, and pixel tracking. They described the content as long, formal, legalistic, and unlikely to be read in detail.

### Interpretation

This is a content clarity issue. The problem is not that the information is missing, but that the wording and presentation may be too dense for users to understand or engage with. The tester's response suggests that legal compliance text may reduce practical usability if it is not written or structured clearly.

### Why This Case Matters

This case shows how R3 semantic analysis can detect readability and plain-language issues from user narration. It also demonstrates why window text should be interpreted semantically rather than only through audio or interaction features.

### Possible Recommendation

Simplify legal or privacy-related explanations, provide summaries, and use layered disclosure so users can understand key points before reading detailed policy text.

## 7. Case Study 4: Sensitive Content Feels Informative But Emotionally Heavy

### Window

- Project: Department of Premier and Cabinet WA
- Window ID: `tianarosie1_wa_w015`
- Friction Type: F6 Support / Trust / Safety Concern
- Severity: medium
- Sentiment: mixed

### Evidence

> "very full-on to read all of the examples"

### What Happened

The tester read examples of coercive control and found them informative but emotionally intense. They noted that the examples helped confirm that the scenario described coercive control, but also described the material as "full-on" to read.

### Interpretation

This is not a simple usability failure. The content is doing important explanatory work, but it also carries emotional weight. This kind of window is important for R3 because it shows that sensitive support content should be evaluated not only for clarity, but also for tone, pacing, and emotional load.

### Why This Case Matters

Support and safety information must balance detail with care. Users may need concrete examples to recognise abuse, but too much intense content at once may feel overwhelming. This case is a strong candidate for qualitative reporting because it captures the nuance of sensitive public service communication.

### Possible Recommendation

Use clear content warnings, chunk sensitive examples into manageable sections, and provide visible support pathways near emotionally heavy content.

## 8. Cross-Case Themes

Across the selected cases, several themes appear:

- Accessibility barriers can completely block access to content, especially when PDFs are not screen-reader friendly.
- Navigation issues often appear through phrases like "I am struggling to find" or repeated attempts to locate a page.
- Content clarity issues often involve formal language, undefined terms, or dense information.
- Sensitive support content can be both useful and emotionally demanding.
- Positive or no-friction cases are useful as contrast examples, but the strongest case studies usually come from high-evidence friction windows.

## 9. Relationship To R3 NLP Work

These case studies support the R3 NLP semantic analysis tasks by showing how transcript windows can be interpreted beyond surface keywords.

They connect to:

- `docs/friction_taxonomy.md`
- `data/annotations/r3_manual_annotations_round1.csv`
- `docs/cluster_interpretation.md`
- `src/layer3/prompts.py`
- `docs/prompt_design.md`

The same examples can later be used to evaluate whether Layer 3 LLM classification correctly identifies friction type, severity, sentiment, narration type, and supporting evidence.

## 10. Current Limitations

These case studies are based on selected transcript windows rather than full video review.

Limitations:

- Some surrounding context may be missing because each case uses a 60-second window.
- Task descriptions have not yet been fully joined into the case table.
- The examples are manually selected and should not be treated as statistically representative.
- Final case studies may change after full clustering and LLM classification are available.
