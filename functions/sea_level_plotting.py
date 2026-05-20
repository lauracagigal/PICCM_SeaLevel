import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy import stats
import matplotlib.colors as mcolors
from matplotlib.colors import Normalize
from matplotlib.ticker import FuncFormatter
import plotly.graph_objects as go
from sea_level import get_trend_info


def add_zebra_frame(ax, lw=2, segment_length=0.5, crs=ccrs.PlateCarree()):
    left, right, bot, top = ax.get_extent(crs=crs)

    left_start = left - left % segment_length
    bot_start = bot - bot % segment_length

    if left % segment_length >= segment_length / 2:
        left_start += segment_length
    if bot % segment_length >= segment_length / 2:
        bot_start += segment_length

    right_end = right + (segment_length - right % segment_length)
    top_end = top + (segment_length - top % segment_length)

    num_segments_x = int(np.ceil((right_end - left_start) / segment_length))
    num_segments_y = int(np.ceil((top_end - bot_start) / segment_length))

    for i in range(num_segments_x):
        color = "black" if (left_start + i * segment_length) % (2 * segment_length) == 0 else "white"
        start_x = left_start + i * segment_length
        end_x = start_x + segment_length
        ax.hlines([bot, top], start_x, end_x, colors=color, linewidth=lw, transform=crs)

    for j in range(num_segments_y):
        color = "black" if (bot_start + j * segment_length) % (2 * segment_length) == 0 else "white"
        start_y = bot_start + j * segment_length
        end_y = start_y + segment_length
        ax.vlines([left, right], start_y, end_y, colors=color, linewidth=lw, transform=crs)


def plot_station_vs_grid_map(lon, lat, sla_nearest_lon, sla_nearest_lat, sla, xmin=134, xmax=135, ymin=6.5, ymax=8):
    crs = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={"projection": crs})
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])

    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)

    ax.plot(lon, lat, marker="o", color="red", markersize=10, transform=crs)
    ax.plot(sla_nearest_lon, sla_nearest_lat, marker="o", color="blue", markersize=8, transform=crs)

    lon2d, lat2d = np.meshgrid(sla.longitude, sla.latitude)
    ax.scatter(lon2d, lat2d, transform=crs)

    degree_interval = 0.25
    ax.set_xticks(np.arange(xmin, xmax, degree_interval), crs=crs)
    ax.set_yticks(np.arange(ymin, ymax, degree_interval), crs=crs)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    add_zebra_frame(ax, lw=5, segment_length=0.25, crs=crs)
    ax.gridlines(
        draw_labels=True,
        linestyle=":",
        color="black",
        alpha=0.5,
        xlocs=ax.get_xticks(),
        ylocs=ax.get_yticks(),
    )

    ax.text(lon + 0.05, lat - 0.05, "Tide Gauge", transform=crs, ha="left", va="top", fontsize=12)
    ax.text(
        sla_nearest_lon,
        sla_nearest_lat + 0.05,
        "Nearest Altimetry \n Grid Point",
        transform=crs,
        ha="center",
        va="bottom",
        fontsize=12,
    )
    return fig, ax


def plot_altimetry_scatter(sla_nearest, lat_str, lon_str, start_date_str, end_date_str, start_date, end_date):
    sns.set_style("whitegrid")
    palette = sns.color_palette("Paired")
    fig, ax = plt.subplots()
    ax.scatter(sla_nearest["time"], 100 * sla_nearest, label="Altimetry", color=palette[1], alpha=1, s=5)
    ax.set_title(f"Altimetry ({lat_str}, {lon_str}) ({start_date_str} to {end_date_str})")
    ax.set_xlabel("Year")
    ax.set_ylabel("Height (cm)")
    ax.set_ylim([-35, 35])
    ax.set_xlim([start_date, end_date])
    return fig, ax


def plot_map_base(xlims, ylims):
    crs = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": crs})
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)
    cmap = sns.color_palette("mako_r", as_cmap=True)
    ax.coastlines()
    ax.add_feature(cfeature.LAND, color="lightgrey")
    return fig, ax, crs, cmap


def plot_zebra_frame(ax, lw=5, segment_length=2, crs=ccrs.PlateCarree()):
    add_zebra_frame(ax=ax, lw=lw, segment_length=segment_length, crs=crs)
    gl = ax.gridlines(
        draw_labels=True,
        linestyle=":",
        color="black",
        alpha=0.5,
        xlocs=ax.get_xticks(),
        ylocs=ax.get_yticks(),
    )
    gl.top_labels = False
    gl.right_labels = False


