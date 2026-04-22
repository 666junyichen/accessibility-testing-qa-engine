"""Prompt templates for Step 5.1-A (finding-level classification).

字段对照
========

本模块产出 Round 5 canonical schema 约定的 finding-level 输出（1:N）：
单个 transcript window 允许 0..N 条 findings。

字段定义见 `schemas_a.py` 模块 docstring。分类依据：
- F1-F7 / S1-S6 / E1-E5   源自 `client/s3_snapshot/06-friction-sentiment-framework.md`
- L1-L5 / signal_alignment / structural_amplification_note
                           源自 `client/s3_snapshot/07-friction-score-calibrator-prompt.md`

本模块不调用 LLM API，仅负责 prompt 文本装配。

R3 Co-write checklist（2026-04-22，R2 Nix 基于 round-1 Kappa 分析列出）
==========================================================================
4 处需要 R3 精修 prompt 正文。文件内 search `R3 TODO` 可快速跳转。

  Item 1. TAXONOMY_PROMPT > Severity 段 > S4 vs S5 边界
          当前 round-1 Kappa raw=0.34 / weighted=0.61，分歧集中在邻级。
          Reference: client/s3_snapshot/06-friction-sentiment-framework.md §Severity

  Item 2. TAXONOMY_PROMPT > Sentiment 段 > E2 vs E3 边界
          当前 round-1 Kappa=0.22（fair），Positive/Satisfied vs Neutral/Indifferent 混淆。
          Reference: client/s3_snapshot/06-friction-sentiment-framework.md §Sentiment

  Item 3. FEW_SHOT_EXAMPLES 常量（当前空 list）
          至少填 3 条 finding 例子，覆盖 signal_alignment 三档：
            - aligned：observed 和 stated 一致
              (推荐：今日 smoke test Sharelinsonny_wa_w000 F6/S2/E3/L4 ChatGPT 绕道)
            - conflicted：observed 和 stated 矛盾
              (从 r3_manual_annotations_round1_canonical.csv 里挑；没有就构造)
            - stated_missing：窗口内无口头表达
              (从 data/processed/layer1_flags.csv 里 SPARSE_NARRATION flag 窗口挑)

  Item 4. OUTPUT_EXAMPLE 可选扩充
          当前只 1 条 F6 样例，可增加 1-2 条覆盖 F1/F3/F7 等其他类型。
          非必做。

Canonical 纪律：R3 **不可** 新增/改名 schema 字段。所有修改只在 prompt 字符串内部
文字层面。Pydantic schema 真源是 `schemas_a.py`。

完成后 Nix 跑 `pytest tests/test_llm_classifier.py` 验证装配仍通过。
"""

import json

FRICTION_TYPES = {
    "F1": "Comprehension Friction",
    "F2": "Confidence Friction",
    "F3": "Accessibility Friction",
    "F4": "Unresponsive Interface",
    "F5": "Unexpected Behaviour",
    "F6": "Content Not Found",
    "F7": "Excessive Effort",
}

SEVERITY_S_LEVELS = {
    "S1": "Blocker (Project)",
    "S2": "Task Blocker",
    "S3": "Severe Friction",
    "S4": "High Friction",
    "S5": "Medium Friction",
    "S6": "Low Friction",
}

SENTIMENT_E_LABELS = {
    "E1": "Positive / Delighted",
    "E2": "Positive / Satisfied",
    "E3": "Neutral / Indifferent",
    "E4": "Negative / Frustrated",
    "E5": "Negative / Angry",
}

CALIBRATOR_SCORE_L_LEVELS = {
    "L1": "Minor friction; task completed without interruption",
    "L2": "Moderate friction; hesitation or non-optimal path; task completed",
    "L3": "Significant friction; struggle, multiple attempts, frustration; task completed",
    "L4": "Severe friction; near-abandonment or facilitator intervention",
    "L5": "Blocking; task not completed without product change",
}

SIGNAL_ALIGNMENT_VALUES = {
    "aligned": "Observed behaviour and stated experience agree",
    "conflicted": "Observed and stated disagree; score to the lower observed level",
    "stated_missing": "No verbal statement in this window; stated_signal is null",
}

OUTPUT_SCHEMA = {
    "findings": [
        {
            "finding": "one-sentence description of what happened",
            "observed_signal": "what the participant actually did",
            "stated_signal": "what the participant said (null if absent)",
            "signal_alignment": "aligned | conflicted | stated_missing",
            "friction_type": "F1 | F2 | F3 | F4 | F5 | F6 | F7",
            "severity_s": "S1 | S2 | S3 | S4 | S5 | S6",
            "sentiment_e": "E1 | E2 | E3 | E4 | E5 | null",
            "calibrator_score_l": "L1 | L2 | L3 | L4 | L5",
            "rationale": "2-3 sentences citing observed, stated, and gate definition",
            "structural_amplification_note": (
                "describe cohort-driven amplification (null if not applicable)"
            ),
        }
    ]
}

