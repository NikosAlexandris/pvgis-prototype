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
import csv
from pathlib import Path
import re
from typing import Dict, Sequence
from pandas import DatetimeIndex, Timestamp

from pvgisprototype.api.position.models import SolarEvent, SolarPositionParameter, SolarPositionParameterColumnName
from pvgisprototype.api.statistics.xarray import calculate_series_statistics
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleType
from numpy import full, ndarray, generic
from pvgisprototype import (
    SurfaceOrientation,
    SurfaceTilt,
)
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import (
    SPECTRAL_FACTOR_COLUMN_NAME,
    ALTITUDE_COLUMN_NAME,
    ALTITUDE_NAME,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_NAME,
    DECLINATION_COLUMN_NAME,
    DECLINATION_NAME,
    FINGERPRINT_COLUMN_NAME,
    HOUR_ANGLE_COLUMN_NAME,
    HOUR_ANGLE_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_NAME,
    LATITUDE_COLUMN_NAME,
    LONGITUDE_COLUMN_NAME,
    NOT_AVAILABLE,
    POSITION_ALGORITHM_COLUMN_NAME,
    POSITION_ALGORITHM_NAME,
    ROUNDING_PLACES_DEFAULT,
    SHADING_STATES_COLUMN_NAME,
    SUN_HORIZON_POSITIONS_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    TIME_ALGORITHM_NAME,
    UNIT_NAME,
    UNITLESS,
    UNITS_COLUMN_NAME,
    ZENITH_COLUMN_NAME,
    ZENITH_NAME,
)


def create_csv_export_panel(
    filename: Path,
    num_rows: int,
    num_columns: int,
) -> Panel:
    """
    Create a Rich Panel displaying CSV export information.
    
    Parameters
    ----------
    filename : Path
        Output CSV file path
    num_rows : int
        Number of data rows written
    num_columns : int
        Number of columns in CSV
    location_info : str, optional
        Location/coordinate information
    time_range_info : str, optional
        Time range information
    
    Returns
    -------
    Panel
        Rich Panel with formatted export information
    """
    # Create info table
    info_table = Table(box=None, show_header=False, padding=(0, 1))
    info_table.add_column(style="cyan", width=20)
    info_table.add_column(style="white")
    
    # Add rows with icons and info
    info_table.add_row("📁 File", Text(str(filename), style="bold green"))
    info_table.add_row("_ Rows", Text(str(num_rows), style="bold yellow"))
    info_table.add_row("| Columns", Text(str(num_columns), style="bold blue"))
    
    panel = Panel(
        info_table,
        title="[bold]CSV output[/bold]",
        title_align="left",
        border_style="dim",
        box=ROUNDED,
        padding=(1, 2),
        expand=False,
    )
    
    return panel


def print_csv_export_info(
    filename: Path,
    num_rows: int,
    num_columns: int,
) -> None:
    """
    Print a formatted info panel for CSV export.
    
    Parameters
    ----------
    filename : Path
        Output CSV file path
    num_rows : int
        Number of data rows written
    num_columns : int
        Number of columns in CSV
    """
    from rich.console import Console
    
    console = Console()
    panel = create_csv_export_panel(
        filename=filename,
        num_rows=num_rows,
        num_columns=num_columns,
    )
    console.print(panel)


def safe_get_value(dictionary, key, index, default=NOT_AVAILABLE):
    """
    Parameters
    ----------
    dictionary: dict
        Input dictionary
    key: str
        key to retrieve from the dictionary
    index: int
        index ... ?

    Returns
    -------
    The value corresponding to the given `key` in the `dictionary` or the
    default value if the key does not exist.

    """
    value = dictionary.get(key, default)
    # if isinstance(value, ndarray) and value.size > 1:
    if isinstance(value, (list, ndarray)) and len(value) > index:
        return value[index]
    return value


def export_statistics_to_csv(data_array, filename):
    statistics = calculate_series_statistics(data_array)
    with open(f"{filename}.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Statistic", "Value"])
        for statistic, value in statistics.items():
            writer.writerow([statistic, value])


