import csv
from pathlib import Path
import numpy as np
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import (
    TITLE_KEY_NAME,
    LONGITUDE_COLUMN_NAME,
    LATITUDE_COLUMN_NAME,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_NAME,
    TIME_ALGORITHM_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    SOLAR_TIME_COLUMN_NAME,
    DECLINATION_COLUMN_NAME,
    DECLINATION_NAME,
    HOUR_ANGLE_COLUMN_NAME,
    HOUR_ANGLE_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    POSITION_ALGORITHM_NAME,
    ZENITH_COLUMN_NAME,
    ZENITH_NAME,
    ALTITUDE_COLUMN_NAME,
    ALTITUDE_NAME,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_NAME,
    UNITS_COLUMN_NAME,
    UNITLESS,
    UNITS_NAME,
    NOT_AVAILABLE,
    ROUNDING_PLACES_DEFAULT,
    RADIANS,
    FINGERPRINT_COLUMN_NAME,
)


def safe_get_value(dictionary, key, index, default='NA'):
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
    if isinstance(value, (list, np.ndarray)) and len(value) > index:
        return value[index]
    return value


def write_irradiance_csv(
    longitude = None,
    latitude = None,
    timestamps = [],
    dictionary = {},
    index: bool = False,
    filename: Path = 'irradiance.csv',
):
    """
    """
    # remove 'Title' and 'Fingerprint' : we don't want repeated values ! ----
    dictionary.pop('Title', NOT_AVAILABLE)
    fingerprint = dictionary.pop(FINGERPRINT_COLUMN_NAME, NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    header = []
    if index:
        header.insert(0, 'Index')
    if longitude:
        header.append('Longitude')
    if latitude:
        header.append('Latitude')
    header.append('Time')
    header.extend(dictionary.keys())

    # Convert single float or int values to arrays of the same length as timestamps
    for key, value in dictionary.items():
        if isinstance(value, (float, int)):
            dictionary[key] = np.full(len(timestamps), value)
        if isinstance(value, str):
            dictionary[key] = np.full(len(timestamps), str(value))
    
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
        row.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        row.extend(values)
        rows.append(row)
    
    # Write to CSV
    if fingerprint:
        filename = filename.with_stem(filename.stem + f'_{fingerprint}')
    with filename.open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # assuming a list of column names
        writer.writerows(rows)  # a list of rows, each row a list of values


def write_solar_position_series_csv(
    longitude,
    latitude,
    timestamps,
    timezone,
    table,
    index: bool = False,
    timing=None,
    declination=None,
    hour_angle=None,
    zenith=None,
    altitude=None,
    azimuth=None,
    surface_orientation=None,
    surface_tilt=None,
    incidence=None,
    user_requested_timestamps=None,
    user_requested_timezone=None,
    rounding_places=ROUNDING_PLACES_DEFAULT,
    group_models=False,
    filename='solar_position.csv',
):
    # Round values
    # longitude = round_float_values(longitude, rounding_places)
    # latitude = round_float_values(latitude, rounding_places)
    # rounded_table = round_float_values(table, rounding_places)
    quantities = [declination, zenith, altitude, azimuth, incidence]

    header = []
    if index:
        header.append("Index")
    if longitude is not None:
        header.append(LONGITUDE_COLUMN_NAME)
    if latitude is not None:
        header.append(LATITUDE_COLUMN_NAME)
    if timestamps is not None:
        header.append('Time')
    if timezone is not None:
        header.append('Zone')
    if user_requested_timestamps is not None and user_requested_timezone is not None:
        header.extend(["Local Time", "Local Zone"])
    if timing is not None:
        header.append(TIME_ALGORITHM_COLUMN_NAME)
    if declination is not None:
        header.append(DECLINATION_COLUMN_NAME)
    if hour_angle is not None:
        header.append(HOUR_ANGLE_COLUMN_NAME)
    if any(quantity is not None for quantity in quantities):
        header.append(POSITION_ALGORITHM_COLUMN_NAME)
    if zenith is not None:
        header.append(ZENITH_COLUMN_NAME)
    if altitude is not None:
        header.append(ALTITUDE_COLUMN_NAME)
    if azimuth is not None:
        header.append(AZIMUTH_COLUMN_NAME)
    if incidence is not None:
        header.append(INCIDENCE_COLUMN_NAME)
    header.append(UNITS_COLUMN_NAME)
    import re
    header = [re.sub(r'[^A-Za-z0-9 ]+', '', h) for h in header]

    rows = []
    # Iterate over each timestamp and its corresponding result
    for model_name, model_result in table.items():
        for _index, timestamp in enumerate(timestamps):
            timing_algorithm = safe_get_value(model_result, TIME_ALGORITHM_NAME, NOT_AVAILABLE)  # If timing is a single value and not a list
            declination_value = safe_get_value(model_result, DECLINATION_NAME, _index) if declination else None
            hour_angle_value = safe_get_value(model_result, HOUR_ANGLE_NAME, _index) if hour_angle else None
            position_algorithm = safe_get_value(model_result, POSITION_ALGORITHM_NAME, NOT_AVAILABLE)
            zenith_value = safe_get_value(model_result, ZENITH_NAME, _index) if zenith else None
            altitude_value = safe_get_value(model_result, ALTITUDE_NAME, _index) if altitude else None
            azimuth_value = safe_get_value(model_result, AZIMUTH_NAME, _index) if azimuth else None
            incidence_value = safe_get_value(model_result, INCIDENCE_NAME, _index) if incidence else None
            units = safe_get_value(model_result, UNITS_NAME, UNITLESS)

            row = []
            if index:
                row.append(str(_index))
            if longitude:
                row.append(str(longitude))
            if latitude:
                row.append(str(latitude))
            row.extend([str(timestamp), str(timezone)])
            
           # ---------------------------------------------------- Implement-Me---
           # Convert the result back to the user's time zone
           # output_timestamp = output_timestamp.astimezone(user_timezone)
           # --------------------------------------------------------------------

           # Redesign Me! =======================================================
            if (
                user_requested_timestamps is not None
                and user_requested_timezone is not None
            ):
                row.extend(
                    [
                        str(user_requested_timestamps.get_loc(timestamp)),
                        str(user_requested_timezone),
                    ]
                )
           #=====================================================================

            if timing is not None:
                row.append(timing_algorithm)
            if declination_value is not None:
                row.append(str(declination_value))
            if hour_angle_value is not None:
                row.append(str(hour_angle_value))
            if position_algorithm is not None:
                row.append(position_algorithm)
            if zenith_value is not None:
                row.append(str(zenith_value))
            if altitude_value is not None:
                row.append(str(altitude_value))
            if azimuth_value is not None:
                row.append(str(azimuth_value))
            if incidence_value is not None:
                row.append(str(incidence_value))
            row.append(str(units))

            rows.append(row)

    # Write to CSV
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def write_solar_position_series_csv(
    longitude,
    latitude,
    timestamps,
    timezone,
    table,
    index: bool = False,
    timing=None,
    declination=None,
    hour_angle=None,
    zenith=None,
    altitude=None,
    azimuth=None,
    surface_orientation=None,
    surface_tilt=None,
    incidence=None,
    user_requested_timestamps=None,
    user_requested_timezone=None,
    rounding_places=ROUNDING_PLACES_DEFAULT,
    group_models=False,
    filename='solar_position.csv',
):
    # Round values
    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    rounded_table = round_float_values(table, rounding_places)
    quantities = [declination, zenith, altitude, azimuth, incidence]

    header = []
    if index:
        header.append("Index")
    if longitude is not None:
        header.append(LONGITUDE_COLUMN_NAME)
    if latitude is not None:
        header.append(LATITUDE_COLUMN_NAME)
    if timestamps is not None:
        header.append('Time')
    if timezone is not None:
        header.append('Zone')
    if user_requested_timestamps is not None and user_requested_timezone is not None:
        header.extend(["Local Time", "Local Zone"])
    if timing is not None:
        header.append(TIME_ALGORITHM_COLUMN_NAME)
    if declination is not None:
        header.append(DECLINATION_COLUMN_NAME)
    if hour_angle is not None:
        header.append(HOUR_ANGLE_COLUMN_NAME)
    if any(quantity is not None for quantity in quantities):
        header.append(POSITION_ALGORITHM_COLUMN_NAME)
    if zenith is not None:
        header.append(ZENITH_COLUMN_NAME)
    if altitude is not None:
        header.append(ALTITUDE_COLUMN_NAME)
    if azimuth is not None:
        header.append(AZIMUTH_COLUMN_NAME)
    if incidence is not None:
        header.append(SURFACE_ORIENTATION_COLUMN_NAME)
        header.append(SURFACE_TILT_COLUMN_NAME)
        header.append(INCIDENCE_COLUMN_NAME)
    header.append(UNITS_COLUMN_NAME)
    import re
    header = [re.sub(r'[^A-Za-z0-9 ]+', '', h) for h in header]

    rows = []
    # Iterate over each timestamp and its corresponding result
    for model_name, model_result in table.items():
        for _index, timestamp in enumerate(timestamps):
            timing_algorithm = safe_get_value(model_result, TIME_ALGORITHM_NAME, NOT_AVAILABLE)  # If timing is a single value and not a list
            declination_value = safe_get_value(model_result, DECLINATION_NAME, _index) if declination else None
            hour_angle_value = safe_get_value(model_result, HOUR_ANGLE_NAME, _index) if hour_angle else None
            position_algorithm = safe_get_value(model_result, POSITION_ALGORITHM_NAME, NOT_AVAILABLE)
            zenith_value = safe_get_value(model_result, ZENITH_NAME, _index) if zenith else None
            altitude_value = safe_get_value(model_result, ALTITUDE_NAME, _index) if altitude else None
            azimuth_value = safe_get_value(model_result, AZIMUTH_NAME, _index) if azimuth else None
            surface_orientation = safe_get_value(model_result, SURFACE_ORIENTATION_NAME, _index) if surface_orientation else None
            surface_tilt = safe_get_value(model_result, SURFACE_TILT_NAME, _index) if surface_tilt else None
            incidence_value = safe_get_value(model_result, INCIDENCE_NAME, _index) if incidence else None
            units = safe_get_value(model_result, UNITS_NAME, UNITLESS)

            row = []
            if index:
                row.append(str(_index))
            if longitude:
                row.append(str(longitude))
            if latitude:
                row.append(str(latitude))
            row.extend([str(timestamp), str(timezone)])
            
           # ---------------------------------------------------- Implement-Me---
           # Convert the result back to the user's time zone
           # output_timestamp = output_timestamp.astimezone(user_timezone)
           # --------------------------------------------------------------------

           # Redesign Me! =======================================================
            if (
                user_requested_timestamps is not None
                and user_requested_timezone is not None
            ):
                row.extend(
                    [
                        str(user_requested_timestamps.get_loc(timestamp)),
                        str(user_requested_timezone),
                    ]
                )
           #=====================================================================

            if timing is not None:
                row.append(timing_algorithm)
            if declination_value is not None:
                row.append(str(declination_value))
            if hour_angle_value is not None:
                row.append(str(hour_angle_value))
            if position_algorithm is not None:
                row.append(position_algorithm)
            if zenith_value is not None:
                row.append(str(zenith_value))
            if altitude_value is not None:
                row.append(str(altitude_value))
            if azimuth_value is not None:
                row.append(str(azimuth_value))
            if incidence_value is not None:
                if surface_orientation is not None:
                    row.append(str(surface_orientation))
                if surface_tilt is not None:
                    row.append(str(surface_tilt))
                row.append(str(incidence_value))
            row.append(str(units))
            rows.append(row)

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)
