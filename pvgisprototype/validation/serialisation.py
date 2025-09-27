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
