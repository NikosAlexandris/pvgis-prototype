import numpy
from pandas import DatetimeIndex
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import calendar
from pvgisprototype.api.statistics.xarray import calculate_series_statistics
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT


def add_statistic_row(table, key, value, rounding_places=None):
    if rounding_places is not None and isinstance(value, float):
        value = round(value, rounding_places)
    table.add_row(key, str(value))


def format_group_statistics(statistics, groupby_label):
    group_rows = []
    if groupby_label == "Yearly means":
        for year, value in enumerate(statistics.get(groupby_label, [])):
            group_rows.append((str(year), value))
    elif groupby_label == "Monthly means":
        for idx, value in enumerate(statistics.get(groupby_label, []), start=1):
            month_name = calendar.month_name[idx]
            group_rows.append((month_name, value))
    elif groupby_label == "Seasonal means":
        seasons = ["DJF", "MAM", "JJA", "SON"]
        for season, value in zip(seasons, statistics.get(groupby_label, [])):
            group_rows.append((season, value))
    elif groupby_label == "Weekly means":
        for week_number, value in enumerate(statistics.get(groupby_label, []), start=1):
            group_rows.append((f"Week {week_number}", value))
    elif groupby_label == "Daily means":  # REVIEW-ME : We want Day-of-Year, not of-Month!
        for day_of_year, value in enumerate(statistics.get(groupby_label, []), start=1):
            group_rows.append((f"Day {day_of_year}", value))
    group_rows.append(["", ""])  # --%<--- Separate ------------------

    return group_rows


def print_series_statistics(
    data_array: numpy.ndarray,
    timestamps: DatetimeIndex,
    title: str = "Time series",
    groupby: str | None = None,
    monthly_overview: bool = False,
    rounding_places: int | None = None,
    verbose = VERBOSE_LEVEL_DEFAULT,
) -> None:
    """
    """
    rename_monthly_output_rows = {
        "Sum of Group Means": "Yearly PV energy",
        "Sum of Global Inclined Irradiance": "Yearly in-plane irradiance",
    }
    if groupby and groupby.lower() == "monthly":
        monthly_overview = True

    table = Table(
        title=title,
        caption="Caption text",
        show_header=True,
        header_style="bold magenta",
        row_styles=["none", "dim"],
        box=SIMPLE_HEAD,
        highlight=True,
    )

    # Compute statistics
    if monthly_overview:  # typical overview !
        table.add_column(
            "Statistic", justify="right", style="bright_blue", no_wrap=True
        )
        table.add_column("Value", style="cyan")
        # get monthly mean values
        statistics = calculate_series_statistics(data_array, timestamps, "M")
    else:
        table.add_column("Statistic", justify="right", style="magenta", no_wrap=True)
        table.add_column("Value", style="cyan")
        statistics = calculate_series_statistics(data_array, timestamps, groupby)
 
    # Basic Metadata
    basic_metadata = ["Start", "End", "Count"] if not monthly_overview else ["Start", "End"]
    for key in basic_metadata:
        if key in statistics:
            add_statistic_row(table, key, statistics[key])

    table.add_row("", "")  # --%<--- Separate ----

    # grouping_labels = {
    #     'Y': 'Yearly means',
    #     'S': 'Seasonal means',
    #     'M': 'Monthly means',
    #     'W': 'Weekly means',
    #     'D': 'Daily means',
    #     'H': 'Hourly means',
    # }

    # Groups by
    time_groupings = [
        "Yearly means",
        "Seasonal means",
        "Monthly means",
        "Weekly means",
        "Daily means",
        "Hourly means",
        f"{groupby} means" if groupby else None,  # do not print custom frequency means
    ]

    if monthly_overview:
        monthly_metadata = [
            # 'Min',
            # 'Mean',
            # 'Max',
            # 'Standard deviation',
            "Sum of Group Means",
            "Irradiance",
            f"Sum of Global Inclined Irradiance",
        ]

    # Add statistics
    for key, value in statistics.items():
        if not monthly_overview:
            if (
                key not in basic_metadata
                and key not in time_groupings
            ):
                add_statistic_row(table, key, value, rounding_places)
        else:
            if (
                key in monthly_metadata
                and key not in basic_metadata
            ):
                display_key = rename_monthly_output_rows.get(key, key)
                add_statistic_row(table, display_key, value, rounding_places)

    table.add_row("", "")  # --%<--- Separate --------------------------------

    # Process Groups with Helper
    custom_frequency_label = (
        f"{groupby} means" if groupby and groupby not in time_groupings else None
    )
    for group in time_groupings:
        if group in statistics:
            group_rows = format_group_statistics(statistics, group)
            for name, value in group_rows:
                add_statistic_row(table, name, value)

    # Custom frequency group
    if custom_frequency_label and custom_frequency_label in statistics:
        custom_freq_data = statistics[custom_frequency_label]
        # ----------------------------------------------------- the Old way --
        # period_count = 1
        # for value in custom_freq_data:
        #     label = f"{groupby} Period {period_count}"
        #     table.add_row(label, str(value))
        #     period_count += 1
        # table.add_row("", "")
        # ----------------------------------------------------- the Old way --
        for period_count, value in enumerate(custom_freq_data, start=1):
            add_statistic_row(
                table=table,
                key=f"{groupby} Period {period_count}",
                value=value,
                rounding_places=rounding_places,
            )

    # Index of items
    index_metadata = (
        [
            "Time of Min",
            "Index of Min",
            "Time of Max",
            "Index of Max",
        ]
        if not monthly_overview
        else []
    )
    # # The old way ! --------------------------------------------------------
    # for key, value in statistics.items():
    #     if key in index_metadata:
    #         # table.add_row(key, str(round_float_values(value, rounding_places)))
    #         table.add_row(key, str(value))
    # # The old way ! --------------------------------------------------------
    for key in index_metadata:
        if key in statistics:
            add_statistic_row(
                table=table,
                key=key,
                value=statistics[key],
            )

    # Create and display Panel with Table
    panel = Panel(table, title="Statistics", expand=False)
    console = Console()
    console.print(panel)
