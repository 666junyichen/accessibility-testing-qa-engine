import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { sanitizePublicLabel } from "./sanitize.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const candidateRoots = [
  path.resolve(__dirname, ".."),
  path.resolve(__dirname, "..", ".."),
];

const projectLabelMap = {
  "department-of-premier-and-cabinet-wa": "DPC-WA",
  "suncorp-insurance": "Suncorp",
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

function formatDuration(durationSec) {
  const totalSeconds = Math.round(Number(durationSec) || 0);
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

  const title = project
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

  return sanitizePublicLabel(title);
}

function buildDistribution(items, toneByKey = {}) {
  return Object.entries(items).map(([label, count]) => ({
    label: `${label} - ${count}`,
    value: Number(count),
    tone: toneByKey[label] ?? "neutral",
  }));
}

function normalizeTier(value) {
  return String(value ?? "").toUpperCase();
}

function averageScore(rows) {
  const scores = rows
    .map((row) => Number(row.score))
    .filter((value) => Number.isFinite(value));

  if (scores.length === 0) {
    return "0.0";
  }

  const total = scores.reduce((sum, value) => sum + value, 0);
  return (total / scores.length).toFixed(1);
}

function countCriticalRows(summaryRows) {
  return summaryRows.filter((row) => ["S1", "S2"].includes(row.top_severity)).length;
}

function countLeadingRows(submissionRows) {
  return submissionRows.filter((row) => row.tier === "Leading").length;
}

function buildTrajectoryRows(submissionRows, testerName) {
  return submissionRows
    .filter((row) => row.tester_name === testerName)
    .map((row) => ({
      label: formatProjectLabel(row.project),
      score: Number(row.score),
      capReason: row.cap_reasons || "No cap applied",
    }));
}

function buildTrajectorySummary(trajectoryRows) {
  if (trajectoryRows.length === 0) {
    return "No additional tester trajectory rows were available in the processed dataset.";
  }

  const scores = trajectoryRows.map((row) => row.score);
  const best = Math.max(...scores);
  const worst = Math.min(...scores);
  const repeatedCaps = trajectoryRows.filter((row) => /S1|S2/i.test(row.capReason)).length;

  return `Across ${trajectoryRows.length} processed submissions, scores range from ${worst.toFixed(1)} to ${best.toFixed(1)}. Task-blocking cap reasons recur in ${repeatedCaps} submission(s), so blocked-pathway handling remains the main coaching priority.`;
}

export async function getShowcaseData() {
  const reportPath = resolveDataPath("reports", "dev55", "Sharelinsonny_wa.json");
  const summaryPath = resolveDataPath("reports", "_summary_dev55.csv");
  const submissionPath = resolveDataPath("performance", "per_submission.csv");

  const [reportText, summaryText, submissionText] = await Promise.all([
    readFile(reportPath, "utf8"),
    readFile(summaryPath, "utf8"),
    readFile(submissionPath, "utf8"),
  ]);

  const report = JSON.parse(reportText);
  const summaryRows = parseCsv(summaryText);
  const submissionRows = parseCsv(submissionText);

  const activeSummary =
    summaryRows.find((row) => row.video_id === report.video_id) ??
    summaryRows.find((row) => row.video_id === "Sharelinsonny_wa");
  const activeSubmission =
    submissionRows.find((row) => row.video_id === report.video_id) ??
    submissionRows.find((row) => row.video_id === "Sharelinsonny_wa");

  const activeProject = formatProjectLabel(report.project);
  const severityDistribution = buildDistribution(report.l3_findings.by_severity, {
    S2: "warning",
    S3: "warm",
    S4: "good",
    S5: "neutral",
    S6: "cool",
  });
  const frictionTypes = buildDistribution(report.l3_findings.by_friction_type);
  const sentimentDistribution = buildDistribution(report.l3_findings.by_sentiment);
  const trajectoryRows = buildTrajectoryRows(submissionRows, report.tester_name);

  return {
    navigationItems: [
      { id: "single-video", label: "Single Video", active: true },
      { id: "tester-trajectory", label: "Tester Trajectory", active: false },
      { id: "cohort-overview", label: "Cohort Overview", active: false },
    ],
    sidebarFilters: [
      `Tier - all (${new Set(summaryRows.map((row) => row.tier)).size})`,
      `Project - all (${new Set(summaryRows.map((row) => formatProjectLabel(row.project))).size})`,
    ],
    totalVideos: summaryRows.length,
    activeCase: {
      id: "sharelinsonny-wa",
      label: report.video_id,
      tester: report.tester_name,
      project: activeProject,
      performanceTier: normalizeTier(report.overall.quality_tier),
      score: `${Math.round(Number(activeSubmission?.score ?? 0))}/100`,
      findingsCount: report.l3_findings.total_findings,
      windowCount: report.total_windows,
      duration: formatDuration(report.duration_sec),
      capReason: activeSubmission?.cap_reasons ?? "No cap applied",
      topSeverity: report.l3_findings.top_severity,
      reason: activeSummary?.reason ?? report.overall.reasoning[0] ?? "",
      tierReasoning: report.overall.reasoning[0] ?? "",
      summary: {
        title: report.overall.reasoning[0] ?? "Processed accessibility QA summary",
        tier: normalizeTier(report.overall.quality_tier),
        score: Math.round(Number(activeSubmission?.score ?? 0)),
        reportQuality: report.overall.reasoning[0] ?? "",
      },
      findings: report.l3_findings.top_findings.slice(0, 5).map((finding) => ({
        severity: finding.severity_s,
        friction: finding.friction_type,
        note: finding.finding,
      })),
      recommendations: report.coaching_recommendations.slice(0, 3).map((recommendation) => ({
        title: recommendation.title,
        detail: recommendation.summary,
      })),
      sessionAssessment: [
        { label: "Narration", value: report.l3_assessment.narration_quality },
        { label: "Recording", value: report.l3_assessment.recording_quality },
        { label: "Coaching evidence", value: report.l3_assessment.coaching_evidence },
      ],
      scoreBreakdown: [
        { label: "Raw composite", value: activeSubmission?.raw_score ?? "0.0" },
        { label: "D1 Narration", value: activeSubmission?.d1_narration ?? "0.0" },
        { label: "D2 Friction", value: activeSubmission?.d2_friction_surfacing ?? "0.0" },
        { label: "D3 Recording", value: activeSubmission?.d3_recording ?? "0.0" },
      ],
      severityDistribution,
      frictionTypes,
      sentimentDistribution,
    },
    trajectoryData: {
      summary: buildTrajectorySummary(trajectoryRows),
      sessions: trajectoryRows,
    },
    cohortOverview: {
      stats: [
        { label: "Total audits", value: String(summaryRows.length), tone: "default" },
        { label: "Avg score", value: averageScore(submissionRows), tone: "default" },
        { label: "Critical sessions", value: String(countCriticalRows(summaryRows)), tone: "warning" },
        { label: "Leading reviews", value: String(countLeadingRows(submissionRows)), tone: "muted" },
      ],
    },
  };
}
