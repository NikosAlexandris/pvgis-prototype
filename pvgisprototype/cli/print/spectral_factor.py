from typing import Dict
from typing import Dict, List
from pvgisprototype.constants import SPECTRAL_FACTOR_COLUMN_NAME
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import numpy


def print_spectral_factor_statistics(
    spectral_factor: Dict,
    spectral_factor_model: List,
    photovoltaic_module_type: List,
    timestamps: DatetimeIndex,
    groupby: str | None = None,
    title: str = "Spectral Mismatch Statistics",
    rounding_places: int = 3,
    verbose: int = 1,
    show_footer: bool = True,
    monthly_overview: bool = False,
) -> None:
    """
    Print the spectral factor statistics in a formatted table.

    """
    rename_monthly_output_rows = {
        "Sum of Group Means": "Yearly PV energy",
        f"Sum of {GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME}": "Yearly in-plane irradiance",
    }

    # Iterate through spectral factor models
    for model in spectral_factor_model:
        if model.value not in spectral_factor:
            print(f"Spectral factor model {model.value} not found in statistics.")
            continue

        # Create a new table for this model
        table = Table(
            title=f"{title} ({model.value})",
            caption="Spectral Factor Statistics",
            show_header=True,
            header_style="bold magenta",
            row_styles=["none", "dim"],
            box=SIMPLE_HEAD,
            highlight=True,
        )

        # Add a column for each photovoltaic module type
        table.add_column(
            "Statistic", justify="right", style="bright_blue", no_wrap=True
        )
        for module_type in photovoltaic_module_type:
            table.add_column(f"{module_type.value}",
                             # justify="right",
                             style="cyan")

        # Calculate statistics for each module type
        statistics = calculate_spectral_factor_statistics(
            spectral_factor, spectral_factor_model, photovoltaic_module_type, timestamps, rounding_places, groupby
        )

        # Basic metadata (Start, End, Count)
        basic_metadata = ["Start", "End", "Count"]
        for stat_name in basic_metadata:
            row = [stat_name]
            for module_type in photovoltaic_module_type:
                try:
                    value = statistics[model.value][module_type.value].get(stat_name, "N/A")
                    rounded_value = f"{round_float_values(value, rounding_places)}"
                except KeyError:
                    rounded_value = "N/A"
                row.append(rounded_value)
            table.add_row(*row)

        # Separate!
        table.add_row("", "")

        # Extended statistics (Min, Mean, Max, Sum, etc.)
        extended_statistics = ["Min", "Mean", "Max", "Sum", "25th Percentile", "Median", "Mode", "Variance", "Standard deviation"]
        for stat_name in extended_statistics:
            row = [stat_name]
            for module_type in photovoltaic_module_type:
                try:
                    value = statistics[model.value][module_type.value].get(stat_name, "N/A")
                    rounded_value = f"{round_float_values(value, rounding_places)}"
                except KeyError:
                    rounded_value = "N/A"
                row.append(rounded_value)
            table.add_row(*row)

        # Separate!
        table.add_row("", "")

        # Add index statistics (Time of Min, Index of Min, Time of Max, Index of Max)
        index_metadata = ["Time of Min", "Index of Min", "Time of Max", "Index of Max"]
        for stat_name in index_metadata:
            row = [stat_name]
            for module_type in photovoltaic_module_type:
                try:
                    value = statistics[model.value][module_type.value].get(stat_name, "N/A")
                    rounded_value = f"{round_float_values(value, rounding_places)}"
                except KeyError:
                    rounded_value = "N/A"
                row.append(rounded_value)
            table.add_row(*row)

        # Add a separating row after the statistics for clarity
        table.add_row("", "")

        # Groupings (Yearly, Monthly, Custom Frequency)
        time_groupings = [
            "Yearly means",
            "Monthly means",
            "Weekly means",
            "Daily means",
            "Hourly means",
        ]
        custom_freq_label = f"{groupby} means" if groupby and groupby not in time_groupings else None
        if custom_freq_label and custom_freq_label in statistics:
            custom_freq_data = statistics[custom_freq_label]
            period_count = 1
            for val in custom_freq_data:
                label = f"{groupby} Period {period_count}"
                table.add_row(label, str(val))
                period_count += 1
            table.add_row("", "")

        # Optionally add footer if show_footer is True
        if show_footer:
            table.add_row("", "")
            table.add_row("Summary", "Footer with additional info")

        # Print the table for this model
        if verbose:
            console = Console()
            console.print(table)

def print_spectral_factor(
    timestamps,
    spectral_factor_container: Dict,
    spectral_factor_model: List,
    photovoltaic_module_type: List,
    rounding_places: int = 3,
    include_statistics: bool = False,
    title: str = "Spectral Factor",
    verbose: int = 1,
    index: bool = False,
    show_footer: bool = True,
) -> None:
    """Print the spectral factor series in a formatted table.

    Parameters
    ----------
    - timestamps :
        The time series timestamps.
    - spectral_factor :
        Dictionary containing spectral factor data for different models and module types.
    - spectral_factor_model :
        List of spectral factor models.
    - photovoltaic_module_type :
        List of photovoltaic module types.
    - rounding_places :
        Number of decimal places for rounding.
    - include_statistics :
        Whether to include mean, median, etc., in the output.
    - verbose : int
        Verbosity level.
    - index : bool
        Whether to show an index column.
    """
    # Initialize the table with title and formatting options
    table = Table(
        title=title,
        caption_justify="left",
        expand=False,
        padding=(0, 1),
        box=SIMPLE_HEAD,
        show_footer=show_footer,
    )
    if index:
        table.add_column("Index")

    table.add_column("Time", footer="μ" if show_footer else None)
        # Initialize dictionary to store the means for each module type
    means = {}

    # Calculate mean values for the footer
    if show_footer:
        for module_type in photovoltaic_module_type:
            model = spectral_factor_model[0]  # Assuming only one model for simplicity
            spectral_factor_series = spectral_factor_container.get(model).get(module_type).get(SPECTRAL_FACTOR_COLUMN_NAME)
            mean_value = numpy.nanmean(spectral_factor_series)
            means[module_type.value] = f"{mean_value:.{rounding_places}f}"

    # Add columns for each photovoltaic module type with optional footer
    for module_type in photovoltaic_module_type:
        footer_text = means.get(module_type.value, "") if show_footer else None
        table.add_column(f"{module_type.value}", justify="right", footer=footer_text)

    # Aggregate data for each timestamp
    for _index, timestamp in enumerate(timestamps):
        row = []

        if index:
            row.append(str(_index + 1))  # count from 1

        row.append(str(timestamp))

        for module_type in photovoltaic_module_type:
            model = spectral_factor_model[0]  # Assuming only one model for simplicity
            sm_value = spectral_factor_container.get(model).get(module_type).get(SPECTRAL_FACTOR_COLUMN_NAME)[_index]
            row.append(f"{round(sm_value, rounding_places):.{rounding_places}f}")
        table.add_row(*row)

    print()

    # Print the table if verbose is enabled
    if verbose:
        console = Console()
        console.print(table)

        # Optionally, display additional information in a panel
        if verbose > 1:
            extra_info = "Spectral Mismatch calculated for different photovoltaic module types using specified models."
            console.print(Panel(extra_info, expand=False))
