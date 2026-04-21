-- ================================================================
-- SMP Database Schema — Research Reference
-- For: Insights Generation Research Project
-- ================================================================
--
-- See Me Please (SMP) is an accessibility testing platform that connects
-- organisations with diverse user cohorts for digital accessibility validation.
--
-- Testers with various disabilities and assistive technologies perform tasks
-- on client products. Their sessions are recorded as videos, transcribed,
-- and surveyed. LLM-powered insight generation then analyses transcriptions
-- and survey responses to produce structured accessibility insights.
--
-- This schema covers the data model relevant to the insights pipeline:
--
--   Organisation → Project → Tasks/Components
--                         → Assignments → Testers (with cohorts & AT)
--                         → Videos → Transcriptions
--                         → Surveys → Responses → Answers
--                         → Individual Insights → Aggregated Insights
--                         → Insight Quotes (evidence from video/survey)
--                         → Scoring Framework → Scores
--
-- NOTE: This is a simplified view. Internal tables (PII, payroll, audit,
-- notifications, auth) have been removed. Indexes and triggers are omitted.
-- All tables have created_at/updated_at TIMESTAMPTZ columns (auto-managed).
-- ================================================================


-- ============================================
-- CORE ENTITIES
-- ============================================

-- Organisations are the top-level tenants (clients who commission testing)
CREATE TABLE organisations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    industry VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Projects represent a single accessibility testing engagement for an organisation
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    organisation_id UUID NOT NULL REFERENCES organisations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    slug VARCHAR(255) UNIQUE,
    type VARCHAR(255),                 -- e.g. website, mobile app, kiosk
    tag TEXT[],                         -- free-form tags for categorisation
    status VARCHAR(10) CHECK (status IN ('NC', 'C', 'TI', 'TIP', 'TC', 'P', 'F')),
    -- NC=Not Complete, C=Complete, TI=Testing Initiated, TIP=Testing In Progress,
    -- TC=Testing Complete, P=Published, F=Failed

    testing_allocation_hours INTEGER,
    testing_deadline TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Tasks are discrete testing activities within a project (e.g. "Navigate to checkout")
CREATE TABLE project_tasks (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id),
    task_order INTEGER NOT NULL,
    title VARCHAR(255),
    instructions TEXT,
    tips TEXT,
    timeguide VARCHAR(255),
    task_type TEXT[],                   -- e.g. ['navigation', 'form_filling']
    exclude_from_collation BOOLEAN DEFAULT FALSE,
    task_url TEXT,                      -- URL the tester navigates to
    component_label VARCHAR(255),      -- links task to a logical component

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,

    UNIQUE (project_id, task_order)
);

-- Components are logical features/areas being tested (e.g. "Search bar", "Checkout flow")
CREATE TABLE project_components (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id),
    component_order INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tags TEXT[],                        -- cross-project categorisation tags

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,

    UNIQUE (project_id, component_order)
);


-- ============================================
-- ACCESSIBILITY CONTEXT — LOOKUP TABLES
-- ============================================

-- Cohorts represent accessibility groups (e.g. "blind", "low_vision", "motor_impairment")
CREATE TABLE cohorts (
    name VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Assistive technologies used by testers
CREATE TABLE assistive_technologies (
    name VARCHAR(100) PRIMARY KEY,
    display_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'screen_reader', 'magnification', 'voice_control',
        'switch_control', 'braille_display', 'other'
    )),
    platform VARCHAR(50),              -- e.g. iOS, Windows, macOS, Android
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);


-- ============================================
-- TESTER PROFILES (non-PII subset)
-- ============================================

