"""Prompt templates for Layer 3 semantic classification.

This module belongs to Step 5.1. It does not call an LLM API. It defines the
prompt text, label options, output schema, and helper functions that format one
transcript window for later LLM classification.
"""

import json

FRICTION_TYPES = {
    "F1": "Navigation / Findability Issue",
    "F2": "Content Clarity Issue",
    "F3": "Interaction / Control Issue",
    "F4": "Accessibility / Assistive Technology Issue",
    "F5": "Task Understanding / Expectation Mismatch",
    "F6": "Support / Trust / Safety Concern",
    "F7": "No Clear Friction / Positive Feedback",
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

SEVERITY_LEVELS = [
    "none",
    "low",
    "medium",
    "high",
]

OUTPUT_SCHEMA = {
    "window_id": "string",
    "friction_type": "F1 | F2 | F3 | F4 | F5 | F6 | F7",
    "friction_label": "string",
    "severity": "none | low | medium | high",
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
    "friction_type": "F1",
    "friction_label": "Navigation / Findability Issue",
    "severity": "medium",
    "sentiment": "negative",
    "narration_type": "navigation",
    "at_context_present": "no",
    "primary_evidence": "I can't find the feedback page.",
    "rationale": "The tester is unable to locate the relevant page.",
    "confidence": "high",
}

SYSTEM_PROMPT = """
You are analysing transcript windows from accessibility and usability testing.

Your task is to classify one transcript window using the R3 friction taxonomy.
Use only the evidence provided in the task context and transcript window.
Do not infer personal attributes or unstated motivations.

Return only valid JSON. Do not include markdown, commentary, or extra text.
"""

TAXONOMY_PROMPT = """
Friction taxonomy:
- F1 Navigation / Findability Issue: the tester cannot find where to go, which
link to click, or how to reach the needed information.
- F2 Content Clarity Issue: wording, terminology, information hierarchy, or
page content is unclear, too complex, missing, or difficult to understand.
- F3 Interaction / Control Issue: the tester has trouble using a button, link,
form, menu, video, authentication step, filter, or other interactive element.
- F4 Accessibility / Assistive Technology Issue: the tester mentions screen
readers, VoiceOver, zoom, headings, labels, keyboard access, focus, PDF
accessibility, or assistive technology behaviour.
- F5 Task Understanding / Expectation Mismatch: the task or page behaviour does
not match what the tester expected, or the tester misunderstands the task/page.
- F6 Support / Trust / Safety Concern: the tester discusses trust, credibility,
safety, sensitive help-seeking, helplines, quick exit, emergency support, or
confidence in support information.
- F7 No Clear Friction / Positive Feedback: the window contains normal progress,
reading aloud, neutral narration, successful task completion, or positive
feedback without a clear problem.

Sentiment labels:
- positive: approval, confidence, usefulness, or satisfaction.
- neutral: mainly describing, reading, or narrating without strong judgement.
- negative: confusion, frustration, concern, dissatisfaction, or failure.
- mixed: both positive and negative feedback appear in the same window.
- unclear: sentiment cannot be confidently inferred.

Narration types:
- thinking_aloud: thoughts, expectations, decisions, or reasoning.
- reading_page: mainly reading page content aloud.
- navigation: moving through pages, links, search results, menus, or forms.
- feedback_evaluation: evaluating clarity, usefulness, accessibility, or trust.
- task_response: directly answering or summarising the assigned task.
- off_task: content is not relevant to the assigned task.
- unclear: too ambiguous to classify.

Severity:
- none: no friction is visible.
- low: minor hesitation or improvement suggestion, but progress continues.
- medium: noticeable confusion, repeated effort, unclear content, or interaction
  issue.
- high: serious blocker, safety concern, major accessibility barrier, or
  inability to complete the task.
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
