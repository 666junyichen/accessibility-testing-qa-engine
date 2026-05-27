"use client";

import { useState } from "react";
import { demoCases } from "../lib/demo-data";
import styles from "./demo-panel.module.css";

export function DemoPanel() {
  const [selectedId, setSelectedId] = useState(demoCases[0]?.id ?? "");
  const selectedCase =
    demoCases.find((demoCase) => demoCase.id === selectedId) ?? demoCases[0];

  if (!selectedCase) {
    return <p className={styles.empty}>Demo data is unavailable.</p>;
  }

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <p className={styles.sidebarLabel}>Sample Cases</p>
        <div className={styles.caseList}>
          {demoCases.map((demoCase) => (
            <button
              key={demoCase.id}
              type="button"
              className={demoCase.id === selectedCase.id ? styles.caseButtonActive : styles.caseButton}
              onClick={() => setSelectedId(demoCase.id)}
            >
              <span>{demoCase.label}</span>
              <small>{demoCase.sector}</small>
            </button>
          ))}
        </div>
      </aside>

      <div className={styles.panel}>
        <section className={styles.summaryCard}>
          <div>
            <p className={styles.eyebrow}>Summary</p>
            <h3>{selectedCase.summary.title}</h3>
          </div>
          <div className={styles.badgeRow}>
            <span className={styles.tierBadge}>{selectedCase.summary.tier}</span>
            <span className={styles.scoreBadge}>{selectedCase.summary.score}/100</span>
          </div>
          <p className={styles.reportQuality}>{selectedCase.summary.reportQuality}</p>
          <div className={styles.metrics}>
            {selectedCase.metrics.map((metric) => (
              <div key={metric.label} className={styles.metricCard}>
                <p>{metric.label}</p>
                <strong>{metric.value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.columns}>
          <article className={styles.card}>
            <p className={styles.eyebrow}>Findings</p>
            <div className={styles.stack}>
              {selectedCase.findings.map((finding) => (
                <div key={`${finding.severity}-${finding.friction}-${finding.note}`} className={styles.findingCard}>
                  <div className={styles.findingMeta}>
                    <span className={styles.severity}>{finding.severity}</span>
                    <span className={styles.friction}>{finding.friction}</span>
                  </div>
                  <p>{finding.note}</p>
                </div>
              ))}
            </div>
          </article>

          <article className={styles.card}>
            <p className={styles.eyebrow}>Coaching</p>
            <div className={styles.stack}>
              {selectedCase.recommendations.map((recommendation) => (
                <div key={recommendation.title} className={styles.recommendationCard}>
                  <h4>{recommendation.title}</h4>
                  <p>{recommendation.detail}</p>
                </div>
              ))}
            </div>
          </article>
        </section>
      </div>
    </div>
  );
}
