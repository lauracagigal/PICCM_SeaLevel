## Skill: Site Setup (notebook `0_site_setup.ipynb`)

### Purpose
Define a new analysis site and pre-download all required datasets ONCE, so every other notebook (`a/b/c/d`) only loads cached data.

### Inputs the assistant must collect
- `site_name` (display name).
- `site_lon`, `site_lat` (decimal degrees; longitudes 0–360 or −180–180 both accepted, but be consistent within the run).
- `station_country_filter` (UHSLC `properties.country` exact match).
- Optional `selected_uhslc_id` (int) or `selected_station_name` (str). If both omitted, the nearest filtered station is chosen.
- `site_eez_shapefile` (path to a polygon shapefile for the site's EEZ).
- `start_date` / `end_date` for analysis (default: `1993-01-01` to `2022-12-31`).
- Optional `cmems_bbox_override` `[min_lon, max_lon, min_lat, max_lat]` (defaults to EEZ bounds).
- `cmems_start_datetime` / `cmems_end_datetime` for the altimetry download window.

### Workflow
1. Build the `site_config` dictionary with the inputs above.
2. Call `prepare_site_data(site_config, Path('../../data/sea_level'))`. This:
   - Resolves UHSLC station selection (id, name, country, lon, lat, distance_km).
   - Downloads UHSLC hourly + daily NetCDFs into `data/sea_level/`.
   - Downloads ONI.
   - Downloads CMEMS L4 SSH for the bbox+time window into `data/sea_level/cmems_L4_SSH_0.125deg_<y0>_<y1>.nc`.
3. Persist the enriched config: `save_site_config(site_config, Path('../../data/sites/<site>.json'))`.

### Output contract
- A JSON file at `data/sites/<site>.json` that includes ALL of: the original inputs PLUS `selected_uhslc_id`, `selected_station_name`, `station`, `country`, `station_lon`, `station_lat`, `station_distance_km`, `cmems_path`, `cmems_filename`.
- Cached NetCDFs in `data/sea_level/`.

### Common follow-up actions for the assistant
- Confirm which station was selected and the distance from the user-provided coordinates. If `station_distance_km` > 100 km, warn the user.
- If `cmems_bbox_override` is None and the EEZ shapefile is missing, fall back to the broad West Pacific box `(125, 140, 0, 15)` and warn.
- After saving the config, recommend opening `a_sea_level_trend.ipynb` next.

### Hard rules
- Do not run `0_site_setup.ipynb` automatically more than once unless the user changes the site or the cached files are missing.
- Never write site config files outside `data/sites/`.
- Never change `selected_uhslc_id` after it has been written — create a new config for a new site instead.
