from pvgisprototype.log import logger
from pandas import DatetimeIndex
from pvgisprototype.constants import LATITUDE_COLUMN_NAME, LONGITUDE_COLUMN_NAME, NOT_AVAILABLE, SURFACE_ORIENTATION_NAME, SURFACE_TILT_NAME, TIME_ALGORITHM_NAME, UNIT_NAME, UNITLESS
from zoneinfo import ZoneInfo
import numpy


def build_caption(
    longitude,
    latitude,
    rounded_table,
    timezone,
    user_requested_timezone,
    minimum_value = None,
    maximum_value = None,
):
    """
    Notes
    -----
    Add the surface orientation and tilt only if they exist in the input
    `rounded_table` !

    """
    first_model = next(iter(rounded_table))
    caption = (
        f"[underline]Position[/underline]  "
        f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold], "
        + (
            f"Orientation : [bold blue]{rounded_table[first_model].get(SURFACE_ORIENTATION_NAME)}[/bold blue], "
            if rounded_table[first_model].get(SURFACE_ORIENTATION_NAME) is not None
            else ""
        )
        + (
            f"Tilt : [bold blue]{rounded_table[first_model].get(SURFACE_TILT_NAME)}[/bold blue] "
            if rounded_table[first_model].get(SURFACE_TILT_NAME) is not None
            else ""
        )
        + f"[dim]{rounded_table[first_model].get(UNIT_NAME, UNITLESS)}[/dim]"
        f"\n[underline]Algorithms[/underline]  "  # ---------------------------
        f"Timing : [bold]{rounded_table[first_model].get(TIME_ALGORITHM_NAME, NOT_AVAILABLE)}[/bold], "
    )
        # f"Positioning: {rounded_table[first_model].get(POSITIONING_ALGORITHM_NAME, NOT_AVAILABLE)}, "
        # f"Incidence: {rounded_table[first_model].get(INCIDENCE_ALGORITHM_NAME, NOT_AVAILABLE)}\n"
        # f"[underline]Definitions[/underline]  "
        # f"Azimuth origin: {rounded_table[first_model].get(AZIMUTH_ORIGIN_NAME, NOT_AVAILABLE)}, "
        # f"Incidence angle: {rounded_table[first_model].get(INCIDENCE_DEFINITION, NOT_AVAILABLE)}\n"

    if user_requested_timezone != ZoneInfo('UTC'):
        caption += f"Local Zone : [bold]{user_requested_timezone}[/bold], "
    else:
        caption += f"Zone : [bold]{timezone}[/bold], "

    if minimum_value:
        caption += f"Minimum : {minimum_value}"

    if maximum_value:
        caption += f"Minimum : {maximum_value}"

    return caption


def get_value_or_default(
        dictionary: dict,
        key: str,
        default: str | None = NOT_AVAILABLE
):
    """Get a value from a dictionary or return a default value"""
    return dictionary.get(key, default)


def determine_frequency(timestamps):
    """ """
    # single timestamp ?
    if len(timestamps) == 1:
        return 'Single', 'Single Timestamp'

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
    elif timestamps.to_period().week.unique().size > 1:
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
        logger.info(
            f"Regular intervals detected: {timestamps.freqstr}",
            alt=f"[bold]Regular intervals detected:[/bold] {timestamps.freqstr}"
        )
        return timestamps.freqstr, f"{timestamps.freqstr}"
    
    else:
        try:
            # Calculate time differences directly with NumPy for regular intervals
            time_deltas = numpy.diff(timestamps).astype('timedelta64[ns]')
            
            # Find the most frequent time delta using numpy.unique
            unique_deltas, counts = numpy.unique(time_deltas, return_counts=True)
            frequency = unique_deltas[numpy.argmax(counts)]
            logger.info(
                f"Inferred frequency of timestamps: {frequency}",
                alt=f"[bold]Inferred frequency of timestamps:[/bold] {frequency}"
            )

            # Calculate the total duration : end - start
            total_duration = (timestamps[-1] - timestamps[0]).astype('timedelta64[ns]')

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
                    logger.info(
                        f"Categorized irregular frequency: {frequency_label}",
                        alt=f"[bold]Categorized irregular frequency:[/bold] {frequency_label}"
                    )

                    return frequency, frequency_label

                except Exception as e:
                    logger.error(f"Error in irregular frequency determination: {e}")
                    return None, "Error in determining irregular frequency"

        except Exception as e:
            logger.error(f"Error in regular frequency determination: {e}")
            return None, "Error in determining regular frequency"
