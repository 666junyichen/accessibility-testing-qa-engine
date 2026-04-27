# R3 Case Studies

## 1. Purpose

This document records Step 8.3 qualitative case studies for the W9 progress
report. The previous version used selected manual annotation windows. This
version uses the full MVP pipeline outputs so that each case is grounded in a
complete video-level report.

Primary evidence sources:

- `data/processed/reports/_summary.csv`
- `data/processed/reports/*.json`
- `data/processed/layer3_findings_filtered.csv`
- `data/processed/layer3_video_assessments.csv`

Each case combines Layer 1 signals, Layer 2 coverage, Layer 3 findings, session
quality assessment, and generated coaching recommendations where available.

## 2. Selection Criteria

The selected cases cover different evidence patterns needed for the progress
report:

- high-volume Layer 3 findings with task-blocking friction
- public-service content pathways where users could not find actionable support
- multilingual or ESL access barriers
- Layer 1 duration or audio anomalies that affect confidence in interpretation
- poor recording quality cases where the pipeline correctly limits claims

The goal is not to choose statistically representative videos. The goal is to
provide clear, report-ready examples showing how R3 semantic analysis turns
pipeline outputs into human-readable usability findings.

## 3. Selected Video Overview

| Case | Video ID | Project | Why Selected | L3 Findings | Top Severity | Narration | Recording | Tier |
|---|---|---|---|---:|---|---|---|---|
| 1 | `ghum_uq` | The University of Queensland | richest finding set and task-blocking authentication/search friction | 93 | S1 | rich | acceptable | poor |
| 2 | `margieflint_wa` | Department of Premier and Cabinet WA | missing support pathways in a sensitive public-service journey | 79 | S2 | rich | acceptable | poor |
| 3 | `giuliaclemente26_wa` | Department of Premier and Cabinet WA | acceptable-tier multilingual access case with many medium findings | 91 | S3 | rich | acceptable | acceptable |
| 4 | `jenniferparry7_uq` | The University of Queensland | Layer 1 duration/audio anomaly plus severe account access barrier | 9 | S1 | rich | acceptable | poor |
| 5 | `thanoptions_wa` | Department of Premier and Cabinet WA | poor recording and sparse narration with zero reliable findings | 0 | none | sparse | poor | poor |

## 4. Case 1: UQ Authentication Flow Blocks Course Discovery

### Source

- Report: `data/processed/reports/ghum_uq.json`
- Summary row: `ghum_uq`
- Windows: 85
- Layer 2 coverage: 1.0
- Layer 3 findings: 93
- `quality_tier` + reason: `poor` - task-blocking friction: S1/S2 present
- L1 flags: none (`total_flags=0`)
- L3 summary: friction distribution `F1=17, F2=24, F3=23, F4=9,
  F5=12, F6=3, F7=5`; severity distribution `S1=1, S2=3, S3=6,
  S4=43, S5=40`; sentiment distribution `E2=1, E3=25, E4=60,
  none=7`; calibrator distribution `L2=40, L3=48, L4=4, L5=1`.
- Coaching recommendation: improve recording quality
  (`recording_quality=acceptable`, priority 2).

### Key Pipeline Signals

The report contains 93 findings across all seven friction types. The dominant
high-risk pattern is not a single wording issue; the participant repeatedly
encounters account, authentication, search, and form barriers while trying to
discover postgraduate course information.

Top findings include:

- `ghum_uq_w077`: F5/S1/L5, trapped in a Google Authenticator setup flow that
  was unrelated to the assigned postgraduate course discovery task.
- `ghum_uq_w027`: F6/S2/L4, Business Law search with Master's Coursework filter
  returned no matching programs.
- `ghum_uq_w058`: F4/S2/L4, a "Heading not found" error appeared during an
  application form submission attempt.
- `ghum_uq_w075`: F2/S2/L4, uncertainty around a required authenticator code
  blocked progression.

### Interpretation

