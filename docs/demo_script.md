# Demo Script for Final Video

## Scope

- This rewrite is aligned to GitHub `origin/main` commit `0e2854b` and uses only remote-tracked repository files as evidence.
- Target runtime: `13.5-14.5` minutes, leaving buffer under the `15` minute cap.
- Live demo path: `Single Video -> Tester Trajectory -> Cohort Overview`.

## Run of Show

| Segment | Time | Focus | Tool |
|---|---:|---|---|
| 1. Project framing | 1.5-2 min | decision-support framing, end-to-end architecture | slides |
| 2. Data and governance | 2.5-3 min | dev55 scope, canonical taxonomy, evidence discipline | slides |
| 3. Pipeline walkthrough | 4.5-5 min | one video from artifacts to report to UI | terminal + Streamlit |
| 4. Evaluation and evidence | 3-3.5 min | kappa, project patterns, ablation, case study, R6 evidence | slides |
| 5. Limitations and next steps | 1.5-2 min | confidence caveats, coaching extension, production path | slides |

---

## 1. Project Framing

**Shot**

- Full-screen slides.
- One title slide, then one architecture slide.

**Voiceover**

“Hello everyone. This project is a decision-support pipeline for usability session review. Our goal is not to replace expert judgement with a black-box score. Our goal is to turn messy session evidence into a structured, auditable report that another reviewer can inspect, challenge, and reuse.

The pipeline starts from transcript-based evidence and then moves through several layers of interpretation. We preprocess session data into windows and supporting artifacts, apply Layer 1 rule-based quality flags, add Layer 2 clustering context, and run Layer 3 semantic classification using a canonical usability taxonomy. Those signals are fused into a per-video Quality Report, and then extended into a reviewer-facing Streamlit application and an R6 performance-tracking layer that aggregates evidence across submissions.

What matters most in this framing is traceability. Every major claim in the demo comes from a stored artifact: a CSV, a JSON report, a schema field, or a documented fusion rule. That is why our framing is decision support and depth over breadth. We would rather show a narrower system whose reasoning can be inspected than claim a broad automated judgement that nobody can verify.

This is also why the Streamlit app should be understood as a review surface, not a live inference system. The app is a read-only consumer of generated reports, filtered findings, and performance tables. So the story we want the audience to see today is not just that a front end exists, but that the front end sits on top of a complete evidence chain from session data to semantic findings to reviewer-facing summaries.

In the next few minutes, I will show that chain at three levels: one session, one tester across submissions, and the full official dev55 cohort.”

**Demo actions**

- Show title slide with the one-sentence aim.
- Show architecture slide with `preprocess -> L1 -> L2 -> L3 -> fusion -> coaching -> performance tracking -> Streamlit`.
- Pause on the phrases `decision support`, `traceability`, and `read-only review surface`.

**Key figures / screenshot location**

- Streamlit app scope and read-only inputs: `app/streamlit_demo.py:1-15`
- Fusion entrypoint and output object: `src/pipeline/fusion.py:28-67`
- Performance tracking outputs and role: `scripts/build_performance_tracking.py:1-20`

---

## 2. Data and Governance

**Shot**

- Slides plus one scope slide for the official development set.
- One taxonomy slide for F/S/E/L.

**Voiceover**

“Before showing the interface, we need to be precise about data scope and governance, because the project deliberately narrows what counts as official evidence.

Our official development set is the old three-project collated suite: Suncorp or AAMI, UQ, and DPC-WA. The repository documentation is explicit that the raw collated total is 57 videos, but two transcript-failure edge cases are excluded from formal reporting, which gives us the official dev55 scope. After exclusion, the project counts are 20 Suncorp, 19 UQ, and 16 DPC-WA.

The second governance point is that our labels are not ad hoc. Layer 3 uses a canonical taxonomy with four independent dimensions: friction type F1 to F7, severity S1 to S6, sentiment E1 to E5, and calibrator score L1 to L5. These dimensions are defined centrally and then reused across prompts, annotations, report JSON, evaluation, and downstream tracking. That consistency is important because it means the same vocabulary appears in both model outputs and evaluation claims.

This matters for credibility. We are deliberately keeping the evidence base narrow and auditable. In other words, the claims in this video are dev-set claims: they are supported by repository artifacts, reproducible from the current pipeline, and bounded by the official dev55 scope.”

**Demo actions**

- Show a scope slide with `57 generated -> 55 official dev`.
- Show project counts after exclusion.
- Show one taxonomy slide with `F1-F7`, `S1-S6`, `E1-E5`, `L1-L5`.
- Show one evidence-discipline slide with `official scope only`.

**Key figures / screenshot location**

- Official dev definition and annotation rule: `docs/eval_freeze.md:9-18`
- Dev55 exclusions and final project counts: `docs/step8_1_dev55_scope.md:18-44`
- Canonical Layer 3 dimensions and definitions: `docs/l3_design.md:51-132`
- Scope discipline and dev-only reporting basis: `docs/step8_1_dev55_scope.md:32-55`

