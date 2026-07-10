import { existsSync } from "node:fs";
import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { sanitizePublicLabel } from "./sanitize.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const candidateRoots = [path.resolve(__dirname, ".."), path.resolve(__dirname, "..", "..")];

const projectLabelMap = {
  "department-of-premier-and-cabinet-wa": "DPC-WA",
  "suncorp-insurance": "Suncorp",
  "the-university-of-queensland": "Junyi Chen",
};

function resolveDataPath(...segments) {
  for (const root of candidateRoots) {
    const candidate = path.join(root, "data", "processed", ...segments);
    if (existsSync(candidate)) {
      return candidate;
    }
  }

  return path.join(candidateRoots[0], "data", "processed", ...segments);
}

function parseCsv(text) {
  const rows = [];
  let current = "";
  let row = [];
  let inQuotes = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];

    if (char === "\"") {
      if (inQuotes && next === "\"") {
        current += "\"";
        index += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === "," && !inQuotes) {
      row.push(current);
      current = "";
      continue;
    }

    if ((char === "\n" || char === "\r") && !inQuotes) {
      if (char === "\r" && next === "\n") {
        index += 1;
      }
      row.push(current);
      current = "";
      if (row.some((cell) => cell.length > 0)) {
        rows.push(row);
      }
      row = [];
      continue;
    }

    current += char;
  }

  if (current.length > 0 || row.length > 0) {
    row.push(current);
    rows.push(row);
  }

  const [headers = [], ...values] = rows;
  return values.map((cells) =>
    Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ""])),
  );
}

