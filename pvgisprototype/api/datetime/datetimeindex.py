"""
Date, time and zones
--------------------

By default, input timestamps will default to the Coordinated Universal Time
(UTC) unless a user explicitly requests another or the system's local time and
zone. Regardless, all timestamps will convert internally to UTC. The rationale
behind this design decision is:

- UTC provides an unambiguous reference point as it does not observe Daylight
Saving Time (DST) which may bring in various complexities.

- UTC is a standard used worldwide, making it a safer choice for
interoperability.

- Using UTC can avoid issues when a server/system's local time zone may not be
  under control.

- While the software allows users to to specify their time zone if they wish,
  internally all timestamps will convert to UTC internally and only convert
  back to the user's time zone when displaying the time to the user.


Things to keep in mind:

> From: https://blog.ganssle.io/articles/2022/04/naive-local-datetimes.html

- The local offset may change during the course of the interpreter run.

- You can use datetime.astimezone with None to convert a naïve time into an
  aware datetime with a fixed offset representing the current system local
  time.

- All arithmetic operations should be applied to naïve datetimes when working
  in system local civil time — only call .astimezone(None) when you need to
  represent an absolute time, e.g. for display or comparison with aware
  datetimes.[3]


Read also:

- https://peps.python.org/pep-0615/
"""

from pathlib import Path
from pandas import DatetimeIndex, Timestamp, date_range

from pvgisprototype.constants import TIMESTAMPS_FREQUENCY_DEFAULT
from pvgisprototype.log import logger
from pvgisprototype.api.series.utilities import read_data_array_or_set


def parse_timestamp_series(
    timestamps: str,
) -> "DatetimeIndex | Timestamp | None":
    """
    Parse an input of type string and generate a Pandas Timestamp or
    DatetimeIndex [1]_.

    either `str`ings or `datetime.datetime` objects and generate a NumPy
    datetime64 array [1]_

    Parameters
    ----------
    timestamps : `str`
            A single `str`ing (i.e. '2111-11-11' or '2121-12-12 12:12:12')

    Returns
    -------
    timestamps :
        Pandas Timestamp or DatetimeIndex

    Notes
    -----
    .. [1] https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Timestamp.html#pandas-timestamp
    .. [2] https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html
    """
    from pandas import to_datetime

    if isinstance(timestamps, str):
        # return to_datetime(timestamps.split(','), format='mixed', utc=True)
        return to_datetime(timestamps.split(","), format="mixed")
    else:
        raise ValueError(
            "The `timestamps` input must be a string of datetime or datetimes separated by comma as expected by Pandas `to_datetime()` function"
        )


def generate_datetime_series(
    start_time: str | None = None,
    end_time: str | None = None,
    periods: str | None = None,
    frequency: str | None = TIMESTAMPS_FREQUENCY_DEFAULT,
    timezone: str | None = None,
    name: str | None = None,
) -> DatetimeIndex:
    """Generate a fixed frequency DatetimeIndex

    Generates a range of equally spaced timestamps wrapping over Pandas'
    date_range() function. The timestamps satisfy `start_time <[=] x <[=]
    end_time`, where the first and last stamps fall on the boundary of the
    requested ``frequency`` string. The difference between any two timestamps
    is specified by the requested ``frequency``.

    If exactly one of ``start_time``, ``end_time``, or ``frequency`` is *not*
    specified, it can be computed by the ``periods``, the number of timesteps
    in the range.

    Parameters
    ----------
    start_time : str, datetime, date, pandas.Timestamp, or period-like, default None
        The starting time (if str in ISO format), also described as the left
        bound for generating periods.
    end_time : str, datetime, date, pandas.Timestamp, or period-like, default None
        The ending time in ISO format. In Pandas described as the right bound
        for generating periods.
    periods : int, default None
        Number of periods to generate.
    frequency : str or DateOffset, optional
        Frequency alias of the timestamps to generate, e.g., 'h' for hourly.
        By default the frequency is taken from start_time or
        end_time if those are Period objects. Otherwise, the default is "h" for
        hourly frequency.
    name : str, default None
        Name of the resulting PeriodIndex.

    Returns
    -------
    DatetimeIndex
        A Pandas DatetimeIndex at the specified frequency.

    See Also
    --------
    pandas.date_range
        Return a fixed frequency DatetimeIndex.

    Notes
    -----
    Of the four parameters ``start_time``, ``end_time``, ``periods``, and
    ``frequency``, exactly three must be specified. If ``frequency`` is
    omitted, the resulting ``DatetimeIndex`` will have ``periods`` linearly
    spaced elements between ``start`` and ``end`` (closed on both sides).

    Common time series frequencies are indexed via a set of string (also
    referred to as offset) aliases described at
    <https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`__.

    Example
    -------
    >>> start_time = '2010-06-01 06:00:00'
    >>> end_time = '2010-06-01 08:00:00'
    >>> frequency = 'h'  # 'h' for hourly
    >>> generate_datetime_series(start_time, end_time, frequency)
    DatetimeIndex(['2010-06-01 06:00:00', '2010-06-01 07:00:00', '2010-06-01 08:00:00'], dtype='datetime64[ns]', freq=None)

    Using the periods input parameter to define the number of timesteps to generate :

    >>> generate_datetime_series(start_time=start_time, periods=4, frequency=frequency)
    DatetimeIndex(['2010-06-01 06:00:00', '2010-06-01 07:00:00',
               '2010-06-01 08:00:00', '2010-06-01 09:00:00'],
              dtype='datetime64[ns]', freq='H')
    """
    # Validate input parameters --
    # Can we do this with a callback and at the Context level ?
    number_of_parameters = sum(
        parameter is not None for parameter in [start_time, end_time, periods]
    )
    if number_of_parameters < 2:
        error_message = (
            f"Insufficient parameters to generate timestamps. "
            f"User input is : start_time={start_time}, end_time={end_time}, periods={periods}. "
            f"At least two of these must be non-null!"
        )
        logger.error(error_message)
        raise ValueError(error_message)

    try:
        timestamps = date_range(
            start=start_time,
            end=end_time,
            periods=periods,
            freq=frequency,
            tz=timezone,
            name=name,
        )
    except Exception as e:
        logger.exception("Failed to generate datetime series.")
        raise ValueError(f"Failed to generate datetime series: {str(e)}")

    if timestamps.empty:
        error_message = "The generated DatetimeIndex is empty! You might want to check the relevant timestamp parameters for accuracy."
        logger.error(error_message)
        raise ValueError(error_message)

    return timestamps