def plot_altimetry_trend_timeseries(
    sla_nearest,
    trend_line_asl,
    trend_mag_asl,
    trend_rate_asl,
    lat_str,
    lon_str,
    start_date_str,
    end_date_str,
    start_date,
    end_date,
):
    sns.set_style("whitegrid")
    palette = sns.color_palette("Set1")
    fig, ax = plt.subplots()
    ax.scatter(sla_nearest["time"], 100 * sla_nearest, label="Altimetry", color=palette[0], alpha=0.2, s=5)
    ax.plot(sla_nearest["time"], 100 * trend_line_asl, label="Altimetry Trend", color=palette[0], linestyle="--")
    ax.set_title(f"Altimetry ({lat_str}, {lon_str}) ({start_date_str} to {end_date_str})")
    ax.set_xlabel("Year")
    ax.set_ylabel("Height (cm)")
    ax.set_xlim([start_date, end_date])
    trendmag_str = f"Δ Sea Level: {100*trend_mag_asl.values:.2f} cm, Trend: {100*trend_rate_asl.values:.2f} cm/year"
    ax.text(
        0.95,
        0.05,
        trendmag_str,
        transform=ax.transAxes,
        verticalalignment="bottom",
        horizontalalignment="right",
        bbox=dict(facecolor="white", alpha=0.5),
    )
    return fig, ax


def plot_tide_gauge_scatter(rsl_daily, station_name, start_date_str, end_date_str, start_date, end_date):
    sns.set_style("whitegrid")
    palette = sns.color_palette("Paired")
    fig, ax = plt.subplots()
    ax.scatter(rsl_daily["time"], 100 * rsl_daily, label="RSL", color=palette[1], alpha=1, s=5)
    ax.set(
        title=f"Tide Gauge ({station_name}) ({start_date_str} to {end_date_str})",
        xlabel="Year",
        ylabel="Water Level (cm)",
        xlim=[start_date, end_date],
    )
    return fig, ax


def plot_tide_gauge_trend_timeseries(
    rsl_daily,
    rsl_monthly,
    trend_line_rsl,
    trend_mag_rsl,
    trend_rate_rsl,
    station_name,
    start_date_str,
    end_date_str,
    start_date,
    end_date,
):
    sns.set_style("whitegrid")
    palette = sns.color_palette("Set1")
    fig, ax = plt.subplots()
    ax.scatter(rsl_daily["time"], 100 * rsl_daily, label="Tide Gauge", color=palette[1], alpha=0.2, s=5)
    ax.plot(rsl_daily["time"], 100 * trend_line_rsl, label="Tide Gauge Trend", color=palette[1], linestyle="--")
    ax.plot(rsl_monthly["time"], 100 * rsl_monthly, label="Tide Gauge", color=palette[3])
    ax.set_title(f"Tide Gauge ({station_name}) ({start_date_str} to {end_date_str})")
    ax.set_xlabel("Year")
    ax.set_ylabel("Height (cm, MSL)")
    ax.set_ylim([-50, 50])
    ax.set_xlim([start_date, end_date])
    trendmag_str = f"Δ Sea Level: {100*trend_mag_rsl:.2f} cm, Trend: {100*trend_rate_rsl:.2f} cm/year"
    ax.text(
        0.95,
        0.05,
        trendmag_str,
        transform=ax.transAxes,
        fontsize=14,
        verticalalignment="bottom",
        horizontalalignment="right",
        bbox=dict(facecolor="white", alpha=0.5),
    )
    return fig, ax


def plot_magnitude_map(trend_mag_cmems, site_eez, rsl, trend_mag_rsl, vmin, vmax, xlims, ylims):
    fig, ax, crs, cmap = plot_map_base(xlims, ylims)
    trend_mag_cmems_cm = trend_mag_cmems * 100
    trend_mag_cmems_cm.plot(
        ax=ax,
        transform=crs,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        add_colorbar=True,
        cbar_kwargs={"label": "Δ Sea Level (cm, 1993-2022)"},
    )
    ax.plot(site_eez[:, 0], site_eez[:, 1], transform=crs, color="black", linewidth=2)
    ax.scatter(
        rsl["lon"],
        rsl["lat"],
        transform=crs,
        s=200,
        c=100 * trend_mag_rsl,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        linewidth=0.5,
        edgecolor="black",
    )
    plot_zebra_frame(ax, lw=5, segment_length=2, crs=crs)
    return fig, ax


def plot_magnitude_map_background(trend_mag_cmems, site_eez, vmin=10, vmax=24, xlims=None, ylims=None):
    """Map CMEMS sea-level magnitude background with EEZ outline."""
    if xlims is None:
        xlims = [128, 138]
    if ylims is None:
        ylims = [0, 13]
    fig, ax, crs, cmap = plot_map_base(xlims=xlims, ylims=ylims)
    trend_mag_cmems_cm = trend_mag_cmems * 100
    trend_mag_cmems_cm.plot(
        ax=ax,
        transform=crs,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        add_colorbar=True,
        cbar_kwargs={"label": "Δ Sea Level (cm, 1993-2022)"},
    )
    ax.plot(site_eez[:, 0], site_eez[:, 1], transform=crs, color="black", linewidth=2)
    plot_zebra_frame(ax, lw=5, segment_length=2, crs=crs)
    return fig, ax


