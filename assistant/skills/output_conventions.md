## Skill: Output Conventions

All persisted artifacts (figures, tables, structured results) MUST follow this convention so multi-site analyses never collide.

### Site tag
- Build with `build_site_tag(site_name, site_lon, site_lat)`.
- Format: `<lowercase_alphanum_site>_lat<lat3dec>p<dec>_lon<lon3dec>p<dec>`.
- Examples:
  - Palau (134.620, 7.340) → `palau_lat7p340_lon134p620`.
  - American Samoa (−170.700, −14.275) → `american_samoa_latm14p275_lonm170p700` (`m` prefix marks negative).

### Filenames
- Build with `build_output_filename(base_name, site_name, site_lon, site_lat, ext=...)`.
- Default extensions: `png` (figures), `csv` (tables), `json` (structured), optional `html` (plotly).
- Always pass a stable `base_name` (no timestamps, no run-specific suffixes).

### Folders
- All outputs go to `outputs/<site_tag>/`. Create with `Path('../../outputs') / build_site_tag(...)`; ensure `mkdir(parents=True, exist_ok=True)`.
- Do NOT write to `data/`, `matrix_cc/`, the notebook directory, or anywhere outside `outputs/<site_tag>/`.

### Canonical filenames (do not rename)
- Trend (notebook `a`):
  - `F10_SeaLevel_map_<site_tag>.png`
  - `SL_magnitude_map_<site_tag>.png`
  - `SL_magnitude_timeseries_<site_tag>.png`
  - `F10_SeaLevel_trends_<site_tag>.png`
  - `SL_ONI_scatter_<site_tag>.png`
  - `SL_magnitude_results_<site_tag>.csv`
  - `ENSO_SL_influence_summary_<site_tag>.csv`
  - `SL_trend_summary_metrics_<site_tag>.json`
- Anomalies (notebook `b`):
  - `1_2_2_SL_anomaly_annual_map_decadal_<site_tag>.png`
  - `SL_anomaly_yearly_mean_<site_tag>.csv`
  - `SL_anomaly_monthly_series_<site_tag>.csv`
  - `SL_anomaly_summary_metrics_<site_tag>.json`
- Flood frequency (notebook `c`):
  - `SL_FloodFrequency_threshold_counts_days_<site_tag>.png`
  - `SL_FloodFrequency_threshold_counts_heatmap_<site_tag>.png`
  - `F11_Minor_flood_matrix_<site_tag>.png`
  - `SL_flood_days_per_year_<site_tag>.csv`
  - `SL_flood_hours_per_year_<site_tag>.csv`
  - `SL_flood_frequency_summary_metrics_<site_tag>.json`
- Rankings (notebook `d`):
  - `SL_rankings_<site_tag>.png`
  - `SL_top_10_table_<site_tag>.csv`
  - `SL_top_10_table_<site_tag>.json`
  - Optional `SL_top_10_table_<site_tag>.png` (great_tables) and `.html` (plotly).

### JSON content contract
- Always include `site_name`, `uhslc_id` (when applicable), and the analysis window.
- Use floats (no numpy scalars) and ISO date strings. `save_dict_json` handles this automatically.
- Group related metrics into sub-dictionaries (`*_stats`) for forward compatibility.

### Hard rules
- Never overwrite a different site's outputs. Always re-derive `site_tag` from the loaded config.
- Never embed a site name into the function name; pass it as a parameter.
- When a notebook adds a new figure, document the filename in this file before merging.
