import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pandas import DatetimeIndex

from pvgisprototype import (
    LinkeTurbidityFactor,
    SpectralFactorSeries,
    TemperatureSeries,
    WindSpeedSeries,
)


class CustomEncoder(json.JSONEncoder):
    def default(self, object):
        if isinstance(
            object,
            (
                DatetimeIndex,
                datetime,
                ZoneInfo,
                LinkeTurbidityFactor,
                SpectralFactorSeries,
                TemperatureSeries,
                WindSpeedSeries,
                Path,
            ),
        ):
            return str(object)  # convert non-serializable objects to string
        return json.JSONEncoder.default(self, object)
