# Accessibility Testing QA Engine - DESIGN.md

Use this file as the design brief for Stitch or any AI-assisted web UI generator.

## Goal

Design a polished web-based demo for `Accessibility Testing QA Engine`.

This is not a portfolio landing page.
This is not a generic SaaS marketing site.
This is a product-style demo website for an internal accessibility testing review platform.

The site should present:

- what the project is
- what the system does
- what parts I completed
- a polished demo experience that reflects the structure of the original project demo

The final result should feel like a serious internal tool with a strong presentation layer.

## Product Framing

This project is an internal review platform for analyzing accessibility testing sessions.

It processes accessibility-testing videos and related evidence to:

- assess session quality
- detect friction patterns
- surface structured findings
- generate quality summaries
- support reviewer coaching
- track tester-level and cohort-level patterns

The website should feel like the final web version of this project demo, not like a personal portfolio.

## What The Site Should Prioritize

Prioritize:

- the actual product demo feel
- clarity of information architecture
- a professional interface
- high-quality visual design
- reviewer workflow
- project explanation in a compact form

Do not prioritize:

- self-promotion as a designer portfolio
- fake business marketing sections
- overlong narrative storytelling
- startup landing page clichés

## High-Level UX Direction

The site should feel like:

- a polished internal analytics/review platform
- a refined product demo for stakeholders
- a modern web application with strong design judgment

It should not feel like:

- a student assignment page
- a case-study-heavy portfolio
- a template SaaS homepage
- a rough Streamlit clone

## Core Structure

Build the website around the same conceptual structure as the original demo, but make it more professional and web-native.

Main structure:

1. Compact project intro
2. Single Video review view
3. Tester Trajectory view
4. Cohort Overview view
5. Short technical/project contribution summary

## Section Details

### 1. Compact Project Intro

This should be relatively short.

Purpose:

- explain what the project is
- explain what the platform helps internal reviewers do
- briefly explain what I completed

Content direction:

- project title
- one-sentence product summary
- short supporting paragraph
- compact chip list of capabilities such as transcript analysis, quality signals, structured findings, coaching support, performance tracking

This intro should not dominate the page.
It should orient the user, then move quickly into the product UI.

### 2. Single Video Review View

This should be the hero feature of the website.

It should feel like the polished web version of the existing demo's single-video analysis area.

This view should include:

- selected sample video/session card
- overview summary
- findings panel
- coaching recommendations
- quality / severity / risk signals
- layer or evidence detail panels if useful

This section should feel like a reviewer workstation.

### 3. Tester Trajectory View

This view should show how tester performance evolves across submissions.

Content direction:

- tester summary card
- score progression or trend chart
- persistent friction patterns
- reviewer-facing interpretation

This should feel analytical but still elegant.

### 4. Cohort Overview View

This view should summarize the broader dataset/demo scope.

Content direction:

- KPI cards
- tier distribution
- cohort-level quality breakdown
- project/category comparison blocks

This should feel like a strong operations dashboard section, but visually calmer and more refined than a BI tool.

### 5. My Contribution Summary

This should be short and factual.

Purpose:

- explain what I completed in the project
- make the site useful for presentation and resume context

Content direction:

- system design / data pipeline parts I built
- model / rules / LLM / fusion / frontend demo responsibilities
- testing / evaluation / deployment responsibilities

Keep this compact and credible.

## Design Style

### Mood

The interface should feel:

- professional
- calm
- precise
- technical
- premium
- trustworthy

### Reference Style

Take inspiration from:

- the restraint and polish of Linear
- the technical confidence of Vercel
- the structured clarity of Stripe

But apply those references to a review product UI, not a marketing page.

### Visual Character

Use:

- layered panels
- precise spacing
- strong hierarchy
- beautiful typography
- intentional use of color
- dashboard-like structure with editorial refinement

Avoid:

- flat generic admin templates
- purple gradients
- noisy startup illustrations
- random 3D blobs
- exaggerated glassmorphism
- loud “AI-generated” aesthetics

