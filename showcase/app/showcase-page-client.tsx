"use client";

import { useEffect, useState } from "react";
import { siteCopy } from "../lib/site-copy";
import styles from "./page.module.css";

type Language = "en" | "zh";

type ShowcaseData = {
  activeCase: {
    label: string;
    tester: string;
    project: string;
    performanceTier: string;
    score: string;
    findingsCount: number;
    windowCount: number;
    duration: string;
    capReason: string;
    topSeverity: string;
    reason: string;
    tierReasoning: string;
    recommendations: Array<{ title: string; detail: string }>;
    sessionAssessment: Array<{ label: string; value: string }>;
    scoreBreakdown: Array<{ label: string; value: string }>;
    severityDistribution: Array<{ label: string; value: number; tone: string }>;
    frictionTypes: Array<{ label: string; value: number }>;
    sentimentDistribution: Array<{ label: string; value: number }>;
  };
  cohortOverview: {
    stats: Array<{ label: string; value: string; tone: string }>;
  };
  navigationItems: Array<{ id: string; label: string; active: boolean }>;
  sidebarFilters: string[];
  totalVideos: number;
  trajectoryData: {
    summary: string;
  };
};

const translations = {
  en: {
    productName: siteCopy.productName,
    sidebarCaption: siteCopy.sidebarCaption,
    pageTitle: siteCopy.pageTitle,
    pageSubtitle: siteCopy.pageSubtitle,
    showing: "Showing",
    of: "of",
    videos: "videos",
    video: "Video",
    tester: "Tester",
    project: "Project",
    tier: "Tier",
    deploy: "中文",
    summaryStats: {
      tier: "TIER",
      score: "SCORE",
      findings: "FINDINGS",
      windows: "WINDOWS",
      duration: "DURATION",
    },
    capReasons: "Cap reasons",
    topSeverity: "TOP SEVERITY",
    reason: "REASON",
    tierReasoning: "Tier reasoning",
    tabs: {
      overview: "Overview",
      findings: "Findings",
      coaching: "Coaching",
      layerDetail: "Layer detail",
    },
    sections: {
      sessionAssessment: "SESSION-LEVEL ASSESSMENT (LAYER 3-B)",
      scoreBreakdown: "R6 SCORE BREAKDOWN",
      severityDistribution: "SEVERITY DISTRIBUTION",
      frictionTypes: "FRICTION TYPES",
      sentiment: "SENTIMENT",
      trajectory: "TESTER TRAJECTORY",
      cohort: "COHORT OVERVIEW",
    },
    footnote: "Weights: D1 0.50 + D2 0.35 + D3 0.15 -> raw composite. Caps bind after raw.",
  },
  zh: {
    productName: "SMP 演示",
    sidebarCaption: "测试员质量评估与辅导原型",
    pageTitle: "智能测试员质量评估",
    pageSubtitle: "See Me Please 决策支持原型",
    showing: "显示",
    of: "/",
    videos: "个视频",
    video: "视频",
    tester: "测试员",
    project: "项目",
    tier: "等级",
    deploy: "EN",
    summaryStats: {
      tier: "等级",
      score: "分数",
      findings: "发现项",
      windows: "窗口数",
      duration: "时长",
    },
    capReasons: "封顶原因",
    topSeverity: "最高严重级别",
    reason: "原因",
    tierReasoning: "等级判断",
    tabs: {
      overview: "总览",
      findings: "发现项",
      coaching: "辅导建议",
      layerDetail: "分层细节",
    },
    sections: {
      sessionAssessment: "会话级评估（LAYER 3-B）",
      scoreBreakdown: "R6 分数拆解",
      severityDistribution: "严重级别分布",
      frictionTypes: "摩擦类型",
      sentiment: "情绪分布",
      trajectory: "测试员轨迹",
      cohort: "群组概览",
    },
    footnote: "权重：D1 0.50 + D2 0.35 + D3 0.15 -> 原始综合分。封顶规则会在原始分之后生效。",
  },
} as const;

const phraseMap: Record<string, string> = {
  poor: "较弱",
  "task-blocking friction: S1/S2 present": "存在 S1/S2 级任务阻塞摩擦",
  ">=2 S2 task-blockers": "至少 2 个 S2 级任务阻塞",
  rich: "完整",
  acceptable: "可接受",
  none: "无",
  "Raw composite": "原始综合分",
  "D1 Narration": "D1 讲述质量",
  "D2 Friction": "D2 摩擦识别",
  "D3 Recording": "D3 录制质量",
  Narration: "讲述质量",
  Recording: "录制质量",
  "Coaching evidence": "辅导证据",
  "Total audits": "总评审数",
  "Avg score": "平均分",
  "Critical sessions": "关键问题会话",
  "Leading reviews": "高表现评审",
};

