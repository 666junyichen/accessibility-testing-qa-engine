# Non-runtime Submission Support Materials

This folder contains materials that are useful for the Final Report,
presentation, final status/demo checking, and client/school handoff, but are
not required to run the project system.

Runtime and reproducibility files remain in the main project folders:

- `src/`
- `scripts/`
- `app/`
- `tests/`
- `data/raw/`
- `data/processed/`
- `data/heldout/bupa/`
- `docs/`

## Folder Map

| Folder | Purpose |
|---|---|
| `00_school_requirements/` | Condensed school submission requirements from the local requirement files. |
| `01_final_report/` | Report source index, fact packs, research notebooks, figures, and supporting review notes. |
| `02_presentation/` | Demo script and slide-ready evidence pack. |
| `03_final_checking/` | Final status/demo checking inputs and technical closeout evidence. |
| `04_archive_do_not_submit/` | Notes about internal files intentionally not restored into the final repository. |

## Boundary

Do not use this folder as runtime input. It is a packaging and writing support
area only. If a file is needed by code, tests, or reproducible pipeline output,
it should stay outside `need/` in the normal project structure.

