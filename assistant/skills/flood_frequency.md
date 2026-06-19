## Skill: Flood Frequency (notebook `c_sea_level_ff.ipynb`)

### Purpose
Quantify minor (nuisance / high-tide) flooding frequency at the tide gauge and its relationship with ENSO.

### Required inputs
- Site config JSON.
- UHSLC hourly NetCDF (cached in `data/sea_level/`).
- `threshold` in cm above MHHW. Default: **30 cm**.

### Definitions
- A **minor flood day** is a calendar day in which the hourly tide gauge water level reaches or exceeds `threshold` cm above MHHW for at least one hour.
- A **flood hour** is any hour exceeding the same threshold.
- The **storm year** runs from May 1 (year `Y`) through April 30 (year `Y+1`), labeled with `Y`.

### Workflow
1. Load config and UHSLC hourly data. Reference to MHHW via `get_uhslc_datum(uhslc_id, 'MHHW')`.
2. Restrict to the official datum epoch (parse `Epoch` from the datum table).
3. Build `flood_days_per_year` and `flood_hours_per_year` DataFrames keyed by `year_storm`.
4. ENSO join:
   - `oni = download_oni_index(...)`, `enso_events = detect_enso_events(oni)`.
   - Yearly aggregate: `enso_yearly = enso_events.groupby('year_storm')['ONI Mode'].agg(get_dominant_enso)`.
   - Merge into `flood_days_per_year` / `flood_hours_per_year` on `year_storm`.
5. Figures — call via `sea_level_plotting`:
   - `plot_histogram_with_threshold(hourly_data, threshold)` for the threshold context.
   - `plot_flood_counts_with_trend(flood_count_per_year=..., timescale='days' | 'hours')` for trend chips.
   - `plot_flood_counts_with_oni(flood_days_per_year, enso_events)` for the combined ENSO panel.
   - `plot_flood_days_heatmap(df, flood_days_per_year)` and `plot_flood_matrix_summary(df, flood_days_per_year)` for the monthly heatmap and composite figure.
   - `plot_oni_only(enso_events)` and `plot_monthly_contribution_vertical(df, month_names)` for auxiliary panels.
6. Persist results:
   - CSVs: `SL_flood_days_per_year_<site_tag>.csv`, `SL_flood_hours_per_year_<site_tag>.csv`.
   - JSON: `SL_flood_frequency_summary_metrics_<site_tag>.json` with `threshold_cm`, `flood_days_per_year_stats`, `flood_hours_per_year_stats`, and `slope_days`, `p_value_days`, `slope_hours`, `p_value_hours` when available.

### Reporting style
- "At <station>, minor flood days exceed <threshold> cm above MHHW. Annual count trend: S days/year (p = P)."
- Always specify storm-year vs calendar-year when reporting yearly counts.
- Color convention: El Niño = red, La Niña = blue, Neutral = gray.

### Hard rules
- Do NOT use percentile thresholds in primary reporting unless explicitly requested; the canonical threshold is 30 cm above MHHW.
- Do NOT mix calendar-year and storm-year aggregations in the same chart without labeling both.
- All figures must come from `sea_level_plotting` helpers; if a new variant is needed, add it there first.
