export const navigationItems = [
  { id: "single-video", label: "Single Video", active: true },
  { id: "tester-trajectory", label: "Tester Trajectory", active: false },
  { id: "cohort-overview", label: "Cohort Overview", active: false },
];

export const sidebarFilters = [
  "Tier · all (3)",
  "Project · all (3)",
];

export const pipelineSteps = [
  {
    name: "Transcript Inputs",
    detail: "Ingest timed transcript evidence and supporting metadata.",
  },
  {
    name: "Rule Signals",
    detail: "Flag narration, pacing, confidence, and silence anomalies.",
  },
  {
    name: "Structured Findings",
    detail: "Convert evidence windows into reportable friction findings.",
  },
  {
    name: "Coaching Output",
    detail: "Translate review outcomes into practical follow-up guidance.",
  },
];

export const demoCases = [
  {
    id: "sharelinsonny-wa",
    label: "Sharelinsonny_wa",
    tester: "Sharelinsonny",
    project: "DPC-WA",
    sector: "DPC-WA",
    performanceTier: "POOR",
    score: "65/100",
    findingsCount: 40,
    windowCount: 105,
    duration: "119m 19s",
    capReason: ">=2 S2 task-blockers",
    topSeverity: "S2",
    reason: "task-blocking friction: S1/S2 present",
    tierReasoning: "task-blocking friction: S1/S2 present",
    summary: {
      title: "task-blocking friction: S1/S2 present",
      tier: "POOR",
      score: 65,
      reportQuality: "task-blocking friction: S1/S2 present",
    },
    findings: [
      {
        severity: "S2",
        friction: "F6",
        note: "Critical action remained hard to discover after the user changed navigation path.",
      },
      {
        severity: "S3",
        friction: "F7",
        note: "Repeated correction loops increased task effort before recovery.",
      },
    ],
    recommendations: [
      {
        title: "Review navigation verification",
        detail: "Call out missing pathway confirmation explicitly when summarizing blocked flows.",
      },
      {
        title: "Strengthen evidence anchors",
        detail: "Pause on the blocking moment long enough to support the report rationale.",
      },
      {
        title: "Preserve coaching traceability",
        detail: "Connect each improvement action to the exact friction pattern it addresses.",
      },
    ],
    sessionAssessment: [
      { label: "Narration", value: "rich" },
      { label: "Recording", value: "acceptable" },
      { label: "Coaching evidence", value: "none" },
    ],
    scoreBreakdown: [
      { label: "Raw composite", value: "84.5" },
      { label: "D1 Narration", value: "90.0" },
      { label: "D2 Friction", value: "82.9" },
      { label: "D3 Recording", value: "70.0" },
    ],
    metrics: [
      { label: "Findings", value: "40" },
      { label: "Windows", value: "105" },
      { label: "Top severity", value: "S2" },
    ],
    severityDistribution: [
      { label: "S2 · 2", value: 5, tone: "warning" },
      { label: "S3 · 2", value: 5, tone: "warm" },
      { label: "S4 · 1", value: 4, tone: "good" },
      { label: "S5 · 32", value: 76, tone: "neutral" },
      { label: "S6 · 3", value: 10, tone: "cool" },
    ],
    frictionTypes: [
      { label: "F1 · 15", value: 30 },
      { label: "F2 · 11", value: 22 },
      { label: "F4 · 2", value: 8 },
      { label: "F5 · 1", value: 5 },
      { label: "F6 · 10", value: 20 },
      { label: "F7 · 1", value: 5 },
    ],
    sentimentDistribution: [
      { label: "E3 · 26", value: 62 },
      { label: "E4 · 14", value: 38 },
    ],
    trajectory: {
      summary: "Score trend indicates improvement over repeat submissions, with blockage handling still the main recurring weakness.",
      sessions: [
        { label: "S1", value: 58 },
        { label: "S2", value: 60 },
        { label: "S3", value: 65 },
      ],
    },
    cohort: {
      totalAudits: "55",
      averageScore: "74.8",
      criticalMisses: "7",
    },
  },
];

export const trajectoryData = {
  title: "Tester Trajectory",
  subtitle: "Trajectory summary for the selected tester across repeated submissions.",
  sessions: [
    { label: "S1", score: 58 },
    { label: "S2", score: 60 },
    { label: "S3", score: 65 },
  ],
  persistentFriction: [
    "Task-blocking friction",
    "Secondary navigation uncertainty",
    "Recovery evidence gaps",
  ],
  summary:
    "Trajectory remains volatile around blocked flows, but overall reviewer output improved across later sessions.",
};

export const cohortOverview = {
  stats: [
    { label: "Total audits", value: "55", tone: "default" },
    { label: "Avg score", value: "74.8", tone: "default" },
    { label: "Critical misses", value: "7", tone: "warning" },
    { label: "Top-tier testers", value: "12", tone: "muted" },
  ],
  panels: [
    {
      title: "Tier Distribution",
      body: "The current cohort skews toward mid-tier performance, with a smaller group of severe blocker-heavy sessions driving review attention.",
    },
    {
      title: "Operational Note",
      body: "This overview is intended to help internal reviewers compare submissions and spot recurring coaching priorities.",
    },
  ],
};

export const contributions = [
  {
    title: "Review workflow implementation",
    detail: "Built the reviewer-facing flow for transcript evidence, findings, and coaching output presentation.",
  },
  {
    title: "Layered assessment support",
    detail: "Contributed to the rule, LLM, and scoring pipeline that powers the summary cards and quality judgments.",
  },
  {
    title: "Demo presentation",
    detail: "Helped shape and present the final demo experience used to communicate project outcomes.",
  },
];