def generate_timestamps(
    data_file: Path,
    start_time: str | None = None,
    end_time: str | None = None,
    periods: str | None = None,
    frequency: str | None = TIMESTAMPS_FREQUENCY_DEFAULT,
    timezone: str | None = None,
    name: str | None = None,
):
    """
    """
    # Extract timestamps from first available space-time data file
    if data_file:
        timestamps = read_data_array_or_set(data_file).time

        # Implement Me ? --------------------------------------------------- #
        #                                                                    #

        # if check_for_duplicate_timestamps:
        #     if timestamps.indexes['time'].duplicated().any():
        #         logger.error(
        #                 f"Duplicate timestamps detected.",
        #                 alt= f"[red]Duplicate timestamps detected![/red]"
        #                 )

        #                                                                    #
        # ----------------------------------------------------- Implement Me #

        logger.info(
                f"Timestamps retrieved from {data_file} :\n{timestamps}",
                alt=f"Timestamps retrieved from [code]{data_file}[/code] :\n{timestamps}"
                )

        if timestamps is None:
            logger.error(
                    "No timestamps found in the provided data file!",
                    alt="[red]No timestamps found in the provided data file![/red]",
                    )
            raise ValueError("Unable to extract timestamps from the data file.")
        
        # Filter timestamps based on start_time and end_time
        if start_time or end_time:
            logger.info(
                    f"Slice timestamps from {start_time} to {end_time}",
                    alt=f"Slice timestamps from {start_time} to {end_time}"
                    )
            timestamps = timestamps.sel(time=slice(start_time, end_time))
            logger.info(
                    f"Sliced timestamps :\n{timestamps}",
                    alt=f"[bold]Sliced timestamps[/bold] :\n{timestamps}"
                    )

        if start_time and periods and not end_time:
            if frequency:
                timestamps = timestamps.resample(time=frequency).nearest()
            timestamps = timestamps.isel(time=slice(0, periods))

        elif end_time and periods and not start_time:
            if frequency:
                timestamps = timestamps.resample(time=frequency).nearest()
            timestamps = timestamps.isel(time=slice(-periods, None))

        elif start_time and end_time and periods:
            logger.error(
                    f"Best if you provide a `start_time` OR an `end_time` along with `periods`, not both!",
                    alt=f"[bold]Best if you provide a[/bold] `start_time` [bold][italics yellow]or[/italics yellow] an[/bold] `end_time` [bold]along with[/bold] `periods`, [bold red]not both![/bold red]"
                    )
            raise ValueError("Best if you provide a `start_time` or an `end_time` along with `periods`, not both! Else, I cannot decide which periods to return, from the start or the the end.. ;-?")

        elif frequency and not periods and (start_time or end_time):
            # resampled_timestamps = DatetimeIndex(
            #     timestamps.resample(time=frequency).nearest()
            # )
            # resampled_timestamps.intersection(timestamps)
            # logger.info(
            #     f"Resampled timestamps at frequency = {frequency} :\n{timestamps}",
            #     alt=f"Resampled timestamps at frequency = {frequency} :\n{timestamps}",
            # )
            logger.warning(
                    f"Resampling the timestamps retrieved from the data would eventually introduce new timestamps! Skipping...",
                    alt=f"[bold red]Resampling the timestamps retrieved from the data would eventually introduce new timestamps! Skipping...[/bold red]"
                    )

        return DatetimeIndex(timestamps)

    else:
        timestamps = generate_datetime_series(
            start_time=start_time,
            end_time=end_time,
            periods=periods,
            frequency=frequency,
            timezone=timezone,
            name=name,
        )
        # from pandas import to_datetime
        # -----------------------------------------------------------------------
        # If we do the following, we need to take care of external naive time series!
        # timezone_aware_timestamps = [
        #     attach_requested_timezone(timestamp, timezone) for timestamp in timestamps
        # ]
        # return to_datetime(timezone_aware_timestamps, format="mixed")
        # -----------------------------------------------------------------------
        return timestamps
