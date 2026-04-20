# Held-out Evaluation Freeze Checklist

> 本文档是 CS20 held-out 评估的**治理工件**。任何"跑 Bupa held-out"的动作，必须同时满足 Gate 1 ∧ Gate 2。Gate 未全绿前跑 held-out 视为 **held-out 失效**，后续 Bupa 数值全部作废。
>
> 本文档由 Round 4 (2026-04-20) CC↔Codex 协商收敛产出。后续改动必须同步更新 `PROJECT.md §9`。

---

## 一、数据切分（不可变）

| 分区 | 内容 | 体量 | 用途 |
|---|---|---|---|
| **dev set** | 老 3 项目 collated：AAMI 21 + UQ 19 + DPC-WA 17（实际 57 含 2 份转录失败 → 55） | 55 视频 | prompt 调参 / schema 定稿 / 标注 Kappa / ablation / rotating validation |
| **held-out** | Bupa collated | 42 视频 | **冻结后一次性评估**（our vs Model B 数值级对比） |
| **不纳入** | Brighton raw（105）+ Bupa raw（315） | — | 无 collated/survey/tasks 元数据，无法对齐 |

**Annotation 铁律**：人工标注（Kappa 主集）严格限 dev set。Bupa held-out 只允许在 **final freeze 后**做极小量 post-hoc qualitative audit，且结论**不得反哺设计**。

## 二、Dev-internal Validation

- **Rotating 单元**：`AAMI` ↔ `UQ` 双轮 project-wise rotating。DPC-WA 永远在 fit 池里，只贡献多样性。
- **Rotating 层级**：放在 **6.1 fusion 层**（不是 5.2 LLM 全量重跑，避免 token 成本翻倍）。
- **Prompt 跨项目稳定性**：放在 **5.4** 做 project-stratified evaluation（label 分布 / 低置信度占比 / 人工标注对齐），5.2 在全 dev 上只跑一次。
- **切分粒度**：video/tester/project group split，**不切窗口**。

## 三、Gate 1 — 代码完成态（客观可验证）

- [ ] Step 6.1 `fusion_*.py` 代码合并到主分支
- [ ] Step 6.1 pytest 全绿（含 fusion rule unit test + R6 mapping unit test）
- [ ] 5.1-A / 5.1-B prompt 有 pinned 版本号 + commit hash
- [ ] 5.2 LLM classifier 在 dev 55 视频上完成一次全量推理，输出 artefact 落盘（`data/processed/layer3_classifications.csv`）
- [ ] 5.4 project-stratified evaluation 报告产出（含 AAMI/UQ/DPC-WA 三项目分布对比）

## 四、Gate 2 — Nix 显式签字（治理动作）

Gate 1 全绿后，Nix 需对以下 **4 类 freeze** 逐条签字。签字形式：在本文件第五节表格填入 commit hash + 日期 + "Nix approved"。

### Freeze 1：friction / severity / sentiment 字段集合
- `friction_type ∈ {F1, F2, F3, F4, F5, F6, F7}` —— canonical 自 `client/s3_snapshot/06-friction-sentiment-framework.md`
- `severity ∈ {S1, S2, S3, S4, S5, S6}` —— canonical，**替换**早期自造的 5 级 Blocker/Severe/High/Medium/Low
- `sentiment ∈ {E1, E2, E3, E4, E5}` —— E3 neutral 按 SMP 规则排除聚合
- `score_L ∈ {L1, L2, L3, L4, L5}` —— calibrator 专用（见 `client/s3_snapshot/07-friction-score-calibrator-prompt.md`），与 S1-S6 **并存不映射**（Round 5 提案 P1，待定）

### Freeze 2：narration / recording quality 字段集合（5.1-B）
- `narration_quality` —— 枚举 + 定义（Round 5 提案 P5，待定）
- `recording_quality` —— 枚举 + 定义
- `coaching_evidence` —— 枚举 + 定义

### Freeze 3：6.1 Fusion 输入/输出 schema
- Input：5.2 classifier 输出（每窗口一条，字段集合 = Freeze 1 所列）+ 5.1-B 视频级 tester-behavior 字段
- Output：per-tester × per-task quality judgement + coaching recommendation seed + 置信度
- Fusion rule：L1 规则 / L2 聚类 / L3 LLM 的合议规则（权重、冲突裁决、兜底策略）

### Freeze 4：R6 Mapping 规则
- 从 5.x/6.1 输出到 R6 Performance Tracking 的字段映射
- 跨 tester / 跨 project 聚合的归一化规则

## 五、Freeze 签字记录

| Freeze 类别 | Commit Hash | 日期 | 签字人 | 备注 |
|---|---|---|---|---|
| Freeze 1 — friction/severity/sentiment | `TBD` | `TBD` | Nix | 等 Round 5 收敛 |
| Freeze 2 — narration/recording quality | `TBD` | `TBD` | Nix | 等 Round 5 收敛 |
| Freeze 3 — 6.1 fusion I/O schema | `TBD` | `TBD` | Nix | 等 Step 6.1 代码完成 |
| Freeze 4 — R6 mapping 规则 | `TBD` | `TBD` | Nix | 等 R6 设计对齐 |

## 六、"只测一次" 纪律

Bupa held-out 跑完后，下列任一层改动都视为 held-out 失效，必须重走 Gate 1 + Gate 2，并且 Bupa 之前的数值结果作废：

1. Prompt（5.1-A / 5.1-B / 5.2 / 5.3 / 5.4）
2. 4.2 参数（final_k / min_samples / eps / 特征集合）
3. 5.x JSON schema 任一字段增删改
4. 6.1 fusion rule / 权重
5. R6 mapping 规则
6. 后处理规则（置信度阈值、低置信度丢弃策略）

## 七、Bupa held-out 允许的动作（freeze 前）

Gate 未全绿前，Bupa collated 42 仅允许：

- ✅ coverage 统计（视频数 / tester 数 / task 数 / 时长分布）
- ✅ 结构化数据分布对比（survey label 分布与 dev 的差异）
- ❌ 任何 LLM prompt 调用 / classifier 推理 / 人工标注
- ❌ 任何基于 Bupa 结果的 schema/prompt 回调

---

*Owner: Nix (R2 + Lead) · 最近更新: 2026-04-20 · 关联: `PROJECT.md §9` / `collab/cc.md` Round 4*