This case shows why video-level aggregation matters. A single window might look
like one authentication issue, one search issue, or one form issue. At the full
session level, the pattern is a broader navigation and account-access breakdown
that repeatedly prevents the participant from returning to the intended course
discovery path.

The case is useful for the progress report because it demonstrates how R3
semantic classification captures both behaviour and stated signals. It also
shows why the MVP tier is poor even though narration is rich and recording is
acceptable: the limiting factor is task-blocking friction, not session quality.

### Reporting Value

Use this case to illustrate high-confidence Layer 3 analysis. The participant
verbalised enough for rich semantic interpretation, and the pipeline identified
severe repeated friction rather than treating each event as isolated noise.

## 5. Case 2: WA Support Pathway Is Not Actionable Enough

### Source

- Report: `data/processed/reports/margieflint_wa.json`
- Summary row: `margieflint_wa`
- Windows: 75
- Layer 3 findings: 79
- `quality_tier` + reason: `poor` - task-blocking friction: S1/S2 present
- L1 flags: none (`total_flags=0`)
- L3 summary: friction distribution `F1=24, F2=20, F3=3, F4=1,
  F5=1, F6=24, F7=6`; severity distribution `S2=1, S3=8,
  S4=12, S5=55, S6=3`; sentiment distribution `E3=19, E4=60`;
  calibrator distribution `L1=9, L2=50, L3=18, L4=2`.
- Coaching recommendation: improve recording quality
  (`recording_quality=acceptable`, priority 2).

### Key Pipeline Signals

This report is dominated by content-not-found and pathway problems in a
sensitive public-service context. The user is trying to locate support options,
but the available pathway repeatedly fails to become actionable.

Top findings include:

- `margieflint_wa_w007`: F6/S2/L4, support options could not be pursued after a
  "not available" error.
- `margieflint_wa_w013`: F6/S3/L4, the participant could not find actionable
  written information and considered using a contact form as a workaround.
- `margieflint_wa_w011`: F6/S3/L3, the participant questioned whether the page
  provided enough information for someone needing help.
- `margieflint_wa_w011`: F6/S3/L3, the participant used a service directory as
  a secondary route after the primary pathway was insufficient.

### Interpretation

The friction is not just that information is hard to read. The participant is
looking for a concrete next step, and the product experience pushes them toward
secondary or workaround routes. In the R3 taxonomy this is primarily F6 Content
Not Found, because the needed support pathway is missing, hidden, unavailable,
or insufficiently signposted.

This case is valuable because it connects semantic findings to service risk. In
a safety or support journey, unclear pathways can prevent users from reaching
help even when the website contains related content somewhere else.

### Reporting Value

Use this case to explain why the MVP pipeline should report pathway-level
failures, not only page-level readability. It is a strong qualitative example
for recommendations around visible support routes, fallback contact options,
and clearer next-action design.

## 6. Case 3: Multilingual Access Requires External Workarounds

### Source

- Report: `data/processed/reports/giuliaclemente26_wa.json`
- Summary row: `giuliaclemente26_wa`
- Windows: 71
- Layer 3 findings: 91
- `quality_tier` + reason: `acceptable` - multiple medium-severity findings
- L1 flags: none (`total_flags=0`)
- L3 summary: friction distribution `F1=21, F2=24, F3=7, F4=11,
  F5=9, F6=6, F7=13`; severity distribution `S3=2, S4=6,
  S5=71, S6=12`; sentiment distribution `E3=36, E4=55`;
  calibrator distribution `L1=21, L2=62, L3=8`.
- Coaching recommendation: improve recording quality
  (`recording_quality=acceptable`, priority 2).

### Key Pipeline Signals

This case has many findings but remains acceptable-tier because the dominant
severity pattern is medium rather than task-blocking. It is useful as a contrast
case: the experience is not a complete failure, but the participant still faces
repeated multilingual access costs.

Top findings include:

- `giuliaclemente26_wa_w013`: F7/S3/L3, a PDF required a multi-step external
  translation workaround involving download and upload to an AI tool.
