## Skill: Anomaly Analysis (notebook `b_sea_level_anomaly.ipynb`)

### Purpose
Quantify and visualize sea level anomalies at regional (CMEMS SLA) and local (UHSLC tide gauge) scale, including decadal maps and annual/monthly variability with ENSO context.

### Required inputs
- A valid site config JSON (`data/sites/<site>.json`).
- Pre-downloaded UHSLC + CMEMS files (from `0_site_setup.ipynb`).

### Workflow
1. Load config and build `site_output_dir`.
2. Reference UHSLC tide gauge to MSL with `get_uhslc_datum(uhslc_id, 'MSL')`.
3. Detrend the tide gauge series with `process_trend_single_series(rsl, 'sea_level_msl')`.
4. Resample to monthly, compute climatology by month, derive `rsl_anomalies` by subtracting climatology.
5. Build the "storm year" view (May–April):
   - Compute `rsl_years` with `storm_time` shifted to start in May.
   - Yearly mean / min / max via `groupby('storm_time.year')`.
6. Maps & figures — call via `sea_level_plotting`:
   - `plot_anomaly_decadal_maps(sla_detrended, rsl, rsl_anomalies, yr_start, yr_stop, yr_start_str, yr_stop_str)` for the 2x2 decadal SLA composite.
   - `plot_anomaly_station_series(rsl_yearly_mean, rsl_years, rsl_monthly, enso_events, sid=0)` for the per-station annual range with ENSO shading.
   - `plot_annual_range_fill(rsl_yearly_mean, rsl_yearly_min, rsl_yearly_max)` for the annual envelope only.
7. ENSO context: use `download_oni_index(...)` + `detect_enso_events(...)`; adjust the index to storm-year fractional years before passing to `plot_anomaly_station_series`.
8. Persist results:
   - CSV: yearly mean anomaly (`SL_anomaly_yearly_mean_<site_tag>.csv`) and monthly series (`SL_anomaly_monthly_series_<site_tag>.csv`).
   - JSON: `SL_anomaly_summary_metrics_<site_tag>.json` with `annual_mean_anomaly_stats` and `monthly_anomaly_stats` (n, mean, min/max, std).

### Reporting style
- State the climatology base period (default: full UHSLC record at the station).
- Always specify "detrended" when reporting anomalies derived from `sea_level_anomaly_detrended`.
- Use storm-year labels (e.g. "Storm year 1997 = May 1997 → April 1998") in narrative.

### Hard rules
- Do NOT inline new figure code; add helper functions to `sea_level_plotting.py` if a new chart type is needed.
- The decadal maps must use `pacific_all_west_formatter` for longitude labels (Pacific-centric).
- Always include the tide gauge marker on the decadal maps via the helper (do not draw it manually).