def plot_combined_trends(
    sla_nearest,
    trend_line_asl,
    trend_rate_asl,
    rsl_daily,
    trend_line_rsl,
    trend_rate_rsl,
    lat_str,
    lon_str,
    station_name,
    start_date_str,
    end_date_str,
    start_date,
    end_date,
):
    sns.set_style("whitegrid")
    palette = sns.color_palette("Set1")
    fig, ax = plt.subplots()

    label_sat = f"Altimetry Trend ({1000*trend_rate_asl.values:.2f} mm/year)"
    ax.scatter(sla_nearest["time"], 100 * sla_nearest, label="Altimetry", color=palette[0], alpha=0.2, s=5)
    ax.plot(sla_nearest["time"], 100 * trend_line_asl, label=label_sat, color=palette[0], linestyle="-")

    label_tg = f"Tide Gauge Trend ({1000*trend_rate_rsl:.2f} mm/year)"
    ax.scatter(rsl_daily["time"], 100 * rsl_daily, label="Tide Gauge", color=palette[1], alpha=0.2, s=10)
    ax.plot(rsl_daily["time"], 100 * trend_line_rsl, label=label_tg, color=palette[1], linestyle="-")

    title = f"Altimetry ({lat_str}, {lon_str}) vs \nTide Gauge ({station_name}) ({start_date_str} to {end_date_str})"
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel("Height (cm, MSL)")
    ax.set_ylim([-40, 40])
    ax.set_xlim([start_date, end_date])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
    return fig, ax


def plot_enso_scatter(oni_daily, deseasoned_rsl):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(oni_daily, deseasoned_rsl, color="gray", alpha=0.2, s=7)
    ax.set_xlabel("ONI (°C)")
    ax.set_ylabel("De-seasoned Sea Level (m)")

    nina_1998 = deseasoned_rsl.sel(time=slice("1998-08-01", "2001-01-30"))
    nino_1997 = deseasoned_rsl.sel(time=slice("1997-06-01", "1998-04-30"))
    ax.scatter(oni_daily.loc["1998-08-01":"2001-01-30"], nina_1998, color="blue", label="1998-2001 La Niña", alpha=0.5)
    ax.scatter(oni_daily.loc["1997-06-01":"1998-04-30"], nino_1997, color="red", label="1997-1998 El Niño", alpha=0.5)

    deseasoned_rsl_series = deseasoned_rsl.to_series()
    valid_mask = ~deseasoned_rsl_series.isna()
    oni_valid = oni_daily.squeeze().loc[valid_mask]
    deseasoned_valid = deseasoned_rsl_series.loc[valid_mask]

    slope, intercept, r_value, p_value, std_err = stats.linregress(oni_valid, deseasoned_valid)
    x = np.linspace(-2, 3, 100)
    y = slope * x + intercept
    ax.plot(x, y, color="black", linestyle="-", label=f"{slope:.2f} m/ °C (r$^2$ = {r_value**2:.2f})")

    ax.set_xlim(-2, 3)
    ax.legend(frameon=False)

    ax.axvspan(-2, -1.5, color="blue", alpha=0.15, linewidth=0, zorder=0)
    ax.axvspan(-1.5, -1, color="blue", alpha=0.10, linewidth=0, zorder=0)
    ax.axvspan(-1, -0.5, color="blue", alpha=0.05, linewidth=0, zorder=0)
    ax.axvspan(-0.5, 0.5, color="gray", alpha=0.05, linewidth=0, zorder=0)
    ax.axvspan(0.5, 1, color="red", alpha=0.05, linewidth=0, zorder=0)
    ax.axvspan(1, 1.5, color="red", alpha=0.10, linewidth=0, zorder=0)
    ax.axvspan(1.5, 2, color="red", alpha=0.15, linewidth=0, zorder=0)
    ax.axvspan(2, 3, color="red", alpha=0.20, linewidth=0, zorder=0)

    for spine in ax.spines.values():
        spine.set_edgecolor("black")
        spine.set_linewidth(1)

    for text in ax.texts:
        text.set_fontname("DejaVu Sans")

    legend = ax.get_legend()
    if legend is not None:
        labels = ax.get_xticklabels() + ax.get_yticklabels() + legend.get_texts()
    else:
        labels = ax.get_xticklabels() + ax.get_yticklabels()
    for label in labels:
        label.set_fontname("DejaVu Sans")

    ax.xaxis.label.set_fontname("DejaVu Sans")
    ax.yaxis.label.set_fontname("DejaVu Sans")

    return fig, ax, slope, intercept, r_value, p_value, std_err, nina_1998, nino_1997


def plot_map(vmin, vmax, xlims, ylims):
    """Compatibility helper for anomaly notebook map base."""
    return plot_map_base(xlims=xlims, ylims=ylims)


