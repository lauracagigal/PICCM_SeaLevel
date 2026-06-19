## Skill: Top-10 Rankings (notebook `d_sea_level_rankings.ipynb`)

### Purpose
Identify and contextualize the 10 highest and 10 lowest hourly sea level events at the tide gauge, joined with the ENSO state at the time of each event.

### Required inputs
- Site config JSON.
- UHSLC hourly NetCDF.

### Workflow
1. Load config and UHSLC hourly data; build `site_output_dir`.
2. Compute monthly aggregates from hourly data:
   - `rsl_monthly_max = rsl.resample(time='1MS').max()`
   - `rsl_monthly_min = rsl.resample(time='1MS').min()`
   - `rsl_monthly_mean = rsl.resample(time='1MS').mean()`
3. Build the top-10 table: `top_10_table = get_top_10_table(rsl, uhslc_id)` (which calls `get_top_ten` for both modes and joins ONI state via `detect_enso_events`).
4. Render styled tables:
   - Pandas `Styler` via `style_oni_based` for HTML rendering.
   - `great_tables.GT(...)` for a print-quality PNG.
5. Build the static comparison figure: `make_rankings_static_figure(rsl_monthly_mean, rsl_monthly_max, rsl_monthly_min, top_10_table, rsl, uhslc_id, station_name)`.
6. Build the interactive plotly version: `make_plotly_figure_rankings(rsl_monthly_mean, rsl_monthly_max, rsl_monthly_min, top_10_table, rsl_subset, record_id, station_name)`.
7. Persist results:
   - CSV: `SL_top_10_table_<site_tag>.csv`.
   - JSON: `SL_top_10_table_<site_tag>.json` containing `site_name`, `uhslc_id`, and `records` (list of row dicts).
   - PNG: `SL_rankings_<site_tag>.png` (static) and optional `.html` (plotly).

### Reporting style
- Refer to events by `(date, water_level_m_MHHW, ONI Mode)`.
- ENSO mode of an event = ONI Mode of the calendar month containing the event (nearest by date).
- Color convention: El Niño = red star, La Niña = blue circle, Neutral = orange dot.

### Hard rules
- Events must be at least 3 days apart (`get_top_ten` enforces this). Do not loosen this rule without explicit user request.
- Always include 10 high AND 10 low events in the same table.
- Always cite the data window of the underlying UHSLC record (it may be shorter than the analysis period for new stations).