function translateText(value: string, language: Language) {
  if (language === "en") {
    return value;
  }

  return phraseMap[value] ?? value;
}

function translateFilter(value: string, language: Language) {
  if (language === "en") {
    return value;
  }

  return value
    .replace("Tier", "等级")
    .replace("Project", "项目")
    .replace("all", "全部");
}

function translateNav(value: string, language: Language) {
  if (language === "en") {
    return value;
  }

  const map: Record<string, string> = {
    "Single Video": "单视频",
    "Tester Trajectory": "测试员轨迹",
    "Cohort Overview": "群组概览",
  };

  return map[value] ?? value;
}

function translateTrajectorySummary(value: string, language: Language) {
  if (language === "en") {
    return value;
  }

  return value
    .replace("Across", "基于")
    .replace("processed submissions, scores range from", "个已处理提交，分数范围从")
    .replace("to", "到")
    .replace(
      "Task-blocking cap reasons recur in",
      "任务阻塞类封顶原因在",
    )
    .replace("submission(s), so blocked-pathway handling remains the main coaching priority.", "个提交中重复出现，因此对阻塞路径的处理仍然是主要辅导重点。");
}

export function ShowcasePageClient({
  activeCase,
  cohortOverview,
  navigationItems,
  sidebarFilters,
  totalVideos,
  trajectoryData,
}: ShowcaseData) {
  const [language, setLanguage] = useState<Language>("en");
  const copy = translations[language];

  useEffect(() => {
    const storedLanguage = window.localStorage.getItem("showcase-language");
    if (storedLanguage === "en" || storedLanguage === "zh") {
      setLanguage(storedLanguage);
    }
  }, []);

  function handleToggleLanguage() {
    const nextLanguage = language === "en" ? "zh" : "en";
    setLanguage(nextLanguage);
    window.localStorage.setItem("showcase-language", nextLanguage);
  }

  return (
    <div className={styles.appShell}>
      <aside className={styles.sidebar}>
        <div className={styles.sidebarBrand}>
          <h2>{copy.productName}</h2>
          <p>{copy.sidebarCaption}</p>
        </div>

        <nav className={styles.sidebarNav}>
          {navigationItems.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={item.active ? styles.navItemActive : styles.navItem}
            >
              <span className={item.active ? styles.navDotActive : styles.navDot} />
              {translateNav(item.label, language)}
            </a>
          ))}
        </nav>

        <div className={styles.sidebarControls}>
          {sidebarFilters.map((filter) => (
            <button key={filter} type="button" className={styles.filterButton}>
              {translateFilter(filter, language)}
              <span className={styles.chevron}>v</span>
            </button>
          ))}

          <p className={styles.sidebarMeta}>
            {copy.showing} {totalVideos} {copy.of} {totalVideos} {copy.videos}
          </p>
          <div className={styles.selectorBlock}>
            <span className={styles.selectorLabel}>
              {copy.video} ({totalVideos})
            </span>
            <button type="button" className={styles.videoSelect}>
              <span className={styles.navDotActive} />
              <span className={styles.videoSelectText}>{activeCase.label}</span>
              <span className={styles.chevron}>v</span>
            </button>
          </div>

          <div className={styles.sidebarDetails}>
            <p>
              <strong>{copy.tester}:</strong> <span>{activeCase.tester}</span>
            </p>
            <p>
              <strong>{copy.project}:</strong> <span>{activeCase.project}</span>
            </p>
            <p>
              <strong>{copy.tier}:</strong> <span>{translateText(activeCase.performanceTier.toLowerCase(), language)}</span>
            </p>
            <p>{translateText(activeCase.reason, language)}</p>
          </div>
        </div>
      </aside>

      <div className={styles.contentShell}>
        <header className={styles.topBar}>
          <button type="button" className={styles.languageToggle} onClick={handleToggleLanguage}>
            {copy.deploy}
          </button>
        </header>

        <main className={styles.main}>
          <section className={styles.heroSection}>
            <div className={styles.heroRule} />
            <h1>{copy.pageTitle}</h1>
            <p>{copy.pageSubtitle}</p>
          </section>

          <section id="single-video" className={styles.summaryCard}>
            <div className={styles.summaryHeader}>
              <div>
                <h2>{activeCase.label}</h2>
                <p>
                  {activeCase.tester} - {activeCase.project}
                </p>
              </div>
            </div>

            <div className={styles.summaryStats}>
              <div className={styles.summaryStat}>
                <span>{copy.summaryStats.tier}</span>
                <strong className={styles.tierPill}>
                  {translateText(activeCase.performanceTier.toLowerCase(), language)}
                </strong>
              </div>
              <div className={styles.summaryStat}>
                <span>{copy.summaryStats.score}</span>
                <strong>{activeCase.score}</strong>
              </div>
              <div className={styles.summaryStat}>
                <span>{copy.summaryStats.findings}</span>
                <strong>{activeCase.findingsCount}</strong>
              </div>
              <div className={styles.summaryStat}>
                <span>{copy.summaryStats.windows}</span>
                <strong>{activeCase.windowCount}</strong>
              </div>
              <div className={styles.summaryStat}>
                <span>{copy.summaryStats.duration}</span>
                <strong>{activeCase.duration}</strong>
              </div>
            </div>

            <p className={styles.capReason}>
              {copy.capReasons}: {translateText(activeCase.capReason, language)}
            </p>
          </section>

          <section className={styles.metaGrid}>
            <article className={styles.metaCard}>
              <span>{copy.tester}</span>
              <strong>{activeCase.tester}</strong>
            </article>
            <article className={styles.metaCard}>
              <span>{copy.project}</span>
              <strong>{activeCase.project}</strong>
            </article>
            <article className={styles.metaCard}>
              <span>{copy.topSeverity}</span>
              <strong>{activeCase.topSeverity}</strong>
            </article>
            <article className={styles.metaCard}>
              <span>{copy.reason}</span>
              <strong>{translateText(activeCase.reason, language)}</strong>
            </article>
          </section>

          <p className={styles.reasoningText}>
            {copy.tierReasoning}: {translateText(activeCase.tierReasoning, language)}
          </p>

          <div className={styles.tabRow}>
            <span className={styles.activeTab}>{copy.tabs.overview}</span>
            <span className={styles.tab}>
              {copy.tabs.findings} ({activeCase.findingsCount})
            </span>
            <span className={styles.tab}>
              {copy.tabs.coaching} ({activeCase.recommendations.length})
            </span>
            <span className={styles.tab}>{copy.tabs.layerDetail}</span>
          </div>

          <section className={styles.sectionBlock}>
            <h3>{copy.sections.sessionAssessment}</h3>
            <div className={styles.infoGrid}>
              {activeCase.sessionAssessment.map((item) => (
                <article key={item.label} className={styles.infoCard}>
                  <span>{translateText(item.label, language)}</span>
                  <strong>{translateText(item.value, language)}</strong>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.sectionBlock}>
            <h3>{copy.sections.scoreBreakdown}</h3>
            <div className={styles.infoGrid}>
              {activeCase.scoreBreakdown.map((item) => (
                <article key={item.label} className={styles.infoCard}>
                  <span>{translateText(item.label, language)}</span>
                  <strong>{item.value}</strong>
                </article>
              ))}
            </div>
            <p className={styles.footnote}>{copy.footnote}</p>
          </section>

          <section className={styles.sectionBlock}>
            <h3>{copy.sections.severityDistribution}</h3>
            <div className={styles.distributionBar}>
              {activeCase.severityDistribution.map((item) => (
                <div
                  key={item.label}
                  className={`${styles.distributionSegment} ${styles[`tone${item.tone[0].toUpperCase()}${item.tone.slice(1)}`] ?? ""}`}
                  style={{ flex: item.value }}
                >
                  {item.label}
                </div>
              ))}
            </div>
          </section>

          <div className={styles.doubleSection}>
            <section className={styles.sectionBlock}>
              <h3>{copy.sections.frictionTypes}</h3>
              <div className={styles.miniBar}>
                {activeCase.frictionTypes.map((item) => (
                  <div key={item.label} className={styles.miniSegment} style={{ flex: item.value }}>
                    {item.label}
                  </div>
                ))}
              </div>
            </section>

            <section className={styles.sectionBlock}>
              <h3>{copy.sections.sentiment}</h3>
              <div className={styles.miniBar}>
                {activeCase.sentimentDistribution.map((item) => (
                  <div key={item.label} className={styles.miniSegment} style={{ flex: item.value }}>
                    {item.label}
                  </div>
                ))}
              </div>
            </section>
          </div>

          <section id="tester-trajectory" className={styles.sectionBlock}>
            <h3>{copy.sections.trajectory}</h3>
            <p className={styles.sectionCopy}>{translateTrajectorySummary(trajectoryData.summary, language)}</p>
          </section>

          <section id="cohort-overview" className={styles.sectionBlock}>
            <h3>{copy.sections.cohort}</h3>
            <div className={styles.infoGrid}>
              {cohortOverview.stats.map((item) => (
                <article key={item.label} className={styles.infoCard}>
                  <span>{translateText(item.label, language)}</span>
                  <strong>{item.value}</strong>
                </article>
              ))}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
