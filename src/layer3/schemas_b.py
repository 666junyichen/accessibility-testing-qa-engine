"""Pydantic schema for Step 5.1-B (video/session-level assessment).

字段文档（中文）
================

5.1-B 是 video/session 级轻量质量信号，粒度 1:1（每 video 一条）。
不持有 rationale 或 audit 字段；debug/audit 走 prompt log 或 notebook 抽查。

3 字段（对齐 flow doc Round 5 canonical）：

`narration_quality`   {none, sparse, adequate, rich}
                      参与者语言叙述对分析的有用程度：
                      - none: 基本没说话
                      - sparse: 只有零散字词或极简短句
                      - adequate: 有足够内容支撑判断
                      - rich: 持续 think-aloud / 充分陈述反应
`recording_quality`   {poor, acceptable, good}
                      "这段 session 对分析是否可用"，非影视质量：
                      - poor: 音频破损 / 大段缺失 / 几乎无法使用
                      - acceptable: 可用但有部分缺陷
                      - good: 完整清晰
`coaching_evidence`   {none, explicit}
                      主持人对参与者的直接引导/提示证据：
                      - none: 无明显引导
                      - explicit: 主持人显式告知操作路径 / 直接给答案
                      （当前交付版保持二值；未来 production 版本可评估
                      是否扩展到 {none, minimal, directive}）
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