function safeNumber(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function formatDuration(durationSec) {
  const totalSeconds = Math.round(safeNumber(durationSec));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m ${seconds}s`;
  }

  return `${minutes}m ${seconds}s`;
}

function formatProjectLabel(project) {
  const mapped = projectLabelMap[project];
  if (mapped) {
    return mapped;
  }

  const title = String(project ?? "")
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

  return sanitizePublicLabel(title);
}

function normalizeTier(value) {
  const tier = String(value ?? "").trim();
  if (!tier) {
    return "Unknown";
  }

  const lower = tier.toLowerCase();
  if (lower === "poor") {
    return "Developing";
  }
  if (lower === "acceptable") {
    return "Proficient";
  }
  if (lower === "good") {
    return "Leading";
  }

  return tier.charAt(0).toUpperCase() + tier.slice(1);
}

function buildDistribution(entries, toneByKey = {}) {
  return Object.entries(entries ?? {}).map(([label, count]) => ({
    key: label,
    label: `${label} - ${count}`,
    value: safeNumber(count),
    tone: toneByKey[label] ?? "neutral",
  }));
}

function averageScore(rows) {
  const scores = rows.map((row) => safeNumber(row.score, Number.NaN)).filter((value) => Number.isFinite(value));
  if (scores.length === 0) {
    return "0.0";
  }

  return (scores.reduce((sum, value) => sum + value, 0) / scores.length).toFixed(1);
}

function parseJsonLikeObject(value) {
  if (!value || typeof value !== "string") {
    return {};
  }

  try {
    return JSON.parse(value);
  } catch {
    try {
      return JSON.parse(value.replace(/'/g, "\""));
    } catch {
      return {};
    }
  }
}

function firstReason(report, summaryRow) {
  return (
    summaryRow?.reason ||
    report?.overall?.reasoning?.[0] ||
    "No report-quality reason was generated."
  );
}

function tierTone(tier) {
  const value = String(tier ?? "").toLowerCase();
  if (value.includes("leading")) {
    return "good";
  }
  if (value.includes("proficient")) {
    return "cool";
  }
  if (value.includes("developing")) {
    return "warm";
  }
  if (value.includes("foundational") || value.includes("poor")) {
    return "warning";
  }
  return "neutral";
}

function buildVideoLabel(videoId, tester, projectLabel) {
  return sanitizePublicLabel(`${tester} - ${projectLabel} - ${videoId.replaceAll("_", " ")}`);
}

function buildSingleVideoData(videoId, report, summaryRow, submissionRow) {
  const topSeverity = report?.l3_findings?.top_severity || summaryRow?.top_severity || "N/A";
  const score = safeNumber(submissionRow?.score, Number.NaN);
  const tier = normalizeTier(submissionRow?.tier || report?.overall?.quality_tier || summaryRow?.tier);
  const reason = firstReason(report, summaryRow);
  const projectLabel = formatProjectLabel(report?.project || summaryRow?.project);
  const tester = report?.tester_name || summaryRow?.tester || submissionRow?.tester_name || "Unknown tester";
  const duration = report?.duration_sec ? formatDuration(report.duration_sec) : formatDuration(summaryRow?.duration_s);
  const findingsCount = safeNumber(report?.l3_findings?.total_findings ?? summaryRow?.l3_findings);
  const windowCount = safeNumber(report?.total_windows ?? summaryRow?.windows);

  return {
    id: videoId,
    label: buildVideoLabel(videoId, tester, projectLabel),
    rawVideoId: videoId,
    tester,
    project: projectLabel,
    performanceTier: tier,
    score: Number.isFinite(score) ? `${Math.round(score)}/100` : "N/A",
    scoreValue: Number.isFinite(score) ? score : null,
    findingsCount,
    windowCount,
    duration,
    capReason: submissionRow?.cap_reasons || "No cap applied",
    topSeverity,
    reason,
    tierReasoning: reason,
    summary: {
      title: reason,
      tier,
      score: Number.isFinite(score) ? Math.round(score) : null,
    },
    findings: (report?.l3_findings?.top_findings || []).map((finding) => ({
      severity: finding.severity_s,
      friction: finding.friction_type,
      note: sanitizePublicLabel(finding.finding),
      rationale: sanitizePublicLabel(finding.rationale || ""),
      sentiment: finding.sentiment_e || "N/A",
      windowId: finding.window_id || "",
    })),
    recommendations: (report?.coaching_recommendations || []).map((recommendation) => ({
      title: sanitizePublicLabel(recommendation.title),
      detail: sanitizePublicLabel(recommendation.summary),
      priority: safeNumber(recommendation.priority, 99),
    })),
    sessionAssessment: [
      { label: "Narration", value: report?.l3_assessment?.narration_quality || "N/A" },
      { label: "Recording", value: report?.l3_assessment?.recording_quality || "N/A" },
      { label: "Coaching evidence", value: report?.l3_assessment?.coaching_evidence || "N/A" },
    ],
    scoreBreakdown: [
      { label: "Raw composite", value: submissionRow?.raw_score || "N/A" },
      { label: "D1 Narration", value: submissionRow?.d1_narration || "N/A" },
      { label: "D2 Friction", value: submissionRow?.d2_friction_surfacing || "N/A" },
      { label: "D3 Recording", value: submissionRow?.d3_recording || "N/A" },
    ],
    severityDistribution: buildDistribution(report?.l3_findings?.by_severity, {
      S1: "warning",
      S2: "warning",
      S3: "warm",
      S4: "good",
      S5: "neutral",
      S6: "cool",
    }),
    frictionTypes: buildDistribution(report?.l3_findings?.by_friction_type),
    sentimentDistribution: buildDistribution(report?.l3_findings?.by_sentiment),
    layerDetails: {
      l1: {
        totalFlags: safeNumber(report?.l1?.total_flags),
        durationAnomaly: Boolean(report?.l1?.duration_anomaly),
        flaggedWindows: (report?.l1?.flagged_window_ids || []).length,
      },
      l2: {
        coverage: report?.l2?.coverage ?? "N/A",
        dominantClusterId: report?.l2?.dominant_cluster_id ?? "N/A",
        dominantClusterPct: report?.l2?.dominant_cluster_pct ?? "N/A",
        caveat: report?.l2?.caveat || "",
      },
    },
  };
}

function buildTesterData(perTesterRows) {
  return perTesterRows.map((row) => {
    const projects = String(row.projects || "")
      .split(",")
      .filter(Boolean)
      .map((project) => formatProjectLabel(project));
    const submissionIds = String(row.submission_video_ids || "").split(",").filter(Boolean);
    const submissionScores = String(row.submission_scores || "")
      .split(",")
      .map((value) => safeNumber(value, Number.NaN));
    const submissionTiers = String(row.submission_tiers || "").split(",").filter(Boolean);
    const trajectory = submissionIds.map((videoId, index) => ({
      videoId,
      label: projects[index] || sanitizePublicLabel(videoId.replaceAll("_", " ")),
      score: Number.isFinite(submissionScores[index]) ? submissionScores[index] : null,
      tier: normalizeTier(submissionTiers[index] || ""),
    }));

    return {
      id: row.tester_name,
      tester: row.tester_name,
      label: `${row.tester_name} (${safeNumber(row.submission_count)} submissions)`,
      tier: normalizeTier(row.tier),
      aggregateScore: row.score,
      direction: row.direction || "stable",
      delta: row.delta_first_to_last || "0",
      submissionsScored: safeNumber(row.submission_count_scored),
      submissionsTotal: safeNumber(row.submission_count),
      projects,
      persistentFrictionTypes: String(row.persistent_friction_types || "").split(",").filter(Boolean),
      sentimentDistribution: buildDistribution(parseJsonLikeObject(row.sentiment_distribution)),
      lanes: String(row.cross_check_lanes || "").split(",").filter(Boolean),
      orderingBasis: row.ordering_basis || "project order",
      trajectory,
    };
  });
}

function buildCohortOverview(summaryRows, submissionRows) {
  const projectLabels = Array.from(new Set(summaryRows.map((row) => formatProjectLabel(row.project))));
  const tierCounts = submissionRows.reduce((accumulator, row) => {
    const tier = normalizeTier(row.tier);
    accumulator[tier] = (accumulator[tier] || 0) + 1;
    return accumulator;
  }, {});

  const projectBreakdown = projectLabels.map((projectLabel) => {
    const projectRows = submissionRows.filter((row) => formatProjectLabel(row.project) === projectLabel);
    const tiers = ["Leading", "Proficient", "Developing", "Foundational"].map((tier) => ({
      label: tier,
      value: projectRows.filter((row) => normalizeTier(row.tier) === tier).length,
      tone: tierTone(tier),
    }));

    return {
      project: projectLabel,
      videos: projectRows.length,
      averageScore:
        projectRows.length > 0
          ? (
              projectRows.reduce((sum, row) => sum + safeNumber(row.score), 0) /
              projectRows.length
            ).toFixed(1)
          : "0.0",
      tiers,
    };
  });

  return {
    stats: [
      { label: "Total audits", value: String(summaryRows.length), tone: "default" },
      { label: "Avg score", value: averageScore(submissionRows), tone: "default" },
      {
        label: "Critical sessions",
        value: String(summaryRows.filter((row) => ["S1", "S2"].includes(row.top_severity)).length),
        tone: "warning",
      },
      {
        label: "Leading reviews",
        value: String(submissionRows.filter((row) => normalizeTier(row.tier) === "Leading").length),
        tone: "good",
      },
    ],
    tierDistribution: ["Leading", "Proficient", "Developing", "Foundational"].map((tier) => ({
      label: tier,
      value: tierCounts[tier] || 0,
      tone: tierTone(tier),
    })),
    projectBreakdown,
  };
}

export async function getShowcaseData() {
  const reportDir = resolveDataPath("reports", "dev55");
  const summaryPath = resolveDataPath("reports", "_summary_dev55.csv");
  const submissionPath = resolveDataPath("performance", "per_submission.csv");
  const perTesterPath = resolveDataPath("performance", "per_tester.csv");

  const [summaryText, submissionText, perTesterText, reportFileNames] = await Promise.all([
    readFile(summaryPath, "utf8"),
    readFile(submissionPath, "utf8"),
    readFile(perTesterPath, "utf8"),
    readdir(reportDir),
  ]);

  const reportEntries = await Promise.all(
    reportFileNames
      .filter((fileName) => fileName.endsWith(".json"))
      .map(async (fileName) => {
        const reportText = await readFile(path.join(reportDir, fileName), "utf8");
        const report = JSON.parse(reportText);
        return [report.video_id || fileName.replace(/\.json$/i, ""), report];
      }),
  );

  const reportMap = new Map(reportEntries);
  const summaryRows = parseCsv(summaryText);
  const submissionRows = parseCsv(submissionText);
  const perTesterRows = parseCsv(perTesterText);

  const submissionMap = new Map(submissionRows.map((row) => [row.video_id, row]));
  const videos = summaryRows
    .map((summaryRow) =>
      buildSingleVideoData(
        summaryRow.video_id,
        reportMap.get(summaryRow.video_id),
        summaryRow,
        submissionMap.get(summaryRow.video_id),
      ),
    )
    .sort((left, right) => {
      const leftScore = left.scoreValue ?? -1;
      const rightScore = right.scoreValue ?? -1;
      if (rightScore !== leftScore) {
        return rightScore - leftScore;
      }
      return left.label.localeCompare(right.label);
    });

  const testers = buildTesterData(perTesterRows).sort((left, right) => left.tester.localeCompare(right.tester));

  return {
    navigationItems: [
      { id: "single-video", label: "Single Video" },
      { id: "tester-trajectory", label: "Tester Trajectory" },
      { id: "cohort-overview", label: "Cohort Overview" },
    ],
    filterOptions: {
      tiers: ["All", ...Array.from(new Set(videos.map((video) => video.performanceTier)))],
      projects: ["All", ...Array.from(new Set(videos.map((video) => video.project)))],
    },
    totalVideos: videos.length,
    videos,
    testers,
    cohortOverview: buildCohortOverview(summaryRows, submissionRows),
  };
}