OUTPUT_EXAMPLE = {
    "findings": [
        {
            "finding": (
                "Participant could not locate the feedback entry point and spent "
                "over a minute searching menus before finding it."
            ),
            "observed_signal": (
                "Participant scrolled the page three times and opened two unrelated "
                "menus before locating the feedback link."
            ),
            "stated_signal": "I'm struggling to find the feedback page.",
            "signal_alignment": "aligned",
            "friction_type": "F6",
            "severity_s": "S4",
            "sentiment_e": "E4",
            "calibrator_score_l": "L3",
            "rationale": (
                "The participant could not locate the feedback entry point and said "
                "so explicitly. Observed struggle and stated frustration both point "
                "to high friction, matching the L3 gate (significant friction, task "
                "completed after multiple attempts)."
            ),
            "structural_amplification_note": None,
        }
    ]
}

SYSTEM_PROMPT = """
You analyse transcript windows from accessibility and usability testing sessions.

Your task is to extract zero or more friction findings from one transcript window,
using the See Me Please classification framework (v1.5) and the calibrator scoring
prompt (v4.0).

Use only the evidence in the task context and transcript window. Do not infer
unstated motivations, diagnoses, or personal attributes.

Return only valid JSON. No markdown, no commentary, no preamble.
"""

# -----------------------------------------------------------------
# [R3 TODO item 1]: Severity S4 vs S5 boundary refinement
#   Round-1 Kappa raw=0.34, weighted=0.61. Disagreement on adjacent levels.
#   In TAXONOMY_PROMPT below, expand S4 and S5 definitions with concrete signs:
#     S4 suggested: multiple failed attempts / detour / substantial extra time /
#                   workaround needed / >N min over expected / facilitator hint
#     S5 suggested: hesitation / single correction / mild confusion /
#                   non-optimal path but recovered quickly / no task risk
#   Reference: client/s3_snapshot/06-friction-sentiment-framework.md §Severity
#
# [R3 TODO item 2]: Sentiment E2 vs E3 boundary refinement
#   Round-1 Kappa=0.22 (fair). Disagreement on expressed mild positive vs neutral.
#   In TAXONOMY_PROMPT below, expand E2 and E3 definitions:
#     E2 suggested: any expressed mild positive valence ("ok good", "nice that
#                   worked", "perfect") — the cue is emotional valence, not magnitude
#     E3 suggested: pure description without emotional valence ("so I'll click
#                   this", "I'm reading the form") — matter-of-fact narration only
#   Reference: client/s3_snapshot/06-friction-sentiment-framework.md §Sentiment
# -----------------------------------------------------------------
TAXONOMY_PROMPT = """
Friction types (F1-F7):
- F1 Comprehension Friction: cannot understand content due to jargon, unclear
  language, complex terminology, or poor writing.
- F2 Confidence Friction: understands content but is uncertain what to do next,
  whether an action is correct, or where to go. Includes wayfinding uncertainty.
- F3 Accessibility Friction: content or functionality does not work correctly
  with assistive technology, keyboard, focus order, labels, headings, zoom, or
  other accessibility requirements.
- F4 Unresponsive Interface: user action produces no visible or timely response.
- F5 Unexpected Behaviour: interface responds in a way the user did not expect
  given the label, prior pattern, or design.
- F6 Content Not Found: user cannot locate information or a pathway needed to
  proceed.
- F7 Excessive Effort: task is possible but requires too many steps, clicks,
  repeated entries, time, scrolling, or cognitive effort.

Severity (S1-S6):
- S1 Blocker (Project): primary project outcome not achieved independently;
  facilitator intervention or task abandonment.
- S2 Task Blocker: overall outcome achieved but one component task completely
  blocked.
- S3 Severe Friction: significant component failure or barrier worked around
  or skipped.
- S4 High Friction: major difficulty requiring substantial effort, workaround,
  or repeated attempts.
- S5 Medium Friction: noticeable delay, hesitation, or confusion; completion
  not seriously threatened.
- S6 Low Friction: minor issue with negligible impact.

Sentiment (E1-E5):
- E1 Positive / Delighted: genuine delight, praise, or pleasant surprise.
- E2 Positive / Satisfied: things worked as expected with mild positive feeling.
- E3 Neutral / Indifferent: matter-of-fact narration without clear emotion.
- E4 Negative / Frustrated: annoyance, confusion, disappointment, irritation.
- E5 Negative / Angry: strong negative emotion, hostility, or intent to abandon.

Calibrator score (L1-L5):
- L1 Minor friction; task completed without interruption; confidence unaffected.
- L2 Moderate friction; hesitation or non-optimal path; task completed.
- L3 Significant friction; struggle, multiple attempts, frustration; task
  completed.
- L4 Severe friction; near-abandonment or facilitator intervention.
- L5 Blocking; task not completed without a product change.

Dual-signal reconciliation:
Every finding must be anchored in two signals:
1. observed_signal: what the participant actually did.
2. stated_signal: what the participant said.

If there is no verbal statement in the window, set stated_signal to null and
signal_alignment to "stated_missing". Do not fabricate stated_signal.

If observed and stated conflict (e.g. participant completed the task quickly
but said it was confusing), score to the lower observed behaviour level and set
signal_alignment to "conflicted". Do not average signals.

Structural amplification:
Certain cohorts (Blind/AT users, Neurodivergent, ESL) experience structurally
higher friction on particular interactions. If applicable, describe this in
structural_amplification_note. Do NOT upweight severity_s or calibrator_score_l for
this reason — scores reflect actual observed experience. Otherwise set to null.

Sentiment null discipline:
- If the participant makes any verbal expression in the window, sentiment_e must
  be one of E1-E5. Use E3 (Neutral/Indifferent) for matter-of-fact narration
  without clear emotion.
- Only set sentiment_e to null when the window contains no verbal expression at
  all (i.e. stated_signal is also null and signal_alignment is stated_missing).
- E3 and null are NOT interchangeable: E3 means neutral was expressed; null
  means no emotion evidence was available.

Extraction rules:
- Produce one finding per distinct friction event in the window. Multiple
  findings per window are allowed.
- If the window shows normal progress, reading aloud, successful completion,
  or positive feedback without any impediment, return an empty findings array.
- The "finding" field is a one-sentence description of what happened (not a
  quote). The transcript itself is the source of truth for verbatim evidence.
- Use task context to decide whether behaviour is relevant to the assigned task.
- If multiple issues appear inside one friction event, choose the dominant
  friction_type and mention secondary issues in rationale.
"""

