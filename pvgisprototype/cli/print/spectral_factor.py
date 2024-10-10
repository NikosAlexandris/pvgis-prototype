from typing import Dict
from typing import Dict, List
from pvgisprototype.constants import SPECTRAL_FACTOR_COLUMN_NAME
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import numpy


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
