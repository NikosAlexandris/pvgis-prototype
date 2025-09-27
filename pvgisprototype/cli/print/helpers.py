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
from pvgisprototype.log import logger
from pandas import DatetimeIndex
import numpy


def determine_frequency(timestamps):
    """ """
    # single timestamp ?
    if len(timestamps) == 1:
        return "Single", "Single Timestamp"

    time_groupings = {
        "YE": "Yearly",
        "S": "Seasonal",
        "ME": "Monthly",
        "W": "Weekly",
        "D": "Daily",
        "3h": "3-Hourly",
        "h": "Hourly",
        "min": "Minutely",
        "8min": "8-Minutely",
    }
    if timestamps.year.unique().size > 1:
        frequency = "YE"
    elif timestamps.month.unique().size > 1:
        frequency = "ME"
    elif timestamps.to_period('W').week.unique().size > 1:
        frequency = "W"
    elif timestamps.day.unique().size > 1:
        frequency = "D"
    elif timestamps.hour.unique().size > 1:
        if timestamps.hour.unique().size < 17:  # Explain Me !
            frequency = "h"
        else:
            frequency = "3h"
    elif timestamps.minute.unique().size < 17:  # Explain Me !
        frequency = "min"
    else:
        frequency = "8min"  # by 8 characters for a sparkline if timestamps > 64 min
    frequency_label = time_groupings[frequency]

    return frequency, frequency_label


def infer_frequency_from_timestamps(timestamps: DatetimeIndex):
    """
    Process timestamps to infer frequency based on regularity or irregularity of intervals.
    """
    if timestamps.freqstr:  # timestamps are regular
        logger.debug(
            f"Regular intervals detected: {timestamps.freqstr}",
            alt=f"[bold]Regular intervals detected:[/bold] {timestamps.freqstr}",
        )
        return timestamps.freqstr, f"{timestamps.freqstr}"

    else:
        try:
            # Calculate time differences directly with NumPy for regular intervals
            time_deltas = numpy.diff(timestamps).astype("timedelta64[ns]")

            # Find the most frequent time delta using numpy.unique
            unique_deltas, counts = numpy.unique(time_deltas, return_counts=True)
            frequency = unique_deltas[numpy.argmax(counts)]
            logger.debug(
                f"Inferred frequency of timestamps: {frequency}",
                alt=f"[bold]Inferred frequency of timestamps:[/bold] {frequency}",
            )

            # Calculate the total duration : end - start
            total_duration = (timestamps[-1] - timestamps[0]).astype("timedelta64[ns]")

            # Calculate the number of intervals
            intervals = total_duration / frequency

            # Check if the number of intervals matches the number of timestamps - 1 (with tolerance)
            if numpy.isclose(len(timestamps) - 1, intervals, atol=1e-8):
                # If the intervals match, we can say the series is regular
                from pandas import to_timedelta

                return frequency, f"Regular intervals of {to_timedelta(frequency)}"

            else:
                try:
                    # Fallback to determine_frequency for irregular intervals
                    frequency, frequency_label = determine_frequency(timestamps)
                    logger.debug(
                        f"Categorized irregular frequency: {frequency_label}",
                        alt=f"[bold]Categorized irregular frequency:[/bold] {frequency_label}",
                    )

                    return frequency, frequency_label

                except Exception as e:
                    logger.error(f"Error in irregular frequency determination: {e}")
                    return None, "Error in determining irregular frequency"

        except Exception as e:
            logger.error(f"Error in regular frequency determination: {e}")
            return None, "Error in determining regular frequency"
