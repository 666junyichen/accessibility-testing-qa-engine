# Demo Script for Final Video

## Scope

- Target length: 13.5 to 14.5 minutes, leaving buffer under the 15-minute cap.
- Language: English-led narration with short Chinese bridges for emphasis.
- This version is repo-wide aligned: it reflects README, core pipeline code, evaluation docs, and current processed artifacts.
- Held-out Bupa results stay as placeholders unless the one-time held-out run is explicitly completed after Gate 1 and Gate 2.

## Run of show

| Segment | Time | Focus |
|---|---:|---|
| 1. Project framing | 1.5-2 min | problem, architecture, delivery scope |
| 2. Data and governance | 2-2.5 min | dev55, held-out, freeze discipline |
| 3. Pipeline walkthrough | 5-5.5 min | raw transcript to report, coaching, performance |
| 4. Evaluation and evidence | 3-3.5 min | kappa, ablation, cases, project differences |
| 5. Limitations and next steps | 1.5-2 min | current risks, what is validated, future path |

---

## 1. Project Framing

**Shot**

- Full-screen slides.
- Start with one title slide, then one system-overview slide.

**Voiceover**

“Hello everyone. This demo presents our CS20 pipeline for turning usability session recordings into structured, reviewable quality evidence. This is not a black-box scorer that directly replaces expert judgment. Instead, it is a decision-support pipeline that helps a reviewer move from raw session evidence to a traceable report that another reviewer can inspect, question, and reuse.

The system is built as a multi-step pipeline. We start from AWS Transcribe outputs, then parse transcripts, split them into 60-second windows, and derive preprocessing artifacts such as audio features and video metadata. On top of that, Layer 1 contributes rule-based quality flags, Layer 2 adds exploratory clustering context, and Layer 3 performs semantic classification using a canonical schema. Those signals are fused into a per-video Quality Report, which also includes coaching recommendations. Finally, a separate performance-tracking layer aggregates report outputs into per-submission and per-tester summaries using SMP-aligned score language, so the project can speak to both session-level evidence and cross-session patterns.

So today's 15 minutes are not just about showing a Streamlit page, but about showing a complete chain of evidence: raw transcript, structured windows, semantic findings, report output, and evaluation evidence. The main value of the project is traceability. Every major claim is anchored to a schema field, a generated artifact, and a documented rule. That is why our framing is decision support and depth over breadth: we would rather make a narrower but auditable system than claim a broad automated judgement that reviewers cannot inspect.”

**Demo actions**

- Title slide: project name and one-sentence aim.
- Architecture slide: `Transcribe -> preprocess -> L1/L2/L3 -> fusion -> coaching -> performance tracking -> Streamlit review`.
- Pause on “decision support” and “traceability”.

**Key figures / Screenshot location**

- Repo structure and processed-artifact positioning: `README.md:24-65`
- End-to-end data flow framing: `README.md:169-224`
- Canonical Layer 3 / SMP label language: `README.md:614-622`
- Fusion entry point: `src/pipeline/fusion.py:28-62`
- Performance tracking as separate layer: `README.md:795-859`

---

## 2. Data and Governance

**Shot**

- Slides plus one table screenshot from README or freeze docs.
- Optional split-screen with dev / held-out partition on the right.

**Voiceover**

“Before the live walkthrough, we need to be explicit about data scope and governance, because the project is deliberately narrower than ‘all files we could run’. Our current official development suite is dev55, built from three collated projects: AAMI or Suncorp, UQ, and DPC-WA. The raw development transcribe export contains 57 videos, but two transcription-failure edge cases are excluded from the official reporting scope, so the formal development set is 55.

At the same time, our semantic outputs are not arbitrary labels. They follow a canonical taxonomy: F1 to F7 friction types, S1 to S6 severity, E1 to E5 sentiment, and L1 to L5 calibrator score. That matters because the same vocabulary carries through prompt design, manual annotation, kappa evaluation, report JSON, and downstream tracking. In other words, this section is not only about dataset size; it is also about the classification language we have committed to.

The held-out target is Bupa, with 42 collated videos. But those numbers are not part of today’s evaluation claims unless the one-time held-out run has actually happened under freeze. The project uses a strict Gate 1 plus Gate 2 policy: prompt versions, schema, fusion behaviour, and R6 mapping all need to be frozen before held-out inference is valid. These are effectively our data-splitting and analysis constraints: human annotation stays inside dev, held-out must not feed back into design, and any post-held-out changes would invalidate the benchmark.