- `giuliaclemente26_wa_w019`: F6/S3/L3, video content was only available in
  English, creating a barrier for non-English speakers.
- `giuliaclemente26_wa_w017`: F4/S4/L3, the Italian language option did not
  function and the Google Translate extension also failed.
- `giuliaclemente26_wa_w028`: F4/S4/L3, translation controls disappeared while
  navigating internal page links, requiring repeated retranslation.

### Interpretation

The pattern is structural rather than incidental. The participant can often
continue, but only by adding external translation steps or repeatedly repairing
the interface state. This makes F7 Excessive Effort and F4 Unresponsive
Interface especially important in the interpretation.

Because the case is acceptable-tier, it helps avoid a progress report that only
shows failures. It demonstrates that the MVP can distinguish between severe
blocking sessions and usable sessions that still contain repeated accessibility
or ESL-related friction.

### Reporting Value

Use this case to support recommendations about multilingual content strategy:
translated pages, translated media alternatives, stable language controls, and
fewer external workarounds for essential support information.

## 7. Case 4: Layer 1 Flags Increase Caution Around Account Access Findings

### Source

- Report: `data/processed/reports/jenniferparry7_uq.json`
- Summary row: `jenniferparry7_uq`
- Windows: 23
- Layer 1 flags: 10 total, including `DURATION_ANOMALY` and `LOW_AUDIO_QUALITY`
- Layer 2 coverage: 1.0
- Layer 3 findings: 9
- `quality_tier` + reason: `poor` - task-blocking friction: S1/S2 present
- L1 flags: `DURATION_ANOMALY=1, LOW_AUDIO_QUALITY=9`
- L3 summary: friction distribution `F1=1, F2=4, F3=1, F4=2,
  F6=1`; severity distribution `S1=1, S5=8`; sentiment
  distribution `E3=2, E4=6, E5=1`; calibrator distribution
  `L2=8, L5=1`.
- Coaching recommendation: improve recording quality
  (`recording_quality=acceptable`, priority 2).

### Key Pipeline Signals

This case has fewer Layer 3 findings than the high-volume cases, but the Layer 1
signals make it important for reporting. The session includes duration and audio
quality flags, so interpretation should be cautious even when the top findings
are severe.

Top findings include:

- `jenniferparry7_uq_w022`: F4/S1/L5, a registration or account access barrier
  prevented the participant from proceeding.
- `jenniferparry7_uq_w005`: F2/S5/L2, a mandatory residential status prompt
  interrupted navigation.
- `jenniferparry7_uq_w007`: F2/S5/L2, the participant was uncertain about which
  search entry point to use.
- `jenniferparry7_uq_w013`: F6/S5/L2, the participant expected cost and fees
  information on the current page but could not locate it.

### Interpretation

This case shows how the report should combine signal layers. Layer 3 identifies
a severe account access barrier, while Layer 1 warns that parts of the session
may have reliability limits. The correct reporting stance is not to discard the
case, but to describe the severe barrier while noting the confidence caveat.

### Reporting Value

Use this case to explain why the MVP includes both semantic findings and quality
signals. It is a good example for the progress report section on reliability:
the pipeline can surface an important usability issue while preserving caution
about the evidence quality.

## 8. Case 5: Poor Recording Produces a Low-Confidence Zero-Finding Session

### Source

- Report: `data/processed/reports/thanoptions_wa.json`
- Summary row: `thanoptions_wa`
- Windows: 2
- Layer 3 findings: 0
- Narration quality: sparse
- Recording quality: poor
- `quality_tier` + reason: `poor` - recording unusable
- L1 flags: none (`total_flags=0`)
- L3 summary: no finding-level friction, severity, sentiment, or calibrator
  scores were produced because the session evidence is too weak for reliable
  downstream interpretation.
- Coaching recommendations: recording quality limits reliable downstream
  analysis (`recording_quality=poor`, priority 5); increase participant
  verbalisation (`narration_quality=sparse`, priority 3).

### Key Pipeline Signals