def pacific_all_west_formatter(x, pos=None):
    x = (x + 360) % 360
    deg_west = (180 - x) % 360
    if deg_west == 0:
        return "180°W"
    return f"{abs(deg_west):.0f}°W"


def plot_tg_rsl_anomaly_annual(rid, ax, rsl_yearly_mean, rsl_subset, rsl_monthly, oni, oni_plot=False):
    ax.set_xlim(1993, 2024)
    ax.set_ylim(-0.5, 0.5)
    ax.grid(alpha=0.2, color="lightgray")

    if oni_plot:
        ymin, ymax = ax.get_ylim()
        ax.fill_between(oni.index, ymin, ymax, where=oni["El Nino"] == 1, color="red", alpha=0.1, label="El Niño")
        ax.fill_between(oni.index, ymin, ymax, where=oni["La Nina"] == 1, color="blue", alpha=0.1, label="La Niña")

    rsl_yearly_min = rsl_subset.groupby("storm_time.year").min("storm_time").isel(record_id=rid)
    rsl_yearly_max = rsl_subset.groupby("storm_time.year").max("storm_time").isel(record_id=rid)
    rsl_yearly_min = rsl_yearly_min["sea_level_anomaly_detrended"] / 1000
    rsl_yearly_max = rsl_yearly_max["sea_level_anomaly_detrended"] / 1000

    ax.fill_between(rsl_yearly_mean.storm_year + 0.5, rsl_yearly_min, rsl_yearly_max, alpha=0.2, label="Range (Annual SLA Min-Max)")
    ax.plot(
        rsl_yearly_mean.storm_year + 0.5,
        0.001 * rsl_yearly_mean["sea_level_anomaly_detrended"].isel(record_id=rid),
        label="Annual Mean Sea Level Anomaly (m)",
        alpha=1,
        linewidth=2,
    )
    storm_time_float = rsl_monthly["time.year"] + (rsl_monthly["time.month"] - 5) / 12
    ax.plot(
        storm_time_float,
        0.001 * rsl_monthly["sea_level_anomaly_detrended"].isel(record_id=rid),
        label="Monthly Mean Sea Level Anomaly (m)",
        alpha=1,
        color="gray",
        linewidth=0.75,
    )
    ax.set_ylabel("")
    ax.set_xlabel("")
    name_id = str(rsl_subset["station_name"].isel(record_id=rid).values) + " (" + str(rsl_subset["record_id"].isel(record_id=rid).values).zfill(3) + ")"
    ax.text(0.5, 0.9, name_id, horizontalalignment="center", verticalalignment="center", transform=ax.transAxes)


def plot_flood_count_per_year(flood_count_per_year, ax, timescale="days", colors="Blues", bar_width=0.9, alpha=1, grid=True):
    x_values = flood_count_per_year["year_storm"]
    x_values_offset = x_values - 4 / 12
    if timescale == "days":
        y_values = flood_count_per_year["flood_days_count"]
        ylabelstring = "Number of Flood Days"
        titlestring = "Flood Days Per Year"
    else:
        y_values = flood_count_per_year["flood_hours_count"]
        ylabelstring = "Number of Flood Hours"
        titlestring = "Flood Hours Per Year"

    if isinstance(colors, str):
        flooding_colors = sns.color_palette(colors, as_cmap=True)
        norm = Normalize(vmin=min(y_values), vmax=max(y_values))
        colors = flooding_colors(norm(y_values))
    ax.bar(x_values_offset, y_values, width=bar_width, color=colors, align="edge", alpha=alpha)
    ax.set_ylabel(ylabelstring)
    ax.set_title(titlestring)
    if grid:
        ax.grid(color="lightgray", linestyle="-", linewidth=0.5, alpha=0.5)
    return x_values_offset.values, y_values.values, bar_width


def plot_trend(ax, x, y, trend_counts, trend_label, linestyle_trend):
    ax.plot(x, trend_counts, color="black", linestyle=linestyle_trend, label=trend_label, linewidth=0.5)
    ax.legend(loc="upper left", fontsize="small")


def plot_oni_segments(enso_events, ax):
    enso_events = enso_events.copy()
    enso_events["year_float"] = enso_events.index.year + (enso_events.index.month - 1) / 12
    ax.set_ylabel("ONI")
    ax.grid(color="lightgray", linestyle="-", linewidth=0.5, alpha=0.5)
    ax.set_ylim(-3, 3)

    for i in range(len(enso_events) - 1):
        x_segment = enso_events["year_float"].iloc[i : i + 2]
        y_segment = enso_events["ONI"].iloc[i : i + 2]
        mode_start = enso_events["ONI Mode"].iloc[i]
        mode_end = enso_events["ONI Mode"].iloc[i + 1]

        if mode_start == mode_end:
            if mode_start == "La Nina":
                color = "blue"
            elif mode_start == "El Nino":
                color = "red"
            else:
                color = "gray"
        else:
            if {mode_start, mode_end} == {"La Nina", "Neutral"}:
                color = "lightblue"
            elif {mode_start, mode_end} == {"El Nino", "Neutral"}:
                color = "lightcoral"
            else:
                color = "gray"

        ax.plot(x_segment, y_segment, color=color, linewidth=2)

    ax.yaxis.tick_right()
    ax.tick_params(axis="both", which="major", labelsize=8)


