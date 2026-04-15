# R3 Cluster Interpretation Notes

## 1. Purpose

This document records R3's initial semantic interpretation of transcript windows.
It supports Step 4.3 cluster interpretation and prepares the semantic labels that will later be used for Layer 2 cluster naming, Layer 3 prompt design, manual annotation, and case studies.

At this stage, the repository does not yet contain Layer 2 clustering outputs. Therefore, this document is based on a manual review of sampled transcript windows from `data/annotations/r3_window_review_sample.csv`.

## 2. Current Status

Layer 2 clustering result is not available yet.

Available inputs:
- `data/processed/windows.csv`
- `data/annotations/r3_window_review_sample.csv`
- `docs/friction_taxonomy.md`

Current output:
- Initial semantic patterns from 50 sampled windows
- Candidate labels for future cluster interpretation

## 3. Sample Overview

The reviewed sample contains 50 transcript windows.

Initial friction type distribution:

| Friction Type | Count |
|---|---:|
| F7 No Clear Friction / Positive Feedback | 15 |
| F2 Content Clarity Issue | 9 |
| F1 Navigation / Findability Issue | 9 |
| F6 Support / Trust / Safety Concern | 6 |
| F3 Interaction / Control Issue | 5 |
| F4 Accessibility / Assistive Technology Issue | 5 |
| F5 Task Understanding / Expectation Mismatch | 1 |

Sentiment distribution:

| Sentiment | Count |
|---|---:|
| mixed | 16 |
| negative | 13 |
| neutral | 12 |
| positive | 9 |

Narration type distribution:

| Narration Type | Count |
|---|---:|
| feedback_evaluation | 18 |
| navigation | 15 |
| thinking_aloud | 7 |
| task_response | 6 |
| reading_page | 4 |

## 4. Observed Semantic Patterns

### 4.1 Navigation / Findability Issues

Some windows show testers trying to locate a specific page, support option, feedback form, online claim pathway, or program information.

Common signs:
- The tester scans menus, headings, links, or search results.
- The tester uses phrases such as "I am looking for", "I can't find", "where is", or "I'm struggling to find".
- The tester moves between pages or repeats navigation attempts.

Representative examples:
- `gameoverdan_suncorp_w040`: repeated attempts to find online claim/contact options.
- `ramazankawish_wa_w075`: struggles to find the feedback page.
- `reececraigie_wa_w043`: scans for support categories such as men or Aboriginal adults.

Candidate cluster label:
`Navigation / Findability Issue`

### 4.2 Content Clarity Issues

Several windows show difficulty with language, information structure, terminology, or the amount of text.

Common signs:
- The tester says something is confusing or not user-friendly.
- The tester asks what a term means.
- The tester suggests simpler language, icons, headings, or better information hierarchy.
- The tester identifies missing information.

Representative examples:
- `Sharelinsonny_uq_w026`: formal legal language is not user-friendly.
- `oliviamitchell22_suncorp_w007`: does not understand "third party".
- `tharayil_wa_w024`: expects simpler explanations for low literacy users.

Candidate cluster label:
`Content Clarity / Plain Language Issue`

### 4.3 Interaction / Control Issues

Some windows show problems using forms, media, authentication, or interface controls.

Common signs:
- The tester cannot operate a feature.
- A video does not play.
- A form validation issue interrupts progress.
- Authentication or account setup creates extra burden.

Representative examples:
- `thanoptions_suncorp_w029`: video is not playing.
- `mgblackwell2001_suncorp_w012`: asks how to work the current interaction.
- `giuliaclemente26_uq_w050`: Google Authenticator setup is described as painful.

Candidate cluster label:
`Interaction / Control Issue`

### 4.4 Accessibility / Assistive Technology Issues

A group of windows explicitly mention screen readers, VoiceOver, headings, focus, accessibility tools, or inaccessible PDF/resource content.

Common signs:
- The tester uses heading navigation.
- The tester says content is not accessible with a screen reader.
- The tester mentions VoiceOver or a lot of content to listen to.
- The tester reports missing headings or focus issues.

Representative examples:
- `ghum_wa_w029`: PDF content is not accessible.
- `ghum_wa_w065`: resource cannot be accessed with a screen reader.
- `marychaunguyen_suncorp_w011`: VoiceOver user finds the homepage information-heavy.

Candidate cluster label:
`Accessibility / Assistive Technology Barrier`

### 4.5 Support, Trust, and Safety Concerns

Some windows are not simple usability problems. They involve sensitive support-seeking, trust in services, emergency information, safety resources, or emotionally heavy content.

Common signs:
- The tester discusses helplines, support services, emergency contacts, or quick exit.
- The tester evaluates whether the source feels trustworthy.
- The tester reacts to sensitive family/domestic violence content.
- The tester considers whether resources could help someone in a real situation.

Representative examples:
- `reececraigie_wa_w012`: positive reaction to shareable coercive control resources.
- `tianarosie1_wa_w015`: content is informative but full-on to read.
- `margieflint_suncorp_w007`: questions whether comparison/search results are trustworthy.

Candidate cluster label:
`Support / Trust / Safety Concern`

### 4.6 No Clear Friction / Positive Feedback

A significant number of windows contain normal task progress, reading page content, or positive evaluation without a clear friction event.

Common signs:
- The tester says the page is clear, useful, simple, or helpful.
- The tester is mainly reading task instructions or page content.
- The tester successfully completes or explains a step.

Representative examples:
- `oliviamitchell22_suncorp_w017`: all-encompassing page is great.
- `thanoptions_uq_w008`: UQ site is nice, simple, and clear.
- `fjone7_uq_w066`: file upload dialogue is fairly accessible.

Candidate cluster label:
`No Clear Friction / Positive Feedback`

## 5. Implications for Future Cluster Interpretation

When Layer 2 clustering outputs become available, each cluster should be interpreted using:

- top keywords
- representative window texts
- dominant friction type
- dominant sentiment
- dominant narration type
- examples from sampled windows

A future cluster interpretation table should include:

| cluster_id | top_keywords | representative_window_ids | dominant_friction_type | semantic_label | notes |
|---|---|---|---|---|---|

## 6. Limitations

This is an initial qualitative interpretation based on 50 randomly sampled windows.
It does not yet represent the final clustering result.

Limitations:
- No `cluster_id` is available yet.
- Some windows contain multiple issues, but only one dominant friction type was assigned.
- Task context was not fully joined into the sample file yet.
- Some transcript text may contain AWS Transcribe errors.

## 7. Next Steps

- Add task title and task instruction context to annotation samples.
- Wait for Layer 2 clustering output.
- Map each cluster to one semantic label.
- Use this interpretation to support `src/layer3/prompts.py`.
- Reuse strong examples for `docs/prompt_design.md` and future `docs/case_studies.md`.