# -----------------------------------------------------------------
# [R3 TODO item 3]: Few-shot examples for 5.1-A
#   Fill below list with 3 complete finding dicts (same 10-field shape as
#   OUTPUT_EXAMPLE), one per signal_alignment value. Examples are injected into
#   the user prompt automatically when non-empty.
#
#   Required coverage (one example each):
#     - signal_alignment="aligned"          (observed ≈ stated)
#     - signal_alignment="conflicted"       (observed != stated; score to lower)
#     - signal_alignment="stated_missing"   (stated_signal=null, sentiment_e=null)
#
#   If empty, prompt stays identical to round-1 骨架 (single OUTPUT_EXAMPLE).
#   Nix's smoke test (Sharelinsonny_wa_w000 → F6/S2/E3/L4) is a ready-to-use
#   `aligned` example template.
# -----------------------------------------------------------------
FEW_SHOT_EXAMPLES: list = []  # R3 TODO item 3: fill with 3 finding dicts

# -----------------------------------------------------------------
# [R3 TODO item 4, OPTIONAL]: Enrich OUTPUT_EXAMPLE above with more friction
# types (current only F6). Non-critical — few-shot coverage matters more.
# -----------------------------------------------------------------

USER_PROMPT_TEMPLATE = """
Extract friction findings from the following transcript window.

Project:
{project}

Video ID:
{video_id}

Window ID:
{window_id}

Task title:
{task_title}

Task instructions:
{task_instructions}

Transcript window:
{window_text}

Return JSON matching exactly this schema (top-level key is "findings", which
is an array of zero or more finding objects):
{output_schema}

Example output:
{output_example}
{few_shot_block}"""


def _json_block(data):
    """Return stable, readable JSON for embedding in prompt text."""
    return json.dumps(data, indent=2, ensure_ascii=True)


def _few_shot_block():
    """Return formatted few-shot block or empty string if list empty."""
    if not FEW_SHOT_EXAMPLES:
        return ""
    return "\nAdditional examples (one per signal_alignment value):\n" + _json_block(
        {"findings": FEW_SHOT_EXAMPLES}
    )


def build_user_prompt(
    window_id,
    project,
    video_id,
    window_text,
    task_title="Unknown task",
    task_instructions="No task instructions provided.",
):
    """Format one transcript window as the user prompt for Step 5.1-A."""
    return USER_PROMPT_TEMPLATE.format(
        window_id=window_id,
        project=project,
        video_id=video_id,
        task_title=task_title,
        task_instructions=task_instructions,
        window_text=window_text,
        output_schema=_json_block(OUTPUT_SCHEMA),
        output_example=_json_block(OUTPUT_EXAMPLE),
        few_shot_block=_few_shot_block(),
    ).strip()


def build_messages(
    window_id,
    project,
    video_id,
    window_text,
    task_title="Unknown task",
    task_instructions="No task instructions provided.",
):
    """Return chat-style messages for a Bedrock Anthropic client."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT.strip()},
        {"role": "user", "content": TAXONOMY_PROMPT.strip()},
        {
            "role": "user",
            "content": build_user_prompt(
                window_id=window_id,
                project=project,
                video_id=video_id,
                window_text=window_text,
                task_title=task_title,
                task_instructions=task_instructions,
            ),
        },
    ]
