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


data = pd.read_excel("../data/algorithms_NOAA.xlsx")

# Testing Solar Incidence JENCO
cases = "Solar Incidence IQBAL"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/iqbal/cases/cases_solar_incidence_iqbal.py", "w") as file:
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from pvgisprototype import SolarIncidence\n")
    file.write("from pvgisprototype import Longitude\n")
    file.write("from pvgisprototype import Latitude\n")
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from zoneinfo import ZoneInfo\n")
    file.write("from pvgisprototype import SurfaceTilt\n")
    file.write("from pvgisprototype import SurfaceOrientation\n")
    file.write("from pvgisprototype.constants import RADIANS\n")
    file.write("from pvgisprototype.constants import DATA_TYPE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT\n\n")
    file.write("cases = [\n")
    for _, row in data.iterrows():
        longitude = float(row["LONGITUDE [RADIANS]"])
        latitude = float(row["LATITUDE [RADIANS]"])
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        surface_orientation = float(row["ORIENTATION [RADIANS]"])
        surface_tilt = float(row["TILT [RADIANS]"])
        target = float(row["SOLAR INCIDENCE [RADIANS] (IQBAL)"])

        file.write("    ({\n")
        file.write(f"        \"longitude\": Longitude(value={longitude}, unit=RADIANS),\n")
        file.write(f"        \"latitude\": Latitude(value={latitude}, unit=RADIANS),\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write("        \"timezone\": ZoneInfo(\"UTC\"),\n")
        file.write(f"        \"surface_orientation\": SurfaceOrientation(value={surface_orientation}, unit=RADIANS),\n")
        file.write(f"        \"surface_tilt\": SurfaceTilt(value={surface_tilt}, unit=RADIANS),\n")
        file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
        file.write("        \"array_backend\": ARRAY_BACKEND_DEFAULT,\n")
        file.write("    },\n")
        file.write(f"     SolarIncidence(value=numpy_array([{round(target,3)}], dtype='float32'), unit=RADIANS)),\n")
        
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
        surface_orientation = float(row["ORIENTATION [DEGREES]"])
        surface_tilt = float(row["TILT [DEGREES]"])

        file.write(f"    'Input: Longitude:{longitude:.2f} Latitude:{latitude:.2f}-{surface_orientation}-{surface_tilt}_{year}-{month}-{day} {hour}:{minutes}:{seconds}',\n")
    file.write("]\n")