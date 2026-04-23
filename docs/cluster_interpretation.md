# R3 Cluster Interpretation Notes

> **WARNING Round-2 diagnostic (2026-04-22) - Boundary declaration**
>
> Round-1 KMeans clusters (commit `b23a5d6`, `final_k=3`) are **tester-dominated**, not natural quality modes:
> - Cluster 0: 97% `ghum` windows
> - Cluster 1: 96% `terryaflint17` windows
> - Cluster 2: mixed-tester remainder
>
> Diagnostic evidence in `data/processed/layer2_round2_*.csv` confirms tuning `k` / `eps` does not resolve tester dominance under the current 6-tester dev sample; principal axes encode tester identity (silence_ratio / narration_density / wpm are the most tester-specific features). This means semantic interpretation of the current clusters will reflect individual speaking styles more than window-level quality differences.
>
> **Implication for Step 4.3**: label these clusters as "exploratory, tester-dominated, interpretation provisional" rather than mapping them to canonical quality tiers. Re-interpret after round-3 (sample expansion + feature selection).

## 1. Purpose

This document records R3's initial semantic interpretation of transcript
windows. It supports Step 4.3 cluster interpretation and prepares the semantic
patterns that will later be used for Layer 2 cluster naming, Layer 3 prompt
design, manual annotation, and case studies.

At this stage, the repository does not yet contain final Layer 2 clustering
outputs. Therefore, this document is based on manual review of sampled
transcript windows from:

`data/annotations/r3_window_review_sample.csv`

The friction labels in this document now follow the client framework in:

`docs/friction_taxonomy.md`

## 2. Current Status

Layer 2 clustering result is not available yet.

Available inputs:

- `data/processed/windows.csv`
- `data/annotations/r3_window_review_sample.csv`
- `data/annotations/r3_manual_annotations_round1.csv`
- `docs/friction_taxonomy.md`

Current output:

- Initial semantic patterns from reviewed windows
- Official F1-F7 mapping for those patterns
- Candidate labels for future cluster interpretation

Important note:

The first review sample used earlier provisional labels. After reviewing the
client `Friction & Sentiment Classification Framework.pdf`, those labels were
re-mapped to the official client taxonomy. In particular, `F7` now means
`Excessive Effort`; it must not be used for no-friction or positive-only
windows.

## 3. Sample Label Overview

The reviewed sample contains 50 windows. It is not the final cluster output; it
is an exploratory sample used to identify semantic patterns before Layer 2
cluster results are available.

Official friction label distribution in the 50-window review sample:

| Friction Type | Count |
|---|---:|
| none No observed friction | 19 |
| F6 Content Not Found | 8 |
| F2 Confidence Friction | 7 |
| F1 Comprehension Friction | 5 |
| F7 Excessive Effort | 5 |
| F3 Accessibility Friction | 5 |
| F4 Unresponsive Interface | 1 |
| F5 Unexpected Behaviour | 0 |

The R3 manual annotation round selects 14 of these windows as a smaller
validation set for Step 5.3 and Step 5.4. That subset is intentionally broad
rather than statistically representative.

## 4. Observed Semantic Patterns

### 4.1 F6 Content Not Found

Some windows show testers trying to locate a specific page, feedback form,
online claim pathway, support option, or program information.

Common signs:

- The tester scans menus, headings, links, or search results.
- The tester uses phrases such as "I am looking for", "I can't find", "where
  is", or "I'm struggling to find".
- The tester repeats navigation attempts because the needed information or
  pathway is hidden, missing, or placed unexpectedly.

Representative examples:

- `gameoverdan_suncorp_w040`: repeated attempts to find online claim/contact
  options.
- `ramazankawish_wa_w075`: struggles to find the feedback page.
- `reececraigie_wa_w043`: scans for support categories such as men or
  Aboriginal adults.

Candidate cluster label:

`Content Not Found / Hidden Pathway`

### 4.2 F1 Comprehension Friction

Several windows show difficulty with language, terminology, explanation, or
meaning.

Common signs:

- The tester says something is confusing or not user-friendly.
- The tester asks what a term means.
- The tester suggests simpler wording, plain language, icons, or clearer
  explanation.
- Legal, insurance, government, or technical terms reduce understanding.

Representative examples:

- `Sharelinsonny_uq_w026`: formal legal language is not user-friendly.
- `oliviamitchell22_suncorp_w007`: does not understand "third party".
- `tharayil_wa_w024`: expects simpler explanations for low literacy users.

Candidate cluster label:

`Comprehension / Plain Language Friction`

### 4.3 F2 Confidence Friction

Some windows show that testers can understand the content but are uncertain
whether they are in the right place, making the right choice, or about what will
happen next.

Common signs:

- The tester hesitates or says they are not sure.
- The tester questions whether a result is trustworthy or relevant.
- The tester understands the words but does not feel confident proceeding.
- The tester expected information or fields to appear elsewhere.

Representative examples:

- `reneerussell99_uq_w009`: expected a required citizenship field to appear in a
  different place.
- `giuliaclemente26_uq_w004`: expresses low confidence when the site asks for
  downloads or input early.
- `margieflint_suncorp_w007`: questions whether comparison/search results are
  trustworthy.

Candidate cluster label:

`Confidence / Next-Step Uncertainty`

### 4.4 F3 Accessibility Friction

A group of windows explicitly mention screen readers, VoiceOver, headings,
focus, accessibility tools, or inaccessible PDF/resource content.

Common signs:

- The tester uses heading navigation.
- The tester says content is not accessible with a screen reader.
- The tester mentions VoiceOver or excessive content to listen to.
- The tester reports missing headings, labels, focus issues, inaccessible PDFs,
  or assistive technology barriers.

Representative examples:

- `ghum_wa_w029`: PDF content is not accessible.
- `ghum_wa_w065`: resource cannot be accessed with a screen reader.
- `marychaunguyen_suncorp_w011`: VoiceOver user finds the homepage
  information-heavy.

Candidate cluster label:

`Accessibility / Assistive Technology Barrier`

### 4.5 F4 Unresponsive Interface And F5 Unexpected Behaviour

Some interface problems are about system response rather than content meaning.
These should be separated from F1/F2/F6 during final cluster interpretation.

Use F4 when:

- The tester clicks or submits something and nothing visibly happens.
- The response is slow or gives no feedback.
- The tester repeats the action because they are unsure whether it registered.

Use F5 when:

- The interface does something surprising.
- A label or control behaves differently from what the tester expected.
- The system changes state, submits, closes, navigates, or loses data without a
  clear warning.

Representative examples from the reviewed sample were limited, so these
categories should be revisited once Layer 2 clusters and more windows are
available.

Candidate cluster labels:

`Unresponsive Interface`

`Unexpected Interface Behaviour`

### 4.6 F7 Excessive Effort

Some windows show that the task is technically possible, but the tester must do
more work than reasonably expected.

Common signs:

- Extra authentication or setup steps are required.
- The tester must repeatedly enter information or move through unnecessary
  steps.
- The tester describes the content or process as heavy, painful, or too much
  work.
- The core issue is effort, not lack of understanding or missing information.

Representative examples:

- `giuliaclemente26_uq_w050`: Google Authenticator setup is described as
  painful.
- `tianarosie1_wa_w015`: sensitive examples are useful but full-on to read.

Candidate cluster label:

`Excessive Effort / High Cognitive Load`

### 4.7 none No Observed Friction

Some windows contain normal task progress, reading page content, or positive
evaluation without a clear friction event. These should not be labelled as F7.

Common signs:

- The tester says the page is clear, useful, simple, accessible, or helpful.
- The tester is mainly reading task instructions or page content.
- The tester successfully completes or explains a step without an impediment.

Representative examples:

- `oliviamitchell22_suncorp_w017`: all-encompassing page is great.
- `thanoptions_uq_w008`: UQ site is nice, simple, and clear.
- `fjone7_uq_w066`: file upload dialogue is fairly accessible.

Candidate cluster label:

`No Observed Friction / Positive Progress`

## 5. Implications For Future Cluster Interpretation

When Layer 2 clustering outputs become available, each cluster should be
interpreted using:

- cluster size
- top keywords
- representative window texts
- dominant official friction type
- dominant severity and sentiment
- dominant narration type
- examples from sampled windows

A future cluster interpretation table should include:

| cluster_id | top_keywords | representative_window_ids | dominant_friction_type | semantic_label | notes |
|---|---|---|---|---|---|

## 6. Limitations

This is an initial qualitative interpretation based on sampled transcript
windows. It does not yet represent the final clustering result.

Limitations:

- No `cluster_id` is available yet.
- Some windows contain multiple issues, but only one dominant friction type was
  assigned.
- Task context was manually inferred for the round 1 annotation set.
- Some transcript text may contain AWS Transcribe errors.
- The full 50-window exploratory sample still needs final review after the team
  confirms the official taxonomy migration.

## 7. Next Steps

- Wait for Layer 2 clustering output.
- Map each cluster to one official semantic label.
- Use this interpretation to support `src/layer3/prompts_a.py` / `prompts_b.py`.
- Reuse strong examples for `docs/prompt_design.md` and future
  `docs/case_studies.md`.
- Ask R8 to annotate the blind round 1 file using the same taxonomy so Step 5.4
  agreement can be calculated.