---

## 3. Pipeline Walkthrough

**Shot**

- Start on one architecture slide.
- Switch to terminal for artifact path checkpoints.
- Switch to Streamlit for the main demo.

**Voiceover**

“Now I’ll show the pipeline in the order the repository actually implements it.

The orchestration script loads five processed inputs: `windows.csv`, `layer1_flags.csv`, `layer2_cluster_assignments.csv`, `layer3_findings_filtered.csv`, and `layer3_video_assessments.csv`. For each video, it filters those tables, validates the Layer 3 video assessment, and then passes everything into `fuse_video()`. Fusion produces one `QualityReport` JSON with Layer 1, Layer 2, Layer 3 findings, the video-level assessment, overall quality, and coaching recommendations.

The overall quality rule is intentionally simple and auditable. If recording quality is poor, the report is poor. If any S1 or S2 finding is present, the report is poor. If there are at least five findings, or if explicit moderator coaching appears, or if narration is sparse, the report becomes acceptable. Only sessions with no major concerns stay good, and even then a duration anomaly can cap the session back to acceptable. This is important for the demo because we can explain the report outcome directly from the stored fields, rather than from opaque model internals.

For the live walkthrough, I’ll use `Sharelinsonny_suncorp`. In the summary CSV, this report has 81 windows, 27 findings, top severity S2, rich narration, acceptable recording, and a final tier of poor. In the report JSON, the two top blockers are both F6 content-not-found moments: the participant explicitly says they do not know how to find the financial hardship information they need. So when the app renders this report as poor, we can trace that back to concrete evidence, not just a headline label.

The Streamlit app then turns these stored artifacts into three reading levels. In `Single Video`, we see the hero summary, findings, coaching, and layer detail tabs. In `Tester Trajectory`, we zoom out to the same tester across three projects. For `Sharelinsonny`, the aggregate score is 61.7, the direction is declining under the current proxy ordering, and the persistent friction types are F1, F2, and F6. Finally, `Cohort Overview` lifts the same evidence to the dev55 cohort: 55 official videos, 27 testers, R6 post-cap tier distribution, per-project fusion tiers, and trajectory direction split.

So the live product story is no longer just ‘open one report’. The current demo is a linked reviewer workflow across one submission, one tester, and one cohort.”

**Demo actions**

- In terminal, show the orchestrator inputs and output path.
- Briefly show `scripts/run_pipeline.py` and `src/pipeline/fusion.py` line ranges in the editor or terminal.
- Launch `streamlit run app/streamlit_demo.py`.
- In `Single Video`, select `Sharelinsonny_suncorp`.
- Pause on hero stats, tier reasoning, and the `Overview`, `Findings`, `Coaching`, and `Layer detail` tabs.
- In findings, pause on the two S2 F6 findings.
- Switch to `Tester Trajectory` and show the `Sharelinsonny` row.
- Switch to `Cohort Overview` and highlight official cohort totals and the summary charts.

**Key figures / screenshot location**

- Orchestrator inputs: `scripts/run_pipeline.py:53-60`
- Per-video run path and summary generation: `scripts/run_pipeline.py:230-318`
- Fusion summary assembly: `src/pipeline/fusion.py:37-67`
- Overall tier logic: `src/pipeline/fusion.py:181-228`
- Streamlit tabs and three views: `app/streamlit_demo.py:304-316`, `app/streamlit_demo.py:479-742`
- `Sharelinsonny_suncorp` summary row: `data/processed/reports/_summary_dev55.csv:35`
- `Sharelinsonny_suncorp` report evidence: `data/processed/reports/dev55/Sharelinsonny_suncorp.json:20-203`
- `Sharelinsonny_suncorp` R6 score row: `data/processed/performance/per_submission.csv:3`
- `Sharelinsonny` trajectory row: `data/processed/performance/per_tester.csv:2`

---

## 4. Evaluation and Evidence

**Shot**

- Slides only.
- One kappa slide, one ablation slide, one case-study slide, one R6 evidence slide.

**Voiceover**

“After the walkthrough, the next question is whether these outputs deserve to be trusted. Our answer uses four kinds of evidence: inter-rater agreement, project-stratified interpretation, ablation, and qualitative case studies.

First, the strongest result is finding-level agreement. On the 14-window evaluation sample, `friction_type` reaches a Cohen’s kappa of 0.7407 for LLM V2 versus R8, and weighted `severity_s` reaches 0.7603. Those are the core reasons Layer 3 finding-level outputs are strong enough to support downstream reporting. At the same time, the evaluation design document is equally clear about what not to overclaim: `sentiment_e` is low confidence, `recording_quality` is low confidence, and the LLM defaults to `rich` narration and `acceptable` recording too often in the 5.1-B path.

Second, project-stratified evaluation shows that the system is not producing one flat pattern everywhere. UQ sessions concentrate more F4 and F5 account, authentication, and form barriers, with higher S1 and S2 rates. DPC-WA sessions are more dominated by F6 content-not-found patterns. This helps us argue that the pipeline is sensitive to different task structures rather than emitting generic summaries.

