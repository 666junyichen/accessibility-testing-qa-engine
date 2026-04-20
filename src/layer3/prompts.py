"""Prompt templates for Layer 3 semantic classification.

This module belongs to Step 5.1. It does not call an LLM API. It defines the
prompt text, label options, output schema, and helper functions that format one
transcript window for later LLM classification.
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
    "none": "No observed friction",
    "unclear": "Unclear friction evidence",
}

SOURCE_SEVERITY_LEVELS = {
    "S1": "Blocker (Project)",
    "S2": "Task Blocker",
    "S3": "Severe Friction",
    "S4": "High Friction",
    "S5": "Medium Friction",
    "S6": "Low Friction",
    "none": "No observed friction",
    "unclear": "Insufficient evidence",
}

SEVERITY_LEVELS = [
    "none",
    "low",
    "medium",
    "high",
]

SOURCE_SENTIMENT_LABELS = {
    "E1": "Positive / Delighted",
    "E2": "Positive / Satisfied",
    "E3": "Neutral / Indifferent",
    "E4": "Negative / Frustrated",
    "E5": "Negative / Angry",
    "unclear": "Insufficient evidence",
}

SENTIMENT_LABELS = [
    "positive",
    "neutral",
    "negative",
    "mixed",
    "unclear",
]

NARRATION_TYPES = [
    "thinking_aloud",
    "reading_page",
    "navigation",
    "feedback_evaluation",
    "task_response",
    "off_task",
    "unclear",
]

OUTPUT_SCHEMA = {
    "window_id": "string",
    "friction_type": "F1 | F2 | F3 | F4 | F5 | F6 | F7 | none | unclear",
    "friction_label": "string",
    "severity_id": "S1 | S2 | S3 | S4 | S5 | S6 | none | unclear",
    "severity": "none | low | medium | high",
    "sentiment_id": "E1 | E2 | E3 | E4 | E5 | unclear",
    "sentiment": "positive | neutral | negative | mixed | unclear",
    "narration_type": (
        "thinking_aloud | reading_page | navigation | feedback_evaluation | "
        "task_response | off_task | unclear"
    ),
    "at_context_present": "yes | no | unclear",
    "primary_evidence": "short quote from the transcript window",
    "rationale": "brief explanation of the classification",
    "confidence": "low | medium | high",
}

OUTPUT_EXAMPLE = {
    "window_id": "<window_id>",
    "friction_type": "F6",
    "friction_label": "Content Not Found",
    "severity_id": "S5",
    "severity": "medium",
    "sentiment_id": "E4",
    "sentiment": "negative",
    "narration_type": "navigation",
    "at_context_present": "no",
    "primary_evidence": "I'm struggling to find the feedback page.",
    "rationale": (
        "The tester cannot locate the information or pathway needed to "
        "complete the assigned feedback task."
    ),
    "confidence": "high",
}

SYSTEM_PROMPT = """
You are analysing transcript windows from accessibility and usability testing.

Your task is to classify one transcript window using the client F1-F7 friction
taxonomy documented in docs/friction_taxonomy.md.

Use only the evidence provided in the task context and transcript window.
Do not infer personal attributes, unstated motivations, or diagnoses.

Return only valid JSON. Do not include markdown, commentary, or extra text.
"""

TAXONOMY_PROMPT = """
Client friction taxonomy:
- F1 Comprehension Friction: the tester cannot understand the meaning of
  content because of jargon, unclear language, complex terminology, legal or
  technical wording, or poorly written text.
- F2 Confidence Friction: the tester understands the words but is uncertain
  what to do next, whether an action is correct, what will happen if they
  proceed, or where they should go next.
- F3 Accessibility Friction: content or functionality does not work correctly
  with assistive technology, keyboard access, focus order, labels, headings,
  zoom, PDF accessibility, or another accessibility requirement.
- F4 Unresponsive Interface: the tester takes an action but the interface does
  not respond as expected, responds slowly, or provides no clear feedback.
- F5 Unexpected Behaviour: the interface responds in a surprising way compared
  with the label, design, prior interaction pattern, or tester expectation.
