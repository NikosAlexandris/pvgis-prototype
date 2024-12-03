from pandas import Timestamp
# import seaborn as sns
import matplotlib.pyplot as plt
from xarray import Dataset, DataArray
import numpy as np
import pandas as pd

def plot_data_distribution(distribution, variable):
    plt.figure(figsize=(10, 6))
    plt.hist(distribution, bins=100, alpha=0.75)
    plt.title(f'Distribution of {variable}')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.show()


def plot_yearly_monthly_ecdfs(
    yearly_monthly_cdfs,
    plot_path="yearly_monthly_ecdfs.png",
):
    """Plot and save ECDFs for each month in a 3x4 grid."""
    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(20, 15))  # 3x4 grid of subplots
    axes = axes.flatten()  # flatten array to simplify indexing ?

    for idx, month in enumerate(yearly_monthly_cdfs.month.values):
        ax = axes[idx]
        yearly_monthly_cdfs.sel(month=month).plot(ax=ax)  # Plot on specific subplot
        ax.set_title(f"Month {month}")
        ax.set_xlabel("Value")
        ax.set_ylabel("ECDF")

    plt.tight_layout()  # prevent overlap ?
    plt.savefig(plot_path)
    plt.close(fig)


# def plot_yearly_monthly_ecdfs_with_seaborn(
#     yearly_monthly_cdfs, plot_path="yearly_monthly_ecdfs.png"
# ):
#     """Plot and save ECDFs for each month using Seaborn's FacetGrid."""
#     # Convert Xarray DataArray to a Pandas DataFrame
#     df = yearly_monthly_cdfs.to_dataframe(name="ECDF").reset_index()
#     g = sns.FacetGrid(
#         df, col="month", col_wrap=4, sharex=True, sharey=True, height=3, aspect=1.5
#     )
#     g.map_dataframe(sns.lineplot, x="data", y="ECDF")
#     g.set_titles("Month {col_name}")
#     g.set_axis_labels("Value", "ECDF")
#     g.add_legend()
#     g.fig.tight_layout(w_pad=1)
#     plt.savefig(plot_path)
#     plt.close(g.fig)


def plot_long_term_monthly_ecdfs(
    long_term_ecdf,
    plot_path="long_term_monthly_ecdfs.png",
):
    """Plot and save ECDFs for each month."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    # ax.plot(long_term_ecdf, label=f'Long-term Monthly')
    long_term_ecdf.plot(label='Long-term Empirical CDF')
    ax.set_title('Long-term Monthly Empirical Cumulative Distribution Function')
    ax.set_xlabel('Value')
    ax.set_ylabel('Month')
    ax.legend(loc='best')
    plt.savefig(plot_path)
    plt.close(fig)


def plot_finkelstein_schafer_statistic(
    finkelstein_schafer_statistic,
    plot_path="finkelstein_schafer_statistic.png",
):
    """Plot and save ECDFs for each month."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    # ax.plot(long_term_ecdf, label=f'Long-term Monthly')
    finkelstein_schafer_statistic.plot(label='FS scores')
    ax.set_title('Finkelstein-Schafer Statistic)')
    ax.set_xlabel('Month')
    ax.set_ylabel('Year')
    ax.legend(loc='best')
    plt.savefig(plot_path)
    plt.close(fig)


def plot_ranked_finkelstein_schafer_statistic(
    ranked_finkelstein_schafer_statistic,
    weighting_scheme: str,
    plot_path="ranked_finkelstein_schafer_statistic.png",
    to_file=True,
):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create heatmap
    c = ax.imshow(ranked_finkelstein_schafer_statistic, aspect='auto', origin='lower')

    # Add month labels as annotations on each tile
    for idx, value in np.ndenumerate(ranked_finkelstein_schafer_statistic):
        year_index, month_index = idx
        year = ranked_finkelstein_schafer_statistic.year.values[year_index]
        month = ranked_finkelstein_schafer_statistic.month.values[month_index]
        month_str = pd.to_datetime(f"{month}", format='%m').strftime('%b')  # Convert month index to month abbreviation
        ax.text(month_index, year_index, month_str, ha='center', va='center', color='white')

    # Set ticks and labels
    ax.set_xticks(range(len(ranked_finkelstein_schafer_statistic.month.values)))
    ax.set_yticks(range(len(ranked_finkelstein_schafer_statistic.year.values)))
    ax.set_xticklabels(
        [pd.to_datetime(f"{month}", format='%m').strftime('%b') for month in ranked_finkelstein_schafer_statistic.month.values]
    )
    ax.set_yticklabels(ranked_finkelstein_schafer_statistic.year.values)
    ax.set_xlabel('Month')
    ax.set_ylabel('Year')

    # Add a title and colorbar
    ax.set_title(f'Monthly Ranking of FS Scores Across Years ({weighting_scheme})')
    fig.colorbar(c, ax=ax, orientation='vertical')

    if to_file:
        plt.savefig(plot_path)
        plt.close(fig)
        return None  # Explicitly return None when saving to a file
    else:
        return fig  # Return the figure object when saving is not required



