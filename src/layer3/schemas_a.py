"""Pydantic schema for Step 5.1-A (finding-level classification).

字段文档（中文）
================

`findings`
    本窗口识别出的 friction 列表。允许空数组 `[]`，表示窗口无摩擦。
    同一窗口可有多条 finding（1:N）。

每条 finding 的 10 个字段（顺序对齐 Round 5 canonical）：

`finding`           一句话描述本次 friction 事件（来自 07 原文首字段）
`observed_signal`   参与者实际做了什么（行为侧证据）
`stated_signal`     参与者说了什么（陈述侧证据）。可 null，当窗口内无口头
                    表达时填 null，并将 signal_alignment 设为 stated_missing
`signal_alignment`  {aligned, conflicted, stated_missing}
                    aligned: observed 与 stated 一致
                    conflicted: 两者矛盾（此时按 observed 打低分，不平均）
                    stated_missing: stated_signal 为 null 时使用（工程扩展，
                    非 07 原文）
`friction_type`     F1-F7 或 null。null 仅作为 LLM shell finding 防御层，
                    classifier 后处理会丢弃该 finding
`severity_s`        S1-S6 或 null。null 仅作为 LLM shell finding 防御层，
                    classifier 后处理会丢弃该 finding
`sentiment_e`       E1-E5 或 null。纪律：
                    - 参与者有口头表达 → 至少 E3（不得 null）
                    - 窗口无任何口头表达 → null（与 stated_signal=null 同步）
                    - E3（neutral/indifferent）≠ null（无情绪证据）
`calibrator_score_l` L1-L5 或 null。null 仅作为 LLM shell finding 防御层，
                    classifier 后处理会丢弃该 finding
`rationale`         2-3 句综合说明，需引用 observed/stated 与 gate 定义
`structural_amplification_note`
                    若 cohort（Blind/ND/ESL 等）造成结构性放大，填描述；
                    否则 null。仅描述，不对分数加权
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
