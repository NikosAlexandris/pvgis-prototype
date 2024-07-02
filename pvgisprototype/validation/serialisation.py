import json
from pandas import DatetimeIndex
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from pvgisprototype import (
        LinkeTurbidityFactor,
        SpectralFactorSeries,
        TemperatureSeries,
        WindSpeedSeries,
        )


class CustomEncoder(json.JSONEncoder):
    def default(self, object):
        if isinstance(object, (DatetimeIndex,
                               datetime,
                               ZoneInfo,
                               LinkeTurbidityFactor,
                               SpectralFactorSeries,
                               TemperatureSeries,
                               WindSpeedSeries,
                               Path,
                               )):
            return str(object)  # convert non-serializable objects to string
        return json.JSONEncoder.default(self, object)