This governance rule matters for credibility. It prevents us from tuning on the benchmark we later want to claim as unseen. So in the demo, when we say a result is strong, we mean it is strong on the governed development split, with documented limits, not that it magically generalises everywhere. If held-out has not been triggered, the correct language is future work pending budget and freeze approval, not an implied result.”

**Demo actions**

- Show slide with project inventory: DPC-WA, Suncorp, UQ, Bupa, Brighton.
- Highlight `57 total generated`, `55 official dev`, `42 held-out target`.
- Show canonical label slide: `F1-F7`, `S1-S6`, `E1-E5`, `L1-L5`.
- Show one slide with Gate 1 / Gate 2 / freeze rule.

**Key figures / Screenshot location**

- Project coverage and split: `README.md:84-100`
- Transcribe coverage totals: `README.md:121-129`
- Canonical taxonomy and schema authority: `docs/l3_design.md:17-29`, `docs/l3_design.md:51-133`
- Dev55 scope and excluded edge cases: `docs/step8_1_dev55_scope.md:5-45`
- Held-out governance and “only once” rule: `docs/eval_freeze.md:9-18`, `docs/eval_freeze.md:26-34`, `docs/eval_freeze.md:69-87`

---

## 3. Pipeline Walkthrough

**Shot**

- Start on slides for one concise end-to-end pipeline map.
- Switch to terminal for artifact checkpoints.
- Switch to Streamlit for the main reviewer-facing demo.

**Voiceover**

“Now I’ll walk through the actual system flow from repo artifacts to the reviewer-facing report. In this section, I will explain the backend process and then the frontend presentation, so that the audience can see that this is not an isolated page.

We begin with transcript and preprocessing outputs. In the current repo state, the pipeline has 57 parsed transcripts, 26,191 segments, and 3,331 sixty-second windows. From there, preprocessing produces 876 audio-feature rows, and Layer 1 emits 278 rule flags. Layer 2 then builds the seven-dimensional feature matrix and cluster assignments. Importantly, Layer 2 is still exploratory: current diagnostics show the clusters are tester-dominated, so they are useful as context but not as final quality modes. That is why we surface Layer 2 as reviewer context rather than pretending it is already a stable cohort taxonomy.

Layer 3 is where the semantic classification happens. Step 5.1-A produces finding-level outputs using the canonical F, S, E, and L schema, while Step 5.1-B produces a video-level assessment of narration quality, recording quality, and coaching evidence. These are then fused into one Quality Report per video. The fusion logic combines L1, L2, L3 summaries, computes a final quality tier, and packages coaching recommendations into the same report object. So at this point the system has moved from low-level evidence to something a reviewer can actually read and use.

Let me show one concrete example in the Streamlit viewer: `Sharelinsonny_suncorp`. In the summary panel, we can immediately see the tester, project, tier, and number of findings. In the detailed report, we can inspect Layer 1, Layer 2, Layer 3, the overall assessment, and coaching recommendations. Here the report is poor, with 27 findings and task-blocking friction in the reasoning. The top findings are not vague summaries; they preserve specific windows where the participant could not locate financial hardship information and explicitly said they did not know how to find it. That is the key reviewer value of the single-video view: it lets us move from headline judgement back down to concrete evidence.

But the latest demo is not limited to one report. We can then switch to the Tester Trajectory view, choose one tester, and inspect the R6 score line across submissions, the persistent friction types that recur across sessions, and the metadata about direction and cross-check lanes. After that, we can switch again to Cohort Overview, where the interface summarises the full dev55 set with cohort KPIs, the R6 tier distribution, the per-project fusion breakdown, and the trajectory split. This matters because it shows the project at three scales: one session, one tester, and the full cohort.

So the complete delivery is not just a report viewer. It is a linked analytical chain from evidence to aggregation, with three reading levels: single-video inspection, tester-level trajectory, and cohort-level overview.”

**Demo actions**

- On slide: show end-to-end pipeline with artifact names.
- In terminal, briefly show or mention:
  - `python src/data/transcript_parser.py`
  - `python src/preprocessing/window_splitter.py`
  - `python src/layer1/rule_detector.py`
  - `python scripts/run_layer3_dev.py`
  - `python scripts/run_pipeline.py --all`
  - `python scripts/build_performance_tracking.py`
- Mention current checkpoint counts from repo outputs.
- Open Streamlit with `streamlit run app/streamlit_demo.py`.
- In sidebar, select `Sharelinsonny_suncorp`.
- Pause on summary metrics and reason.
- Scroll through `Layer 1 Summary`, `Layer 2 Summary`, `Layer 3 Findings`, `Layer 3 Assessment`, `Overall Assessment`, `Coaching Recommendations`.
- Switch sidebar `View` from `Single Video` to `Tester Trajectory`.
- Select one tester with multiple submissions and show the score line, persistent friction types, and cross-check / ordering metadata.
- Switch sidebar `View` again to `Cohort Overview`.
- Highlight dev55 KPIs, R6 per-submission tier distribution, per-project fusion breakdown, and trajectory-direction split.