def plot_monthly_contribution(df, ax, month_names, direction="vertical"):
    vals = df.iloc[-1, :-1][::-1]
    if direction == "horizontal":
        ax.barh(range(1, 13), vals, color="gray", alpha=0.6)
        ax.set_yticks(range(1, 13))
        ax.set_yticklabels(month_names[::-1])
        ax.set_ylabel("Month (Storm Year: May 1st - April 30th)")
        ax.set_xlabel("Percentage of Total Flood Days")
        ax.set_xlim(0, vals.max() + 2)
        for i, value in enumerate(vals):
            ax.text(value + 0.5, i + 1, f"{value:.0f}%", ha="left", va="center", fontsize=8)
    else:
        ax.bar(range(1, 13), vals, color="gray", alpha=0.6)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(month_names, rotation=45)
        ax.set_xlabel("Month (Storm Year: May 1st - April 30th)")
        ax.set_ylabel("Percentage of Total Flood Days")
        ax.set_ylim(0, vals.max() + 2)
        for i, value in enumerate(vals):
            ax.text(i + 1, value + 0.5, f"{value:.0f}%", ha="center", va="bottom", fontsize=8)
    ax.set_title("Monthly Contribution to Total Flood Days")


def style_oni_based(row, norm, cmap):
    styles = {}
    if row["Highest ONI Mode"] in ["El Nino", "La Nina"]:
        styles["Highest"] = f'background-color: {mcolors.rgb2hex(cmap(norm(row["ONI max"])))}'
    else:
        styles["Highest"] = "color: black"
    if row["Lowest ONI Mode"] in ["El Nino", "La Nina"]:
        styles["Lowest"] = f'background-color: {mcolors.rgb2hex(cmap(norm(row["ONI min"])))}'
    else:
        styles["Lowest"] = "color: black"
    return pd.Series(styles)


def make_plotly_figure_rankings(rsl_monthly_mean, rsl_monthly_max, rsl_monthly_min, top_10_table, rsl_subset, record_id, station_name):
    figly = go.Figure()
    max_sl = rsl_monthly_max["sea_level"].sel(record_id=record_id)
    min_sl = rsl_monthly_min["sea_level"].sel(record_id=record_id)
    mean_sl = rsl_monthly_mean["sea_level"].sel(record_id=record_id)
    x = mean_sl.time - np.timedelta64(15, "D")

    max_sl_clean = max_sl.dropna(dim="time")
    min_sl_clean = min_sl.dropna(dim="time")
    mean_sl_clean = mean_sl.dropna(dim="time")

    figly.add_trace(go.Scatter(x=x, y=max_sl_clean, mode="lines", line_color="rgba(0,176,246,0.2)", name="Monthly Max"))
    figly.add_trace(
        go.Scatter(
            x=x,
            y=min_sl_clean,
            mode="lines",
            line_color="rgba(0,176,246,0.2)",
            fill="tonexty",
            fillcolor="rgba(0,176,246,0.2)",
            name="Range (Monthly Max/Min)",
        )
    )
    figly.add_trace(go.Scatter(x=x, y=mean_sl_clean, mode="lines", line_color="rgba(0,176,246,1)", name="Monthly Mean"))
    figly.add_trace(
        go.Scatter(
            x=top_10_table[top_10_table["ONI Mode"] == "El Nino"].date,
            y=top_10_table[top_10_table["ONI Mode"] == "El Nino"]["sea level (m)"],
            mode="markers",
            marker=dict(color="red", size=12, symbol="star"),
            name="El Niño",
            hoverinfo="none",
        )
    )
    figly.add_trace(
        go.Scatter(
            x=top_10_table[top_10_table["ONI Mode"] == "La Nina"].date,
            y=top_10_table[top_10_table["ONI Mode"] == "La Nina"]["sea level (m)"],
            mode="markers",
            marker=dict(color="blue", size=12, symbol="circle"),
            name="La Niña",
            hoverinfo="none",
        )
    )
    figly.add_trace(
        go.Scatter(
            x=top_10_table.date,
            y=top_10_table["sea level (m)"],
            mode="markers",
            marker=dict(color="orange", size=6, symbol="circle"),
            name="Highest/Lowest Events",
            hovertemplate="%{x}, %{y:.2f} m<extra></extra>",
        )
    )
    figly.update_layout(
        title=str(station_name),
        xaxis_title="Time",
        yaxis_title=f"{rsl_subset['sea_level'].attrs['long_name']} [{rsl_subset['sea_level'].attrs['units']}]",
        showlegend=True,
        autosize=True,
        plot_bgcolor="white",
    )
    return figly


