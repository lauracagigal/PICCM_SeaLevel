from pathlib import Path

import copernicusmarine
import numpy as np
import pandas as pd
import requests
import xarray as xr
from scipy import stats
import json

from data_downloaders import download_oni_index, download_uhslc_data

__all__ = [
    "get_CMEMS_data",
    "process_trend_with_nan",
    "build_enso_summary_table",
    "build_sl_magnitude_results",
    "save_table_to_csv",
    "save_dict_json",
    "select_uhslc_station",
    "save_site_config",
    "load_site_config",
    "build_site_tag",
    "build_output_filename",
    "get_uhslc_datum",
    "process_trend_single_series",
    "detect_enso_events",
    "get_dominant_enso",
    "get_top_ten",
    "get_top_10_table",
    "get_trend_info",
    "prepare_site_data",
]


# =========================
# Calculation functions
# =========================
def get_CMEMS_data(
    data_dir,
    minlon=125,
    maxlon=140,
    minlat=0,
    maxlat=15,
    start_date_str="1993-01-01T00:00:00",
    end_date_str="2025-04-30T23:59:59",
):
    """Download CMEMS L4 SSH data for a region/time period and return local path."""
    output_filename = f"cmems_L4_SSH_0.125deg_{start_date_str[0:4]}_{end_date_str[0:4]}.nc"
    output_path = Path(data_dir) / output_filename

    if output_path.exists():
        print(f"Using cached CMEMS file: {output_path}")
        return output_path

    copernicusmarine.subset(
        dataset_id="cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1D",
        variables=["adt", "sla"],
        minimum_longitude=minlon,
        maximum_longitude=maxlon,
        minimum_latitude=minlat,
        maximum_latitude=maxlat,
        start_datetime=start_date_str,
        end_datetime=end_date_str,
        output_directory=data_dir,
        output_filename=output_filename,
    )

    if not output_path.exists():
        raise FileNotFoundError(f"CMEMS download finished but file was not found: {output_path}")

    return output_path


def process_trend_with_nan(sea_level_anomaly):
    """Compute linear trend magnitude/rate and residual error, preserving NaNs."""
    sea_level_anomaly = sea_level_anomaly.transpose("time", ...)

    if sea_level_anomaly.sizes.get("time", 0) < 3:
        raise ValueError("At least 3 time steps are required to estimate trend and uncertainty.")

    t = pd.to_datetime(sea_level_anomaly.time.values)
    t_years = (t - t[0]).days / 365.25
    t_years = xr.DataArray(t_years, dims="time", coords={"time": sea_level_anomaly.time})

    t_centered = t_years - t_years.mean(dim="time")
    y_centered = sea_level_anomaly - sea_level_anomaly.mean(dim="time", skipna=True)

    denominator = (t_centered**2).sum(dim="time")
    slope = (t_centered * y_centered).sum(dim="time", skipna=True) / denominator

    intercept = sea_level_anomaly.mean(dim="time", skipna=True) - slope * t_years.mean()
    sea_level_trend = slope * t_years + intercept

    trend_mag = sea_level_trend.isel(time=-1) - sea_level_trend.isel(time=0)
    time_mag = float(t_years.isel(time=-1) - t_years.isel(time=0))
    trend_rate = trend_mag / time_mag

    residuals = sea_level_anomaly - sea_level_trend
    n = sea_level_anomaly.count(dim="time")
    trend_err = np.sqrt((residuals**2).sum(dim="time", skipna=True) / (n - 2)) / time_mag
    trend_err = trend_err.where(n > 2)

    p_value = xr.full_like(trend_rate, np.nan)
    return trend_mag, sea_level_trend, trend_rate, p_value, trend_err


def format_with_units(value, unit):
    """Format scalar values with optional units for reporting tables."""
    if pd.isna(value):
        return "N/A"
    if unit:
        return f"{value:.2f} {unit}"
    return f"{value:.2f}"


