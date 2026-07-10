import { getShowcaseData } from "../lib/real-showcase-data";
import { siteCopy } from "../lib/site-copy";
import styles from "./page.module.css";

export default async function Page() {
  const { activeCase, cohortOverview, navigationItems, sidebarFilters, totalVideos, trajectoryData } =
    await getShowcaseData();

  return (
    <div className={styles.appShell}>
      <aside className={styles.sidebar}>
        <div className={styles.sidebarBrand}>
          <h2>{siteCopy.productName}</h2>
          <p>{siteCopy.sidebarCaption}</p>
        </div>

        <nav className={styles.sidebarNav}>
          {navigationItems.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={item.active ? styles.navItemActive : styles.navItem}
            >
              <span className={item.active ? styles.navDotActive : styles.navDot} />
              {item.label}
            </a>
          ))}
        </nav>

        <div className={styles.sidebarControls}>
          {sidebarFilters.map((filter) => (
            <button key={filter} type="button" className={styles.filterButton}>
              {filter}
              <span className={styles.chevron}>v</span>
            </button>
          ))}

          <p className={styles.sidebarMeta}>Showing {totalVideos} of {totalVideos} videos</p>
          <div className={styles.selectorBlock}>
            <span className={styles.selectorLabel}>Video ({totalVideos})</span>
            <button type="button" className={styles.videoSelect}>
              <span className={styles.navDotActive} />
              <span className={styles.videoSelectText}>{activeCase.label}</span>
              <span className={styles.chevron}>v</span>
            </button>
          </div>

          <div className={styles.sidebarDetails}>
            <p>
              <strong>Tester:</strong> <span>{activeCase.tester}</span>
            </p>
            <p>
              <strong>Project:</strong> <span>{activeCase.project}</span>
            </p>
            <p>
              <strong>Tier:</strong> <span>{activeCase.performanceTier}</span>
            </p>
            <p>{activeCase.reason}</p>
          </div>
        </div>
      </aside>

      <div className={styles.contentShell}>
        <header className={styles.topBar}>
          <span className={styles.deployLabel}>Deploy</span>
        </header>

        <main className={styles.main}>
          <section className={styles.heroSection}>
            <div className={styles.heroRule} />
            <h1>{siteCopy.pageTitle}</h1>
            <p>{siteCopy.pageSubtitle}</p>
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
                <span>TIER</span>
                <strong className={styles.tierPill}>{activeCase.performanceTier}</strong>
              </div>
              <div className={styles.summaryStat}>
                <span>SCORE</span>
                <strong>{activeCase.score}</strong>
              </div>
              <div className={styles.summaryStat}>
                <span>FINDINGS</span>
                <strong>{activeCase.findingsCount}</strong>
              </div>
              <div className={styles.summaryStat}>
                <span>WINDOWS</span>
                <strong>{activeCase.windowCount}</strong>
              </div>
              <div className={styles.summaryStat}>
                <span>DURATION</span>
                <strong>{activeCase.duration}</strong>
              </div>
            </div>

            <p className={styles.capReason}>Cap reasons: {activeCase.capReason}</p>
          </section>

          <section className={styles.metaGrid}>
            <article className={styles.metaCard}>
              <span>TESTER</span>
              <strong>{activeCase.tester}</strong>
            </article>
            <article className={styles.metaCard}>
              <span>PROJECT</span>
              <strong>{activeCase.project}</strong>
            </article>
            <article className={styles.metaCard}>
              <span>TOP SEVERITY</span>
              <strong>{activeCase.topSeverity}</strong>
            </article>
            <article className={styles.metaCard}>
              <span>REASON</span>
              <strong>{activeCase.reason}</strong>
            </article>
          </section>

          <p className={styles.reasoningText}>Tier reasoning: {activeCase.tierReasoning}</p>

          <div className={styles.tabRow}>
            <span className={styles.activeTab}>Overview</span>
            <span className={styles.tab}>Findings ({activeCase.findingsCount})</span>
            <span className={styles.tab}>Coaching ({activeCase.recommendations.length})</span>
            <span className={styles.tab}>Layer detail</span>
          </div>

          <section className={styles.sectionBlock}>
            <h3>SESSION-LEVEL ASSESSMENT (LAYER 3-B)</h3>
            <div className={styles.infoGrid}>
              {activeCase.sessionAssessment.map((item) => (
                <article key={item.label} className={styles.infoCard}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.sectionBlock}>
            <h3>R6 SCORE BREAKDOWN</h3>
            <div className={styles.infoGrid}>
              {activeCase.scoreBreakdown.map((item) => (
                <article key={item.label} className={styles.infoCard}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </article>
              ))}
            </div>
            <p className={styles.footnote}>
              Weights: D1 0.50 + D2 0.35 + D3 0.15 -&gt; raw composite. Caps bind after raw.
            </p>
          </section>

          <section className={styles.sectionBlock}>
            <h3>SEVERITY DISTRIBUTION</h3>
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
              <h3>FRICTION TYPES</h3>
              <div className={styles.miniBar}>
                {activeCase.frictionTypes.map((item) => (
                  <div key={item.label} className={styles.miniSegment} style={{ flex: item.value }}>
                    {item.label}
                  </div>
                ))}
              </div>
            </section>

            <section className={styles.sectionBlock}>
              <h3>SENTIMENT</h3>
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
            <h3>TESTER TRAJECTORY</h3>
            <p className={styles.sectionCopy}>{trajectoryData.summary}</p>
          </section>

          <section id="cohort-overview" className={styles.sectionBlock}>
            <h3>COHORT OVERVIEW</h3>
            <div className={styles.infoGrid}>
              {cohortOverview.stats.map((item) => (
                <article key={item.label} className={styles.infoCard}>
                  <span>{item.label}</span>
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
