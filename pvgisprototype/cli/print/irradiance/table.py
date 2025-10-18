#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import numpy
from pvgisprototype.cli.print.irradiance.columns import add_key_table_columns
from pvgisprototype.cli.print.irradiance.keys import KEYS_TO_EXCLUDE
from pvgisprototype.cli.print.irradiance.text import format_string
from pvgisprototype.log import logger
from rich.box import SIMPLE_HEAD
from xarray import DataArray
from pandas import to_datetime
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import (
    NOT_AVAILABLE,
    SYMBOL_SUMMATION,
)


def build_irradiance_table(
    title: str | None,
    index: bool,
    dictionary,
    timestamps,
    rounding_places,
    keys_to_sum: dict,
    keys_to_average: dict,
    keys_to_exclude: dict,
    time_column_name: RenderableType = "Time",
    time_column_footer: RenderableType = SYMBOL_SUMMATION,
    time_column_footer_style: str = "purple",
) -> RenderableType:
    """
    """
    table = Table(
        title=title,
        # caption=caption.rstrip(', '),  # Remove trailing comma + space
        caption_justify="left",
        expand=False,
        padding=(0, 1),
        box=SIMPLE_HEAD,
        header_style="bold gray50",
        show_footer=True,
        footer_style='white',
        row_styles=["none", "dim"],
        highlight=True,
    )

    # base columns

    if index:
        table.add_column("Index")

    ## Time column

    table.add_column(
        time_column_name,
        no_wrap=True,
        footer=time_column_footer,
        footer_style=time_column_footer_style,
    )

    # remove the 'Title' entry! ---------------------------------------------
    dictionary.pop("Title", NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    # add and process additional columns

    table = add_key_table_columns(
                        table=table,
                        dictionary=dictionary,
                        timestamps=timestamps,
                        rounding_places=rounding_places,
                        keys_to_sum=keys_to_sum,
                        keys_to_average=keys_to_average,
                        keys_to_exclude=keys_to_exclude,
                    )

    return table


def populate_irradiance_table(
    table,
    dictionary,
    timestamps,
    index,
    rounding_places,
    keys_to_exclude: set = KEYS_TO_EXCLUDE,
) -> RenderableType:
    """
    """
    # Zip series and timestamps
    filtered_dictionary = {
        key: numpy.atleast_1d(value) for key, value in dictionary.items()
        if key not in keys_to_exclude
    }
    none_keys = [key for key, value in filtered_dictionary.items() if value is None]
    if none_keys:
        raise ValueError(f"The following keys are of `NoneType` which is not iterable and thus cannot be zipped: {none_keys}")
    zipped_series = zip(*filtered_dictionary.values())
    zipped_data = zip(timestamps, zipped_series)

    index_counter = 1
    for timestamp, values in zipped_data:
        row = []

        if index:
            row.append(str(index_counter))
            index_counter += 1

        row.append(to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S"))

        for idx, (column_name, value) in enumerate(
            zip(filtered_dictionary.keys(), values)
        ):
            # First row of the table is the header
            if idx == 0:  # assuming after 'Time' is the value of main interest
                # Make first row item bold
                bold_value = Text(
                    str(round_float_values(value, rounding_places)), style="bold dark_orange",
                )
                row.append(bold_value)

            else:
                # if not isinstance(value, str) or isinstance(value, float):

                row.append(
                    format_string(
                        value=value,
                        column_name=column_name,
                        rounding_places=rounding_places,
                    )
                )
                    # # If values of this column are negative / represent loss
                    # if f" {SYMBOL_LOSS}" in column_name or f"{SYMBOL_REFLECTIVITY}" in column_name or value < 0:  # Avoid matching any `-`
                    #     # Make them bold red
                    #     red_value = Text(
                    #         str(round_float_values(value, rounding_places)),
                    #         style="bold red",
                    #     )
                    #     row.append(red_value)

                    # else:
                    #     row.append(str(round_float_values(value, rounding_places)))

                # else:
                    # from pvgisprototype.api.position.models import SunHorizonPositionModel
                    # print(f"{value=}")
                    # row.append(format_string(value=value, rounding_places=rounding_places))
                    # if value == SunHorizonPositionModel.above.value:
                    #     yellow_value = Text(
                    #         str(round_float_values(value, rounding_places)),
                    #         style="bold yellow",
                    #     )
                    #     row.append(yellow_value)
                    # elif value == SunHorizonPositionModel.low_angle.value:
                    #     orange_value = Text(
                    #         str(round_float_values(value, rounding_places)),
                    #         style="dark_orange",
                    #     )
                    #     row.append(orange_value)
                    # elif value == SunHorizonPositionModel.below.value:
                    #     red_value = Text(
                    #         str(round_float_values(value, rounding_places)),
                    #         style="red",
                    #     )
                    #     row.append(red_value)
                    # else:  # value is not None:
                    #     row.append(value)

        table.add_row(*row)

    return table


def print_table_and_legend(
    caption: RenderableType,
    table: RenderableType,
    rear_side_table: RenderableType | None,
    legend: RenderableType,
    caption_subtitle: str = 'Reference',
    legend_subtitle: str = 'Legend',
) -> None:
    """
    Print panels for both caption and legend

    """
    Console().print(table)
    if rear_side_table:
        Console().print(rear_side_table)

    panels = []
    if caption:
        caption_panel = Panel(
            caption,
            subtitle=f"[gray]{caption_subtitle}[/gray]",
            subtitle_align="right",
            border_style="dim",
            expand=False
        )
        panels.append(caption_panel)

    if legend:
        legend_panel = Panel(
            legend,
            subtitle=f"[dim]{legend_subtitle}[/dim]",
            subtitle_align="right",
            border_style="dim",
            expand=False,
            padding=(0,1),
            # style="dim",
        )
        panels.append(legend_panel)

    # Use Columns to place them side-by-side
    from rich.columns import Columns
    Console().print(Columns(panels))


def print_irradiance_xarray(
    location_time_series: DataArray,
    longitude=None,
    latitude=None,
    elevation=None,
    coordinate: str = None,
    title: str | None = "Irradiance data",
    rounding_places: int = 3,
    verbose: int = 1,
    index: bool = False,
) -> None:
    """
    Print the irradiance time series in a formatted table with each center wavelength as a column.

    Parameters
    ----------
    location_time_series : xr.DataArray
        The time series data with dimensions (time, center_wavelength).
    longitude : float, optional
        The longitude of the location.
    latitude : float, optional
        The latitude of the location.
    elevation : float, optional
        The elevation of the location.
    title : str, optional
        The title of the table.
    rounding_places : int, optional
        The number of decimal places to round to.
    verbose : int, optional
        Verbosity level.
    index : bool, optional
        Whether to show an index column.
    """
    console = Console()
    # Extract relevant data from the location_time_series

    # Prepare the table
    table = Table(
        title=title,
        caption_justify="left",
        expand=False,
        padding=(0, 1),
        box=SIMPLE_HEAD,
        show_footer=True,
    )

    if index:
        table.add_column("Index")

    if 'time' in location_time_series.dims:
        table.add_column("Time", footer=f"{SYMBOL_SUMMATION}")

    # Add columns for each center wavelength (irradiance wavelength)
    if 'center_wavelength' in location_time_series.coords:
        center_wavelengths = location_time_series.coords['center_wavelength'].values
        if center_wavelengths.size > 0:
            for wavelength in center_wavelengths:
                table.add_column(f"{wavelength:.0f} nm", justify="right")
        else:
            logger.warning("No center_wavelengths found in the dataset.")
    else:
        logger.warning("No 'center_wavelength' coordinate found in the dataset.")

    # Populate the table with the irradiance data

    # case of scalar data
    if 'time' not in location_time_series.dims:
        row = []
        if index:
            row.append("1")  # Single row for scalar data

        # Handle the presence of a coordinate (like center_wavelength)
        # if coordinate ... ?
        if 'center_wavelength' in location_time_series.coords:
            for irradiance_value in location_time_series.values:
                row.append(f"{round(irradiance_value, rounding_places):.{rounding_places}f}")
        else:
            row.append(f"{round(location_time_series.item(), rounding_places):.{rounding_places}f}")

        table.add_row(*row)


    else:
        irradiance_values = location_time_series.values
        for idx, timestamp in enumerate(location_time_series.time.values):
            row = []

            if index:
                row.append(str(idx + 1))

            # Convert timestamp to string format
            try:
                row.append(to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                logger.error(f"Invalid timestamp at index {idx}: {e}")
                row.append("Invalid timestamp")

            if 'center_wavelength' in location_time_series.coords:
                # add data variable values for each "coordinate" value at this timestamp
                # i.e. : irradiance values for each "center_wavelength" at this timestamp
                for irradiance_value in irradiance_values[idx]:
                    row.append(f"{round(irradiance_value, rounding_places):.{rounding_places}f}")
            else:
                #  a scalar, i.e. no Xarray "coordinate"
                row.append(f"{round(irradiance_values[idx], rounding_places):.{rounding_places}f}")

            table.add_row(*row)

    # Prepare a caption with the location information
    caption = str()
    if longitude is not None and latitude is not None:
        caption += f"Location  Longitude ϑ, Latitude ϕ = {longitude}, {latitude}"

    if elevation is not None:
        caption += f", Elevation: {elevation} m"

    caption += "\nLegend: Center Wavelengths (nm)"

    if verbose:
        console.print(table)
        console.print(Panel(caption, expand=False))
