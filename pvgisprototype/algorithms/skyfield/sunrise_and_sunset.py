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
Source: https://techoverflow.net/2022/06/19/how-to-compute-sunrise-sunset-in-python-using-skyfield/
"""

from datetime import datetime, timedelta

import dateutil.parser
from skyfield import almanac, api

# from calendar import monthrange


ts = api.load.timescale()
ephemeris = api.load_file("de413.bsp")


def calculate_sunrise_sunset(location, year=2019, month=1, day=1):
    t0 = ts.utc(year, month, day, 0)
    # t1 = t0 plus one day
    t1 = ts.utc(t0.utc_datetime() + timedelta(days=1))
    t, y = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(ephemeris, location))
    sunrise = None
    sunset = None
    for time, is_sunrise in zip(t, y):
        if is_sunrise:
            sunrise = dateutil.parser.parse(time.utc_iso())
        else:
            sunset = dateutil.parser.parse(time.utc_iso())
    return sunrise, sunset


# Compute sunrise & sunset for random location near Munich
location = api.Topos("48.324777 N", "11.405610 E", elevation_m=519)
now = datetime.now()
sunrise, sunset = calculate_sunrise_sunset(location, now.year, now.month, now.day)


# Print result (example)
print(f"Sunrise today: {sunrise}")
print(f"Sunset today: {sunset}")
