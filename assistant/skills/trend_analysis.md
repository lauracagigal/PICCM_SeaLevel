## Skill: Trend Analysis (notebook `a_sea_level_trend.ipynb`)

### Purpose
Compare absolute sea level (CMEMS altimetry, SLA) and relative sea level (UHSLC tide gauge) trends at the site and quantify ENSO modulation.

### Required inputs
- A valid site config JSON at `data/sites/<site>.json` (produced by `0_site_setup.ipynb`).

### Workflow
1. Load config: `site_cfg = load_site_config(site_config_path)`. Build `site_output_dir = Path('../../outputs') / build_site_tag(site_name, site_lon, site_lat)`.
2. Load UHSLC daily + hourly NetCDFs and the CMEMS file from `site_cfg['cmems_path']`.
3. Subset CMEMS to nearest grid point at `(site_lon, site_lat)`.
4. Compute trends:
   - Use `process_trend_with_nan(sla)` for altimetry; same for tide gauge `rsl` after datum adjustment.
   - Convert to mm/yr (`1000 * trend_rate`) and Δcm (`100 * trend_mag`).
5. Build tables and figures (always via helpers):
   - `plot_station_vs_grid_map(...)` — verifies which CMEMS cell maps to the gauge.
   - `plot_altimetry_scatter(...)`, `plot_altimetry_trend_timeseries(...)`.
   - `plot_tide_gauge_scatter(...)`, `plot_tide_gauge_trend_timeseries(...)`.
   - `plot_combined_trends(...)` — single panel for paper-style comparison.
   - `plot_magnitude_map_background(...)` and/or `plot_magnitude_map(...)` for the regional context map.
6. ENSO correlation:
   - Use `plot_enso_scatter(oni_daily, deseasoned_rsl)` to compute slope, r, p.
   - Build the ENSO summary table via `build_enso_summary_table(...)`.
7. Persist results in `site_output_dir`:
   - Magnitude table CSV via `save_table_to_csv(SL_magnitude_results, ...)`.
   - ENSO summary CSV via `save_table_to_csv(summary_table, ...)`.
   - Structured metrics JSON via `save_dict_json(summary_metrics, ...)` — must include altimetry/tide gauge trend (mm/yr), Δ sea level (cm), ENSO slope (m/°C), r, p-value, station, country, period.

### Reporting style
- "Altimetry trend (CMEMS L4, <start>–<end>): X mm/yr (Δ Y cm)."
- "Tide gauge trend (UHSLC <station>, <start>–<end>): X mm/yr (Δ Y cm)."
- "ENSO sensitivity (slope vs ONI): S m/°C, r = R, p = P."
- Always cite which JSON in `outputs/<site_tag>/` backs each number.

### Hard rules
- Do NOT redefine `process_trend_with_nan` or any plotting code inline.
- Do NOT save outputs outside `site_output_dir`.
- Use `site_eez` (loaded from `site_cfg['site_eez_shapefile']`) — never `palau_eez`.
