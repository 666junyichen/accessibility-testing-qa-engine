"""Prompt templates for Step 5.1-B (video/session-level assessment).

Step 5.1-B is decoupled from 5.1-A: it uses a separate prompt, runs once per
full video transcript, and returns the three fields defined in `schemas_b.py`.

The outputs are used as confidence weights in Step 6.1 fusion and as the main
session-quality basis for Step 6.2 coaching recommendations.

This module does not call an LLM API; it only assembles prompt text.

Prompt design anchors from the 2026-04-22 round-1 Kappa review are retained
near the relevant prompt text. Search for `DESIGN NOTE` to find them.

Item 5. DEFINITIONS_PROMPT > recording_quality boundary
        Round-1 Kappa was 0.00, so the prompt explicitly separates recording
        completeness / analysis usability from production-level audio quality.

Item 6. FEW_SHOT_EXAMPLES_B
        Future examples should cover one rich/good/none ideal think-aloud
        session and one sparse/acceptable/explicit moderated session.

Canonical discipline: schema fields are locked. In particular,
`coaching_evidence` remains the binary enum `none | explicit`. The Pydantic
source of truth is `schemas_b.py`.
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

# -----------------------------------------------------------------
# [DESIGN NOTE item 5]: recording_quality boundary refinement
#   Round-1 Kappa=0.00 → R3 and R8 disagree or labels collapsed to single value.
#   In DEFINITIONS_PROMPT below, expand poor/acceptable/good with concrete
#   audio-integrity signs (NOT production/video quality):
#     poor suggested: long silences breaking comprehension / transcript gaps
#                     >30s / sustained noise obscuring speech / truncated session
#     acceptable suggested: brief gaps <10s / mild background noise / occasional
#                           clipping but all task-relevant speech understandable
#     good suggested: clean audio throughout / minimal gaps / speech consistently
#                     clear / no analysis-impeding defects
#   Emphasise: this is about usability of the transcript for downstream LLM
#   analysis, not about whether the recording "looks professional".
# -----------------------------------------------------------------
DEFINITIONS_PROMPT = """
Field definitions:

narration_quality — how useful the participant's verbalisation is for analysis:
- none: participant barely spoke during the session.
- sparse: only fragments or very short utterances.
- adequate: enough verbal content to support judgement.
- rich: sustained think-aloud or thorough verbal reactions.

recording_quality — whether the session is usable for downstream analysis
(this is about transcript/audio integrity, NOT production/film quality):
- poor: recording/transcript defects prevent reliable analysis. Use poor when
  long silences or transcript gaps over 30 seconds break comprehension,
  sustained background noise or microphone clipping obscures task-relevant
  speech, or the session is truncated/missing important task sections.
- acceptable: usable for analysis despite limited defects. Use acceptable for
  brief gaps under about 10 seconds, mild background noise, or occasional
  clipping when all task-relevant speech and participant intent remain
  understandable.
- good: clean, complete, and consistently understandable recording. Use good
  when speech is clear throughout, gaps are minimal or irrelevant, and there
  are no audio/transcript defects that impede downstream LLM analysis.

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

# -----------------------------------------------------------------
# [DESIGN NOTE item 6]: Few-shot examples for 5.1-B
#   The list below preserves two complete VideoAssessment dicts (3-field shape:
#   narration_quality / recording_quality / coaching_evidence).
#
#   Suggested coverage:
#     - Example A: rich + good + none (ideal think-aloud session)
#     - Example B: sparse + acceptable + explicit (moderator-guided session)
#
#   These examples keep the video-level prompt stable while documenting
#   expected output shape for the current schema.
# -----------------------------------------------------------------
FEW_SHOT_EXAMPLES_B: list = [
    {
        "narration_quality": "rich",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    {
        "narration_quality": "sparse",
        "recording_quality": "acceptable",
        "coaching_evidence": "explicit",
    },
]


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
{few_shot_block}"""


def _json_block(data):
    """Return stable, readable JSON for embedding in prompt text."""
    return json.dumps(data, indent=2, ensure_ascii=True)


def _few_shot_block():
    """Return formatted few-shot block or empty string if list empty."""
    if not FEW_SHOT_EXAMPLES_B:
        return ""
    return "\nAdditional examples:\n" + _json_block(FEW_SHOT_EXAMPLES_B)


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
        few_shot_block=_few_shot_block(),
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
