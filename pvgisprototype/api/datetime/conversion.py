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
"""
Timestamp relevant conversions
"""

from pvgisprototype.log import logger
import time
import typer
from zoneinfo import ZoneInfo
from pandas import DatetimeIndex, Timestamp
from pvgisprototype.api.datetime.timezone import ZONEINFO_UTC


def convert_hours_to_datetime_time(value: float):
    if value < 0 or value > 24:
        raise typer.BadParameter(
            f"Value {value} is out of the expected range [0, 24] hours."
        )

    hours = int(value)
    minutes = int((value - hours) * 60)
    seconds = int(((value - hours) * 60 - minutes) * 60)

    return time(hours, minutes, seconds)


def convert_timestamps_to_utc(
    user_requested_timezone: ZoneInfo | None = None,
    user_requested_timestamps: Timestamp | DatetimeIndex | None = None,
) -> Timestamp | DatetimeIndex:
    """ """
    if user_requested_timestamps is None:
        user_requested_timestamps = Timestamp.now()

    logger.debug(
        f"Input time zone : {user_requested_timezone}",
        alt=f"Input time zone : [code]{user_requested_timezone}[/code]",
    )
    utc_timestamps = user_requested_timestamps  # Fallback if already UTC

    # naive timestamps
    if user_requested_timestamps.tz is None:
        utc_timestamps = user_requested_timestamps.tz_localize(ZONEINFO_UTC)
        logger.debug(
            f"Naive input timestamps\n({user_requested_timestamps})\nlocalized to UTC aware for all internal calculations :\n{utc_timestamps}"
        )

    # timezone aware timestamps
    elif user_requested_timestamps.tz != ZONEINFO_UTC:
        utc_timestamps = user_requested_timestamps.tz_convert(ZONEINFO_UTC)
        logger.debug(
            f"Input zone\n{user_requested_timezone}\n& timestamps :\n{user_requested_timestamps}\n\nconverted for all internal calculations to :\n{utc_timestamps}",
            alt=f"Input zone : [code]{user_requested_timezone}[/code]\n& timestamps :\n{user_requested_timestamps}\n\nconverted for all internal calculations to :\n{utc_timestamps}",
        )

    return utc_timestamps
