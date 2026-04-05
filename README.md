# CS20 Project

## Data Source
AWS S3 bucket:
usyd-03-2025-cs20-1-proj-assets

## Structure
- data/raw: raw data (S3)
- data/processed: processed data
- src: core code
- notebooks: experiments
- outputs: results

## Pipeline
MP4 → JSON → Parser → Analysis

## Environment
Python 3.10+

## Setup
pip install -r requirements.txt

## Usage
Run notebooks or scripts in src/ for data processing and analysis.

## Step 1.1
Completed: Built a parser to convert AWS Transcribe JSON into structured transcript, word-level items, and sentence-level segments.