def plot_tmy(
    tmy_series: Dataset,
    variable: str,
    finkelstein_schafer_statistic: DataArray,
    typical_months: DataArray,
    input_series: DataArray,
    input_series_label: str = "Input time series",
    weighting_scheme: str = "",
    limit_x_axis_to_tmy_extent: bool = False,
    title: str = "",
    y_label: str = "",
    data_source: str = '',
    fingerprint: bool = False,
    width: int = 16,
    height: int = 7,
    plot_path="typical_meteorological_year.png",
    to_file=True,
):
    """
    Plot the TMY data with annotations for each month, alongside the original time series.

    Parameters:
    tmy: Dataset - The TMY dataset containing 'era5_t2m', 'year', and 'month' coordinates.
    location_series_data_array: xr.DataArray - The original time series to compare with.
    title: str - Optional title for the plot.
    """
    fig, ax = plt.subplots(figsize=(width, height))
    # supertitle = getattr(time_series, "long_name", "Untitled")
    if input_series.name:
        input_series_label = getattr(input_series, "name", input_series_label)

    # Plot the original location time series (in gray)
    if limit_x_axis_to_tmy_extent:
        start_time_in_tmy = Timestamp(tmy_series.time.min().values)
        end_time_in_tmy = Timestamp(tmy_series.time.max().values)
        input_series: DataArray = input_series.sel(time=slice(start_time_in_tmy, end_time_in_tmy))
        input_series_label += f" (actual extent : {start_time_in_tmy} - {end_time_in_tmy})"

    input_series.plot( # type: ignore
        color="lightgray",
        linewidth=1,
        ax=ax,
        label=input_series_label,
    )
    month_colors = [
        "#74C2E1",  # January - Icy blue for winter
        "#85A6D9",  # February - Frosty blue hinting at winter's end
        "#9AE4B0",  # March - Fresh green for early spring
        "#A9E4A2",  # April - Light green for blooming spring
        "#F4E956",  # May - Bright yellow for late spring
        "#F2BE4A",  # June - Warm orange for early summer
        "#F58A4E",  # July - Hot red-orange for midsummer heat
        "#F5A65A",  # August - Deep orange for the height of summer
        "#D48443",  # September - Earthy brown-orange for early autumn
        "#B86F32",  # October - Deep brown hinting at autumn leaves
        "#92672C",  # November - Dark brown for late autumn
        "#7894B1",  # December - Cool blue for winter
    ]
    plotted_months = set()
    # Plot the TMY data and annotate with month

    # for year in unique(tmy_series["year"]):  # in case, indent the following !
    for month, color in zip(tmy_series["month"].values, month_colors):
        year_index = int(typical_months.sel(month=month).values)
        # Which year literally ?  ...from finkelstein_schafer_statistic
        year = finkelstein_schafer_statistic.isel(
            year=year_index
        ).year.values
        tmy_month = tmy_series[variable].dropna(dim="time", how="all").sel(
            year=year, month=month
        )

        # Plot only one legend item per month
        if month not in plotted_months:
            # tmy_month.plot(ax=ax, marker="o", label=f"TMY Month {month}, Year {year}")
            tmy_month.plot.line(
                ax=ax,
                marker="o",
                # label=f"Typical month {month}",
                color=color,
            )
            plotted_months.add(month)
        else:
            tmy_month.plot.line(
                ax=ax,
                marker="o",
                color=color,
            )

        # Limit data to period in question
        tmy_month = (
            tmy_series[variable].sel(year=year)
            .sel(month=month)
            .dropna(dim="time", how="all")
        )

        # Annotate the month at the midpoint of the data for each month
        # Retrieve the middle timestamp of the Typical Month data
        midpoint_time = tmy_month.isel(time=tmy_month.time.size // 2).time.values
        average = float(tmy_month.mean().values)
        import calendar
        month_name = calendar.month_name[month]
        ax.annotate(
            f"{month_name}",
            xy=(midpoint_time, average),
            xytext=(midpoint_time, average + 1),
            ha="center",
            fontsize=10,
            color="0.2",
        )

    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("")
    ax.set_ylabel(y_label)
    ax.legend(frameon=False)

    main_title = title if title else "Typical Meteorological Year"
    plt.suptitle(main_title, fontsize=14, color="darkgray", ha="center")
    if weighting_scheme:
        plt.title(f"{weighting_scheme}", fontsize=12, color="gray")

    # Identity
    plt.subplots_adjust(bottom=0.18)
    identity_text = f"© PVGIS" f"  ·  Joint Research Centre, European Commission"
    if data_source:
        identity_text += f"  ·  Data source : {data_source}"
    if fingerprint:
        from pvgisprototype.core.hashing import generate_hash
        data_array_hash = generate_hash(tmy_series[variable])
        identity_text += f"  ·  Fingerprint : {data_array_hash}"
    fig.text(
        0.5,
        0.02,
        identity_text,
        fontsize=12,
        color="gray",
        ha="center",
        alpha=0.5,
    )

    if to_file:
        plt.savefig(plot_path, bbox_inches="tight")
    else:
        return fig
