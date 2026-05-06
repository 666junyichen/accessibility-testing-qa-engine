# Layer 3 Design Reference

This is the single maintained Layer 3 design reference for R3 prompt
classification. It replaces the older split documents
`docs/friction_taxonomy.md` and `docs/prompt_design.md`, which now redirect here.

The schema source of truth remains:

- `src/layer3/schemas_a.py` for Step 5.1-A finding-level output.
- `src/layer3/schemas_b.py` for Step 5.1-B video-level output.

Use this document for taxonomy meaning, prompt design, boundary rules, and Round
5/Round 11 decisions. If a field name, enum value, or optionality rule differs
from the Pydantic models, the model files win and this document should be
updated.

## Source Authority

Canonical F/S/E taxonomy follows the client See Me Please friction and sentiment
framework, exported in the project materials as `Friction & Sentiment
Classification Framework.txt`. The leader's W10 task refers to the same source
as `client/s3_snapshot/06-friction-sentiment-framework.md`.

Round 5 additions follow the leader calibrator source referred to as
`client/s3_snapshot/07-friction-score-calibrator-prompt.md`. That source governs
L1-L5, `signal_alignment`, and `structural_amplification_note`.

This document intentionally keeps compact labels and project-specific
interpretation rules. It does not copy the full client framework.

## Layer 3 Units

Step 5.1-A classifies one transcript window. Output may contain zero, one, or
many findings. A finding is one friction event only, not a task summary, not a
positive outcome, and not a general observation. If no friction occurred, the
correct output is:

```json
{"findings": []}
```

Step 5.1-B classifies one video/session. It does not extract friction events. It
outputs one session-level assessment for narration quality, recording quality,
and coaching evidence.

Keep the tracks separate:

- 5.1-A asks what friction events happened.
- 5.1-B asks how usable the session evidence is for analysis.

## Canonical Taxonomy

Layer 3 uses four independent dimensions:

- `friction_type`: what kind of impediment occurred.
- `severity_s`: how much the event affected task progress.
- `sentiment_e`: what affect the participant expressed.
- `calibrator_score_l`: Round 5 event-strength judgement.

Do not map `calibrator_score_l` directly from `severity_s`. Severity measures
task impact. L score captures event strength under the calibrator, including
independence, workaround burden, evidence strength, and repair concern.

### Friction Types F1-F7

- F1 Comprehension Friction: unclear wording, instructions, content, labels, or
  meaning.
- F2 Confidence Friction: uncertainty about correctness, trust, progress, or the
  next action.
- F3 Accessibility Friction: screen reader, keyboard, focus, heading, visual,
  zoom, contrast, PDF, or assistive-technology barrier.
- F4 Unresponsive Interface: the interface appears not to respond, gives no
  usable feedback, freezes, stalls, or fails to load.
- F5 Unexpected Behaviour: the system responds differently from the label,
  design, instruction, or participant expectation.
- F6 Content Not Found: required page, content, control, help, form section, or
  option cannot be located.
- F7 Excessive Effort: the task is possible but requires too many steps,
  repeated actions, scrolling, setup, loops, or cognitive effort.

Choose the dominant impediment for the event. Do not choose type only from the
participant's emotion.

### Severity S1-S6

- S1 Blocker (Project): primary project/task outcome cannot be achieved
  independently.
- S2 Task Blocker: current task cannot be completed without workaround,
  facilitator intervention, or major strategy change.
- S3 Severe Friction: task is still possible but with major difficulty,
  repeated failure, sustained confusion, or substantial delay.
- S4 High Friction: clear difficulty with multiple failed attempts, obvious
  detours, much extra time, workaround, or facilitator hint.
- S5 Medium Friction: noticeable but recoverable difficulty, such as a short
  pause, one correction, mild confusion, or quick recovery from a non-optimal
  path. The task is not at risk.
- S6 Low Friction: minor issue, brief hesitation, small annoyance, or momentary
  inefficiency with little effect on progress.