-- Testers are individuals who perform accessibility testing
-- NOTE: PII fields (name, email, address, etc.) are stored separately and excluded here
CREATE TABLE tester_profiles (
    id UUID PRIMARY KEY,
    status VARCHAR(50) NOT NULL,       -- e.g. active, pending, suspended
    region VARCHAR(100) NOT NULL,      -- e.g. APAC, EMEA, NA
    country VARCHAR(100) NOT NULL,
    star_rating DECIMAL(3,2) CHECK (star_rating >= 0 AND star_rating <= 5),
    projects_completed INTEGER DEFAULT 0,
    communication_preference VARCHAR(100),
    english_first_language BOOLEAN,
    english_proficiency VARCHAR(50),

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Many-to-many: which cohorts a tester belongs to
CREATE TABLE tester_cohorts (
    tester_id UUID NOT NULL REFERENCES tester_profiles(id),
    cohort_name VARCHAR(50) NOT NULL REFERENCES cohorts(name),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,  -- primary cohort for multi-cohort testers

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,

    PRIMARY KEY (tester_id, cohort_name)
);

-- Many-to-many: which assistive technologies a tester uses
CREATE TABLE tester_assistive_technologies (
    tester_id UUID NOT NULL REFERENCES tester_profiles(id),
    tech_name VARCHAR(100) NOT NULL REFERENCES assistive_technologies(name),
    proficiency_level VARCHAR(20) CHECK (proficiency_level IN ('beginner', 'intermediate', 'expert')),
    years_experience INTEGER CHECK (years_experience >= 0),

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,

    PRIMARY KEY (tester_id, tech_name)
);


-- ============================================
-- ASSIGNMENTS
-- ============================================

-- Links testers to projects they are assigned to test
CREATE TABLE assignments (
    project_id UUID NOT NULL REFERENCES projects(id),
    tester_id UUID NOT NULL REFERENCES tester_profiles(id),
    status VARCHAR(50) NOT NULL,       -- e.g. assigned, accepted, in_progress, completed, declined

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,

    PRIMARY KEY (project_id, tester_id)
);


-- ============================================
-- VIDEO & TRANSCRIPTION PIPELINE
-- ============================================

-- Videos captured during testing sessions
CREATE TABLE videos (
    id UUID PRIMARY KEY,
    type VARCHAR(20) NOT NULL CHECK (type IN (
        'project_task',        -- individual tester recording for a task
        'presales',            -- pre-sales demo recording
        'project_collated',    -- stitched video of all testers for a task
        'highlight_reel',      -- curated highlights
        'thank_you_reel'       -- thank-you compilation
    )),
    name VARCHAR(255),
    video_path TEXT NOT NULL,
    duration DECIMAL(10,2),            -- seconds
    file_size_mb INTEGER,
    mime_type VARCHAR(100),

    -- Relationships
    project_id UUID REFERENCES projects(id),
    task_id UUID REFERENCES project_tasks(id),
    tester_id UUID REFERENCES tester_profiles(id),

    uploaded_at TIMESTAMPTZ NOT NULL,

    -- Processing pipeline status
    processing_status VARCHAR(50) DEFAULT 'pending',
    is_active BOOLEAN DEFAULT TRUE,

    -- Type-specific metadata as JSONB
    -- project_task: { task_order, tester_cohorts }
    -- presales: { hubspot_lead_id, company_name }
    metadata JSONB DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Transcriptions produced from videos (1:1 relationship)
-- This is a primary input for LLM insight generation
CREATE TABLE video_transcriptions (
    video_id UUID PRIMARY KEY REFERENCES videos(id),

    -- Transcription provider details
    job_id VARCHAR(255) UNIQUE,
    provider VARCHAR(50),              -- e.g. AssemblyAI, AWS Transcribe

    -- Core transcription output
    transcription_text TEXT,           -- full plain-text transcript
    confidence DECIMAL(5,4),           -- overall confidence score (0.0-1.0)
    language_code VARCHAR(10),

    -- Structured data (JSONB)
    words JSONB,                       -- word-level timestamps and confidence
    speaker_labels JSONB,              -- speaker diarisation data
    topics JSONB,                      -- auto-detected topics

    -- Generated file outputs
    srt_path TEXT,                     -- SubRip subtitle file
    vtt_path TEXT,                     -- WebVTT subtitle file
    transcript_doc_path TEXT,          -- formatted transcript document
    chapters_path TEXT,                -- auto-generated chapters

    -- Timing
    requested_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);


-- ============================================
-- SURVEY SYSTEM (simplified)
-- ============================================

-- Each project can have one survey that testers complete after testing
CREATE TABLE surveys (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Questions within a survey
CREATE TABLE survey_questions (
    id UUID PRIMARY KEY,
    survey_id UUID NOT NULL REFERENCES surveys(id),

    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL CHECK (question_type IN (
        'free_text',       -- open-ended text response
        'linear_scale',    -- numeric scale (e.g. 1-5)
        'checkbox',        -- select multiple options
        'multi_choice'     -- select one option
    )),
    question_order INTEGER NOT NULL,
    is_mandatory BOOLEAN NOT NULL DEFAULT FALSE,

    -- Type-specific config:
    --   free_text:    { max_length, validation_rules }
    --   linear_scale: { min, max, min_label, max_label }
    --   checkbox:     { options: ["opt1", "opt2", ...] }
    --   multi_choice: { options: ["opt1", "opt2", ...] }
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- One response per tester per survey
CREATE TABLE survey_responses (
    id UUID PRIMARY KEY,
    survey_id UUID NOT NULL REFERENCES surveys(id),
    project_id UUID NOT NULL REFERENCES projects(id),
    tester_id UUID NOT NULL REFERENCES tester_profiles(id),

    status VARCHAR(20) NOT NULL DEFAULT 'in_progress'
        CHECK (status IN ('in_progress', 'completed')),
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    time_spent_seconds INTEGER,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,

    UNIQUE (survey_id, tester_id)
);

-- Individual answers to survey questions
CREATE TABLE survey_answers (
    id UUID PRIMARY KEY,
    response_id UUID NOT NULL REFERENCES survey_responses(id),
    question_id UUID NOT NULL REFERENCES survey_questions(id),

    -- Answer stored as JSONB. Structure varies by question type:
    --   free_text:    { "text": "..." }
    --   linear_scale: { "value": 4 }
    --   checkbox:     { "selected": ["opt1", "opt3"] }
    --   multi_choice: { "selected": "opt2" }
    answer_data JSONB NOT NULL,

    answered_at TIMESTAMPTZ NOT NULL,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,

    UNIQUE (response_id, question_id)
);


-- ============================================
-- INSIGHTS SYSTEM
-- ============================================
-- The core of the LLM-powered analysis pipeline.
-- Individual insights are extracted per-video, then aggregated across
-- multiple videos/testers to identify patterns and themes.

-- Individual insights extracted from a single video's transcription
CREATE TABLE individual_insights (
    id UUID PRIMARY KEY,

    -- Every individual insight ties to one video of one tester doing one task
    project_id UUID NOT NULL REFERENCES projects(id),
    video_id UUID NOT NULL REFERENCES videos(id),
    task_id UUID NOT NULL REFERENCES project_tasks(id),
    tester_id UUID NOT NULL REFERENCES tester_profiles(id),

    -- Classification
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'friction',    -- usability issue that slowed the tester
        'blocker',     -- issue that prevented task completion
        'positive',    -- good UX / accessibility win
        'neutral'      -- neutral observation
    )),
    severity VARCHAR(20) CHECK (severity IN ('severe', 'high', 'medium', 'low')),
    -- severity is required for friction/blocker, NULL for positive/neutral
    friction_type VARCHAR(50) CHECK (friction_type IN (
        'comprehension',           -- tester didn't understand something
        'confidence',              -- tester was unsure/hesitant
        'accessibility',           -- AT-specific barrier
        'unresponsive_interface',  -- UI didn't respond as expected
        'unexpected_behaviour',    -- UI behaved contrary to expectations
        'content_not_found',       -- tester couldn't find what they needed
        'excessive_effort'         -- task required too many steps/actions
    )),

    -- Content
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,

    -- AI metadata
    confidence NUMERIC(3,2) NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    llm_metadata JSONB DEFAULT '{}'::JSONB,  -- model version, prompt template, token counts, etc.

    -- Approval workflow
    approval_status VARCHAR(50) NOT NULL DEFAULT 'draft' CHECK (approval_status IN (
        'draft', 'pending_review', 'approved', 'rejected'
    )),
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMPTZ,
    approved_by VARCHAR(255),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,

    -- Version control
    version INTEGER NOT NULL DEFAULT 1,
    edit_history JSONB DEFAULT '[]'::JSONB,  -- [{version, edited_by, edited_at, changes}]

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Aggregated insights synthesised from multiple individual insights
-- These identify patterns, themes, and unique findings across testers
CREATE TABLE aggregated_insights (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id),

    -- Aggregation dimensions (flexible JSONB)
    -- Keys: tester_id, cohort, task_id, assistive_tech, component_id,
    --        geographic_region, geographic_country
    dimensions JSONB NOT NULL,

    -- Aggregation type
    insight_type VARCHAR(50) NOT NULL CHECK (insight_type IN (
        'pattern',   -- recurring issue seen across multiple testers
        'unique',    -- notable finding from a single perspective
        'theme'      -- higher-level thematic grouping
    )),
    affected_tester_count INTEGER NOT NULL CHECK (affected_tester_count >= 2),
    synthesis_rationale TEXT,          -- why these findings were grouped

    -- Content
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    recommendation_text TEXT,          -- resolution guidance
    wcag_criteria TEXT[],              -- related WCAG success criteria (e.g. '1.4.3', '2.4.1')
    is_quick_win BOOLEAN NOT NULL DEFAULT FALSE,

    -- Classification (same taxonomy as individual_insights)
    category VARCHAR(50) CHECK (category IN ('friction', 'blocker', 'positive', 'neutral')),
    severity VARCHAR(20) CHECK (severity IN ('severe', 'high', 'medium', 'low')),
    friction_type VARCHAR(50) CHECK (friction_type IN (
        'comprehension', 'confidence', 'accessibility',
        'unresponsive_interface', 'unexpected_behaviour',
        'content_not_found', 'excessive_effort'
    )),

    -- AI metadata
    confidence NUMERIC(3,2) NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    llm_metadata JSONB DEFAULT '{}'::JSONB,

    -- Approval workflow
    approval_status VARCHAR(50) NOT NULL DEFAULT 'draft' CHECK (approval_status IN (
        'draft', 'pending_review', 'approved', 'rejected'
    )),
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMPTZ,
    approved_by VARCHAR(255),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,

    -- Version control
    version INTEGER NOT NULL DEFAULT 1,
    edit_history JSONB DEFAULT '[]'::JSONB,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Links aggregated insights to the individual insights they were synthesised from
CREATE TABLE aggregated_insight_sources (
    aggregated_insight_id UUID NOT NULL REFERENCES aggregated_insights(id),
    source_insight_id UUID NOT NULL REFERENCES individual_insights(id),
    contribution_weight NUMERIC(3,2) DEFAULT 1.0,  -- 0.0-1.0, how strongly this source influenced the aggregation

    created_at TIMESTAMPTZ NOT NULL,

    PRIMARY KEY (aggregated_insight_id, source_insight_id)
);

-- Evidence quotes supporting insights (from video transcripts or survey responses)
CREATE TABLE insight_quotes (
    id UUID PRIMARY KEY,

    -- Parent insight (can reference individual OR aggregated insight)
    insight_id UUID NOT NULL,
    insight_type VARCHAR(20) NOT NULL CHECK (insight_type IN ('individual', 'aggregated')),

    -- Quote content
    quote_source VARCHAR(20) NOT NULL CHECK (quote_source IN ('video', 'survey')),
    quote_text TEXT NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,

    -- Video-specific fields (when quote_source = 'video')
    video_id UUID REFERENCES videos(id),
    start_time_seconds NUMERIC(10,2),  -- timestamp for jump-to playback
    end_time_seconds NUMERIC(10,2),
    speaker_label VARCHAR(100),
    transcription_confidence NUMERIC(5,4),

    -- Survey-specific fields (when quote_source = 'survey')
    survey_response_id UUID REFERENCES survey_responses(id),
    question_text TEXT,
    response_type VARCHAR(50),         -- open_text, rating, multiple_choice
    respondent_tester_id UUID REFERENCES tester_profiles(id),
    respondent_cohort VARCHAR(50) REFERENCES cohorts(name),

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Tracks async LLM insight generation jobs
CREATE TABLE insight_generation_jobs (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id),

    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'running', 'completed', 'failed'
    )),

    -- Progress
    total_videos INTEGER NOT NULL,
    videos_processed INTEGER NOT NULL DEFAULT 0,

    -- Cost tracking
    llm_tokens_consumed BIGINT DEFAULT 0,
    estimated_cost_usd NUMERIC(10,4) DEFAULT 0.00,

    -- Error handling
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,

    -- Timing
    queued_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    processing_time_seconds INTEGER,

    -- Job configuration (model params, confidence thresholds, dimension prefs, etc.)
    job_config JSONB DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);


-- ============================================
-- SCORING FRAMEWORK
-- ============================================
-- Calculates accessibility and usability scores from insights and survey data.
-- Supports versioned algorithm configurations and editorial overrides.

-- Algorithm configurations per project (supports A/B testing of scoring approaches)
CREATE TABLE scoring_frameworks (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id),
    name TEXT NOT NULL,
    description TEXT,
    version TEXT NOT NULL,
    config JSONB NOT NULL DEFAULT '{}'::JSONB,  -- algorithm weights, thresholds, etc.
    is_active BOOLEAN NOT NULL DEFAULT FALSE,   -- only one active per project

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Execution history of scoring runs
CREATE TABLE scoring_runs (
    id UUID PRIMARY KEY,
    framework_id UUID NOT NULL REFERENCES scoring_frameworks(id),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    total_tester_tasks INTEGER NOT NULL DEFAULT 0,
    tester_tasks_processed INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    run_metadata JSONB DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- Calculated scores per tester per task per scoring run
CREATE TABLE scoring_framework_scores (
    id UUID PRIMARY KEY,
    scoring_run_id UUID NOT NULL REFERENCES scoring_runs(id),
    project_id UUID NOT NULL REFERENCES projects(id),
    task_id UUID NOT NULL REFERENCES project_tasks(id),
    tester_id UUID NOT NULL REFERENCES tester_profiles(id),

    -- Input: raw survey rating (0-5 scale)
    raw_survey_rating NUMERIC(3,1) CHECK (raw_survey_rating >= 0 AND raw_survey_rating <= 5),

    -- Output: calculated scores (0-100 scale)
    accessibility_score NUMERIC(5,2) NOT NULL CHECK (accessibility_score >= 0 AND accessibility_score <= 100),
    usability_score NUMERIC(5,2) NOT NULL CHECK (usability_score >= 0 AND usability_score <= 100),

    -- Algorithm breakdown for explainability
    score_breakdown JSONB DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ NOT NULL,

    UNIQUE (scoring_run_id, task_id, tester_id)
);

-- Editorial score overrides (non-destructive, take precedence over calculated scores)
CREATE TABLE score_overrides (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id),
    task_id UUID NOT NULL REFERENCES project_tasks(id),
    tester_id UUID NOT NULL REFERENCES tester_profiles(id),

    -- Override values (0-100 scale) — can override just one score independently
    accessibility_score NUMERIC(5,2) CHECK (accessibility_score >= 0 AND accessibility_score <= 100),
    usability_score NUMERIC(5,2) CHECK (usability_score >= 0 AND usability_score <= 100),

    reason TEXT NOT NULL,
    overridden_by TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,

    UNIQUE (project_id, task_id, tester_id)
);


-- ============================================
-- VIEWS — Score Aggregations
-- ============================================

-- Effective scores: resolves editorial overrides over calculated values
-- from the active framework's latest completed run
CREATE OR REPLACE VIEW effective_tester_task_scores AS
WITH latest_completed_runs AS (
    SELECT DISTINCT ON (sf.project_id)
        sr.id AS scoring_run_id,
        sf.id AS framework_id,
        sf.project_id
    FROM scoring_frameworks sf
    JOIN scoring_runs sr ON sr.framework_id = sf.id
    WHERE sf.is_active = TRUE
      AND sr.status = 'completed'
    ORDER BY sf.project_id, sr.completed_at DESC
)
SELECT
    sfs.id AS score_id,
    sfs.project_id,
    sfs.task_id,
    sfs.tester_id,
    lcr.framework_id,
    lcr.scoring_run_id,
    sfs.raw_survey_rating,
    COALESCE(so.accessibility_score, sfs.accessibility_score) AS accessibility_score,
    COALESCE(so.usability_score, sfs.usability_score) AS usability_score,
    (so.id IS NOT NULL) AS is_overridden,
    so.reason AS override_reason,
    sfs.accessibility_score AS calculated_accessibility_score,
    sfs.usability_score AS calculated_usability_score,
    sfs.score_breakdown,
    (SELECT array_agg(tc.cohort_name ORDER BY tc.cohort_name)
     FROM tester_cohorts tc WHERE tc.tester_id = sfs.tester_id) AS cohort_names
FROM latest_completed_runs lcr
JOIN scoring_framework_scores sfs ON sfs.scoring_run_id = lcr.scoring_run_id
LEFT JOIN score_overrides so
    ON so.project_id = sfs.project_id
    AND so.task_id = sfs.task_id
    AND so.tester_id = sfs.tester_id;

-- Task-level score averages
CREATE OR REPLACE VIEW score_aggregates_by_task AS
SELECT
    ets.project_id, ets.task_id, ets.framework_id,
    pt.component_label,
    COUNT(*) AS tester_count,
    AVG(ets.accessibility_score) AS avg_accessibility_score,
    AVG(ets.usability_score) AS avg_usability_score,
    MIN(ets.accessibility_score) AS min_accessibility_score,
    MAX(ets.accessibility_score) AS max_accessibility_score,
    MIN(ets.usability_score) AS min_usability_score,
    MAX(ets.usability_score) AS max_usability_score,
    COUNT(*) FILTER (WHERE ets.is_overridden) AS override_count
FROM effective_tester_task_scores ets
JOIN project_tasks pt ON pt.id = ets.task_id
GROUP BY ets.project_id, ets.task_id, ets.framework_id, pt.component_label;

-- Cohort-level score averages
CREATE OR REPLACE VIEW score_aggregates_by_cohort AS
SELECT
    ets.project_id, tc.cohort_name, ets.framework_id,
    COUNT(DISTINCT ets.tester_id) AS tester_count,
    AVG(ets.accessibility_score) AS avg_accessibility_score,
    AVG(ets.usability_score) AS avg_usability_score,
    MIN(ets.accessibility_score) AS min_accessibility_score,
    MAX(ets.accessibility_score) AS max_accessibility_score
FROM effective_tester_task_scores ets
JOIN tester_cohorts tc ON tc.tester_id = ets.tester_id
GROUP BY ets.project_id, tc.cohort_name, ets.framework_id;

-- Project-level score averages (executive summary)
CREATE OR REPLACE VIEW score_aggregates_by_project AS
SELECT
    project_id, framework_id,
    COUNT(DISTINCT tester_id) AS tester_count,
    COUNT(DISTINCT task_id) AS task_count,
    AVG(accessibility_score) AS avg_accessibility_score,
    AVG(usability_score) AS avg_usability_score,
    COUNT(*) FILTER (WHERE is_overridden) AS override_count
FROM effective_tester_task_scores
GROUP BY project_id, framework_id;
