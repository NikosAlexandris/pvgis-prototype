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
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.cli.print.helpers import build_caption
from pvgisprototype.constants import LOCAL_TIME_COLUMN_NAME, NOT_AVAILABLE, ROUNDING_PLACES_DEFAULT, SOLAR_TIME_NAME, TIME_ALGORITHM_NAME, TIME_COLUMN_NAME
from pvgisprototype import TrueSolarTime


def print_solar_time_series_table(
    longitude,
    timestamps,
    timezone,
    solar_time_series,
    title="True Solar Time",
    index: bool = False,
    rounding_places=ROUNDING_PLACES_DEFAULT,
    user_requested_timestamps=None,
    user_requested_timezone=None,
    group_models=False,
) -> None:
    """
    Print the solar time series results in a table format, with repeated values (like min/max time, unit)
    placed in the caption.
    """
    # Round longitude for consistent display
    longitude = round_float_values(longitude, rounding_places)
    rounded_solar_time_series = round_float_values(solar_time_series, rounding_places)

    # Define columns for the table
    columns = []
    if index:
        columns.append("Index")

    # Define the time column name based on the timezone or user request
    time_column_name = TIME_COLUMN_NAME if user_requested_timestamps is None else LOCAL_TIME_COLUMN_NAME
    columns.append(time_column_name)
    columns.append("Solar Time")

    # Extract metadata that will be placed in the caption
    caption = build_caption(
        longitude=longitude,
        latitude=None,
        rounded_table=rounded_solar_time_series,
        timezone=timezone,
        user_requested_timezone=user_requested_timezone,
    )

    for model_name, model_result in rounded_solar_time_series.items():
        model_caption = caption
        model_caption += f"\n Timing Model : [bold]{model_name}[/bold]"

        # Extract metadata for the caption
        from pvgisprototype.cli.print.helpers import get_value_or_default

        true_solar_time = model_result.get(SOLAR_TIME_NAME, {})
        if isinstance(true_solar_time, TrueSolarTime):
            solar_timing_algorithm = true_solar_time.timing_algorithm 
            unit = true_solar_time.unit
            min_time = true_solar_time.min_minutes
            max_time = true_solar_time.max_minutes

        caption = build_caption(
            longitude=longitude,
            latitude=None,
            rounded_table=rounded_solar_time_series,
            timezone=timezone,
            user_requested_timezone=user_requested_timezone,
            minimum_value=min_time,
            maximum_value=max_time,
        )

        # Create the table object
        table_obj = Table(
            *columns,
            title=title,
            box=SIMPLE_HEAD,
            show_header=True,
            header_style="bold magenta",
        )

        # Iterate over timestamps and add rows for each timestamp with the corresponding solar time
        for _index, timestamp in enumerate(timestamps):
            row = []
            if index:
                row.append(str(_index + 1))  # Add index if requested

            row.append(str(timestamp))  # Add timestamp

            # Extract solar time values for the current timestamp
            solar_time_values = true_solar_time.value
            solar_time_value = (
                f'{solar_time_values[_index]:.{rounding_places}f}' if _index < len(solar_time_values) else NOT_AVAILABLE
            )
            # row.append(model_name)  # Add model name
            row.append(solar_time_value)  # Add solar time for the given timestamp

            table_obj.add_row(*row)

        # Print the table and caption
        Console().print(table_obj)
        Console().print(Panel(model_caption, expand=False))
