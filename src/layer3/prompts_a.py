"""Prompt templates for Step 5.1-A (finding-level classification).

字段对照
========

本模块产出 Round 5 canonical schema 约定的 finding-level 输出（1:N）：
单个 transcript window 允许 0..N 条 findings。

字段定义见 `schemas_a.py` 模块 docstring。分类依据：
- F1-F7 / S1-S6 / E1-E5   源自 `client/s3_snapshot/06-friction-sentiment-framework.md`
- L1-L5 / signal_alignment / structural_amplification_note
                           源自 `client/s3_snapshot/07-friction-score-calibrator-prompt.md`

本模块不调用 LLM API，仅负责 prompt 文本装配。调用方见 `src/layer3/client.py`（待建）。
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
"""


def _json_block(data):
    """Return stable, readable JSON for embedding in prompt text."""
    return json.dumps(data, indent=2, ensure_ascii=True)


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