- F6 Content Not Found: the tester cannot locate information needed to make a
  decision or complete the task because it is missing, hidden, or placed
  somewhere unexpected.
- F7 Excessive Effort: the task is possible but requires too many steps, clicks,
  repeated entries, time, scrolling, or cognitive effort.

No-friction handling:
- Use friction_type "none" when the window shows normal progress, neutral
  narration, reading aloud, successful completion, or positive feedback without
  evidence of an impediment.
- Use friction_type "unclear" when there is not enough transcript or task
  context to decide whether friction is present.
- Do not use F7 for no-friction cases. F7 means excessive effort.

Severity IDs from the client framework:
- S1 Blocker (Project): the primary project outcome could not be achieved
  independently, or facilitator intervention/abandonment occurred.
- S2 Task Blocker: the overall outcome may be achieved, but one task was
  completely blocked.
- S3 Severe Friction: a significant component failure or barrier was worked
  around or skipped.
- S4 High Friction: major difficulty requiring substantial effort, workaround,
  repeated attempts, or extended time.
- S5 Medium Friction: noticeable delay, hesitation, or confusion, but
  completion is not seriously threatened.
- S6 Low Friction: minor issue with negligible impact.
- none: no observed friction.
- unclear: insufficient evidence to assess severity.

Simplified severity labels:
- none: no observed friction.
- low: maps to S6.
- medium: maps to S4 or S5.
- high: maps to S1, S2, or S3.

Sentiment IDs from the client framework:
- E1 Positive / Delighted: genuine delight, praise, or pleasant surprise.
- E2 Positive / Satisfied: things worked as expected with mild positive feeling.
- E3 Neutral / Indifferent: matter-of-fact narration without clear emotion.
- E4 Negative / Frustrated: annoyance, confusion, disappointment, or irritation.
- E5 Negative / Angry: strong negative emotion, hostility, or intent to abandon.
- unclear: insufficient evidence.

Simplified sentiment labels:
- positive: maps to E1 or E2.
- neutral: maps to E3.
- negative: maps to E4 or E5.
- mixed: positive and negative reactions appear in the same window.
- unclear: sentiment cannot be confidently inferred.

Narration types:
- thinking_aloud: thoughts, expectations, decisions, or reasoning.
- reading_page: mainly reading page content aloud.
- navigation: moving through pages, links, search results, menus, or forms.
- feedback_evaluation: evaluating clarity, usefulness, accessibility, or trust.
- task_response: directly answering or summarising the assigned task.
- off_task: content is not relevant to the assigned task.
- unclear: too ambiguous to classify.

Classification rules:
- Choose one dominant friction_type.
- Use task context to decide whether behaviour is relevant to the assigned task.
- If multiple issues appear, choose the main barrier and mention secondary
  issues in rationale.
- Quote the strongest transcript evidence in primary_evidence.
- If the transcript is only positive or neutral progress, use friction_type
  "none", severity_id "none", and severity "none".
"""

USER_PROMPT_TEMPLATE = """
Classify the following transcript window.

Project:
{project}

Window ID:
{window_id}

Video ID:
{video_id}

Task title:
{task_title}

Task instructions:
{task_instructions}

Transcript window:
{window_text}

Return JSON using exactly this schema:
{output_schema}

Example JSON format:
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
    """Format one transcript window as the user prompt for Layer 3."""
    return USER_PROMPT_TEMPLATE.format(
        window_id=window_id,
        project=project,
        video_id=video_id,
        task_title=task_title,
        task_instructions=task_instructions,
        window_text=window_text,
        output_schema=_json_block(OUTPUT_SCHEMA),
        output_example=_json_block(
            {
                **OUTPUT_EXAMPLE,
                "window_id": window_id,
            }
        ),
    ).strip()


def build_messages(
    window_id,
    project,
    video_id,
    window_text,
    task_title="Unknown task",
    task_instructions="No task instructions provided.",
):
    """Return chat-style messages for an LLM client."""
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
