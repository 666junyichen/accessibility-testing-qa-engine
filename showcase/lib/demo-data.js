export const navigationItems = [
  { id: "single-video", label: "Single Video" },
  { id: "tester-trajectory", label: "Tester Trajectory" },
  { id: "cohort-overview", label: "Cohort Overview" },
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

export const capabilityChips = [
  "Transcript Analysis",
  "Quality Signals",
  "Structured Findings",
  "Coaching Support",
];

export const demoCases = [
  {
    id: "case-a",
    label: "Case A",
    workspaceId: "4823-XJ",
    sessionId: "492-B",
    duration: "12:04 / 45:00",
    sector: "Education portal",
    analystNote: "Repeated task switching exposed navigation friction and low confidence around secondary actions.",
    summary: {
      title: "Navigation friction during repeated task switching",
      tier: "Watch",
      score: 72,
      reportQuality: "Multiple medium-severity findings with coaching follow-up required.",
    },
    findings: [
      {
        severity: "High Risk",
        timestamp: "04:12",
        friction: "F6",
        note: "Tester bypassed the secondary navigation structure before confirming screen reader access.",
        coaching: "Review navigation verification steps before progressing to account actions.",
      },
      {
        severity: "Standard",
        timestamp: "08:45",
        friction: "F2",
        note: "Valid aria-label coverage was identified on the submit action after a brief hesitation.",
        coaching: "Keep the evidence snippet because it supports the positive report outcome.",
      },
    ],
    recommendations: [
      {
        title: "Review navigation verification",
        detail: "Require explicit confirmation of secondary navigation and assistive support before progressing.",
      },
      {
        title: "Capture stronger evidence anchors",
        detail: "Pause on blocked states long enough to support the final written finding.",
      },
    ],
    metrics: [
      { label: "Signals reviewed", value: "18" },
      { label: "High-priority findings", value: "2" },
      { label: "Coaching actions", value: "2" },
    ],
  },
  {
    id: "case-b",
    label: "Case B",
    workspaceId: "5180-ZP",
    sessionId: "715-C",
    duration: "18:31 / 33:00",
    sector: "Service dashboard",
    analystNote: "The main interaction path was stable, but recording quality reduced confidence on one key sequence.",
    summary: {
      title: "Low-friction path with isolated recording caveats",
      tier: "Strong",
      score: 88,
      reportQuality: "Mostly clear signals with one recording caveat and low escalation risk.",
    },
    findings: [
      {
        severity: "Standard",
        timestamp: "03:27",
        friction: "F2",
        note: "User confidence dipped briefly during account setup, but recovery was immediate.",
        coaching: "Capture the hesitation in the narrative while preserving the overall positive assessment.",
      },
      {
        severity: "Recording",
        timestamp: "14:18",
        friction: "F7",
        note: "Audio clipping reduced certainty when interpreting the final confirmation step.",
        coaching: "Flag the evidence caveat and recommend a quieter retest environment.",
      },
    ],
    recommendations: [
      {
        title: "Flag recording caveats clearly",
        detail: "Keep positive findings intact while separating evidence-confidence issues from UX issues.",
      },
    ],
    metrics: [
      { label: "Signals reviewed", value: "12" },
      { label: "High-priority findings", value: "0" },
      { label: "Coaching actions", value: "1" },
    ],
  },
];

export const trajectoryData = {
  title: "Tester Trajectory",
  subtitle:
    "Score stability, recurring friction, and reviewer interpretation across sequential submissions.",
  sessions: [
    { label: "S1", score: 46 },
    { label: "S2", score: 58 },
    { label: "S3", score: 54 },
    { label: "S4", score: 73 },
    { label: "S5", score: 82 },
  ],
  persistentFriction: [
    "Complex table navigation",
    "Dynamic modal focus handling",
    "Low-confidence narration during recovery steps",
  ],
  summary:
    "Consistent improvement in core WCAG issue identification, with the main remaining gap concentrated in advanced state changes and dynamic content transitions.",
};

export const cohortOverview = {
  stats: [
    { label: "Total audits", value: "1,248", tone: "default" },
    { label: "Avg quality score", value: "92.4%", tone: "default" },
    { label: "Critical misses", value: "14", tone: "warning" },
    { label: "Top-tier testers", value: "28", tone: "muted" },
  ],
  panels: [
    {
      title: "Tier Distribution",
      body: "Leading and proficient reviewers make up the dominant share, while a smaller developing group drives most intervention planning.",
    },
    {
      title: "Review Operations",
      body: "Cohort-level summaries help internal reviewers spot where escalation guidance or coaching templates should be standardized.",
    },
  ],
};

export const contributions = [
  {
    title: "Review Workflow",
    detail:
      "Built and refined the reviewer-facing flow for transcript evidence, quality signals, and structured findings.",
  },
  {
    title: "Layered Analysis",
    detail:
      "Contributed to the rule, clustering, and LLM-supported pipeline that turns raw evidence into reportable findings.",
  },
  {
    title: "Demo Presentation",
    detail:
      "Shaped the polished web demo layer so the final project outcome can be presented as a coherent product experience.",
  },
];