def plot_anomaly_decadal_maps(sla_detrended, rsl, rsl_anomalies, yr_start, yr_stop, yr_start_str, yr_stop_str):
    """Plot 2x2 decadal sea-level anomaly maps."""
    crs_main = ccrs.PlateCarree(central_longitude=180)
    crs_sub = ccrs.PlateCarree()
    fig, axs = plt.subplots(2, 2, figsize=(6, 5), subplot_kw={"projection": crs_main})
    cbar_ax = fig.add_axes([0.92, 0.15, 0.03, 0.7])
    fig.subplots_adjust(right=0.9)
    vmin, vmax = -0.075, 0.075
    c = None

    for i, ax in enumerate(axs.flat):
        sla_mean = sla_detrended.sel(time=slice(yr_start_str[i], yr_stop_str[i])).mean(dim="time", skipna=True)
        c = sla_mean.plot(ax=ax, add_colorbar=False, transform=crs_sub, cmap="RdBu_r")
        c.set_clim(vmin, vmax)
        ax.set_title(f"{yr_start[i]}-{yr_stop[i]}")
        cmap = sns.color_palette("RdBu_r", as_cmap=True)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.LAND, color="lightgrey")

        ax.scatter(rsl["lon"], rsl["lat"], transform=crs_sub, s=50, c="white", linewidth=0.5, edgecolor="black", zorder=10)
        ax.scatter(
            rsl["lon"],
            rsl["lat"],
            transform=crs_sub,
            s=100,
            c=rsl_anomalies.sel(time=slice(yr_start_str[i], yr_stop_str[i])).sea_level_anomaly_detrended.mean(dim="time") / 1000,
            vmin=vmin,
            vmax=vmax,
            cmap=cmap,
            linewidth=0.5,
            edgecolor="black",
            zorder=10,
        )
        gl = ax.gridlines(
            crs=crs_main, draw_labels=False, linestyle=":", color="black", alpha=0.5, xlocs=ax.get_xticks(), ylocs=ax.get_yticks()
        )
        gl.xformatter = FuncFormatter(pacific_all_west_formatter)
        if i > 1:
            gl.bottom_labels = True
        if i in (0, 2):
            gl.left_labels = True
        gl.xlabel_style = {"size": 8}
        gl.ylabel_style = {"size": 8}

    if c is not None:
        cbar = fig.colorbar(c, cax=cbar_ax)
        cbar.set_label("Sea Level Anomaly (m)")
    return fig, axs


def plot_anomaly_station_series(rsl_yearly_mean, rsl_years, rsl_monthly, enso_events, sid=0):
    """Plot station anomaly annual range + monthly series with ENSO shading."""
    fig, ax = plt.subplots(figsize=(10, 5))
    plot_tg_rsl_anomaly_annual(sid, ax, rsl_yearly_mean, rsl_years, rsl_monthly, enso_events, oni_plot=True)
    ax.legend(loc="upper right", ncol=1, bbox_to_anchor=(1.45, 1.0))
    fig.text(0.05, 0.5, "Sea Level Anomaly (m)", va="center", rotation="vertical")
    fig.text(0.5, 0, "Storm Year", ha="center")
    station = str(rsl_yearly_mean["station_name"].isel(record_id=sid).values)
    return fig, ax, station


def plot_histogram_with_threshold(hourly_data, threshold):
    """Plot histogram of sea level with user threshold and p98."""
    sea_level_data_cm = hourly_data["sea_level_mhhw"].values / 10
    sea_level_data_cm = sea_level_data_cm[~np.isnan(sea_level_data_cm)]
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.hist(sea_level_data_cm, bins=100, density=True, label="Sea Level Data")
    threshold98 = np.percentile(sea_level_data_cm, 98)
    ax.axvline(threshold, color="r", linestyle="--", label=f"Threshold: {threshold:.4f} cm")
    ax.axvline(threshold98, color="c", linestyle="--", label=f"Threshold: {threshold98:.4f} cm")
    ax.set_xlabel("Sea Level (cm)")
    ax.set_ylabel("Probability Density")
    ax.set_title("Sea Level Histogram\nwith 98th Percentile Threshold")
    ymin, ymax = ax.get_ylim()
    y_middle = ymin + 0.75 * (ymax - ymin)
    ax.text(threshold + 4, y_middle, f"{threshold:.1f} cm", rotation=90, va="center", ha="left", color="r")
    ax.text(threshold98, y_middle, f"{threshold98:.1f} cm", rotation=90, va="center", ha="right", color="c")
    return fig, ax, threshold98


