"""Pydantic schema for Step 5.1-A (finding-level classification).

`findings` is the list of friction events detected in one transcript window.
The empty list `[]` means no friction was detected. A single window may contain
multiple findings.

Each finding uses the Round 5 canonical ten-field shape:

`finding`
    One-sentence description of the friction event.
`observed_signal`
    Behavioural evidence: what the participant did.
`stated_signal`
    Verbal evidence: what the participant said. Use null when the window has
    no relevant utterance and set `signal_alignment` to `stated_missing`.
`signal_alignment`
    `aligned`, `conflicted`, or `stated_missing`.
`friction_type`
    F1-F7 or null. Null is accepted only as a defensive shell value and is
    dropped by classifier post-processing.
`severity_s`
    S1-S6 or null. Null is accepted only as a defensive shell value and is
    dropped by classifier post-processing.
`sentiment_e`
    E1-E5 or null. Spoken evidence should receive at least E3; windows with no
    relevant utterance use null in sync with `stated_signal`.
`calibrator_score_l`
    L1-L5 or null. Null is accepted only as a defensive shell value and is
    dropped by classifier post-processing.
`rationale`
    Two to three sentences tying observed/stated evidence to the gate
    definitions.
`structural_amplification_note`
    Optional cohort or accessibility amplification note. It is descriptive
    only and does not weight the score.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


FrictionType = Literal["F1", "F2", "F3", "F4", "F5", "F6", "F7"]
SeverityS = Literal["S1", "S2", "S3", "S4", "S5", "S6"]
SentimentE = Literal["E1", "E2", "E3", "E4", "E5"]
CalibratorScoreL = Literal["L1", "L2", "L3", "L4", "L5"]
SignalAlignment = Literal["aligned", "conflicted", "stated_missing"]


class Finding(BaseModel):
    """One friction event extracted from a transcript window."""

    finding: str = Field(min_length=1)
    observed_signal: str = Field(min_length=1)
    stated_signal: Optional[str] = None
    signal_alignment: SignalAlignment
    friction_type: Optional[FrictionType] = None
    severity_s: Optional[SeverityS] = None
    sentiment_e: Optional[SentimentE] = None
    calibrator_score_l: Optional[CalibratorScoreL] = None
    rationale: str = Field(min_length=1)
    structural_amplification_note: Optional[str] = None

    model_config = {"extra": "forbid"}


class FindingsOutput(BaseModel):
    """Top-level 5.1-A output. Empty list means no friction in this window."""

    findings: list[Finding]

    model_config = {"extra": "forbid"}
