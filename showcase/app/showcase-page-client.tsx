"use client";

import type { ChangeEventHandler } from "react";
import { useEffect, useMemo, useState } from "react";
import { siteCopy } from "../lib/site-copy";
import styles from "./page.module.css";

type Language = "en" | "zh";
type ViewKey = "single-video" | "tester-trajectory" | "cohort-overview";
type TabKey = "overview" | "findings" | "coaching" | "layer-detail";

type DistributionItem = {
  key: string;
  label: string;
  value: number;
  tone?: string;
};

const distributionPalettes = {
  severity: ["#f6c445", "#f59e0b", "#a3e635", "#4ade80", "#60a5fa", "#818cf8", "#c084fc"],
  friction: ["#38bdf8", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#14b8a6", "#ec4899", "#64748b"],
  sentiment: ["#7dd3fc", "#34d399", "#fbbf24", "#fb7185", "#a78bfa", "#94a3b8"],
} as const;

type VideoRecord = {
  id: string;
  label: string;
  rawVideoId: string;
  tester: string;
  project: string;
  performanceTier: string;
  score: string;
  scoreValue: number | null;
  findingsCount: number;
  windowCount: number;
  duration: string;
  capReason: string;
  topSeverity: string;
  reason: string;
  tierReasoning: string;
  summary: {
    title: string;
    tier: string;
    score: number | null;
  };
  findings: Array<{
    severity: string;
    friction: string;
    note: string;
    rationale: string;
    sentiment: string;
    windowId: string;
  }>;
  recommendations: Array<{
    title: string;
    detail: string;
    priority: number;
  }>;
  sessionAssessment: Array<{ label: string; value: string }>;
  scoreBreakdown: Array<{ label: string; value: string }>;
  severityDistribution: DistributionItem[];
  frictionTypes: DistributionItem[];
  sentimentDistribution: DistributionItem[];
  layerDetails: {
    l1: {
      totalFlags: number;
      durationAnomaly: boolean;
      flaggedWindows: number;
    };
    l2: {
      coverage: string;
      dominantClusterId: string;
      dominantClusterPct: string;
      caveat: string;
    };
  };
};

type TesterRecord = {
  id: string;
  tester: string;
  label: string;
  tier: string;
  aggregateScore: string;
  direction: string;
  delta: string;
  submissionsScored: number;
  submissionsTotal: number;
  projects: string[];
  persistentFrictionTypes: string[];
  sentimentDistribution: DistributionItem[];
  lanes: string[];
  orderingBasis: string;
  trajectory: Array<{
    videoId: string;
    label: string;
    score: number | null;
    tier: string;
  }>;
};

type CohortOverview = {
  stats: Array<{ label: string; value: string; tone: string }>;
  tierDistribution: Array<{ label: string; value: number; tone: string }>;
  projectBreakdown: Array<{
    project: string;
    videos: number;
    averageScore: string;
    tiers: Array<{ label: string; value: number; tone: string }>;
  }>;
};

type ShowcaseData = {
  navigationItems: Array<{ id: string; label: string }>;
  filterOptions: {
    tiers: string[];
    projects: string[];
  };
  totalVideos: number;
  videos: VideoRecord[];
  testers: TesterRecord[];
  cohortOverview: CohortOverview;
};

const copy = {
  en: {
    productName: siteCopy.productName,
    sidebarCaption: siteCopy.sidebarCaption,
    title: siteCopy.pageTitle,
    subtitle: siteCopy.pageSubtitle,
    toggle: "中文",
    views: {
      "single-video": "Single Video",
      "tester-trajectory": "Tester Trajectory",
      "cohort-overview": "Cohort Overview",
    },
    viewDescriptions: {
      "single-video": "Single submission",
      "tester-trajectory": "Same tester across submissions",
      "cohort-overview": "Whole cohort distribution",
    },
    filters: {
      tier: "Performance tier",
      project: "Project",
      video: "Video",
      tester: "Tester",
      all: "All",
    },
    sidebar: {
      showing: "Showing",
      videos: "videos",
      score: "Score",
      report: "Report quality risk",
    },
    tabs: {
      overview: "Overview",
      findings: "Findings",
      coaching: "Coaching",
      "layer-detail": "Layer detail",
    },
    labels: {
      tester: "Tester",
      project: "Project",
      tier: "Performance tier",
      score: "Score",
      findings: "Findings",
      windows: "Windows",
      duration: "Duration",
      topSeverity: "Top severity",
      reason: "Risk reason",
      capReason: "Cap reasons",
      tierReasoning: "Tier reasoning",
      delta: "Delta",
      totalFindings: "Total findings",
      topFriction: "Top friction",
      visibleTypes: "Visible friction types",
      totalFlags: "Total flags",
      durationAnomaly: "Duration anomaly",
      flaggedWindows: "Flagged windows",
      coverage: "Coverage",
      dominantCluster: "Dominant cluster",
      dominantPct: "Dominance %",
      aggregate: "Aggregate",
      direction: "Direction",
      submissions: "Submissions",
      persistentFriction: "Persistent friction types",
      sentimentRollup: "Sentiment roll-up",
      projectBreakdown: "Per-project performance tier",
      averageScore: "Average score",
      videos: "Videos",
      lane: "Lane",
      ordering: "Ordering",
    },
    helper: {
      project: "Three different video sources.",
      tier: "Tier guide: Leading, Proficient, Developing, Foundational.",
    },
    headings: {
      sessionAssessment: "Session-level assessment (Layer 3-B)",
      scoreBreakdown: "R6 score breakdown",
      severityDistribution: "Severity distribution",
      frictionTypes: "Friction types",
      sentiment: "Sentiment",
      keyFindings: "Highlighted findings",
      coaching: "Coaching recommendations",
      layerRules: "Layer 1 - rule-based flags",
      layerClusters: "Layer 2 - clustering coverage",
      trajectory: "Submission scores",
      cohort: "Cohort overview",
      tierDistribution: "Per-submission score tier",
    },
    empty: {
      noVideos: "No videos match the selected filters.",
      noFindings: "No findings were available for this submission.",
      noCoaching: "No coaching recommendations were generated for this submission.",
      noTrajectory: "No scored submissions are available for this tester.",
    },
    misc: {
      yes: "Yes",
      no: "No",
      footnote: "Weights: D1 0.50 + D2 0.35 + D3 0.15 -> raw composite. Caps bind after raw.",
    },
  },
  zh: {
    productName: "SMP 演示",
    sidebarCaption: "测试员质量评估与辅导原型",
    title: "智能测试员质量评估",
    subtitle: "See Me Please 决策支持原型",
    toggle: "EN",
    views: {
      "single-video": "单视频",
      "tester-trajectory": "测试员轨迹",
      "cohort-overview": "群组概览",
    },
    viewDescriptions: {
      "single-video": "单条提交",
      "tester-trajectory": "同一人跨提交",
      "cohort-overview": "全体分布",
    },
    filters: {
      tier: "表现等级",
      project: "项目",
      video: "视频",
      tester: "测试员",
      all: "全部",
    },
    sidebar: {
      showing: "当前显示",
      videos: "个视频",
      score: "分数",
      report: "报告风险",
    },
    tabs: {
      overview: "总览",
      findings: "发现项",
      coaching: "辅导建议",
      "layer-detail": "分层细节",
    },
    labels: {
      tester: "测试员",
      project: "项目",
      tier: "表现等级",
      score: "分数",
      findings: "发现项",
      windows: "窗口数",
      duration: "时长",
      topSeverity: "最高严重级别",
      reason: "风险原因",
      capReason: "封顶原因",
      tierReasoning: "等级判断",
      delta: "变化幅度",
      totalFindings: "发现总数",
      topFriction: "主要摩擦类型",
      visibleTypes: "可见摩擦类型",
      totalFlags: "规则标记数",
      durationAnomaly: "时长异常",
      flaggedWindows: "标记窗口",
      coverage: "覆盖率",
      dominantCluster: "主聚类",
      dominantPct: "主聚类占比",
      aggregate: "综合分",
      direction: "趋势",
      submissions: "提交数",
      persistentFriction: "持续出现的摩擦类型",
      sentimentRollup: "情绪汇总",
      projectBreakdown: "按项目划分的表现等级分布",
      averageScore: "平均分",
      videos: "视频数",
      lane: "轨道",
      ordering: "排序依据",
    },
    helper: {
      project: "这里表示 3 个不同的视频来源。",
      tier: "等级说明：Leading 领先，Proficient 稳定，Developing 发展中，Foundational 基础。",
    },
    headings: {
      sessionAssessment: "会话级评估（Layer 3-B）",
      scoreBreakdown: "R6 分数拆解",
      severityDistribution: "严重级别分布",
      frictionTypes: "摩擦类型",
      sentiment: "情绪分布",
      keyFindings: "重点发现",
      coaching: "辅导建议",
      layerRules: "Layer 1 - 规则标记",
      layerClusters: "Layer 2 - 聚类覆盖",
      trajectory: "提交分数轨迹",
      cohort: "群组概览",
      tierDistribution: "单次提交表现等级分布",
    },
    empty: {
      noVideos: "当前筛选条件下没有视频。",
      noFindings: "该提交暂时没有可展示的发现项。",
      noCoaching: "该提交暂时没有辅导建议。",
      noTrajectory: "该测试员暂时没有可展示的评分轨迹。",
    },
    misc: {
      yes: "是",
      no: "否",
      footnote: "权重：D1 0.50 + D2 0.35 + D3 0.15 -> 原始综合分。封顶规则会在原始分之后生效。",
    },
  },
} as const;

const phraseMap: Record<string, string> = {
  poor: "较弱",
  acceptable: "可接受",
  good: "良好",
  rich: "充分",
  none: "无",
  stable: "稳定",
  improving: "上升",
  declining: "下降",
  Narration: "讲述质量",
  Recording: "录制质量",
  "Coaching evidence": "辅导证据",
  "Raw composite": "原始综合分",
  "D1 Narration": "D1 讲述质量",
  "D2 Friction": "D2 摩擦识别",
  "D3 Recording": "D3 录制质量",
  "Total audits": "总评审数",
  "Avg score": "平均分",
  "Critical sessions": "关键问题会话",
  "Leading reviews": "领先档评审",
  Leading: "Leading（领先）",
  Proficient: "Proficient（稳定）",
  Developing: "Developing（发展中）",
  Foundational: "Foundational（基础）",
  "No cap applied": "未触发封顶",
  "task-blocking friction: S1/S2 present": "存在 S1/S2 级任务阻塞摩擦",
  ">=2 S2 task-blockers": "至少存在 2 个 S2 级任务阻塞",
  "S1 project-level blocker present": "存在 S1 级项目阻塞",
  "multiple medium-severity findings": "存在多个中等级别问题",
};

const tierNotes: Record<string, string> = {
  Leading: "领先，高质量完成",
  Proficient: "稳定，整体可靠",
  Developing: "发展中，仍有改进空间",
  Foundational: "基础阶段，需要更多支持",
};

const severityNotes: Record<string, string> = {
  S1: "项目级阻塞",
  S2: "任务阻塞",
  S3: "高强度摩擦",
  S4: "明显摩擦",
  S5: "中等摩擦",
  S6: "轻微摩擦",
};

const frictionNotes: Record<string, string> = {
  F1: "理解障碍",
  F2: "信心/确认障碍",
  F3: "无障碍访问障碍",
  F4: "界面无响应",
  F5: "系统行为不符合预期",
  F6: "找不到内容或入口",
  F7: "操作成本过高",
};

const priorityNotes: Record<string, string> = {
  P1: "最高优先级",
  P2: "高优先级",
  P3: "中优先级",
  P4: "模式级辅导建议",
};

function t(value: string, language: Language) {
  if (language === "en") {
    return value;
  }
  return phraseMap[value] ?? value;
}

function tierLabel(value: string, language: Language) {
  if (language === "zh") {
    return t(value, language);
  }

  return tierNotes[value] ? `${value} (${tierNotes[value]})` : value;
}

function codedLabel(value: string, language: Language, notes: Record<string, string>) {
  const note = notes[value];
  if (!note) return value;
  return language === "zh" ? `${value} ${note}` : `${value} (${note})`;
}

function toneClass(tone: string | undefined) {
  if (tone === "warning") return styles.toneWarning;
  if (tone === "warm") return styles.toneWarm;
  if (tone === "good") return styles.toneGood;
  if (tone === "cool") return styles.toneCool;
  return styles.toneNeutral;
}

function formatPercent(value: number, total: number) {
  if (!total) return "0%";
  return `${Math.round((value / total) * 100)}%`;
}

function MiniBar({
  items,
  palette = distributionPalettes.severity,
}: {
  items: DistributionItem[];
  palette?: readonly string[];
}) {
  const total = items.reduce((sum, item) => sum + item.value, 0) || 1;
  return (
    <div className={styles.distributionWrap}>
      <div className={styles.miniBar}>
        {items.map((item, index) => {
          const color = palette[index % palette.length];
          const itemPercent = formatPercent(item.value, total);

          return (
            <div
              key={`${item.key}-${item.label}`}
              className={`${styles.miniSegment} ${toneClass(item.tone)}`}
              style={{ flex: item.value || 1, backgroundColor: color }}
              title={`${item.label}: ${item.value} (${itemPercent})`}
            >
              <span className={styles.segmentLabel}>{item.label}</span>
              <span className={styles.segmentValue}>{item.value}</span>
            </div>
          );
        })}
      </div>

      <div className={styles.distributionLegend}>
        {items.map((item, index) => {
          const color = palette[index % palette.length];
          const itemPercent = formatPercent(item.value, total);

          return (
            <article key={`${item.key}-${item.label}-legend`} className={styles.legendCard}>
              <div className={styles.legendHeader}>
                <span className={styles.legendSwatch} style={{ backgroundColor: color }} />
                <strong>{item.label}</strong>
              </div>
              <div className={styles.legendStats}>
                <span>{item.value}</span>
                <span>{itemPercent}</span>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}

function LineChart({
  trajectory,
}: {
  trajectory: Array<{ videoId: string; label: string; score: number | null; tier: string }>;
}) {
  const points = trajectory.filter((entry) => entry.score !== null);
  if (points.length === 0) {
    return null;
  }

  const width = 640;
  const height = 220;
  const paddingX = 36;
  const paddingY = 28;
  const chartWidth = width - paddingX * 2;
  const chartHeight = height - paddingY * 2;

  const coords = points.map((point, index) => {
    const x =
      paddingX +
      (points.length === 1 ? chartWidth / 2 : (chartWidth * index) / (points.length - 1));
    const y = paddingY + chartHeight - ((point.score ?? 0) / 100) * chartHeight;
    return { ...point, x, y };
  });

  const polyline = coords.map((point) => `${point.x},${point.y}`).join(" ");

  return (
    <div className={styles.chartWrap}>
      <svg viewBox={`0 0 ${width} ${height}`} className={styles.chart}>
        {[0, 25, 50, 75, 100].map((tick) => {
          const y = paddingY + chartHeight - (tick / 100) * chartHeight;
          return (
            <g key={tick}>
              <line x1={paddingX} y1={y} x2={width - paddingX} y2={y} className={styles.chartGrid} />
              <text x={8} y={y + 4} className={styles.chartAxisLabel}>
                {tick}
              </text>
            </g>
          );
        })}
        <polyline points={polyline} className={styles.chartLine} />
        {coords.map((point) => (
          <g key={point.videoId}>
            <circle cx={point.x} cy={point.y} r={5} className={styles.chartPoint} />
            <text x={point.x} y={height - 6} textAnchor="middle" className={styles.chartAxisLabel}>
              {point.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
  helper,
}: {
  label: string;
  value: string;
  onChange: ChangeEventHandler<HTMLSelectElement>;
  options: Array<{ value: string; label: string }>;
  helper?: string;
}) {
  return (
    <label className={styles.selectorBlock}>
      <span className={styles.selectorLabel}>{label}</span>
      <select className={styles.selectField} value={value} onChange={onChange}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {helper ? <span className={styles.selectorHelper}>{helper}</span> : null}
    </label>
  );
}

export function ShowcasePageClient({
  navigationItems,
  filterOptions,
  totalVideos,
  videos,
  testers,
  cohortOverview,
}: ShowcaseData) {
  const [language, setLanguage] = useState<Language>("en");
  const [view, setView] = useState<ViewKey>("single-video");
  const [selectedTier, setSelectedTier] = useState("All");
  const [selectedProject, setSelectedProject] = useState("All");
  const [selectedVideoId, setSelectedVideoId] = useState(videos[0]?.id ?? "");
  const [selectedTesterId, setSelectedTesterId] = useState(testers[0]?.id ?? "");
  const [activeTab, setActiveTab] = useState<TabKey>("overview");

  useEffect(() => {
    const storedLanguage = window.localStorage.getItem("showcase-language");
    if (storedLanguage === "en" || storedLanguage === "zh") {
      setLanguage(storedLanguage);
    }
  }, []);

  const localized = copy[language];

  const filteredVideos = useMemo(() => {
    return videos.filter((video) => {
      const tierMatch = selectedTier === "All" || video.performanceTier === selectedTier;
      const projectMatch = selectedProject === "All" || video.project === selectedProject;
      return tierMatch && projectMatch;
    });
  }, [selectedProject, selectedTier, videos]);

  useEffect(() => {
    if (!filteredVideos.some((video) => video.id === selectedVideoId)) {
      setSelectedVideoId(filteredVideos[0]?.id ?? "");
    }
  }, [filteredVideos, selectedVideoId]);

  const activeVideo = filteredVideos.find((video) => video.id === selectedVideoId) ?? filteredVideos[0] ?? videos[0];
  const activeTester = testers.find((tester) => tester.id === selectedTesterId) ?? testers[0];

  function handleToggleLanguage() {
    const nextLanguage = language === "en" ? "zh" : "en";
    setLanguage(nextLanguage);
    window.localStorage.setItem("showcase-language", nextLanguage);
  }

  return (
    <div className={styles.appShell}>
      <aside className={styles.sidebar}>
        <div className={styles.sidebarBrand}>
          <h2>{localized.productName}</h2>
          <p>{localized.sidebarCaption}</p>
        </div>

        <nav className={styles.sidebarNav}>
          {navigationItems.map((item) => {
            const viewKey = item.id as ViewKey;
            const active = item.id === view;

            return (
              <button
                key={item.id}
                type="button"
                className={active ? styles.navItemActive : styles.navItem}
                onClick={() => setView(viewKey)}
              >
                <span className={styles.navDotWrap}>
                  <span className={active ? styles.navDotActive : styles.navDot} />
                </span>
                <span className={styles.navText}>
                  <span>{localized.views[viewKey]}</span>
                  <span className={styles.navHint}>{localized.viewDescriptions[viewKey]}</span>
                </span>
              </button>
            );
          })}
        </nav>

        <div className={styles.sidebarControls}>
          {view === "single-video" ? (
            <>
              <SelectField
                label={localized.filters.tier}
                value={selectedTier}
                onChange={(event) => setSelectedTier(event.target.value)}
                helper={localized.helper.tier}
                options={filterOptions.tiers.map((option) => ({
                  value: option,
                  label:
                    option === "All"
                      ? localized.filters.all
                      : tierLabel(option, language),
                }))}
              />
              <SelectField
                label={localized.filters.project}
                value={selectedProject}
                onChange={(event) => setSelectedProject(event.target.value)}
                helper={localized.helper.project}
                options={filterOptions.projects.map((option) => ({
                  value: option,
                  label: option === "All" ? localized.filters.all : option,
                }))}
              />
              <p className={styles.sidebarMeta}>
                {localized.sidebar.showing} {filteredVideos.length} / {totalVideos} {localized.sidebar.videos}
              </p>
              <SelectField
                label={localized.filters.video}
                value={activeVideo?.id ?? ""}
                onChange={(event) => setSelectedVideoId(event.target.value)}
                options={filteredVideos.map((video) => ({
                  value: video.id,
                  label: video.label,
                }))}
              />
              {activeVideo ? (
                <div className={styles.sidebarDetails}>
                  <p>
                    <strong>{localized.labels.tester}:</strong> <span>{activeVideo.tester}</span>
                  </p>
                  <p>
                    <strong>{localized.labels.project}:</strong> <span>{activeVideo.project}</span>
                  </p>
                  <p>
                    <strong>{localized.labels.tier}:</strong> <span>{tierLabel(activeVideo.performanceTier, language)}</span>
                  </p>
                  <p>
                    <strong>{localized.sidebar.score}:</strong> {activeVideo.score}
                  </p>
                  <p>{t(activeVideo.reason, language)}</p>
                </div>
              ) : (
                <p className={styles.sidebarMeta}>{localized.empty.noVideos}</p>
              )}
            </>
          ) : null}

          {view === "tester-trajectory" ? (
            <>
              <SelectField
                label={localized.filters.tester}
                value={activeTester?.id ?? ""}
                onChange={(event) => setSelectedTesterId(event.target.value)}
                options={testers.map((tester) => ({ value: tester.id, label: tester.label }))}
              />
              {activeTester ? (
                <div className={styles.sidebarDetails}>
                  <p>
                    <strong>{localized.labels.tier}:</strong> <span>{tierLabel(activeTester.tier, language)}</span>
                  </p>
                  <p>
                    <strong>{localized.labels.aggregate}:</strong> {activeTester.aggregateScore}
                  </p>
                  <p>
                    <strong>{localized.labels.direction}:</strong> {t(activeTester.direction, language)}
                  </p>
                  <p>
                    <strong>{localized.labels.submissions}:</strong> {activeTester.submissionsScored}/{activeTester.submissionsTotal}
                  </p>
                </div>
              ) : null}
            </>
          ) : null}

          {view === "cohort-overview" ? (
            <div className={styles.sidebarDetails}>
              {cohortOverview.stats.map((item) => (
                <p key={item.label}>
                  <strong>{t(item.label, language)}:</strong> {item.value}
                </p>
              ))}
            </div>
          ) : null}
        </div>
      </aside>

      <div className={styles.contentShell}>
        <header className={styles.topBar}>
          <button type="button" className={styles.languageToggle} onClick={handleToggleLanguage}>
            {localized.toggle}
          </button>
        </header>

        <main className={styles.main}>
          <section className={styles.heroSection}>
            <div className={styles.heroRule} />
            <h1>{localized.title}</h1>
            <p>{localized.subtitle}</p>
          </section>

          {view === "single-video" && activeVideo ? (
            <>
              <section className={styles.summaryCard}>
                <div className={styles.summaryHeader}>
                  <div>
                    <h2>{activeVideo.label}</h2>
                    <p>{activeVideo.rawVideoId}</p>
                  </div>
                </div>

                <div className={styles.summaryStats}>
                  <div className={styles.summaryStat}>
                    <span>{localized.labels.tier}</span>
                    <strong className={styles.tierPill}>{tierLabel(activeVideo.performanceTier, language)}</strong>
                  </div>
                  <div className={styles.summaryStat}>
                    <span>{localized.labels.score}</span>
                    <strong>{activeVideo.score}</strong>
                  </div>
                  <div className={styles.summaryStat}>
                    <span>{localized.labels.findings}</span>
                    <strong>{activeVideo.findingsCount}</strong>
                  </div>
                  <div className={styles.summaryStat}>
                    <span>{localized.labels.windows}</span>
                    <strong>{activeVideo.windowCount}</strong>
                  </div>
                  <div className={styles.summaryStat}>
                    <span>{localized.labels.duration}</span>
                    <strong>{activeVideo.duration}</strong>
                  </div>
                </div>

                <p className={styles.capReason}>
                  {localized.labels.capReason}: {t(activeVideo.capReason, language)}
                </p>
              </section>

              <section className={styles.metaGrid}>
                <article className={styles.metaCard}>
                  <span>{localized.labels.tester}</span>
                  <strong>{activeVideo.tester}</strong>
                </article>
                <article className={styles.metaCard}>
                  <span>{localized.labels.project}</span>
                  <strong>{activeVideo.project}</strong>
                </article>
                <article className={styles.metaCard}>
                  <span>{localized.labels.topSeverity}</span>
                  <strong>{codedLabel(activeVideo.topSeverity, language, severityNotes)}</strong>
                </article>
                <article className={styles.metaCard}>
                  <span>{localized.labels.reason}</span>
                  <strong>{t(activeVideo.reason, language)}</strong>
                </article>
              </section>

              <p className={styles.reasoningText}>
                {localized.labels.tierReasoning}: {t(activeVideo.tierReasoning, language)}
              </p>

              <div className={styles.tabRow}>
                {(["overview", "findings", "coaching", "layer-detail"] as TabKey[]).map((tab) => (
                  <button
                    key={tab}
                    type="button"
                    className={activeTab === tab ? styles.activeTab : styles.tab}
                    onClick={() => setActiveTab(tab)}
                  >
                    {localized.tabs[tab]}
                    {tab === "findings" ? ` (${activeVideo.findingsCount})` : ""}
                    {tab === "coaching" ? ` (${activeVideo.recommendations.length})` : ""}
                  </button>
                ))}
              </div>

              {activeTab === "overview" ? (
                <>
                  <section className={styles.sectionBlock}>
                    <h3>{localized.headings.sessionAssessment}</h3>
                    <div className={styles.infoGrid}>
                      {activeVideo.sessionAssessment.map((item) => (
                        <article key={item.label} className={styles.infoCard}>
                          <span>{t(item.label, language)}</span>
                          <strong>{t(item.value, language)}</strong>
                        </article>
                      ))}
                    </div>
                  </section>

                  <section className={styles.sectionBlock}>
                    <h3>{localized.headings.scoreBreakdown}</h3>
                    <div className={styles.infoGrid}>
                      {activeVideo.scoreBreakdown.map((item) => (
                        <article key={item.label} className={styles.infoCard}>
                          <span>{t(item.label, language)}</span>
                          <strong>{item.value}</strong>
                        </article>
                      ))}
                    </div>
                    <p className={styles.footnote}>{localized.misc.footnote}</p>
                  </section>

                  <section className={styles.sectionBlock}>
                    <h3>{localized.headings.severityDistribution}</h3>
                    <MiniBar items={activeVideo.severityDistribution} palette={distributionPalettes.severity} />
                  </section>

                  <div className={styles.doubleSection}>
                    <section className={styles.sectionBlock}>
                      <h3>{localized.headings.frictionTypes}</h3>
                      <MiniBar items={activeVideo.frictionTypes} palette={distributionPalettes.friction} />
                    </section>
                    <section className={styles.sectionBlock}>
                      <h3>{localized.headings.sentiment}</h3>
                      <MiniBar items={activeVideo.sentimentDistribution} palette={distributionPalettes.sentiment} />
                    </section>
                  </div>
                </>
              ) : null}

              {activeTab === "findings" ? (
                <section className={styles.sectionBlock}>
                  <h3>{localized.headings.keyFindings}</h3>
                  <p className={styles.sectionCopy}>
                    {language === "zh"
                      ? "S = 严重级别，F = 摩擦类型。例如 S3 表示高强度摩擦，F5 表示系统行为不符合预期。"
                      : "S = severity level, F = friction type. For example, S3 means severe friction and F5 means unexpected behaviour."}
                  </p>
                  <div className={styles.infoGrid}>
                    <article className={styles.infoCard}>
                      <span>{localized.labels.totalFindings}</span>
                      <strong>{activeVideo.findingsCount}</strong>
                    </article>
                    <article className={styles.infoCard}>
                      <span>{localized.labels.topSeverity}</span>
                      <strong>{codedLabel(activeVideo.topSeverity, language, severityNotes)}</strong>
                    </article>
                    <article className={styles.infoCard}>
                      <span>{localized.labels.topFriction}</span>
                      <strong>
                        {activeVideo.findings[0]?.friction
                          ? codedLabel(activeVideo.findings[0].friction, language, frictionNotes)
                          : "N/A"}
                      </strong>
                    </article>
                    <article className={styles.infoCard}>
                      <span>{localized.labels.visibleTypes}</span>
                      <strong>{new Set(activeVideo.findings.map((finding) => finding.friction)).size}</strong>
                    </article>
                  </div>
                  {activeVideo.findings.length === 0 ? (
                    <p className={styles.sectionCopy}>{localized.empty.noFindings}</p>
                  ) : (
                    <div className={styles.stackList}>
                      {activeVideo.findings.map((finding) => (
                        <article key={`${finding.windowId}-${finding.note}`} className={styles.contentCard}>
                          <div className={styles.findingHeader}>
                            <span className={styles.findingBadge}>{codedLabel(finding.severity, language, severityNotes)}</span>
                            <span className={styles.findingBadgeMuted}>{codedLabel(finding.friction, language, frictionNotes)}</span>
                            <span className={styles.findingMeta}>{finding.windowId}</span>
                          </div>
                          <h4>{finding.note}</h4>
                          <p>{finding.rationale}</p>
                        </article>
                      ))}
                    </div>
                  )}
                </section>
              ) : null}

              {activeTab === "coaching" ? (
                <section className={styles.sectionBlock}>
                  <h3>{localized.headings.coaching}</h3>
                  <p className={styles.sectionCopy}>
                    {language === "zh"
                      ? "P = 建议优先级。例如 P4 表示模式级辅导建议，适合用于总结一类重复出现的问题。"
                      : "P = coaching priority. For example, P4 means a pattern-level coaching recommendation."}
                  </p>
                  {activeVideo.recommendations.length === 0 ? (
                    <p className={styles.sectionCopy}>{localized.empty.noCoaching}</p>
                  ) : (
                    <div className={styles.stackList}>
                      {activeVideo.recommendations.map((item) => (
                        <article key={item.title} className={styles.contentCard}>
                          <div className={styles.findingHeader}>
                            <span className={styles.findingBadgeMuted}>
                              {codedLabel(`P${item.priority}`, language, priorityNotes)}
                            </span>
                          </div>
                          <h4>{item.title}</h4>
                          <p>{item.detail}</p>
                        </article>
                      ))}
                    </div>
                  )}
                </section>
              ) : null}

              {activeTab === "layer-detail" ? (
                <>
                  <section className={styles.sectionBlock}>
                    <h3>{localized.headings.layerRules}</h3>
                    <div className={styles.infoGrid}>
                      <article className={styles.infoCard}>
                        <span>{localized.labels.totalFlags}</span>
                        <strong>{activeVideo.layerDetails.l1.totalFlags}</strong>
                      </article>
                      <article className={styles.infoCard}>
                        <span>{localized.labels.durationAnomaly}</span>
                        <strong>{activeVideo.layerDetails.l1.durationAnomaly ? localized.misc.yes : localized.misc.no}</strong>
                      </article>
                      <article className={styles.infoCard}>
                        <span>{localized.labels.flaggedWindows}</span>
                        <strong>{activeVideo.layerDetails.l1.flaggedWindows}</strong>
                      </article>
                    </div>
                  </section>
                  <section className={styles.sectionBlock}>
                    <h3>{localized.headings.layerClusters}</h3>
                    <div className={styles.infoGrid}>
                      <article className={styles.infoCard}>
                        <span>{localized.labels.coverage}</span>
                        <strong>{activeVideo.layerDetails.l2.coverage}</strong>
                      </article>
                      <article className={styles.infoCard}>
                        <span>{localized.labels.dominantCluster}</span>
                        <strong>{activeVideo.layerDetails.l2.dominantClusterId}</strong>
                      </article>
                      <article className={styles.infoCard}>
                        <span>{localized.labels.dominantPct}</span>
                        <strong>{activeVideo.layerDetails.l2.dominantClusterPct}</strong>
                      </article>
                    </div>
                    {activeVideo.layerDetails.l2.caveat ? (
                      <p className={styles.sectionCopy}>{activeVideo.layerDetails.l2.caveat}</p>
                    ) : null}
                  </section>
                </>
              ) : null}
            </>
          ) : null}

          {view === "tester-trajectory" && activeTester ? (
            <>
              <section className={styles.summaryCard}>
                <div className={styles.summaryHeader}>
                  <div>
                    <h2>{activeTester.tester}</h2>
                    <p>{activeTester.projects.join(" / ")}</p>
                  </div>
                </div>
                <div className={styles.summaryStats}>
                  <div className={styles.summaryStat}>
                    <span>{localized.labels.aggregate}</span>
                    <strong>{activeTester.aggregateScore}</strong>
                  </div>
                  <div className={styles.summaryStat}>
                    <span>{localized.labels.tier}</span>
                    <strong className={styles.tierPill}>{tierLabel(activeTester.tier, language)}</strong>
                  </div>
                  <div className={styles.summaryStat}>
                    <span>{localized.labels.direction}</span>
                    <strong>{t(activeTester.direction, language)}</strong>
                  </div>
                  <div className={styles.summaryStat}>
                    <span>{localized.labels.submissions}</span>
                    <strong>
                      {activeTester.submissionsScored}/{activeTester.submissionsTotal}
                    </strong>
                  </div>
                  <div className={styles.summaryStat}>
                    <span>{localized.labels.delta}</span>
                    <strong>{activeTester.delta}</strong>
                  </div>
                </div>
              </section>

              <section className={styles.sectionBlock}>
                <h3>{localized.headings.trajectory}</h3>
                {activeTester.trajectory.some((item) => item.score !== null) ? (
                  <>
                    <LineChart trajectory={activeTester.trajectory} />
                    <div className={styles.trajectoryGrid}>
                      {activeTester.trajectory.map((item) => (
                        <article key={item.videoId} className={styles.infoCard}>
                          <span>{item.label}</span>
                          <strong>{item.score === null ? "N/A" : `${Math.round(item.score)}/100`}</strong>
                          <p className={styles.cardMeta}>{tierLabel(item.tier, language)}</p>
                        </article>
                      ))}
                    </div>
                  </>
                ) : (
                  <p className={styles.sectionCopy}>{localized.empty.noTrajectory}</p>
                )}
              </section>

              <div className={styles.doubleSection}>
                <section className={styles.sectionBlock}>
                  <h3>{localized.labels.persistentFriction}</h3>
                  <div className={styles.chipRow}>
                    {activeTester.persistentFrictionTypes.map((item) => (
                      <span key={item} className={styles.grayChip}>
                        {item}
                      </span>
                    ))}
                  </div>
                </section>
                <section className={styles.sectionBlock}>
                  <h3>{localized.labels.sentimentRollup}</h3>
                  <MiniBar items={activeTester.sentimentDistribution} palette={distributionPalettes.sentiment} />
                </section>
              </div>

              <section className={styles.sectionBlock}>
                <div className={styles.infoGrid}>
                  <article className={styles.infoCard}>
                    <span>{localized.labels.lane}</span>
                    <strong>{activeTester.lanes.join(", ") || "N/A"}</strong>
                  </article>
                  <article className={styles.infoCard}>
                    <span>{localized.labels.ordering}</span>
                    <strong>{activeTester.orderingBasis}</strong>
                  </article>
                </div>
              </section>
            </>
          ) : null}

          {view === "cohort-overview" ? (
            <>
              <section className={styles.summaryCard}>
                <div className={styles.summaryHeader}>
                  <div>
                    <h2>{localized.headings.cohort}</h2>
                    <p>{language === "zh" ? `${totalVideos} 个正式开发视频` : `${totalVideos} official development videos`}</p>
                  </div>
                </div>
                <div className={styles.summaryStats}>
                  {cohortOverview.stats.map((item) => (
                    <div key={item.label} className={styles.summaryStat}>
                      <span>{t(item.label, language)}</span>
                      <strong>{item.value}</strong>
                    </div>
                  ))}
                </div>
              </section>

              <section className={styles.sectionBlock}>
                <h3>{localized.headings.tierDistribution}</h3>
                <MiniBar
                  items={cohortOverview.tierDistribution.map((item) => ({ ...item, key: item.label }))}
                  palette={distributionPalettes.severity}
                />
              </section>

              <section className={styles.sectionBlock}>
                <h3>{localized.labels.projectBreakdown}</h3>
                <div className={styles.projectGrid}>
                  {cohortOverview.projectBreakdown.map((project) => (
                    <article key={project.project} className={styles.contentCard}>
                      <h4>{project.project}</h4>
                      <p className={styles.cardMeta}>
                        {localized.labels.videos}: {project.videos} / {localized.labels.averageScore}: {project.averageScore}
                      </p>
                      <MiniBar
                        items={project.tiers.map((item) => ({ ...item, key: `${project.project}-${item.label}` }))}
                        palette={distributionPalettes.severity}
                      />
                    </article>
                  ))}
                </div>
              </section>
            </>
          ) : null}
        </main>
      </div>
    </div>
  );
}
