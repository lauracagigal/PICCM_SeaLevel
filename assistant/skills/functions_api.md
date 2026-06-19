## Skill: Functions API Reference (`functions/sea_level.py` + `functions/sea_level_plotting.py`)

This is the single source of truth for what the assistant is allowed to call. If something is missing, ADD a function here — do not inline it in notebooks.

### `functions/sea_level.py` — calculations & utilities
- `get_CMEMS_data(data_dir, minlon, maxlon, minlat, maxlat, start_date_str, end_date_str)` → cached NetCDF path.
- `process_trend_with_nan(sea_level_anomaly)` → `(trend_mag, sea_level_trend, trend_rate, p_value, trend_err)` (xarray-aware, time-major).
- `process_trend_single_series(data, var)` → `(coefficients, trendline, rate_per_year)` for a single 1-D series.
- `build_enso_summary_table(slope, nino_1997, nina_1998, r_value, p_value)` → `(summary_df, styled_df)`.
- `build_sl_magnitude_results(trend_rate_asl, trend_rate_rsl, trend_mag_asl, trend_mag_rsl, sla_nearest_lat, sla_nearest_lon, rsl_lat, rsl_lon, start_date_str, end_date_str)` → `(results_df, glue_values_dict)`.
- `save_table_to_csv(table_df, output_dir, filename, index=False)` → output path.
- `save_dict_json(data_dict, output_dir, filename)` → output path (handles numpy and datetime types).
- `select_uhslc_station(site_lon, site_lat, station_country_filter, selected_uhslc_id=None, selected_station_name=None)` → dict with `options_df`, `selection_reason`, `uhslc_id`, `station`, `country`, `lon`, `lat`, `distance_km`.
- `save_site_config(config_dict, output_path)` / `load_site_config(config_path)` — JSON I/O for site configs.
- `build_site_tag(site_name, site_lon, site_lat)` and `build_output_filename(base_name, site_name, site_lon, site_lat, ext='png')` — canonical naming.
- `get_uhslc_datum(uhslc_id, datum_name)` → `(value_mm, datum_table)`.
- `detect_enso_events(oni_df)` and `get_dominant_enso(series)` — ENSO classification (5-month rule, dominant per group).
- `get_top_ten(rsl, record_id, mode)` and `get_top_10_table(rsl, record_id)` — ranking helpers.
- `get_trend_info(x, y, timescale='days')` → `(trend_counts, trend_label, linestyle_trend, slope, p_value)`.
- `prepare_site_data(site_config, data_dir)` → enriched `site_config` after running station selection + downloads (UHSLC, ONI, CMEMS).

### `functions/sea_level_plotting.py` — figure builders
- Base helpers: `plot_map_base`, `plot_zebra_frame`, `add_zebra_frame`, `pacific_all_west_formatter`.
- Trend / map: `plot_station_vs_grid_map`, `plot_altimetry_scatter`, `plot_altimetry_trend_timeseries`, `plot_tide_gauge_scatter`, `plot_tide_gauge_trend_timeseries`, `plot_combined_trends`, `plot_magnitude_map`, `plot_magnitude_map_background`.
- ENSO scatter: `plot_enso_scatter`.
- Anomalies: `plot_tg_rsl_anomaly_annual`, `plot_anomaly_decadal_maps`, `plot_anomaly_station_series`, `plot_annual_range_fill`.
- Flood frequency: `plot_flood_count_per_year`, `plot_trend`, `plot_oni_segments`, `plot_monthly_contribution`, `plot_histogram_with_threshold`, `plot_flood_counts_with_trend`, `plot_flood_counts_with_oni`, `plot_flood_days_heatmap`, `plot_flood_matrix_summary`, `plot_simple_timeseries`, `plot_daily_max_timeseries`, `plot_oni_only`, `plot_monthly_contribution_vertical`.
- Rankings: `style_oni_based`, `make_plotly_figure_rankings`, `make_rankings_static_figure`.
- Compatibility: `plot_map` (alias for `plot_map_base`).

### `functions/data_downloaders.py` — raw downloaders
- `download_uhslc_data(data_dir, uhslc_id, frequency)` — hourly/daily NetCDFs; `record_id` and string columns are cleaned automatically.
- `download_oni_index(p_data)` — NOAA ONI as a monthly DataFrame.
- `download_ERDDAP_data(base_url, dataset_id, date_ini, date_end, lon_range, lat_range)` — generic ERDDAP fetcher.
- `download_ibtracs(url, basin=None)` — IBTrACS storm tracks (only if the user explicitly asks for storms).
- `download_MLO_CO2_data`, `download_HOT_CO2_data`, `GHCN.*` — out-of-scope for SL; do not invoke unless asked.
- `filter_by_time_completeness(df, time_col, month_threshold, year_threshold)` — completeness QC for daily series.

### Hard rules
- If a function is needed but missing, add it to `sea_level.py` (calculations) or `sea_level_plotting.py` (figures), then import it in the notebook. Never inline.
- Public API is captured in `__all__` of `sea_level.py`. Keep it updated when adding new exports.
- After editing modules, reload them in the active notebook with `import importlib; import sea_level as sea_level_mod; importlib.reload(sea_level_mod)`.