def build_enso_summary_table(slope, nino_1997, nina_1998, r_value, p_value):
    """Build the ENSO influence summary table and styled output."""
    summary_data = {
        "Description": [
            "Slope of Correlation Line",
            "El Niño 1997-1998 Min Sea Level",
            "El Niño 1997-1998 Median Sea Level",
            "La Niña 1998-2000 Max Sea Level",
            "La Niña 1998-2000 Median Sea Level",
            "Correlation Coefficient (r)",
            "p-value",
        ],
        "Value": [
            slope,
            100 * nino_1997.min().values,
            100 * nino_1997.median().values,
            100 * nina_1998.max().values,
            100 * nina_1998.median().values,
            r_value,
            p_value,
        ],
        "units": ["m/°C", "cm", "cm", "cm", "cm", "", ""],
    }

    summary_df = pd.DataFrame(summary_data)
    summary_df.attrs["description"] = "Correlation of Sea Level at Malakal with ONI 1983-2024."
    summary_df.attrs["source"] = "NOAA / University of Hawaii Sea Level Center"
    summary_df.attrs["notes"] = "Sea level data has been deseasoned and detrended."

    summary_df["Formatted"] = summary_df.apply(lambda row: format_with_units(row["Value"], row["units"]), axis=1)
    formatted_df = summary_df[["Description", "Formatted"]].rename(columns={"Formatted": "Value"}).reset_index(drop=True)

    footer_df = pd.DataFrame(
        {
            "Description": [f"Source: {summary_df.attrs['source']}", f"Notes: {summary_df.attrs['notes']}"],
            "Value": ["", ""],
        }
    )

    summary_table = pd.concat([formatted_df, footer_df], ignore_index=True)
    styled_df = summary_table.style.set_caption(summary_df.attrs["description"]).set_table_styles(
        [
            {"selector": "caption", "props": [("color", "black"), ("font-size", "16px"), ("font-weight", "bold")]},
            {
                "selector": "tbody tr:last-child td, tbody tr:nth-last-child(2) td",
                "props": [("font-style", "italic"), ("font-align", "center")],
            },
        ]
    )
    return summary_table, styled_df


def build_sl_magnitude_results(
    trend_rate_asl,
    trend_rate_rsl,
    trend_mag_asl,
    trend_mag_rsl,
    sla_nearest_lat,
    sla_nearest_lon,
    rsl_lat,
    rsl_lon,
    start_date_str,
    end_date_str,
):
    """Build sea level magnitude comparison table and metrics used for glue."""
    data_source_altimetry = "CMEMS SSH L4 0.125 deg (SLA)"
    data_source_tide_gauge = "UHSLC RQDS"
    time_period = f"{start_date_str} to {end_date_str}"

    trend_mmyr_altimetry = 1000 * trend_rate_asl.values
    trend_mmyr_tide_gauge = 1000 * trend_rate_rsl.values
    delta_sea_level_altimetry = 100 * trend_mag_asl.values
    delta_sea_level_tide_gauge = 100 * trend_mag_rsl.values

    results = pd.DataFrame(
        {
            "Trend (mm/yr)": [trend_mmyr_altimetry, trend_mmyr_tide_gauge],
            "Trend (in/yr)": [trend_mmyr_altimetry * 0.0393701, trend_mmyr_tide_gauge * 0.0393701],
            "Δ Sea Level (cm)": [delta_sea_level_altimetry, delta_sea_level_tide_gauge],
            "Δ Sea Level (in)": [delta_sea_level_altimetry * 0.393701, delta_sea_level_tide_gauge * 0.393701],
            "Latitude": [sla_nearest_lat, rsl_lat],
            "Longitude": [sla_nearest_lon, rsl_lon],
            "Time_Period": [time_period, time_period],
            "Data_Source": [data_source_altimetry, data_source_tide_gauge],
        },
        index=["Altimetry", "Tide Gauge"],
    )

    glue_values = {
        "trend_mmyr_altimetry": trend_mmyr_altimetry,
        "trend_inyr_altimetry": trend_mmyr_altimetry * 0.0393701,
        "trend_mmyr_tide_gauge": trend_mmyr_tide_gauge,
        "trend_inyr_tide_gauge": trend_mmyr_tide_gauge * 0.0393701,
        "delta_cm_altimetry": delta_sea_level_altimetry,
        "delta_in_altimetry": delta_sea_level_altimetry * 0.393701,
        "delta_cm_tide_gauge": delta_sea_level_tide_gauge,
        "delta_in_tide_gauge": delta_sea_level_tide_gauge * 0.393701,
    }
    return results, glue_values


