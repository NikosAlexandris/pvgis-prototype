"""
Timestamp relevant conversions
"""

import time
from datetime import datetime, timedelta
from typing import Sequence, Union
import typer
from numpy import ndarray, array


def convert_hours_to_datetime_time(value: float):
    if value < 0 or value > 24:
        raise typer.BadParameter(f'Value {value} is out of the expected range [0, 24] hours.')

    hours = int(value)
    minutes = int((value - hours) * 60)
    seconds = int(((value - hours) * 60 - minutes) * 60)

    return time(hours, minutes, seconds)
