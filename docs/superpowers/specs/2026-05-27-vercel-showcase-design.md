# Vercel Showcase Design

## Goal

Create a public-facing Vercel website for `Junyi Chen` that presents this repository as an accessibility testing QA and coaching project. The site should explain the project clearly for recruiters and collaborators, while also including a lightweight interactive demo that feels real without exposing internal school- or client-specific details.

## Outcome

The repository will gain a separate frontend showcase application that:

- introduces the project in portfolio-friendly language
- visualizes the pipeline from transcript inputs to report outputs
- includes a lightweight interactive demo backed by sanitized sample data
- removes or replaces school references in public-facing copy and labels
- remains deployable on Vercel without requiring the Python pipeline to run at request time

## Why This Shape

This repository is currently strongest as a Python research and evaluation codebase with a Streamlit demo. That is useful internally, but it is not the best public delivery format for a polished portfolio site on Vercel. A separate frontend showcase gives better control over:

- branding and presentation quality
- selective disclosure of data and labels
- deployment simplicity
- future extension if a real API or richer frontend is added later

## Scope

In scope:

- build a frontend showcase app inside this repository
- create a landing page with project explanation and visual structure
- create a lightweight interactive demo using sanitized local sample data
- sanitize public-facing labels so school names are removed or replaced
- update repository-facing public copy that would otherwise surface school-specific naming

Out of scope for this phase:

- migrating the full Streamlit app to Vercel
- exposing the full raw dataset or internal reports
- adding a live backend inference service
- rewriting the Python pipeline architecture
- bulk-sanitizing every historical raw data file in the repository

## Users And Success Criteria

Primary audience:

- recruiters reviewing `Junyi Chen`'s work
- engineering collaborators who want a fast understanding of the system

Success looks like:

- a visitor understands the problem, pipeline, and outputs within one minute
- the site looks intentional and portfolio-grade on desktop and mobile
- the demo feels interactive and concrete without leaking school-specific context
- the Vercel deployment runs as a static or mostly static frontend

## Product Structure

The site will be a single polished landing page with two layers:

1. project narrative sections near the top
2. a lightweight interactive demo section further down the page

### Section Plan

#### 1. Hero

Purpose:

- establish `Junyi Chen` ownership immediately
- frame the project as an accessibility QA and coaching engine
- communicate the value in one short sentence

Content:

- title
- short subtitle
- compact technical highlights such as layered analysis, report generation, and coaching output

#### 2. Project Story

Purpose:

- explain what goes in, what the system does, and what comes out

Content:

- transcript and structured signals as inputs
- layered quality analysis
- fused report and coaching outputs

#### 3. Pipeline Overview

Purpose:

- visually explain the architecture in a fast-scanning format

Content:

- transcript parsing
- rule-based detection
- feature engineering and clustering
- LLM finding extraction
- fusion and performance reporting
- coaching recommendation generation

This section should look visual, not like a long documentation block.

#### 4. Interactive Demo

Purpose:

- let visitors inspect a sanitized example output
- simulate the feel of the internal review tool without shipping internal artifacts directly

Content:

- selectable sample case cards or tabs
- summary status
- example findings with severity and friction labels
- example coaching recommendations
- optional compact metrics row

The demo data should be local static JSON or TypeScript objects checked into the frontend app.

#### 5. Engineering Notes

Purpose:

- show technical depth for engineering reviewers

Content:

- core stack and modeling layers
- testing emphasis
- design choices behind layered analysis
- deployment note that the public demo is a sanitized frontend showcase

## Technical Approach

### Frontend Framework

Use `Next.js` in a new frontend app inside the repository.

Reasoning:

- strong Vercel fit
- good support for static generation
- easy to ship a polished portfolio-grade UI
- easy to expand later with routes, assets, or APIs

### Rendering Model

Prefer a static site approach for the showcase page and local demo data.

Reasoning:

- simplest deployment path
- no runtime dependency on the Python pipeline
- avoids exposing internal processing artifacts dynamically

### Data Strategy

Use sanitized derived sample data for the public demo.

Allowed:

- aggregate descriptions
- anonymized sample case names
- generalized project labels
- representative findings and recommendation structures

Avoid:

- raw school identifiers
- internal client naming where not necessary
- full historical report dumps
- transcript-heavy raw content

## Sanitization Strategy

Public-facing places that should be sanitized:

- repository README text that frames the project publicly
- frontend showcase copy and demo labels
- public label mappings inherited from the Streamlit demo logic

Sanitization rules:

- school names should be removed or replaced with `Junyi Chen`
- project labels in the new public demo should use neutral names such as `Case A`, `Case B`, or domain-based names
- if a name is not necessary to explain the engineering, remove it instead of replacing it

Repository data files may still contain historical source material, but the new public-facing experience must not depend on those names.

## Information Architecture And UX

The page should feel modern, deliberate, and slightly editorial rather than like an academic report dump.

Design direction:

- strong typography
- warm neutral base with one clear accent family
- visual pipeline blocks
- compact cards for demo content
- clear spacing and hierarchy

The demo should not attempt to reproduce every Streamlit control. It should instead present a smaller, better-curated experience with just enough interaction to show how outputs are explored.

## Component Boundaries

Expected frontend units:

- page shell and global theme
- hero and narrative sections
- pipeline visualization component
- demo case selector
- demo findings list
- demo recommendations panel
- technical notes section

Each unit should have a narrow purpose so the page remains maintainable.

## Error Handling And Edge Cases

The public demo should degrade gracefully if sample data is missing or incomplete.

Expected behavior:

- show fallback copy instead of crashing
- avoid assumptions that every case has every metric
- keep the demo readable on mobile without hover-only interactions

## Testing Strategy

Frontend checks should cover:

- build success
- basic lint or type validation if configured
- smoke verification that the landing page renders and the demo switches cases

Manual verification should confirm:

- no school names remain in public-facing UI copy
- responsive layout works for desktop and mobile widths
- demo interactions feel coherent

## Deployment Plan

Deploy the new frontend app to Vercel as the public showcase.

The Python codebase remains in the repository as the implementation source of the project, while the Vercel site acts as the presentation layer.

## Risks And Mitigations

Risk:

- public copy accidentally exposes old dataset naming

Mitigation:

- centralize public labels in a small sanitized data layer
- review README and showcase strings specifically for name leakage

Risk:

- the demo feels too fake if it is oversimplified

Mitigation:

- keep the structure close to the real report model: summary, findings, recommendations, metrics

Risk:

- trying to port Streamlit too literally leads to a cluttered frontend

Mitigation:

- design the public demo as a curated subset, not a one-to-one migration

## Implementation Direction

Recommended implementation path:

1. create a new `Next.js` frontend app in-repo
2. define sanitized demo data and public label mappings
3. build the landing page sections
4. build the interactive demo section
5. update public repository copy that still exposes school references
6. verify locally and prepare for Vercel deployment

## Open Assumptions Locked For Planning

- `Junyi Chen` is the public-facing display name
- the site should combine a portfolio-style explanation with a lightweight demo
- the public site should use sanitized static data, not live pipeline execution
- removing school names from the user-facing experience is more important than preserving exact historical labels