**Key figures / Screenshot location**

- Reproduction counts: `README.md:1143-1144`, `README.md:1163-1164`, `README.md:1194`, `README.md:1217-1224`
- Layer 1 rules and thresholds: `docs/layer1_design.md:74-97`, `docs/layer1_design.md:113-125`
- Layer 2 tester-dominated caveat: `docs/cluster_interpretation.md:3-12`
- Layer 3 schema split and semantic lock: `docs/l3_design.md:31-50`, `docs/l3_design.md:135-191`, `docs/l3_design.md:193-225`
- Fusion behaviour: `src/pipeline/fusion.py:37-49`, `src/pipeline/fusion.py:128-173`, `src/pipeline/fusion.py:176-223`
- Orchestration path and summary generation: `scripts/run_pipeline.py:53-60`, `scripts/run_pipeline.py:178-227`, `scripts/run_pipeline.py:230-272`
- Streamlit interface and views: `app/streamlit_demo.py:1-15`, `app/streamlit_demo.py:140-156`, `app/streamlit_demo.py:248-317`, `app/streamlit_demo.py:479-636`, `app/streamlit_demo.py:643-742`
- `Sharelinsonny_suncorp` summary row: `data/processed/reports/_summary_dev55.csv:35`
- `Sharelinsonny_suncorp` findings and final tier: `data/processed/reports/dev55/Sharelinsonny_suncorp.json:20-50`, `data/processed/reports/dev55/Sharelinsonny_suncorp.json:53-82`, `data/processed/reports/dev55/Sharelinsonny_suncorp.json:139-143`
- Coaching engine design: `README.md:735-760`, `src/coaching/recommendation_engine.py:47-97`, `src/coaching/recommendation_engine.py:103-205`
- Performance tracking design and outputs: `README.md:795-859`, `docs/performance tracking.md:24-31`, `docs/performance tracking.md:89-149`, `docs/performance tracking.md:203-243`

---

## 4. Evaluation and Evidence

**Shot**

- Slides with one kappa slide, one ablation slide, and one case-study slide.
- Optional split-screen with `ghum_uq` case screenshot and one performance summary table.

**Voiceover**

“After the walkthrough, the obvious question is: how do we know the outputs are worth trusting? We will use four types of evidence to answer this question: kappa, project-stratified evaluation, ablation, and qualitative case studies.

First, the key gate is Layer 3 friction-type agreement. LLM V2 versus R8 reaches a Cohen’s kappa of 0.7407 on `friction_type`, which is substantial agreement and above the 0.5 acceptance gate. Weighted severity agreement is also substantial. So the core finding-level semantic layer is strong enough to support downstream reporting. At the same time, the evaluation also tells us where not to overclaim: LLM-generated `sentiment_e`, `recording_quality`, and `narration_quality` have known confidence caveats, especially the 5.1-B defaulting behaviour.

Second, project-stratified evaluation shows that the system is not surfacing the same pattern everywhere. UQ sessions concentrate more F4 and F5 authentication or form barriers, with higher S1 and S2 rates. DPC-WA sessions are more dominated by F6 content-not-found patterns. This result shows that the model does not simply output flat values, but interacts with different project task structures.

Third, the ablation study gives us a very clear systems story. Removing Layer 1 or Layer 2 causes zero tier changes on dev55. Removing Layer 3 collapses the decision logic. In other words, L3 is currently the binding signal, while L1 and L2 are mainly audit and context layers in the current fusion design.

Fourth, the case studies show what the metrics mean in real sessions. For example, `ghum_uq` has 93 findings and repeated authentication, search, and form barriers, including a Google Authenticator detour and a ‘Heading not found’ error. Other cases cover multilingual access, public-service support pathways, and recording-quality caveats. Finally, the performance-tracking outputs extend this evidence from one report to a portfolio view: 57 per-submission rows and 27 per-tester rows, with tier and trajectory distributions already computed. So we have both quantitative validation and qualitative interpretability.

[PLACEHOLDER if held-out runs] If the Bupa held-out evaluation is completed under freeze, this is where we would compare our held-out outputs against SMP-side reference signals and discuss whether the same schema, fusion logic, and score language remain credible without retuning.

[Fallback if held-out does not run] If held-out is not yet run, we stop our validated claims at dev55 and describe the Bupa comparison to SMP as future work pending budget approval and held-out freeze.”

**Demo actions**