def plot_flood_counts_with_trend(flood_count_per_year, timescale="days", colors="Blues"):
    """Plot annual flood counts and linear trend."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    x, y, bar_width = plot_flood_count_per_year(flood_count_per_year, ax, timescale=timescale, colors=colors)
    trend_counts, trend_label, linestyle_trend, slope, p_value = get_trend_info(x + 0.5, y, timescale=timescale)
    plot_trend(ax, x + 0.5, y, trend_counts, trend_label, linestyle_trend)
    ax.set_xlim(x.min() - bar_width, x.max() + bar_width)
    return fig, ax, slope, p_value, trend_counts


def plot_flood_counts_with_oni(flood_days_per_year, enso_events):
    """Plot flood days per year with ONI panel."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 4), sharex=True, gridspec_kw={"height_ratios": [5, 1], "hspace": 0.04})
    x, y, bar_width = plot_flood_count_per_year(flood_days_per_year, ax1)
    trend_counts, trend_label, linestyle_trend, slope_days, p_value_days = get_trend_info(x + 0.5, y, timescale="days")
    plot_trend(ax1, x + 0.5, y, trend_counts, trend_label, linestyle_trend)
    plot_oni_segments(enso_events, ax2)
    ax1.set_xlim(x.min() - bar_width, x.max() + 1)
    return fig, (ax1, ax2), slope_days, p_value_days


def plot_flood_days_heatmap(df, flood_days_per_year):
    """Plot monthly flood-day heatmap with ENSO-colored years."""
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(df.iloc[:-1, :-1].T, cmap="Purples", annot=True, fmt=".0f", linewidths=0.2, ax=ax, cbar=False, annot_kws={"size": 7})
    ax.set_ylabel("Monthly Flood Days \n(Total Per Month)")
    ax.set_xlabel("Storm Year (May 1st - April 30th)")
    ax.tick_params(axis="y", labelsize=9)
    ax.tick_params(axis="x", labelsize=9)
    year_to_mode = flood_days_per_year.set_index("year_storm")["ONI Mode"]
    color_map = {"El Nino": "red", "La Nina": "blue", "Neutral": "black"}
    for label in ax.get_xticklabels():
        year = int(label.get_text())
        mode = year_to_mode.get(year, "Neutral")
        label.set_color(color_map.get(mode, "black"))
    return fig, ax


