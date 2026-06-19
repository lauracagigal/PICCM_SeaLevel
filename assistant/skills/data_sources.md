## Skill: Data Sources & Attribution

### Tide gauges — UHSLC (University of Hawaii Sea Level Center)
- Fast hourly: `https://uhslc.soest.hawaii.edu/data/netcdf/fast/hourly/h<uhslc_id:03>.nc`.
- Fast daily: `https://uhslc.soest.hawaii.edu/data/netcdf/fast/daily/d<uhslc_id:03>.nc`.
- Metadata GeoJSON: `https://uhslc.soest.hawaii.edu/data/meta.geojson`.
- Datums (in mm relative to Station Zero, GMT): `http://uhslc.soest.hawaii.edu/stations/TIDES_DATUMS/fd/LST/fd<id>/datumTable_<id>_mm_GMT.csv`.
- Units: millimeters relative to Station Zero, timezone GMT/UTC.
- Citation: University of Hawaii Sea Level Center (UHSLC). Always credit UHSLC for any tide-gauge result. Treat user-supplied tide gauge files as overlays unless explicitly stated.

### Altimetry — CMEMS L4 SSH
- Dataset id: `cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1D`.
- Variables in use: `adt` (absolute dynamic topography), `sla` (sea level anomaly).
- Spatial resolution: 0.125°. Temporal: daily.
- Access: via `copernicusmarine.subset(...)` wrapped by `get_CMEMS_data(...)`.
- Cached locally as `data/sea_level/cmems_L4_SSH_0.125deg_<year_start>_<year_end>.nc`.
- Citation: E.U. Copernicus Marine Service Information.

### ENSO — NOAA ONI
- URL: `https://psl.noaa.gov/data/correlation/oni.data`.
- Format: monthly Niño 3.4 anomalies. Replace `-99.9` with NaN on load.
- Classification rules:
  - El Niño when 5 consecutive months of ONI ≥ 0.5.
  - La Niña when 5 consecutive months of ONI ≤ −0.5.
  - Otherwise Neutral.
- Color convention everywhere: El Niño = red, La Niña = blue, Neutral = gray.
- Citation: NOAA Climate Prediction Center / Physical Sciences Laboratory.

### EEZ polygons
- Per-site polygon shapefile referenced in the site config (`site_eez_shapefile`).
- Read with `geopandas.read_file(...)` from the path stored in the site config.
- Used both for plotting (EEZ outline on maps) and for inferring the default CMEMS bbox.

### Optional / out-of-scope data sources
The following exist in `data_downloaders.py` but are NOT part of CIndRA's standard PICCM Sea Level workflow:
- `download_MLO_CO2_data`, `download_HOT_CO2_data` — atmospheric / ocean CO2.
- `GHCN.*` — daily land station climatology.
- `download_ibtracs` — tropical cyclone tracks.

Only invoke these when the user explicitly asks for them; otherwise stick to UHSLC + CMEMS + ONI.

### Hard rules
- Always attribute the data source in narrative outputs (e.g. "Source: UHSLC FAST hourly").
- Never present user-uploaded data as primary. If a custom file is provided, ask the user whether it should overlay, replace, or validate the canonical source.
- Never invent station names or UHSLC IDs; always go through `select_uhslc_station(...)` or the cached site config.
- Always state units (mm, cm, mm/yr, °C, days/yr) and timezone (GMT for tide gauge) in any numeric statement.