Severity is based on observed task impact, not emotional intensity alone.

### Sentiment E1-E5

- E1 Positive / Delighted: clear delight, strong praise, pleasant surprise, or
  enthusiasm.
- E2 Positive / Satisfied: routine positive approval, such as "good", "nice",
  "perfect", or "that worked".
- E3 Neutral / Indifferent: matter-of-fact narration with no clear affect, such
  as "I'll click this" or "I'm reading the form".
- E4 Negative / Frustrated: confusion, complaint, annoyance, stress, or
  dissatisfaction.
- E5 Negative / Angry: anger, strong distress, explicit hostility, or intense
  negative reaction.

If there is participant speech, sentiment should normally be E1-E5. Use E3 for
neutral narration. Use `null` only when no useful participant speech is present,
paired with `stated_signal = null` and `signal_alignment = stated_missing`.

### Calibrator Score L1-L5

- L1: minor friction; task completed without interruption and confidence is not
  materially affected.
- L2: low-impact friction; small detour, pause, or uncertainty with easy
  recovery.
- L3: moderate friction; meaningful delay, effort, uncertainty, or
  analyst-relevant evidence.
- L4: high friction; repeated attempts, workaround, strong uncertainty, or
  facilitator hint.
- L5: critical friction; independent completion fails, task is blocked, or the
  evidence indicates a serious access/usability barrier.

L is an event-strength calibrator. It may correlate with S, but it is not a
severity remap.

## Step 5.1-A Schema Contract

See `src/layer3/schemas_a.py` for exact fields and enums. The top-level object
is `FindingsOutput` with `findings: list[Finding]`.

A valid finding:

- describes one friction event in the `finding` sentence;
- records behaviour in `observed_signal`;
- records speech in `stated_signal`, or `null` when speech is missing;
- assigns `signal_alignment` as `aligned`, `conflicted`, or `stated_missing`;
- assigns valid F, S, and L enum values;
- assigns E1-E5 when speech exists, or `null` when speech is missing;
- uses `rationale` to justify the labels from observed/stated evidence;
- uses `structural_amplification_note` only when cohort or access context
  structurally amplifies the event.

The schema allows defensive nulls for some enum fields, but the prompt contract
does not. If the model cannot assign a valid `friction_type`, `severity_s`, and
`calibrator_score_l`, it should not emit that finding.

`signal_alignment` means:

- `aligned`: behaviour and speech support the same friction event.
- `conflicted`: speech and behaviour disagree; classify from the observed
  evidence rather than averaging.
- `stated_missing`: there is no useful speech evidence.

Do not emit findings for smooth progress, successful completion, praise, neutral
reading, routine navigation, or positive feedback without an impediment.

## Step 5.1-B Schema Contract

See `src/layer3/schemas_b.py` for exact fields and enums. A `VideoAssessment`
has exactly three fields.

`narration_quality` describes how useful participant speech is:

- `none`: almost no participant speech.
- `sparse`: isolated words or very short fragments.
- `adequate`: enough speech to support judgement.
- `rich`: sustained think-aloud or detailed reaction.

`recording_quality` describes analytic usability, not production polish:

- `poor`: broken audio, major missing sections, or barely usable evidence.
- `acceptable`: usable with gaps, unclear audio, or partial missing context.
- `good`: relevant evidence is complete and clear.

`coaching_evidence` is binary by Round 11:

- `none`: no direct coaching; neutral think-aloud prompts still count as none.
- `explicit`: moderator tells the participant where to click, what answer to
  choose, or how to complete the task.

5.1-B has no rationale/audit fields. Keep debug context in logs, notebooks, or
manual notes, not in schema output.

## Prompt Structure

`src/layer3/prompts_a.py` builds the 5.1-A chat prompt:

- `SYSTEM_PROMPT`: strict JSON, no extra fields, and V2 semantic lock.
- `TAXONOMY_PROMPT`: compact F/S/E/L labels plus boundary rules.
- `USER_PROMPT_TEMPLATE`: project, video, window, task, and transcript context.
- Few-shot examples: valid findings, empty findings, and all three alignment
  states.

