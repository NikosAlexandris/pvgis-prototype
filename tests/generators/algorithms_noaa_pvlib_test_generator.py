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
import pandas as pd
from pvlib import solarposition
from pandas import DatetimeIndex, Timestamp
from zoneinfo import ZoneInfo
import math

data = pd.read_excel("../data/algorithms_NOAA.xlsx")

# Testing Event Time
cases = "NOAA vs PVlib (Solar Azimuth)"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_solar_azimuth_noaa_pvlib.py", "w") as file:
    file.write("from pandas import date_range\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from pvgisprototype import SolarAzimuth\n")
    file.write("from pvgisprototype import Longitude\n")
    file.write("from pvgisprototype import Latitude\n")
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from zoneinfo import ZoneInfo\n")
    file.write("from pvgisprototype import SurfaceTilt\n")
    file.write("from pvgisprototype import SurfaceOrientation\n")
    file.write("from pvgisprototype.constants import RADIANS\n")
    file.write("from pvgisprototype.constants import DATA_TYPE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT\n\n")
    file.write("cases = [\n")
    for _, row in data.iterrows():
        longitude = float(row["LONGITUDE [DEGREES]"])
        latitude = float(row["LATITUDE [DEGREES]"])
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        timestamp =  DatetimeIndex([Timestamp(year=year, month=month, day=day, hour=hour, minute=minutes, second=seconds)])
        solpos = solarposition.get_solarposition(timestamp, latitude, longitude)
        target = solpos.azimuth.iloc[0]

        longitude = float(row["LONGITUDE [RADIANS]"])
        latitude = float(row["LATITUDE [RADIANS]"])
        apply_atmospheric_refraction = bool(row["APPLY ATMOSPHERIC REFRACTION"])

        file.write("    ({\n")
        file.write(f"        \"longitude\": Longitude(value={longitude}, unit=RADIANS),\n")
        file.write(f"        \"latitude\": Latitude(value={latitude}, unit=RADIANS),\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write("        \"timezone\": ZoneInfo(\"UTC\"),\n")
        file.write(f"        \"apply_atmospheric_refraction\": {apply_atmospheric_refraction},\n")
        #file.write(f"        \"apply_atmospheric_refraction\": True,\n")
        file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
        file.write("        \"array_backend\": ARRAY_BACKEND_DEFAULT,\n")
        file.write("    },\n")
        file.write(f"     numpy_array([{round(target,3)}], dtype='float32')),\n")
    
    longitude = 8.628
    latitude = 45.812
    start_time = '2010-01-01 00:10:00'
    end_time = '2010-12-31 23:59:00'
    frequency = 'h'
    timestamps = pd.date_range(start_time, end_time, freq=frequency, tz=ZoneInfo("UTC"))
    solpos = solarposition.get_solarposition(timestamps, latitude, longitude)
    target = solpos.azimuth.values.tolist()
    
    file.write("    ({\n")
    file.write(f"        \"longitude\": Longitude(value={math.radians(longitude)}, unit=RADIANS),\n")
    file.write(f"        \"latitude\": Latitude(value={math.radians(latitude)}, unit=RADIANS),\n")
    file.write(f"        \"timestamps\": date_range('{start_time}', '{end_time}', freq='{frequency}', tz=ZoneInfo(\"UTC\")),\n")
    file.write("        \"timezone\": ZoneInfo(\"UTC\"),\n")
    file.write("        \"apply_atmospheric_refraction\": False,\n")
    #file.write(f"        \"apply_atmospheric_refraction\": True,\n")
    file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
    file.write("        \"array_backend\": ARRAY_BACKEND_DEFAULT,\n")
    file.write("    },\n")
    file.write(f"     numpy_array({[round(t,3) for t in target]}, dtype='float32')),\n")
    
    file.write("]\n")
    
    file.write("cases_ids = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        longitude = float(row["LONGITUDE [DEGREES]"])
        latitude = float(row["LATITUDE [DEGREES]"])

        file.write(f"    'Input vs PVLIB: Longitude:{longitude:.2f}, Latitude:{latitude:.2f}|{year}-{month}-{day} {hour}:{minutes}:{seconds}',\n")
    
    file.write(f"    'Input vs PVLIB: Longitude:{45.812}, Latitude:{8.628}|Start: {start_time}, End: {end_time}',\n")

    file.write("]\n")