def save_table_to_csv(table_df, output_dir, filename, index=False):
    """Save a table DataFrame to output directory and return saved path."""
    output_path = Path(output_dir) / filename
    table_df.to_csv(output_path, index=index)
    return output_path


def save_dict_json(data_dict, output_dir, filename):
    """Save dictionary as JSON in output directory and return saved path."""
    output_path = Path(output_dir) / filename

    def _default(obj):
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if hasattr(obj, "isoformat"):
            try:
                return obj.isoformat()
            except Exception:
                pass
        return str(obj)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2, ensure_ascii=False, default=_default)
    return output_path


def _haversine_km(lon1, lat1, lon2, lat2):
    """Great-circle distance in km between two lon/lat points."""
    earth_radius_km = 6371.0
    lon1, lat1, lon2, lat2 = np.radians([lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return earth_radius_km * c


def select_uhslc_station(
    site_lon,
    site_lat,
    station_country_filter=None,
    selected_uhslc_id=None,
    selected_station_name=None,
    metadata_url="https://uhslc.soest.hawaii.edu/data/meta.geojson",
    timeout=30,
):
    """
    Fetch UHSLC metadata, build station options, and select one station.

    Selection priority:
    1) selected_uhslc_id (if provided)
    2) selected_station_name (if provided)
    3) nearest station in filtered list (default fallback)
    """
    response = requests.get(metadata_url, timeout=timeout)
    response.raise_for_status()
    data = response.json()

    candidates = []
    for feature in data.get("features", []):
        geometry = feature.get("geometry", {})
        properties = feature.get("properties", {})
        coordinates = geometry.get("coordinates")

        if not coordinates or len(coordinates) < 2:
            continue

        feat_lon, feat_lat = coordinates[0], coordinates[1]
        dist_km = _haversine_km(site_lon, site_lat, feat_lon, feat_lat)

        candidates.append(
            {
                "feature": feature,
                "distance_km": float(dist_km),
                "uhslc_id": properties.get("uhslc_id"),
                "name": properties.get("name"),
                "country": properties.get("country"),
                "lon": feat_lon,
                "lat": feat_lat,
            }
        )

    if not candidates:
        raise ValueError("No valid UHSLC station found in metadata response.")

    if station_country_filter:
        filtered = [
            c
            for c in candidates
            if (c.get("country") or "").strip().lower() == station_country_filter.strip().lower()
        ]
    else:
        filtered = candidates

    if not filtered:
        raise ValueError(f"No UHSLC stations found for country filter: {station_country_filter}")

    filtered = sorted(filtered, key=lambda c: c["distance_km"])
    options_df = pd.DataFrame(
        [
            {
                "uhslc_id": c["uhslc_id"],
                "name": c["name"],
                "country": c["country"],
                "distance_km": round(c["distance_km"], 1),
                "lon": c["lon"],
                "lat": c["lat"],
            }
            for c in filtered
        ]
    )

    selected = None
    selection_reason = None
    if selected_uhslc_id is not None:
        selected = next((c for c in filtered if c["uhslc_id"] == selected_uhslc_id), None)
        if selected is None:
            raise ValueError(f"selected_uhslc_id={selected_uhslc_id} not found in filtered candidates.")
        selection_reason = "selected_uhslc_id"
    elif selected_station_name is not None:
        selected = next(
            (c for c in filtered if (c["name"] or "").strip().lower() == selected_station_name.strip().lower()),
            None,
        )
        if selected is None:
            raise ValueError(f'selected_station_name="{selected_station_name}" not found in filtered candidates.')
        selection_reason = "selected_station_name"
    else:
        selected = filtered[0]
        selection_reason = "nearest_fallback"

    feature = selected["feature"]
    return {
        "options_df": options_df,
        "selection_reason": selection_reason,
        "distance_km": selected["distance_km"],
        "uhslc_id": feature["properties"]["uhslc_id"],
        "station": feature["properties"]["name"],
        "country": feature["properties"]["country"],
        "lon": feature["geometry"]["coordinates"][0],
        "lat": feature["geometry"]["coordinates"][1],
    }


def save_site_config(config_dict, output_path):
    """Save site configuration dictionary as JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.Series(config_dict).to_json(output_path, indent=2, force_ascii=False)
    return output_path


def load_site_config(config_path):
    """Load site configuration dictionary from JSON file."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Site config not found: {config_path}")
    return pd.read_json(config_path, typ="series").to_dict()


def build_site_tag(site_name, site_lon, site_lat):
    """Build a filename-safe site tag including name and coordinates."""
    safe_name = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(site_name)).strip("_")
    safe_name = "_".join(part for part in safe_name.split("_") if part)
    lat_str = f"{float(site_lat):.3f}".replace(".", "p").replace("-", "m")
    lon_str = f"{float(site_lon):.3f}".replace(".", "p").replace("-", "m")
    return f"{safe_name}_lat{lat_str}_lon{lon_str}"