`src/layer3/prompts_b.py` builds the 5.1-B chat prompt:

- `SYSTEM_PROMPT`: video-level assessment role and exact JSON output.
- `DEFINITIONS_PROMPT`: narration, recording, and coaching definitions.
- `USER_PROMPT_TEMPLATE`: session metadata and transcript summary.
- Few-shot examples: common session-quality combinations.

The V2 semantic lock is the key prompt rule: finding equals friction event. It
prevents the model from creating findings for positive outcomes, neutral
narration, general summaries, or evidence-free observations.

## Round 5 And Round 11 Decisions

Round 5 canonical finding-level fields are:
`finding`, `observed_signal`, `stated_signal`, `signal_alignment`,
`friction_type`, `severity_s`, `sentiment_e`, `calibrator_score_l`, `rationale`,
and `structural_amplification_note`.

Round 5 also made L1-L5 independent from S1-S6. Do not collapse these dimensions
in prompts, CSV annotation, or Kappa analysis.

Round 11 locked `coaching_evidence` to `none` / `explicit` for the MVP. Earlier
three-level coaching ideas are deferred and should not appear in current output.

CSV annotation files may include workflow fields such as `annotated`,
`confidence`, `notes`, and `annotator`; those are not LLM output schema fields.

## Boundary Cases

F1 vs F2: use F1 when the participant does not understand content, wording,
instructions, labels, or meaning. Use F2 when the participant understands the
content but is uncertain about correctness, trust, progress, or next action.

F2 vs F6: use F6 when the needed item cannot be found. Use F2 when the item is
visible/reachable but the participant lacks confidence about using it.

F3 vs other types: use F3 when the access mechanism is the barrier, such as
screen reader output, focus order, keyboard access, heading structure, zoom,
contrast, or inaccessible PDF content. Add structural context when it amplifies
the event; do not automatically upweight S or L.

F4 vs F5: use F4 when there is no usable response or feedback after action. Use
F5 when the system responds but the response is unexpected, misleading, or
inconsistent.

F6 vs F7: use F6 when the content/control is not located. Use F7 when it is
locatable but requires excessive steps or effort.

S2 vs S3: use S2 when the current task is blocked without workaround,
facilitator help, or strategy change. Use S3 when the task continues but with
major difficulty or substantial delay.

S3 vs S4: use S3 for difficulty that substantially threatens or reshapes
completion. Use S4 for high friction that is still recoverable.

S4 vs S5: use S4 for multiple failures, obvious detours, much extra time,
workarounds, or facilitator hints. Use S5 for short pauses, one correction, mild
confusion, or a non-optimal path with quick recovery.

E2 vs E3: use E2 for positive affect words such as "good", "nice", "perfect",
or "that worked". Use E3 for pure narration without affect.

E3 vs null: E3 means neutral speech exists. Null means speech is missing. Do not
use null just because speech is unemotional.

Poor recording vs sparse narration: recording quality is about damaged or missing
evidence. Narration quality is about how much useful speech the participant
provides. They are independent.

Explicit coaching vs facilitation: explicit coaching gives the participant the
answer or direct operation path. Neutral prompts such as "what are you thinking?"
remain `coaching_evidence = none`.

## Maintenance Checklist

When Layer 3 changes, keep this order of authority:

1. Client framework and leader snapshot decisions define canonical meaning.
2. `schemas_a.py` and `schemas_b.py` define exact output structure.
3. `prompts_a.py` and `prompts_b.py` implement the prompt wording.
4. `docs/l3_design.md` explains design and boundary rules.
5. README points readers here for Layer 3 context.

Before marking an L3 change done, confirm the docs still answer:

- What is one finding?
- When should `{"findings": []}` be returned?
- Which file is schema truth?
- How are E3 and null different?
- Why is L independent from S?
- Why is `coaching_evidence` binary?