Third, the ablation result is decisive. Removing Layer 1 changes zero tiers. Removing Layer 2 changes zero tiers. Removing Layer 3 collapses all 55 official dev videos to `good`. That tells a very honest systems story: the final quality tier is currently L3-dependent, while L1 and L2 are contextual and audit layers in the present fusion design.

Fourth, the case studies make the metrics concrete. The clearest high-risk example is `ghum_uq`, which has 93 findings, one S1, three S2s, and repeated account, authentication, search, and submission barriers. The top examples include a Google Authenticator detour, a ‘no matching programs’ result, and a ‘Heading not found’ submission error. This is the kind of session where the repository’s structured evidence and the human narrative clearly point in the same direction.

Finally, R6 extends that evidence from single reports into two portfolio tables: 57 per-submission rows and 27 per-tester rows. That means the project now supports not only one-report inspection, but also cross-submission score language and tester-level trajectory summaries.

So the validated claims in this demo stop at the official development evidence base, which is exactly the right scope for an auditable final walkthrough.”

**Demo actions**

- Show the kappa table slide with `0.7407` and `0.7603`.
- Show one caveat slide listing low-confidence fields.
- Show the ablation table with `Full / No-L1 / No-L2 / No-L3`.
- Show the `ghum_uq` case-study slide with the three example findings.
- End with one slide showing the existence of `per_submission.csv` and `per_tester.csv`.

**Key figures / screenshot location**

- Kappa tables and lower-confidence rules: `docs/evaluation_design.md:53-101`
- LLM error patterns and project-stratified summary: `docs/evaluation_design.md:200-228`
- Ablation distributions and implications: `docs/ablation_study.md:41-100`
- Case-study overview and `ghum_uq` narrative: `docs/case_studies.md:35-98`
- `ghum_uq` report evidence: `data/processed/reports/dev55/ghum_uq.json:23-212`
- Performance tracking output scope: `docs/performance tracking.md:12-15`

---

## 5. Limitations and Next Steps

**Shot**

- Closing slides only.
- Final slide with `Validated now / Known caveats / Next step`.

**Voiceover**

“To close, I want to be explicit about the project’s current boundaries.

First, Layer 2 should not be oversold. The current cluster diagnostics show tester-dominated clusters rather than natural quality modes, so Layer 2 is useful as exploratory context but not yet as a stable quality taxonomy. Second, the 5.1-B path still has important confidence caveats. The evaluation docs show that LLM-generated `recording_quality` and `narration_quality` have default-bias problems, and `sentiment_e` remains low confidence. So the safe claim is that the strongest validated layer is finding-level semantic classification, not every video-level label equally.

Third, the ablation study shows that the present fusion outcome is highly dependent on Layer 3. That makes the system interpretable, but it also means a future production path needs stronger fallback behaviour than we have today. Fourth, the R6 layer is intentionally labelled as heuristic v1. Its 0.50 / 0.35 / 0.15 weights are locked for now, and its direction label is an ordered proxy because the dev set still lacks reliable submission timestamps. So the trajectory view is useful, but it should not be narrated as a true longitudinal performance claim.

On the coaching side, the current engine is more capable than the original session-only template version: it already supports severity-aware and friction-aggregation recommendations. But it is still template-based. The natural extension path is timestamp-aware grounding, denser-session compression, adaptive tone, and more contextual LLM-assisted coaching for cases where static templates are too blunt.

The broader next step is production hardening: improve weak-label calibration, add more robust fallback logic around non-L3 evidence, deepen coaching grounding, and package the current reviewer workflow into a more durable operational review tool.

So the final takeaway is simple: what is validated now is a traceable dev-set review pipeline. What remains open is stronger fallback logic, richer coaching, and production hardening.”

**Demo actions**

- Show a closing three-column slide: `Validated now`, `Known caveats`, `Next step`.
- End on the system boundary statement, not on a UI screenshot.

**Key figures / screenshot location**

- Tester-dominated Layer 2 warning: `docs/cluster_interpretation.md:3-12`
- 5.1-B and sentiment confidence caveats: `docs/evaluation_design.md:79-101`, `docs/evaluation_design.md:215-228`
- L3 dependence in ablation: `docs/ablation_study.md:78-100`
- R6 heuristic-v1 weights and ordered-proxy caveat: `docs/performance tracking.md:128-149`, `docs/performance tracking.md:203-223`, `docs/performance tracking.md:269-272`
- Coaching engine extensions and future direction: `docs/coaching_templates.md:294-355`, `docs/coaching_templates.md:394-404`

---

## Backup Notes

- If time is tight, compress Segment 2 and keep Segment 3 intact; the three-view Streamlit story is the part that is most different from the old script.
- If the live app feels too dense, keep `Sharelinsonny_suncorp` for the UI and move `ghum_uq` fully into slides.
- Keep the whole story inside the official `dev55` evidence base and avoid introducing side topics that are not shown in the demo.
