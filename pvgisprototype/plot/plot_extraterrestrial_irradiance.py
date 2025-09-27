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
from datetime import datetime, timedelta
from random import randint

import matplotlib.pyplot as plt
from pandas import date_range

from pvgisprototype.api.irradiance.extraterrestrial import (
    calculate_extraterrestrial_normal_irradiance_time_series,
)
from pvgisprototype.api.utilities.timestamp import get_days_in_year
from pvgisprototype.constants import ECCENTRICITY_PHASE_OFFSET, SOLAR_CONSTANT


def generate_timestamps_for_a_year(
    year: int = None,
    frequency: str = "h",  # default to hourly timestamps
    random: bool = False,
):
    """
    Generate timestamps for a given or random year.

    Parameters
    ----------
    year: int, optional
        The year for which to generate timestamps. If not specified, a random
        year is chosen.

    frequency: str
        The frequency of timestamps to generate, e.g., 'h' for hourly. Defaults
        to 'h'.

    Returns:
    - DatetimeIndex: A Pandas DatetimeIndex of timestamps for the specified or
      random year

    """
    if random:
        year = randint(2005, 2024)  # Relating to PVGIS' 2005 starting year

    start_time = f"{year}-01-01 00:00:00"
    end_time = f"{year+1}-01-01 00:00:00"

    timestamps = date_range(
        start=start_time,
        end=end_time,
        freq=frequency,
        inclusive="left",  # Exclude the end_time to keep within the year
    )

    return timestamps


def plot_extraterrestrial_irradiance(
    year: int,
    filename: str = "extraterrestrial_irradiance",
):
    timestamps = generate_timestamps_for_a_year(year=year)
    extraterrestrial_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_time_series(
            timestamps=timestamps,
        )
    )

    figure = plt.figure(figsize=(10, 6))
    # plt.plot(timestamps, extraterrestrial_irradiance_series, label='Solar Constant')  # print from 1972 and on !
    days_of_year = [(ts - datetime(year, 1, 1)).days + 1 for ts in timestamps]
    plt.plot(days_of_year, extraterrestrial_irradiance_series, label="Solar Constant")
    plt.axhline(
        y=SOLAR_CONSTANT, color="gray", linestyle="--", label="Average Solar Constant"
    )

    perigee_day = 2.8408  # Perigee day : January 2 at 8:18pm or day number :
    perigee_timestamp = datetime(year, 1, 1) + timedelta(days=perigee_day - 1)
    perigee_value = calculate_extraterrestrial_normal_irradiance_time_series(
        timestamps=perigee_timestamp,
    )
    plt.scatter(perigee_day, perigee_value, c="red", marker="o", label="Perigee")

    days_in_year = get_days_in_year(year)
    apogee_day = 0.5 * (days_in_year + ECCENTRICITY_PHASE_OFFSET)
    apogee_timestamp = datetime(year, 1, 1) + timedelta(days=apogee_day - 1)
    apogee_value = calculate_extraterrestrial_normal_irradiance_time_series(
        timestamps=apogee_timestamp,
    )
    plt.scatter(apogee_day, apogee_value, c="blue", marker="o", label="Apogee")

    plt.xlabel(f"Day of {year}")
    plt.ylabel("Solar Constant (W/m^2)")
    plt.title(f"Annual Variation of Solar Constant for {year}")
    # plt.grid(True)
    plt.legend(loc="lower right")
    plt.savefig(f"{filename}_{year}.png")

    return figure