- Show slide: `friction_type κ = 0.7407`, `severity weighted κ = 0.7603`.
- Show one slide summarising low-confidence fields: `sentiment_e`, `recording_quality`, `LLM-generated narration_quality`.
- Show ablation headline table.
- Show `ghum_uq` as the flagship case example.
- Show one final mini-table for per-submission / per-tester distribution.

**Key figures / Screenshot location**

- Evaluation architecture and dev / held-out roles: `docs/evaluation_design.md:23-36`
- Kappa table and confidence tiers: `docs/evaluation_design.md:53-71`, `docs/evaluation_design.md:79-117`
- Project-stratified summary and error patterns: `docs/evaluation_design.md:172-229`
- Kappa gate in README: `README.md:703-713`
- Ablation summary: `README.md:1054-1074`, `docs/evaluation_design.md:121-129`, `docs/ablation_study.md:78-100`
- Case-study overview: `README.md:1078-1083`, `docs/case_studies.md:35-43`
- `ghum_uq` case details: `docs/case_studies.md:45-94`, `data/processed/reports/dev55/ghum_uq.json:23-59`, `data/processed/reports/dev55/ghum_uq.json:62-123`
- Performance summary distributions: `README.md:849-858`
- Current CSV state:
  - `data/processed/performance/per_submission.csv` = 57 rows
  - `data/processed/performance/per_tester.csv` = 27 rows
  - tier distributions match `README.md:851-856`

---

## 5. Limitations and Next Steps

**Shot**

- Closing slides only.
- End with one “validated now / risky now / next step” slide.

**Voiceover**

“To close, I want to be very clear about the project’s current boundaries. 第一，Layer 3 is the strongest part of the current system, but it is also the main binding signal in fusion. That makes the system interpretable, but it also creates a single-point-of-failure risk if semantic classification drifts.

Second, Layer 2 should not be oversold. The current clustering outputs are tester-dominated, not natural quality modes. They are still useful as exploratory context, but not as a stable quality taxonomy. Third, some 5.1-B labels have known confidence issues: LLM-generated `recording_quality` and `narration_quality` should be treated cautiously, and `sentiment_e` is explicitly low-confidence for downstream LLM use. There is also a residual calibration caveat in the broader system: some fields are stable enough for reporting, while others still need prompt or downstream calibration before they can be treated as strong signals.

Fourth, the performance-tracking layer is useful, but still heuristic. Its weights are locked as v1, and the trajectory direction is an ordered proxy rather than a real time-series claim because true submission timestamps are not available yet. On the coaching side, the current engine is still template-based, with severity-aware extension as a first step rather than a full contextual recommendation system. A natural next extension is to connect richer finding-level evidence, stronger grounding, and more reviewer-friendly prioritisation into that coaching layer.

Finally, held-out generalisation is still a governed future step. If Bupa is run, it must happen once, under freeze, and without feeding back into design. Beyond that, the production path is relatively clear: stabilise the weaker labels, strengthen fallback logic around non-L3 evidence, improve coaching grounding, and package the current review surfaces into a more durable internal workflow.

So the final takeaway is this: the project already delivers a full evidence pipeline from transcript to report to reviewer-facing summary. What is validated today is the dev-set workflow and its traceability. What remains open is held-out generalisation, stronger fallback logic, coaching extension, and a more production-ready reviewer path.”

**Demo actions**

- Closing slide with three columns:
  - `Validated now`
  - `Known caveats`
  - `Next step`
- End on the repo-wide takeaway, not on the UI.

**Key figures / Screenshot location**

- Layer 2 tester-dominated warning: `docs/cluster_interpretation.md:3-12`
- Layer 3 confidence caveats: `docs/evaluation_design.md:79-101`, `docs/evaluation_design.md:211-229`, `docs/evaluation_design.md:232-245`
- L3 single-point-of-failure implication: `docs/ablation_study.md:78-100`
- Heuristic-v1 performance weights and ordered proxy caveat: `docs/performance tracking.md:128-149`, `docs/performance tracking.md:207-223`, `docs/performance tracking.md:257-273`
- Coaching extension directions: `README.md:790-793`, `docs/coaching_templates.md:294-330`
- Held-out governance and freeze status: `docs/eval_freeze.md:26-39`, `docs/eval_freeze.md:60-87`

---

## Backup notes

- If time is short, compress Segment 3 by summarising terminal checkpoints on one slide and spend more time in Streamlit.
- If time is slightly over, trim the performance-tracking paragraph in Segment 4 before trimming the core kappa or ablation story.
- If held-out still has not run on recording day, delete the held-out placeholder sentence entirely and keep only the future-work fallback.