def build_output_filename(base_name, site_name, site_lon, site_lat, ext="png"):
    """Build standardized output filename with site and coordinates."""
    site_tag = build_site_tag(site_name, site_lon, site_lat)
    ext = ext.lstrip(".")
    return f"{base_name}_{site_tag}.{ext}"


def get_uhslc_datum(uhslc_id, datum_name):
    """Retrieve a tide datum value (mm) and full datum table for a UHSLC station."""
    url = (
        "https://uhslc.soest.hawaii.edu/stations/TIDES_DATUMS/fd/LST/fd"
        f"{int(uhslc_id):03}/datumTable_{int(uhslc_id):03}_mm_GMT.csv"
    )
    datum_table = pd.read_csv(url)
    datum_value = datum_table[datum_table["Name"] == datum_name]["Value"].values[0]
    return float(datum_value), datum_table


def process_trend_single_series(data, var):
    """Fit linear trend for one xarray time series variable and return coefficients and trendline."""
    data = data[var].dropna(dim="time")
    time_num = data["time"].astype("datetime64[D]").astype(float)
    y = data[0].values
    coefficients = np.polyfit(time_num, y, 1)
    trendline = np.poly1d(coefficients)
    return coefficients, trendline, coefficients[0] * 365.25


def detect_enso_events(oni_df):
    """Detect El Nino / La Nina events using 5-month ONI threshold rule."""
    oni_df = oni_df.copy()
    oni_df["ONI Mode"] = "Neutral"
    oni_df["year_storm"] = oni_df.index.year
    oni_df.loc[oni_df.index.month < 5, "year_storm"] -= 1

    el_nino_rolling = (oni_df["ONI"] > 0.5).rolling(window=5, min_periods=5).sum() == 5
    oni_df["El Nino"] = False
    for i in range(len(oni_df)):
        if el_nino_rolling.iloc[i]:
            start_idx = max(0, i - 4)
            oni_df.iloc[start_idx : i + 1, oni_df.columns.get_loc("El Nino")] = True

    la_nina_rolling = (oni_df["ONI"] < -0.5).rolling(window=5, min_periods=5).sum() == 5
    oni_df["La Nina"] = False
    for i in range(len(oni_df)):
        if la_nina_rolling.iloc[i]:
            start_idx = max(0, i - 4)
            oni_df.iloc[start_idx : i + 1, oni_df.columns.get_loc("La Nina")] = True

    oni_df.loc[oni_df["La Nina"] == True, "ONI Mode"] = "La Nina"
    oni_df.loc[oni_df["El Nino"] == True, "ONI Mode"] = "El Nino"
    return oni_df


def get_dominant_enso(series):
    """Return dominant ENSO mode in a grouped series."""
    el_nino_count = (series == "El Nino").sum()
    la_nina_count = (series == "La Nina").sum()
    if el_nino_count > la_nina_count:
        return "El Nino"
    if la_nina_count > el_nino_count:
        return "La Nina"
    return "Neutral"


def get_top_ten(rsl, record_id, mode="max"):
    """Get top/bottom 10 unique sea-level events at least 3 days apart."""
    sea_level_series = rsl.sea_level.sel(record_id=record_id).to_series()
    if mode == "max":
        top_values = sea_level_series.nlargest(100)
    elif mode == "min":
        top_values = sea_level_series.nsmallest(100)
    else:
        raise ValueError('mode must be either "max" or "min"')

    filtered_dates = []
    top_10_values = pd.Series(dtype=float)
    for date, value in top_values.items():
        if all(abs((date - pd.to_datetime(added_date)).days) > 3 for added_date in filtered_dates):
            filtered_dates.append(date)
            top_10_values.loc[date] = value
        if len(filtered_dates) == 10:
            break

    rank = np.arange(1, 11)
    station_name = str(rsl["station_name"].sel(record_id=record_id).values)
    top_10_values = pd.DataFrame({"rank": rank, "date": top_10_values.index, "sea level (m)": top_10_values.values})
    top_10_values["station_name"] = station_name
    top_10_values["record_id"] = record_id
    top_10_values["type"] = mode
    top_10_values["date"] = top_10_values["date"].dt.round("h")
    return top_10_values


