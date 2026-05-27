import {
  capabilityChips,
  cohortOverview,
  contributions,
  demoCases,
  navigationItems,
  trajectoryData,
} from "../lib/demo-data";
import { siteCopy } from "../lib/site-copy";
import styles from "./page.module.css";

const activeCase = demoCases[0];
const maxTrajectoryScore = Math.max(...trajectoryData.sessions.map((session) => session.score));

export default function Page() {
  return (
    <div className={styles.appShell}>
      <aside className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <h2>{activeCase.label}</h2>
          <p>ID: {activeCase.workspaceId}</p>
        </div>

        <nav className={styles.sideNav}>
          {navigationItems.map((item, index) => (
            <a
              key={item.id}
              className={index === 0 ? styles.navLinkActive : styles.navLink}
              href={`#${item.id}`}
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className={styles.sidebarFooter}>
          <button type="button" className={styles.auditButton}>
            Run New Audit
          </button>
          <div className={styles.supportLinks}>
            <span>Documentation</span>
            <span>Support</span>
          </div>
        </div>
      </aside>

      <div className={styles.contentShell}>
        <header className={styles.topBar}>
          <div className={styles.brand}>{siteCopy.productName}</div>
          <div className={styles.topTabs}>
            <span className={styles.topTabActive}>Dashboard</span>
            <span className={styles.topTab}>Sessions</span>
            <span className={styles.topTab}>Reports</span>
            <span className={styles.topTab}>Settings</span>
          </div>
          <div className={styles.topActions}>
            <span>Alerts</span>
            <span>Profile</span>
          </div>
        </header>

        <main className={styles.main}>
          <section className={styles.hero}>
            <p className={styles.owner}>{siteCopy.ownerName}</p>
            <h1>{siteCopy.projectName}</h1>
            <p className={styles.heroLead}>{siteCopy.intro}</p>
            <p className={styles.heroSubLead}>{siteCopy.subIntro}</p>
            <div className={styles.chipRow}>
              {capabilityChips.map((chip) => (
                <span key={chip} className={styles.chip}>
                  {chip}
                </span>
              ))}
            </div>
          </section>

          <section id="single-video" className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2>Single Video Review</h2>
              <p>{activeCase.summary.reportQuality}</p>
            </div>

            <div className={styles.singleVideoGrid}>
              <article className={styles.videoStageCard}>
                <div className={styles.videoStage}>
                  <div className={styles.videoGlow} />
                  <div className={styles.playButton}>▶</div>
                  <div className={styles.videoOverlay}>
                    <span>SESSION: {activeCase.sessionId}</span>
                    <span>{activeCase.duration}</span>
                  </div>
                </div>
                <div className={styles.videoSummary}>
                  <div>
                    <p className={styles.panelLabel}>Session Summary</p>
                    <h3>{activeCase.summary.title}</h3>
                  </div>
                  <div className={styles.metricBadges}>
                    <span className={styles.tierBadge}>{activeCase.summary.tier}</span>
                    <span className={styles.scoreBadge}>{activeCase.summary.score}/100</span>
                  </div>
                </div>
                <p className={styles.analystNote}>{activeCase.analystNote}</p>
                <div className={styles.metricsRow}>
                  {activeCase.metrics.map((metric) => (
                    <div key={metric.label} className={styles.metricCard}>
                      <span>{metric.label}</span>
                      <strong>{metric.value}</strong>
                    </div>
                  ))}
                </div>
              </article>

              <aside className={styles.inspectorCard}>
                <h3>Inspector Findings</h3>
                <div className={styles.findingStack}>
                  {activeCase.findings.map((finding) => (
                    <article key={`${finding.timestamp}-${finding.note}`} className={styles.findingCard}>
                      <div className={styles.findingTopRow}>
                        <span
                          className={
                            finding.severity === "High Risk"
                              ? styles.riskChip
                              : finding.severity === "Recording"
                                ? styles.recordingChip
                                : styles.standardChip
                          }
                        >
                          {finding.severity}
                        </span>
                        <span className={styles.timestamp}>{finding.timestamp}</span>
                      </div>
                      <p className={styles.findingText}>{finding.note}</p>
                      <div className={styles.coachingRow}>
                        <span>Coaching</span>
                        <p>{finding.coaching}</p>
                      </div>
                    </article>
                  ))}
                </div>
              </aside>
            </div>
          </section>

          <section id="tester-trajectory" className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2>Tester Trajectory</h2>
              <p>{trajectoryData.subtitle}</p>
            </div>

            <div className={styles.trajectoryCard}>
              <div className={styles.chart}>
                {trajectoryData.sessions.map((session) => (
                  <div key={session.label} className={styles.barColumn}>
                    <div
                      className={styles.bar}
                      style={{ height: `${Math.max(20, (session.score / maxTrajectoryScore) * 100)}%` }}
                    />
                    <span>{session.label}</span>
                  </div>
                ))}
              </div>

              <div className={styles.trajectoryNotes}>
                <div>
                  <p className={styles.panelLabel}>Persistent Friction</p>
                  <ul className={styles.bulletList}>
                    {trajectoryData.persistentFriction.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className={styles.panelLabel}>Performance Summary</p>
                  <p className={styles.noteBody}>{trajectoryData.summary}</p>
                </div>
              </div>
            </div>
          </section>

          <section id="cohort-overview" className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2>Cohort Overview</h2>
              <p>Aggregated quality, escalation, and reviewer coverage across the broader demo scope.</p>
            </div>

            <div className={styles.statsGrid}>
              {cohortOverview.stats.map((stat) => (
                <article
                  key={stat.label}
                  className={
                    stat.tone === "warning"
                      ? styles.statCardWarning
                      : stat.tone === "muted"
                        ? styles.statCardMuted
                        : styles.statCard
                  }
                >
                  <span>{stat.label}</span>
                  <strong>{stat.value}</strong>
                </article>
              ))}
            </div>

            <div className={styles.cohortPanels}>
              {cohortOverview.panels.map((panel) => (
                <article key={panel.title} className={styles.cohortPanel}>
                  <p className={styles.panelLabel}>{panel.title}</p>
                  <p className={styles.noteBody}>{panel.body}</p>
                </article>
              ))}
            </div>
          </section>

          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2>What I Completed</h2>
              <p>Core implementation and final presentation responsibilities carried through the project demo.</p>
            </div>

            <div className={styles.contributionCard}>
              {contributions.map((item) => (
                <article key={item.title} className={styles.contributionItem}>
                  <div className={styles.checkMark}>✓</div>
                  <div>
                    <h3>{item.title}</h3>
                    <p>{item.detail}</p>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
