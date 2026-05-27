# Accessibility Testing QA Engine

Public-facing repository for `Junyi Chen`'s accessibility testing QA and coaching project.

This project explores how transcript evidence, structured signals, rule-based checks, clustered behavior patterns, and LLM-supported analysis can be fused into reviewer-friendly quality summaries and coaching guidance.

## What The System Does

The pipeline turns session evidence into:

- transcript windows and structured metadata
- heuristic quality flags
- grouped behavior patterns
- structured friction findings
- fused report summaries
- coaching recommendations
- reviewer and submission performance tables

The repository also includes:

- a Python implementation of the processing pipeline
- a Streamlit demo for internal-style report exploration
- a Vercel-ready `Next.js` showcase app under `showcase/`

## Repository Structure

| Path | Purpose |
|---|---|
| `src/` | Core pipeline logic for preprocessing, layered analysis, fusion, coaching, and tracking |
| `scripts/` | Command-line helpers for pipeline runs, postprocessing, clustering, and report generation |
| `app/` | Existing Streamlit review demo |
| `showcase/` | Public-facing Vercel frontend with sanitized demo content |
| `tests/` | Python regression and unit tests |
| `docs/` | Design notes, evaluation notes, and project documentation |
| `data/` | Local project artifacts and source snapshots used during development |

## Public Showcase

The `showcase/` app is designed for public presentation. It:

- explains the project in portfolio-friendly language
- visualizes the layered review pipeline
- includes a lightweight interactive demo backed by sanitized sample data
- removes school-specific public labels from the public-facing experience

## Local Setup

### Python pipeline

```bash
pip install -r requirements.txt
pytest
```

### Vercel showcase

```bash
cd showcase
npm install
npm run dev
```

## Privacy And Presentation Notes

This repository contains historical development materials from real project work. The new public showcase experience is intentionally sanitized and curated so that the Vercel site presents the engineering approach without depending on school-specific public naming.