def plot_flood_matrix_summary(df, flood_days_per_year):
    """Plot composite flood matrix figure (annual, heatmap, monthly contribution, legend)."""
    fig, axs = plt.subplots(
        2, 2, figsize=(12, 6), gridspec_kw={"height_ratios": [1, 2], "hspace": 0.05, "width_ratios": [5, 1], "wspace": 0.05}
    )
    year_to_mode = flood_days_per_year.set_index("year_storm")["ONI Mode"]
    color_map = {"El Nino": "red", "La Nina": "blue", "Neutral": "black"}

    sns.heatmap(df.iloc[:-1, :-1].T, cmap="Grays", annot=True, fmt=".0f", linewidths=0.2, ax=axs[1, 0], cbar=False, annot_kws={"size": 7})
    axs[1, 0].set_ylabel("Monthly Flood Days \n(Total Per Month)")
    axs[1, 0].set_xlabel("Storm Year (May 1st - April 30th)")
    axs[1, 0].tick_params(axis="y", labelsize=9)
    axs[1, 0].tick_params(axis="x", labelsize=9)
    for label in axs[1, 0].get_xticklabels():
        year = int(label.get_text())
        mode = year_to_mode.get(year, "Neutral")
        label.set_color(color_map.get(mode, "black"))

    ax2 = axs[0, 0]
    enso_colors = ["red" if val == "El Nino" else "blue" if val == "La Nina" else "gray" for val in flood_days_per_year["ONI Mode"]]
    x, y, bar_width = plot_flood_count_per_year(
        flood_days_per_year, ax2, timescale="days", colors=enso_colors, grid=False, alpha=0.6, bar_width=0.8
    )
    ax2.set_xlim(df.index[0] - 0.5, df.index[-2] + 0.5)
    for xi, yi in zip(x, y):
        ax2.text(xi + bar_width / 2, yi + 0.5, str(int(yi)), ha="center", va="bottom", fontsize=7, color="black")
    for spine in ["top", "right"]:
        ax2.spines[spine].set_visible(False)
    ax2.set_ylabel("Annual Flood Days \n(Total Per Year)")
    ax2.set_title("")
    ax2.grid(visible=False)
    trend_counts, trend_label, linestyle_trend, slope_days, p_value_days = get_trend_info(x + 0.5, y, timescale="days")
    plot_trend(ax2, x + 0.5, y, trend_counts, trend_label, linestyle_trend)
    ax2.legend(loc="upper left", fontsize="small", frameon=False, prop={"family": "DejaVu Sans"})

    ax3 = axs[1, 1]
    month_names = ["May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
    plot_monthly_contribution(df, ax3, month_names=month_names, direction="horizontal")
    ax3.set_yticklabels([])
    ax3.set_ylabel("")
    ax3.set_title("")
    ax3.set_xticks([])
    ax3.set_xlabel("Monthly Contribution \n (% Total Flood Days)")
    for spine in ax3.spines.values():
        spine.set_visible(False)
    ax3.spines["left"].set_visible(True)

    ax4 = axs[0, 1]
    ax4.axis("off")
    legend_elements = [
        plt.Line2D([0], [0], marker="o", color="w", label="El Niño", markerfacecolor="red", markersize=10, alpha=0.6),
        plt.Line2D([0], [0], marker="o", color="w", label="La Niña", markerfacecolor="blue", markersize=10, alpha=0.6),
        plt.Line2D([0], [0], marker="o", color="w", label="Neutral", markerfacecolor="gray", markersize=10),
    ]
    legend = ax4.legend(handles=legend_elements, loc="center left", title="ENSO Events (Niño 3.4)", frameon=False)
    legend.get_title().set_fontsize("10")
    legend.get_title().set_fontname("DejaVu Sans")
    for text in legend.get_texts():
        text.set_fontname("DejaVu Sans")
        text.set_fontsize("10")

    for ax in axs.flat:
        for item in [ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels():
            item.set_fontname("DejaVu Sans")
    return fig, axs, slope_days, p_value_days


def make_rankings_static_figure(rsl_monthly_mean, rsl_monthly_max, rsl_monthly_min, top_10_table, rsl, uhslc_id, station_name):
    """Build static rankings figure used in notebook d."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 3))
    x = rsl_monthly_mean.time - np.timedelta64(15, "D")
    ax.set_title(station_name)
    ax.set_ylabel(f"{rsl['sea_level'].attrs['long_name']} [{rsl['sea_level'].attrs['units']}]")
    ax.plot(x, rsl_monthly_max["sea_level"].sel(record_id=uhslc_id), color=(0 / 255, 176 / 255, 246 / 255, 0.2))
    ax.plot(x, rsl_monthly_min["sea_level"].sel(record_id=uhslc_id), color=(0 / 255, 176 / 255, 246 / 255, 0.2))
    ax.fill_between(
        x,
        rsl_monthly_max["sea_level"].sel(record_id=uhslc_id),
        rsl_monthly_min["sea_level"].sel(record_id=uhslc_id),
        color=(0 / 255, 176 / 255, 246 / 255, 0.2),
        label="Range (Monthly Max/Min)",
    )
    ax.plot(x, rsl_monthly_mean["sea_level"].sel(record_id=uhslc_id), color=(0 / 255, 176 / 255, 246 / 255, 1), label="Monthly Mean")
    ax.scatter(
        top_10_table[top_10_table["ONI Mode"] == "La Nina"].date,
        top_10_table[top_10_table["ONI Mode"] == "La Nina"]["sea level (m)"],
        color="blue",
        s=120,
        label="La Niña",
        marker="o",
    )
    ax.scatter(
        top_10_table[top_10_table["ONI Mode"] == "El Nino"].date,
        top_10_table[top_10_table["ONI Mode"] == "El Nino"]["sea level (m)"],
        color="red",
        s=120,
        label="El Niño",
        marker="*",
    )
    ax.scatter(top_10_table.date, top_10_table["sea level (m)"], color="orange", s=20, label="Highest/Lowest Events", marker="o")
    ax.set_xlim(pd.Timestamp("1993-01-01"), pd.Timestamp("2024-12-31"))
    ax.grid(True, color="gray", alpha=0.5, linewidth=0.5)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False, fontsize=10)
    return fig, ax


def plot_simple_timeseries(time_values, sea_level_cm, ylabel):
    """Simple 1-panel time series line plot."""
    fig, ax = plt.subplots(sharex=True)
    fig.autofmt_xdate()
    ax.plot(time_values, sea_level_cm)
    ax.set_ylabel(ylabel)
    return fig, ax


def plot_daily_max_timeseries(SL_daily_max):
    """Daily maximum sea-level time series plot."""
    fig, ax = plt.subplots(sharex=True)
    ax.plot(SL_daily_max.time.values, SL_daily_max.sea_level_mhhw.values / 10)
    ax.set_xlabel("Date (Calendar Year)")
    ax.set_ylabel("Sea Level (cm)")
    ax.set_title("Sea Level Daily Maximum Time Series")
    return fig, ax


def plot_annual_range_fill(rsl_yearly_mean, rsl_yearly_min, rsl_yearly_max):
    """Annual anomaly min-max envelope."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(rsl_yearly_mean.storm_year + 0.5, rsl_yearly_min, rsl_yearly_max, alpha=0.2, label="Range (Annual SLA Min-Max)")
    return fig, ax


def plot_oni_only(enso_events):
    """Single-panel ONI segments plot."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    plot_oni_segments(enso_events, ax)
    return fig, ax


def plot_monthly_contribution_vertical(df, month_names):
    """Vertical monthly contribution bars."""
    fig, ax = plt.subplots(figsize=(6, 4))
    plot_monthly_contribution(df, ax, month_names, direction="vertical")
    return fig, ax
