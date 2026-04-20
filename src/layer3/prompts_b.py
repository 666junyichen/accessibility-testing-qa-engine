"""Prompt templates for Step 5.1-B (video/session-level assessment).

字段对照
========

与 5.1-A 解耦：独立 prompt、独立输入粒度（整段 transcript，per video 一次）。
输出 3 字段，字段定义见 `schemas_b.py` 模块 docstring。

用途：6.1 fusion 时作为置信度 weight；6.2 Coaching 建议的主轴基底。

本模块不调用 LLM API，仅负责 prompt 文本装配。
"""

import json

NARRATION_QUALITY_VALUES = {
    "none": "Participant barely spoke during the session.",
    "sparse": "Only fragments or very short utterances.",
    "adequate": "Enough verbal content to support judgement.",
    "rich": "Sustained think-aloud or thorough verbal reactions.",
}

RECORDING_QUALITY_VALUES = {
    "poor": "Audio broken or large gaps; session barely usable for analysis.",
    "acceptable": "Usable with some defects (brief gaps, noise, minor clipping).",
    "good": "Clean and complete recording.",
}

COACHING_EVIDENCE_VALUES = {
    "none": "No clear moderator coaching detected.",
    "explicit": (
        "Moderator directly tells the participant the path, names the target "
        "button, or gives the answer rather than letting them discover it."
    ),
}

OUTPUT_SCHEMA = {
    "narration_quality": "none | sparse | adequate | rich",
    "recording_quality": "poor | acceptable | good",
    "coaching_evidence": "none | explicit",
}

OUTPUT_EXAMPLE = {
    "narration_quality": "adequate",
    "recording_quality": "good",
    "coaching_evidence": "none",
}

SYSTEM_PROMPT = """
You assess one full transcript from an accessibility and usability testing
session and assign three session-level quality signals.

This is NOT a friction-extraction task. Do not list issues. Do not score
severity. Produce exactly the three session-level fields defined below.

Use only the evidence in the transcript. Return only valid JSON. No markdown,
no commentary, no preamble.
"""

DEFINITIONS_PROMPT = """
Field definitions:

narration_quality — how useful the participant's verbalisation is for analysis:
- none: participant barely spoke during the session.
- sparse: only fragments or very short utterances.
- adequate: enough verbal content to support judgement.
- rich: sustained think-aloud or thorough verbal reactions.

recording_quality — whether the session is usable for downstream analysis
(this is about transcript/audio integrity, NOT production/film quality):
- poor: audio broken or large gaps; session barely usable.
- acceptable: usable with some defects (brief gaps, noise, minor clipping).
- good: clean and complete recording.

coaching_evidence — whether the moderator directly coached the participant
through tasks (binary scale for now):
- none: no clear moderator coaching detected. Moderator may still prompt
  neutrally (e.g. "what are you thinking?"), that is not coaching.
- explicit: moderator directly tells the participant where to click, names
  the target control, or gives the answer rather than letting the participant
  discover it.

Judging rules:
- Assess the entire session, not individual moments.
- Do not infer content beyond the transcript.
- For coaching_evidence, neutral think-aloud prompts ("what do you see?",
  "can you describe that?") are NOT coaching.
- If moderator is absent or silent, coaching_evidence is "none".
"""

USER_PROMPT_TEMPLATE = """
Assess the following test session transcript.

Project:
{project}

Video ID:
{video_id}

Task title:
{task_title}

Task instructions:
{task_instructions}

Full transcript:
{transcript}

Return JSON matching exactly this schema:
{output_schema}

Example output:
{output_example}
"""


def _json_block(data):
    """Return stable, readable JSON for embedding in prompt text."""
    return json.dumps(data, indent=2, ensure_ascii=True)


def build_user_prompt(
    video_id,
    project,
    transcript,
    task_title="Unknown task",
    task_instructions="No task instructions provided.",
):
    """Format one full transcript as the user prompt for Step 5.1-B."""
    return USER_PROMPT_TEMPLATE.format(
        project=project,
        video_id=video_id,
        task_title=task_title,
        task_instructions=task_instructions,
        transcript=transcript,
        output_schema=_json_block(OUTPUT_SCHEMA),
        output_example=_json_block(OUTPUT_EXAMPLE),
    ).strip()


def build_messages(
    video_id,
    project,
    transcript,
    task_title="Unknown task",
    task_instructions="No task instructions provided.",
):
    """Return chat-style messages for a Bedrock Anthropic client."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT.strip()},
        {"role": "user", "content": DEFINITIONS_PROMPT.strip()},
        {
            "role": "user",
            "content": build_user_prompt(
                video_id=video_id,
                project=project,
                transcript=transcript,
                task_title=task_title,
                task_instructions=task_instructions,
            ),
        },
    ]