def write_irradiance_csv(
    longitude: float = None,
    latitude: float = None,
    timestamps: list = [],
    dictionary: dict = {},
    index: bool = False,
    filename: Path = Path("irradiance.csv"),
) -> None:
    """
    Write time series data to a CSV file in a structured format.

    This function takes location information (longitude and latitude), a time
    series (timestamps), and a dictionary containing irradiance or photovoltaic
    power data, generated by PVGIS' API functions, and writes them into a CSV
    file.

    Attention ! The function modifies the input dictionary by removing certain
    keys (such as 'Title' and 'Fingerprint') to avoid repeated values in the
    output file. It is essential to place this function last in the workflow if
    the original dictionary is needed elsewhere in the code, as it alters the
    input dictionary in place to save memory.

    Parameters
    ----------
    longitude : float, optional
        Longitude of the location to include in the CSV output.
    
    latitude : float, optional
        Latitude of the location to include in the CSV output.
    
    timestamps : list, optional
        A Pandas DatetimeIndex. Each timestamp will correspond to a row in the
        CSV file.
    
    dictionary : dict
        A dictionary containing the irradiance or photovoltaic data, where 
        each key is a variable name and each value is either a list/array of 
        data or a single value to be replicated for all timestamps.
    
    index : bool, optional
        If True, an index column will be added to the CSV file, where each 
        row will be numbered sequentially.
    
    filename : Path, optional
        The output file path where the CSV will be saved. Defaults to 
        "irradiance.csv".
    
    Notes
    -----
    - The function is optimized to avoid deep copying the dictionary, 
      reducing memory consumption. It should be placed at the end of any 
      process that requires the original dictionary to remain unmodified.

    - Fingerprint information is removed from the input dictionary and added 
      as part of the filename.
    
    - Single float or integer values in the dictionary are expanded to match 
      the length of the timestamps.
    
    - This function expects the `photovoltaic_power_output_series.components` 
      structure to match the format required for writing to CSV.

    Example
    -------
    >>> write_irradiance_csv(
            longitude=-3.7038,
            latitude=40.4168,
            timestamps=some_timestamps,
            dictionary=some_data,
            filename=Path("output.csv"),
            index=True
        )

    This will generate a CSV file named 'output.csv' with the specified 
    data and location.
    """
    # remove 'Title' and 'Fingerprint' : we don't want repeated values ! ----
    dictionary.pop("Title", NOT_AVAILABLE)
    fingerprint = dictionary.pop(FINGERPRINT_COLUMN_NAME, None)
    if not fingerprint:
        fingerprint = Timestamp.now().isoformat(timespec="seconds")
        # Sanitize the ISO datetime for a safe filename
    safe_fingerprint = re.sub(r"[:]", "-", fingerprint)  # Replace colons with hyphens
    safe_fingerprint = safe_fingerprint.replace(" ", "T")  # Ensure ISO format with 'T'
    # remove 'Sun Horizon Positions' : we don't need a list of possible options !
    sun_horizon_positions = dictionary.pop(SUN_HORIZON_POSITIONS_NAME, NOT_AVAILABLE)
    shading_states = dictionary.pop(SHADING_STATES_COLUMN_NAME, NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    header = []
    if index:
        header.insert(0, "Index")
    if longitude:
        header.append("Longitude")
    if latitude:
        header.append("Latitude")

    header.append("Time")
    header.extend(dictionary.keys())

    # Convert single float or int values to arrays of the same length as timestamps
    for key, value in dictionary.items():
        if isinstance(value, (float, int)):
            dictionary[key] = full(len(timestamps), value)
        if isinstance(value, str):
            dictionary[key] = full(len(timestamps), str(value))
        if isinstance(value, PhotovoltaicModuleType):
            dictionary[key] = full(len(timestamps), str(value.value))


    # Zip series and timestamps
    zipped_series = zip(*dictionary.values())
    zipped_data = zip(timestamps, zipped_series)

    rows = []
    for idx, (timestamp, values) in enumerate(zipped_data):
        row = []
        if index:
            row.append(idx)
        if longitude and latitude:
            row.extend([longitude, latitude])
        row.append(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        row.extend(values)
        rows.append(row)

    # Write to CSV
    if fingerprint:
        # use the _safe_ fingerprint !
        filename = filename.with_stem(filename.stem + f"_{safe_fingerprint}")
    with filename.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)  # assuming a list of column names
        writer.writerows(rows)  # a list of rows, each row a list of values


# def write_solar_position_series_csv(
#     longitude,
#     latitude,
#     timestamps,
#     timezone,
#     table,
#     index: bool = False,
#     timing=None,
#     declination=None,
#     hour_angle=None,
#     zenith=None,
#     altitude=None,
#     azimuth=None,
#     surface_orientation=None,
#     surface_tilt=None,
#     incidence=None,
#     user_requested_timestamps=None,
#     user_requested_timezone=None,
#     rounding_places=ROUNDING_PLACES_DEFAULT,
#     group_models: bool = False,
#     filename: Path = Path("solar_position.csv"),
# ):
#     print(f"{table=}")
#     # Round values
#     longitude = round_float_values(longitude, rounding_places)
#     latitude = round_float_values(latitude, rounding_places)
#     # rounded_table = round_float_values(table, rounding_places)
#     quantities = [declination, zenith, altitude, azimuth, incidence]

#     header = []
#     if index:
#         header.append("Index")
#     if longitude is not None:
#         header.append(LONGITUDE_COLUMN_NAME)
#     if latitude is not None:
#         header.append(LATITUDE_COLUMN_NAME)
#     if timestamps is not None:
#         header.append("Time")
#     if timezone is not None:
#         header.append("Zone")
#     if user_requested_timestamps is not None and user_requested_timezone is not None:
#         header.extend(["Local Time", "Local Zone"])
#     if timing is not None:
#         header.append(SolarPositionParameterColumnName.timing.value)
#     if declination is not None:
#         header.append(SolarPositionParameterColumnName.declination.value)
#     if hour_angle is not None:
#         header.append(SolarPositionParameterColumnName.hour_angle.value)
#     if any(quantity is not None for quantity in quantities):
#         header.append(SolarPositionParameterColumnName.positioning.value)
#     if zenith is not None:
#         header.append(SolarPositionParameterColumnName.zenith.value)
#     if altitude is not None:
#         header.append(SolarPositionParameterColumnName.altitude.value)
#     if azimuth is not None:
#         header.append(SolarPositionParameterColumnName.azimuth.value)
#     if incidence is not None:
#         header.append(SURFACE_ORIENTATION_COLUMN_NAME)
#         header.append(SURFACE_TILT_COLUMN_NAME)
#         header.append(INCIDENCE_COLUMN_NAME)
#     header.append(UNITS_COLUMN_NAME)
#     import re

#     header = [re.sub(r"[^A-Za-z0-9 ]+", "", h) for h in header]

#     rows = []
#     # Iterate over each timestamp and its corresponding result
#     for _, model_result in table.items():
#         for _index, timestamp in enumerate(timestamps):
#             timing_algorithm = safe_get_value(
#                 model_result, TIME_ALGORITHM_NAME, NOT_AVAILABLE
#             )  # If timing is a single value and not a list
#             declination_value = (
#                 safe_get_value(model_result, DECLINATION_NAME, _index)
#                 if declination
#                 else None
#             )
#             hour_angle_value = (
#                 safe_get_value(model_result, HOUR_ANGLE_NAME, _index)
#                 if hour_angle
#                 else None
#             )
#             solar_positioning_algorithm = safe_get_value(
#                 model_result, POSITION_ALGORITHM_NAME, NOT_AVAILABLE
#             )
#             zenith_value = (
#                 safe_get_value(model_result, ZENITH_NAME, _index) if zenith else None
#             )
#             altitude_value = (
#                 safe_get_value(model_result, ALTITUDE_NAME, _index)
#                 if altitude
#                 else None
#             )
#             azimuth_value = (
#                 safe_get_value(model_result, AZIMUTH_NAME, _index) if azimuth else None
#             )
#             surface_orientation = (
#                 safe_get_value(model_result, SURFACE_ORIENTATION_NAME, _index)
#                 if surface_orientation
#                 else None
#             )
#             surface_tilt = (
#                 safe_get_value(model_result, SURFACE_TILT_NAME, _index)
#                 if surface_tilt
#                 else None
#             )
#             incidence_value = (
#                 safe_get_value(model_result, INCIDENCE_NAME, _index)
#                 if incidence
#                 else None
#             )
#             units = safe_get_value(model_result, UNIT_NAME, UNITLESS)

#             row = []
#             if index:
#                 row.append(str(_index))
#             if longitude:
#                 row.append(str(longitude))
#             if latitude:
#                 row.append(str(latitude))
#             row.extend([str(timestamp), str(timezone)])

#             # ---------------------------------------------------- Implement-Me---
#             # Convert the result back to the user's time zone
#             # output_timestamp = output_timestamp.astimezone(user_timezone)
#             # --------------------------------------------------------------------

#             # Redesign Me! =======================================================
#             if user_requested_timestamps is not None and (
#                 user_requested_timestamps.tz is None
#                 and user_requested_timezone is not None
#             ):
#                 user_requested_timestamps = user_requested_timestamps.tz_localize(
#                     user_requested_timezone
#                 )
#                 row.extend(
#                     [
#                         str(user_requested_timestamps.get_loc(timestamp)),
#                         str(user_requested_timezone),
#                     ]
#                 )
#             # =====================================================================

#             if timing is not None:
#                 row.append(timing_algorithm)
#             if declination_value is not None:
#                 row.append(str(declination_value))
#             if hour_angle_value is not None:
#                 row.append(str(hour_angle_value))
#             if solar_positioning_algorithm is not None:
#                 row.append(solar_positioning_algorithm)
#             if zenith_value is not None:
#                 row.append(str(zenith_value))
#             if altitude_value is not None:
#                 row.append(str(altitude_value))
#             if azimuth_value is not None:
#                 row.append(str(azimuth_value))
#             if incidence_value is not None:
#                 if surface_orientation is not None:
#                     row.append(str(surface_orientation))
#                 if surface_tilt is not None:
#                     row.append(str(surface_tilt))
#                 row.append(str(incidence_value))
#             row.append(str(units))
#             rows.append(row)

#     with open(filename, "w", newline="") as file:
#         writer = csv.writer(file)
#         writer.writerow(header)
#         writer.writerows(rows)



def write_spectral_factor_csv(
    longitude,
    latitude,
    timestamps: DatetimeIndex,
    spectral_factor_dictionary: Dict,
    filename: Path = Path("spectral_factor.csv"),
    index: bool = False,
):
    """
    Write the spectral factor data to a CSV file.

    Parameters
    ----------
    - longitude: Longitude of the location.
    - latitude: Latitude of the location.
    - timestamps: DatetimeIndex of the time series.
    - spectral_factor_dictionary: Dictionary containing spectral factor data.
    - filename: Path for the output CSV file.
    - index: Whether to include the index in the CSV.

    """
    header = []
    if index:
        header.append("Index")
    if longitude:
        header.append("Longitude")
    if latitude:
        header.append("Latitude")
    
    header.append("Time")

    # Prepare the data for each spectral factor model and module type
    data_rows = []
    for spectral_factor_model, result in spectral_factor_dictionary.items():
        for module_type, data in result.items():
            spectral_factor_series = data.get(SPECTRAL_FACTOR_COLUMN_NAME)

            # If spectral_factor_series is a scalar, expand it to match the length of timestamps
            if isinstance(spectral_factor_series, (float, int)):
                spectral_factor_series = full(len(timestamps), spectral_factor_series)

            # Add the header for this particular module type and spectral factor model
            header.append(f"{module_type.value} ({spectral_factor_model.name})")

            # Prepare the rows
            for idx, timestamp in enumerate(timestamps):
                if len(data_rows) <= idx:
                    data_row = []
                    if index:
                        data_row.append(idx)
                    if longitude and latitude:
                        data_row.extend([longitude, latitude])
                    data_row.append(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                    data_rows.append(data_row)

                # Append spectral factor data for this timestamp and module type
                data_rows[idx].append(spectral_factor_series[idx])

    # Write to CSV
    with filename.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write header
        writer.writerows(data_rows)  # Write rows of data


def write_surface_position_csv(
    longitude: float,
    latitude: float,
    timestamps: list = [],
    timezone: str | None = None,
    dictionary: dict = {},
    fingerprint: str | None = None,
    index: bool = False,
    filename: Path = Path("optimal_surface_position.csv"),
) -> None:
    """
    """
    # remove 'Title' and 'Fingerprint' : we don't want repeated values ! ----
    dictionary.pop("Title", NOT_AVAILABLE)
    fingerprint = dictionary.pop(FINGERPRINT_COLUMN_NAME, None)
    if not fingerprint:
        fingerprint = Timestamp.now().isoformat(timespec="seconds")
        # Sanitize the ISO datetime for a safe filename
    safe_fingerprint = re.sub(r"[:]", "-", fingerprint)  # Replace colons with hyphens
    safe_fingerprint = safe_fingerprint.replace(" ", "T")  # Ensure ISO format with 'T'
    # ------------------------------------------------------------- Important

    header: list = []
    if index:
        header.insert(0, "Index")
    if longitude:
        header.append("Longitude")
    if latitude:
        header.append("Latitude")

    header.append("Start Time")
    header.append("End Time")
    header.append("Timezone")
    header.extend(dictionary.keys())


    # Convert special types to strings
    for key, value in dictionary.items():
        if isinstance(value, generic):  # NumPy scalar
            dictionary[key] = str(value)
        elif (isinstance(value, SurfaceOrientation) or isinstance(value, SurfaceTilt)) and hasattr(value, "value"):  # Enums or custom objects with .value
            dictionary[key] = str(value.value)
        elif isinstance(value, (float, int)):
            dictionary[key] = str(value)

    # Compose single row
    row = []
    if index:
        row.append(0)
    row.extend([
        longitude, # type:ignore[list-item]
        latitude, # type:ignore[list-item]
        timestamps[0].strftime("%Y-%m-%d %H:%M:%S"),
        timestamps[-1].strftime("%Y-%m-%d %H:%M:%S"),
        timezone, # type:ignore[list-item]
    ])
    row.extend(dictionary.values())

    rows = [row]

    # Generate filename with fingerprint
    if fingerprint:
        filename = filename.with_stem(filename.stem + f"_{safe_fingerprint}")

    # Write to CSV
    with filename.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def write_solar_position_series_csv(
    longitude: float,
    latitude: float,
    timestamps,
    timezone: str,
    table: dict,
    position_parameters: Sequence[SolarPositionParameter],
    index: bool = False,
    rounding_places: int = 2,
    filename: Path = Path("solar_position_overview.csv"),
) -> None:
    """
    Write solar position overview data to CSV from nested dictionary structure.

    This function flattens the nested table dictionary and writes time-series
    data to CSV format, handling numpy arrays, enums, and special types.
    """
    import csv
    import re
    from numpy import datetime64, isnat, bool_
    from pandas import to_datetime, isna
    import numpy

    # Helper function to find nested values (reused from printing)
    def find_nested_value(d: dict, key: str):
        if key in d:
            return d[key]
        for v in d.values():
            if isinstance(v, dict):
                found = find_nested_value(v, key)
                if found is not None:
                    return found
        return None

    # Helper to check if value exists in dict by identity
    def value_in_dict(value, d):
        """Check if value is in dictionary by object identity."""
        for v in d.values():
            if v is value:
                return True
        return False

    # Helper to safely get scalar value from array at index
    def get_scalar(value_array, idx, rounding_places):
        if value_array is None:
            return None
        if not hasattr(value_array, "__len__"):
            return value_array
        if len(value_array) <= idx:
            return None

        value = value_array[idx]

        # Round numeric values
        if isinstance(value, (int, float, numpy.floating, numpy.integer)):
            return round(float(value), rounding_places)

        return value

    # Extract the first model result (e.g., 'noaa')
    first_model_key = next(iter(table))
    model_result = table[first_model_key]

    # Extract core data and events data
    core_data = model_result.get("Core", {})
    events_data = model_result.get("Solar Events", {})
    algorithms_data = model_result.get("Solar Position Algorithms", {})

    # Build header columns
    header = []
    columns_to_extract = []  # Store (header_name, data_source_dict) tuples

    if index:
        header.append("Index")

    header.extend(["Longitude", "Latitude", "Time", "Timezone"])

    # Add columns for each requested parameter
    for parameter in position_parameters:
        # Skip enum members without a matching ColumnName
        if parameter.name not in SolarPositionParameterColumnName.__members__:
            continue

        # Get the human-readable column name
        column_name = SolarPositionParameterColumnName[parameter.name].value

        # Find where this data lives
        value = None
        source_dict = None

        if column_name in core_data:
            value = core_data[column_name]
            source_dict = core_data
        elif column_name in events_data:
            value = events_data[column_name]
            source_dict = events_data
        elif column_name in algorithms_data:
            value = algorithms_data[column_name]
            source_dict = algorithms_data
        else:
            # Try nested search
            value = find_nested_value(model_result, column_name)
            if value is not None:
                # Use identity check instead of 'in' to avoid array comparison
                if value_in_dict(value, core_data):
                    source_dict = core_data
                elif value_in_dict(value, events_data):
                    source_dict = events_data
                elif value_in_dict(value, algorithms_data):
                    source_dict = algorithms_data

        if value is None:
            continue

        # For event columns, check if there's actual data
        if parameter in (
            SolarPositionParameter.event_type,
            SolarPositionParameter.event_time,
        ):
            if not hasattr(value, "__iter__") or isinstance(value, str):
                value_list = [value]
            else:
                value_list = value

            def is_real_event(ev):
                if isinstance(ev, datetime64):
                    return not isnat(ev)
                if ev is not None and hasattr(ev, "name") and ev.name == "none":
                    return False
                return ev not in (None, "None")

            has_data = any(is_real_event(v) for v in value_list)
            if not has_data:
                continue

        # Clean column name for CSV (remove special characters)
        clean_column_name = re.sub(r"[^A-Za-z0-9 ]+", "", column_name).strip()
        header.append(clean_column_name)
        columns_to_extract.append((column_name, source_dict))

    # Build rows
    rows = []
    for idx, timestamp in enumerate(timestamps):
        row = []

        if index:
            row.append(str(idx))

        # Add location and time info
        row.append(str(longitude))
        row.append(str(latitude))
        row.append(to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S"))
        row.append(str(timezone))

        # Extract each parameter value for this timestamp
        for column_name, source_dict in columns_to_extract:
            if source_dict is None:
                row.append("")
                continue

            value_array = source_dict.get(column_name)
            value = get_scalar(value_array, idx, rounding_places)

            # Format value for CSV
            if value is None or (isinstance(value, float) and isna(value)):
                row.append("")
            elif isinstance(value, SolarEvent):
                row.append(value.value)
            elif isinstance(value, datetime64):
                if isnat(value):
                    row.append("")
                else:
                    dt = value.astype("datetime64[s]").astype("O")
                    row.append(str(dt.time()))
            elif isinstance(value, (bool_, bool)):
                row.append(str(bool(value)))
            elif isinstance(value, (int, float, numpy.generic)):
                row.append(str(value))
            else:
                row.append(str(value))

        rows.append(row)

    # Write to CSV
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)

    print_csv_export_info(
        filename=filename,
        num_rows=len(rows),
        num_columns=len(header),
    )