## Color Direction

Use a light, premium interface.

Suggested palette direction:

- warm off-white or soft stone background
- paper-like panel surfaces
- charcoal text
- deep teal / petroleum green as the main accent
- muted rust or amber for warning/severity emphasis
- slate neutrals for structure

Color should communicate information, not just decoration.

Severity and quality states can use accent colors, but the interface overall should stay restrained.

## Typography

Use typography with authority and clarity.

Suggested direction:

- elegant serif or refined display type for titles and major section headings
- clean sans-serif for UI, labels, controls, and body text
- monospace for small technical tags, metrics, IDs, or evidence labels

Avoid bland default type choices.

## Layout Principles

The site should feel like a real product.

Use:

- strong grids
- asymmetrical but balanced composition
- structured content bands
- large overview panels
- nested cards for findings and metrics
- desktop-first information richness with mobile-safe collapse

The product sections should feel more important than the intro section.

## Demo Interaction Direction

The demo should not be a simple one-column landing page.

It should feel like a usable application surface.

Preferred interaction patterns:

- segmented navigation or view switcher for `Single Video`, `Tester Trajectory`, `Cohort Overview`
- left-side selectors or filter rail where appropriate
- rich content panel on the right
- tabs or panel sub-sections inside major views
- meaningful chips, badges, and structured metric cards

The page can be a single-page app-like experience or a multi-section page that behaves like an internal product demo.

## Data Presentation Direction

The website should present the same kinds of content as the original demo, but with stronger visual hierarchy.

Key content types:

- summary cards
- findings lists
- severity labels
- friction categories
- recommendations
- trend charts
- cohort statistics
- evidence snippets

Make this feel thoughtful and operational, not decorative.

## Project Introduction Copy Direction

The intro should say, in a concise and professional way, that:

- this is an accessibility testing QA and coaching engine
- it supports internal reviewers working with accessibility session evidence
- it combines structured signals, layered analysis, and reviewer-facing outputs
- I contributed to core project implementation and demo presentation

Do not make the intro read like a personal portfolio biography.

## Contribution Summary Direction

Include a short section such as:

- built and refined the review workflow
- contributed to the layered analysis pipeline
- supported findings/report generation
- helped shape the demo experience and final presentation

This should feel factual and resume-friendly, not self-congratulatory.

## Motion

Motion should be subtle and product-like.

Good motion:

- smooth panel switching
- soft hover lift on cards
- restrained chart or metric transitions
- quiet fade and rise on section entrance

Bad motion:

- aggressive parallax
- flashy hero animation
- floating decorations for no reason

## What To Avoid

Do not generate:

- a portfolio homepage
- testimonial sections
- pricing tables
- call-to-action sections like “book a demo”
- fake enterprise logos
- startup growth copy
- cheesy AI buzzwords
- excessive marketing content

This is a project demo site, not a commercial company homepage.

## Desired Outcome

The result should make someone think:

`This feels like the polished web version of a real internal accessibility review system.`

And also:

`The project scope, the demo logic, and the contributor's role are all clear within a few minutes.`

## Short Prompt Version For Stitch

Design a polished web-based demo for `Accessibility Testing QA Engine`. This is not a portfolio site and not a generic SaaS marketing page. It is the final web-style demo for an internal accessibility testing review platform that analyzes accessibility testing sessions, surfaces quality signals, detects friction patterns, generates structured findings, supports coaching, and shows tester/cohort-level insights. The page should include a compact project intro, a strong `Single Video` review view, a `Tester Trajectory` view, a `Cohort Overview` view, and a short summary of what I completed in the project. Preserve the information architecture of a serious review tool, but redesign it as a more refined, modern, professional web product. Use a calm premium light theme with warm off-white backgrounds, layered paper-like panels, charcoal text, deep teal accents, muted rust warning colors, elegant typography, strong grids, and subtle technical UI details. The result should feel like a real internal product demo, not a student project, not a personal portfolio, and not a generic SaaS landing page.