def get_top_10_table(rsl, record_id):
    """Build top-10 high/low events table joined with nearest ONI state."""
    top_10_values_max = get_top_ten(rsl, record_id, mode="max")
    top_10_values_min = get_top_ten(rsl, record_id, mode="min")
    top_10_table = pd.concat([top_10_values_max, top_10_values_min])

    oni = download_oni_index("https://psl.noaa.gov/data/correlation/oni.data")
    oni = detect_enso_events(oni).drop(columns=["La Nina", "El Nino"])
    oni_val = oni.reindex(top_10_table["date"], method="nearest")
    top_10_table = pd.merge(top_10_table, oni_val, left_on="date", right_index=True)
    return top_10_table


def get_trend_info(x, y, timescale="days"):
    """Linear trend metadata for flood count charts."""
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    trend_counts = intercept + slope * x
    if timescale == "days":
        trend_label = "Increasing {:.2f} days/year (p= {:.2f})".format(slope, p_value)
    else:
        trend_label = "Increasing {:.2f} hours/year (p= {:.2f})".format(slope, p_value)
    linestyle_trend = "-" if p_value < 0.05 else "--"
    return trend_counts, trend_label, linestyle_trend, slope, p_value


def prepare_site_data(site_config, data_dir):
    """
    Resolve station selection, save it into config, and pre-download common datasets.

    Returns updated configuration dictionary.
    """
    cfg = dict(site_config)
    selection = select_uhslc_station(
        site_lon=float(cfg["site_lon"]),
        site_lat=float(cfg["site_lat"]),
        station_country_filter=cfg.get("station_country_filter"),
        selected_uhslc_id=cfg.get("selected_uhslc_id"),
        selected_station_name=cfg.get("selected_station_name"),
    )

    cfg["selected_uhslc_id"] = int(selection["uhslc_id"])
    cfg["selected_station_name"] = selection["station"]
    cfg["station"] = selection["station"]
    cfg["country"] = selection["country"]
    cfg["station_lon"] = float(selection["lon"])
    cfg["station_lat"] = float(selection["lat"])
    cfg["station_distance_km"] = float(selection["distance_km"])

    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    # Prefetch tide-gauge data products used across notebooks.
    download_uhslc_data(data_dir, cfg["selected_uhslc_id"], "daily")
    download_uhslc_data(data_dir, cfg["selected_uhslc_id"], "hourly")

    # Prefetch ONI index.
    download_oni_index("https://psl.noaa.gov/data/correlation/oni.data")

    # Prefetch CMEMS data.
    cmems_bbox_override = cfg.get("cmems_bbox_override")
    if cmems_bbox_override is None:
        try:
            import geopandas as gpd

            site_eez_path = Path(cfg["site_eez_shapefile"])
            if not site_eez_path.is_absolute():
                site_eez_path = (Path.cwd() / site_eez_path).resolve()
            site_shp = gpd.read_file(site_eez_path)
            geom = site_shp["geometry"].iloc[0]
            min_lon, min_lat, max_lon, max_lat = geom.bounds
        except Exception:
            # Fallback to broad W Pacific box if EEZ bounds are unavailable.
            min_lon, max_lon, min_lat, max_lat = 125, 140, 0, 15
    else:
        min_lon, max_lon, min_lat, max_lat = cmems_bbox_override

    cmems_path = get_CMEMS_data(
        data_dir=data_dir,
        minlon=float(min_lon),
        maxlon=float(max_lon),
        minlat=float(min_lat),
        maxlat=float(max_lat),
        start_date_str=cfg.get("cmems_start_datetime", "1993-01-01T00:00:00"),
        end_date_str=cfg.get("cmems_end_datetime", "2025-04-30T23:59:59"),
    )
    cfg["cmems_path"] = str(cmems_path)
    cfg["cmems_filename"] = Path(cmems_path).name
    return cfg
