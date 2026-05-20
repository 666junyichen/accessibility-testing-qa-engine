"""Pydantic schema for Step 5.1-B (video/session-level assessment).

Step 5.1-B provides one lightweight session-quality record per video. It does
not carry rationale or audit fields; debugging evidence belongs in prompt logs
or review notes.

The Round 5 canonical fields are:

`narration_quality`
    `none`, `sparse`, `adequate`, or `rich`; describes how useful the
    participant's verbal narration is for analysis.
`recording_quality`
    `poor`, `acceptable`, or `good`; describes whether the recording is usable
    for analysis, not production-grade audio quality.
`coaching_evidence`
    `none` or `explicit`; records whether the moderator directly guided the
    participant by naming a path, target, or answer.
"""

from pydantic import BaseModel
from typing import Literal


NarrationQuality = Literal["none", "sparse", "adequate", "rich"]
RecordingQuality = Literal["poor", "acceptable", "good"]
CoachingEvidence = Literal["none", "explicit"]


class VideoAssessment(BaseModel):
    """Session-level quality assessment for one test video."""

    narration_quality: NarrationQuality
    recording_quality: RecordingQuality
    coaching_evidence: CoachingEvidence

    model_config = {"extra": "forbid"}