This is a negative case rather than a friction-rich case. The session has zero
Layer 3 findings, but the pipeline does not treat that as strong evidence of a
smooth experience. Instead, the video-level assessment marks narration as sparse
and recording quality as poor.

The generated recommendations are:

- Recording quality limits reliable downstream analysis.
- Increase participant verbalisation.

### Interpretation

This case is important because a zero-finding output can mean two very different
things: either the user had little friction, or the evidence is not strong enough
to support detailed interpretation. Here, the second explanation is more
appropriate. Poor recording and sparse narration make the session low-confidence
evidence.

### Reporting Value

Use this case to show that the MVP does not over-claim. The pipeline can flag
analysis risk and recommend recording/narration improvements rather than
pretending that a lack of findings means a successful user experience.

## 9. Retained Window-Level Evidence From Previous Draft

The previous Step 8.3 draft contained four window-level cases. They are no
longer the primary unit of analysis because W9 reporting now needs video-level
MVP outputs from `data/processed/reports/`. They are retained here as
qualitative evidence snippets that support the same themes identified in the
video-level cases.

| Window ID | Project | Previous Focus | Evidence Use In Current Draft |
|---|---|---|---|
| `ghum_wa_w029` | Department of Premier and Cabinet WA | Screen reader could not access PDF content | Supports the accessibility-barrier theme behind F3 findings and document-format recommendations. |
| `ramazankawish_wa_w075` | Department of Premier and Cabinet WA | Feedback pathway could not be found | Supports the missing-pathway theme used in the WA support pathway case. |
| `Sharelinsonny_uq_w026` | The University of Queensland | Formal legal language reduced readability | Supports the comprehension-friction theme for UQ content and policy pages. |
| `tianarosie1_wa_w015` | Department of Premier and Cabinet WA | Sensitive examples created high cognitive effort | Supports the excessive-effort theme for safety/support content. |

Retained evidence notes:

- `ghum_wa_w029`: the participant said "I've got no access to the content in
  here at all" while encountering PDF content that was not exposed usefully to a
  screen reader.
- `ramazankawish_wa_w075`: the participant said "I'm struggling to find the
  feedback page", making it a concise evidence point for F6 Content Not Found.
- `Sharelinsonny_uq_w026`: the participant described policy wording as "formal
  legal language" and "not very user-friendly", which remains useful evidence
  for F1 Comprehension Friction.
- `tianarosie1_wa_w015`: the participant described coercive-control examples as
  "very full-on to read all of the examples", supporting F7 Excessive Effort in
  sensitive public-service content.

## 10. Cross-Case Themes

Across the five selected cases, several themes are visible:

- Severe task blockers often come from account, authentication, or form flows
  rather than from page content alone.
- Public-service support journeys need visible and actionable next steps, not
  just related information.
- ESL and multilingual access issues often appear as external workarounds,
  repeated translation steps, or English-only media.
- Layer 1 quality flags are useful guardrails for deciding how confidently to
  interpret Layer 3 findings.
- Zero findings must be interpreted alongside narration and recording quality.

## 11. Relationship To R3 Work

These case studies connect R3 semantic analysis to the W9 progress report. They
show how the R3 layer contributes:

- friction type interpretation (`F1`-`F7`)
- severity and calibrator scoring (`S1`-`S6`, `L1`-`L5`)
- signal alignment between observed and stated evidence
- session-level narration and recording quality assessment
- qualitative explanation for coaching and reporting

The selected cases can be used directly in the progress report as qualitative
examples after team review.

## 12. Limitations

These case studies are based on generated MVP pipeline reports, not a fresh
manual re-watch of each full video. They should therefore be treated as
report-ready draft evidence rather than final client-facing claims.

Remaining caveats:

- Top findings are generated by the Layer 3 LLM pipeline and may need spot-check
  validation before final submission.
- Layer 2 clusters remain exploratory and tester-dominated.
- Recording-poor sessions should not be used to make strong product conclusions.
- The final report should align case wording with R8 Kappa findings once Step
  5.4 is complete.
