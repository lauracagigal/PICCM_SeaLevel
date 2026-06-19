# CIndRA Assistant — Training Material

This folder holds the instructions used to train an external assistant — **CIndRA** (Climate Indicators Report Analysis) — e.g. as a ChatGPT custom GPT. The current skill set specializes CIndRA in the PICCM_SeaLevel repository workflow.

## How to use
- `CIndRA_role.md` — paste the contents into the "Instructions" / system prompt of the assistant. Defines CIndRA's identity, scope, conventions, data sources, analysis rules, plotting rules, output naming, and error handling.
- `aggregated_CIndRA_markdowns.md` — single file with **all** markdowns below concatenated (role + skills + this README). Use when the assistant platform accepts one large knowledge file instead of separate uploads. Regenerate after any source change: `python assistant/build_aggregated_CIndRA.py`.
- `skills/` — modular workflow-specific instructions. Attach each one as a separate "skill" file (or concatenate them into the assistant's knowledge base):
  - `site_setup.md` — how to run `0_site_setup.ipynb`.
  - `trend_analysis.md` — workflow for `a_sea_level_trend.ipynb`.
  - `anomaly_analysis.md` — workflow for `b_sea_level_anomaly.ipynb`.
  - `flood_frequency.md` — workflow for `c_sea_level_ff.ipynb`.
  - `rankings.md` — workflow for `d_sea_level_rankings.ipynb`.
  - `functions_api.md` — single source of truth for callable functions in `functions/`.
  - `output_conventions.md` — naming and folder rules for figures, CSVs and JSONs.
  - `data_sources.md` — canonical data sources, units, and citations.

## Repository quick map
- `notebooks/historical/` — 5 notebooks (`0`, `a`, `b`, `c`, `d`).
- `functions/` — Python modules (calculations, plotting, downloaders).
- `data/sea_level/` — cached UHSLC + CMEMS NetCDFs.
- `data/sites/` — per-site config JSON files.
- `outputs/<site_tag>/` — per-site figures, CSVs, JSONs.

## Updating the assistant
- When you add or rename a function in `functions/`, update `skills/functions_api.md` in the same PR.
- When you introduce a new persisted artifact (figure/CSV/JSON), document it in `skills/output_conventions.md`.
- When a new analysis notebook is added, mirror its workflow in a new `skills/<name>.md`.
- After editing any markdown in `assistant/` or `assistant/skills/`, run `python assistant/build_aggregated_CIndRA.py` to refresh `aggregated_CIndRA_markdowns.md`.
