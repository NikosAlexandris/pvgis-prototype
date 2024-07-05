import pandas as pd


data = pd.read_excel("../data/algorithms_NOAA.xlsx")

# Testing FRACTIONAL YEAR NOAA
cases = "Fractional Year NOAA"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_fractional_year.py", "w") as file:
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from pvgisprototype import FractionalYear\n")
    file.write("from pvgisprototype.constants import RADIANS\n\n")
    file.write("cases = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        fractional_year = float(row["FRACTIONAL YEAR [RADIANS]"])

        file.write("    ({\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write("    },\n")
        file.write(f"     FractionalYear(value=numpy_array([{round(fractional_year,3)}], dtype='float32'), unit=RADIANS)),\n")
    file.write("]\n")

    file.write("cases_ids = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])

        file.write(f"    'Input: {year}-{month}-{day} {hour}:{minutes}:{seconds}',\n")
    file.write("]\n")

# Testing EQUATION OF TIME NOAA
cases = "Equation of time NOAA"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_equation_of_time.py", "w") as file:
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from pvgisprototype import EquationOfTime\n")
    file.write("from pvgisprototype.constants import MINUTES\n\n")
    file.write("cases = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        target = float(row["EQUATION OF TIME [MINUTES]"])

        file.write("    ({\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write("    },\n")
        file.write(f"     EquationOfTime(value=numpy_array([{round(target,3)}], dtype='float32'), unit=MINUTES)),\n")
    file.write("]\n")

    file.write("cases_ids = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])

        file.write(f"    'Input: {year}-{month}-{day} {hour}:{minutes}:{seconds}',\n")
    file.write("]\n")


# Testing SOLAR DECLINATION
cases = "Solar declination NOAA"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_solar_declination.py", "w") as file:
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from pvgisprototype import SolarDeclination\n")
    file.write("from pvgisprototype.constants import DATA_TYPE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT\n")
    file.write("from pvgisprototype.constants import RADIANS\n\n")
    file.write("cases = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        target = float(row["SOLAR DECLINATION [RADIANS]"])

        file.write("    ({\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
        file.write("        \"array_backend\": ARRAY_BACKEND_DEFAULT,\n")
        file.write("    },\n")
        file.write(f"     SolarDeclination(value=numpy_array([{round(target,3)}], dtype='float32'), unit=RADIANS)),\n")
    file.write("]\n")

    file.write("cases_ids = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        file.write(f"    'Input: {year}-{month}-{day} {hour}:{minutes}:{seconds}',\n")
    file.write("]\n")

# Testing Time offset
cases = "Time offset NOAA"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_time_offset.py", "w") as file:
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from zoneinfo import ZoneInfo\n")
    file.write("from math import radians\n")
    file.write("from pvgisprototype import TimeOffset\n")
    file.write("from pvgisprototype.constants import DATA_TYPE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT\n")
    file.write("from pvgisprototype import Longitude\n")
    file.write("from pvgisprototype import TimeOffset\n")
    file.write("from pvgisprototype.constants import RADIANS\n")
    file.write("from pvgisprototype.constants import MINUTES\n\n")

    file.write("cases = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        longitude = float(row["LONGITUDE [DEGREES]"])
        target = float(row["TIME OFFSET [MINUTES]"])

        file.write("    ({\n")
        file.write(f"        \"longitude\": Longitude(value=radians({longitude}), unit=RADIANS),\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write("        \"timezone\": ZoneInfo(\"UTC\"),\n")
        file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
        file.write("        \"array_backend\": ARRAY_BACKEND_DEFAULT,\n")
        file.write("    },\n")
        file.write(f"     TimeOffset(value=numpy_array([{round(target,3)}], dtype='float32'), unit=MINUTES)),\n")
    file.write("]\n")

    file.write("cases_ids = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        file.write(f"    'Input: {year}-{month}-{day} {hour}:{minutes}:{seconds}',\n")
    file.write("]\n")

# Testing True solar time
cases = "True solar time NOAA"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_true_solar_time.py", "w") as file:
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from zoneinfo import ZoneInfo\n")
    file.write("from math import radians\n")
    file.write("from pvgisprototype import TrueSolarTime\n")
    file.write("from pvgisprototype.constants import DATA_TYPE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT\n")
    file.write("from pvgisprototype import Longitude\n")
    file.write("from pvgisprototype.constants import RADIANS\n")
    file.write("from pvgisprototype.constants import MINUTES\n\n")

    file.write("cases = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        longitude = float(row["LONGITUDE [DEGREES]"])
        target = float(row["TRUE SOLAR TIME [MINUTES]"])

        file.write("    ({\n")
        file.write(f"        \"longitude\": Longitude(value=radians({longitude}), unit=RADIANS),\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write("        \"timezone\": ZoneInfo(\"UTC\"),\n")
        file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
        file.write("        \"array_backend\": ARRAY_BACKEND_DEFAULT,\n")
        file.write("    },\n")
        file.write(f"     TrueSolarTime(value=numpy_array([{round(target,3)}], dtype='float32'), unit=MINUTES)),\n")
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
        file.write(f"    'Input: Longitude:{longitude:.2f}_{year}-{month}-{day} {hour}:{minutes}:{seconds}',\n")
    file.write("]\n")


# Testing Solar Hour Angle
cases = "Solar Hour Angle NOAA"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_solar_hour_angle.py", "w") as file:
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from zoneinfo import ZoneInfo\n")
    file.write("from math import radians\n")
    file.write("from pvgisprototype import SolarHourAngle\n")
    file.write("from pvgisprototype.constants import DATA_TYPE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT\n")
    file.write("from pvgisprototype import Longitude\n")
    file.write("from pvgisprototype.constants import RADIANS\n")
    file.write("from pvgisprototype.constants import MINUTES\n\n")

    file.write("cases = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        longitude = float(row["LONGITUDE [DEGREES]"])
        target = float(row["SOLAR HOUR ANGLE [RADIANS]"])

        file.write("    ({\n")
        file.write(f"        \"longitude\": Longitude(value=radians({longitude}), unit=RADIANS),\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write("        \"timezone\": ZoneInfo(\"UTC\"),\n")
        file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
        file.write("        \"array_backend\": ARRAY_BACKEND_DEFAULT,\n")
        file.write("    },\n")
        file.write(f"     SolarHourAngle(value=numpy_array([{round(target, 3)}], dtype='float32'), unit=RADIANS)),\n")
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
        file.write(f"    'Input: Longitude:{longitude:.2f}_{year}-{month}-{day} {hour}:{minutes}:{seconds}',\n")
    file.write("]\n")

# Testing Solar Zenith Angle
cases = "Solar Zenith NOAA"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_solar_zenith.py", "w") as file:
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from math import radians\n")
    file.write("from zoneinfo import ZoneInfo\n")
    file.write("from pvgisprototype import SolarHourAngle\n")
    file.write("from pvgisprototype import SolarZenith\n")
    file.write("from pvgisprototype.constants import DATA_TYPE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT\n")
    file.write("from pvgisprototype import Latitude\n")
    file.write("from pvgisprototype import Longitude\n")
    file.write("from pvgisprototype.constants import RADIANS\n")
    file.write("from pvgisprototype.constants import MINUTES\n\n")

    file.write("cases = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        latitude = float(row["LATITUDE [DEGREES]"])
        longitude = float(row["LONGITUDE [DEGREES]"])
        solar_hour_angle = float(row["SOLAR HOUR ANGLE [RADIANS]"])
        apply_atmospheric_refraction = bool(row["APPLY ATMOSPHERIC REFRACTION"])
        target = float(row["SOLAR ZENITH [RADIANS]"])

        file.write("    ({\n")
        file.write(f"        \"longitude\": Longitude(value=radians({longitude}), unit=RADIANS),\n")
        file.write(f"        \"latitude\": Latitude(value=radians({latitude}), unit=RADIANS),\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write("        \"timezone\": ZoneInfo(\"UTC\"),\n")
        file.write(f"        \"solar_hour_angle_series\": SolarHourAngle(value={solar_hour_angle}, unit=RADIANS),\n")
        file.write(f"        \"apply_atmospheric_refraction\": {apply_atmospheric_refraction},\n")
        file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
        file.write("        \"array_backend\": ARRAY_BACKEND_DEFAULT,\n")
        file.write("    },\n")
        file.write(f"     SolarZenith(value=numpy_array([{round(target,3)}], dtype='float32'), unit=RADIANS)),\n")
    file.write("]\n")

    file.write("cases_ids = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        latitude = float(row["LATITUDE [DEGREES]"])
        file.write(f"    'Input: Latitude:{latitude:.2f}_{year}-{month}-{day} {hour}:{minutes}:{seconds}',\n")
    file.write("]\n")

# Testing Solar Altitude Angle
cases = "Solar Altitude NOAA"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_solar_altitude.py", "w") as file:
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from math import radians\n")
    file.write("from zoneinfo import ZoneInfo\n")
    file.write("from pvgisprototype import SolarAltitude\n")
    file.write("from pvgisprototype.constants import DATA_TYPE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT\n")
    file.write("from pvgisprototype import Latitude\n")
    file.write("from pvgisprototype import Longitude\n")
    file.write("from pvgisprototype.constants import RADIANS\n")
    file.write("from pvgisprototype.constants import MINUTES\n\n")

    file.write("cases = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        latitude = float(row["LATITUDE [DEGREES]"])
        longitude = float(row["LONGITUDE [DEGREES]"])
        apply_atmospheric_refraction = bool(row["APPLY ATMOSPHERIC REFRACTION"])
        timezone = str(row["TIMEZONE"])
        target = float(row["SOLAR ALTITUDE [RADIANS]"])

        file.write("    ({\n")
        file.write(f"        \"longitude\": Longitude(value=radians({longitude}), unit=RADIANS),\n")
        file.write(f"        \"latitude\": Latitude(value=radians({latitude}), unit=RADIANS),\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write(f"        \"timezone\": ZoneInfo('{timezone}'),\n")
        file.write(f"        \"apply_atmospheric_refraction\": {apply_atmospheric_refraction},\n")
        file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
        file.write("        \"array_backend\": ARRAY_BACKEND_DEFAULT,\n")
        file.write("    },\n")
        file.write(f"     SolarAltitude(value=numpy_array([{round(target, 3)}], dtype='float32'), unit=RADIANS)),\n")
    file.write("]\n")

    file.write("cases_ids = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        latitude = float(row["LATITUDE [DEGREES]"])
        longitude = float(row["LONGITUDE [DEGREES]"])
        file.write(f"    'Input: Latitude,Longitude:{latitude:.2f}-{longitude:.2f}_{year}-{month}-{day}T{hour}:{minutes}:{seconds}',\n")
    file.write("]\n")

# Testing Solar Azimuth Angle
cases = "Solar Azimuth NOAA"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_solar_azimuth.py", "w") as file:
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from math import radians\n")
    file.write("from zoneinfo import ZoneInfo\n")
    file.write("from pvgisprototype import SolarAzimuth\n")
    file.write("from pvgisprototype.constants import DATA_TYPE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT\n")
    file.write("from pvgisprototype import Latitude\n")
    file.write("from pvgisprototype import Longitude\n")
    file.write("from pvgisprototype.constants import RADIANS\n")
    file.write("from pvgisprototype.constants import MINUTES\n\n")

    file.write("cases = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        latitude = float(row["LATITUDE [RADIANS]"])
        longitude = float(row["LONGITUDE [RADIANS]"])
        apply_atmospheric_refraction = bool(row["APPLY ATMOSPHERIC REFRACTION"])
        timezone = str(row["TIMEZONE"])
        target = float(row["SOLAR AZIMUTH [RADIANS]"])

        file.write("    ({\n")
        file.write(f"        \"longitude\": Longitude(value={round(longitude,4)}, unit=RADIANS),\n")
        file.write(f"        \"latitude\": Latitude(value={round(latitude, 4)} , unit=RADIANS),\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write(f"        \"timezone\": ZoneInfo('{timezone}'),\n")
        file.write(f"        \"apply_atmospheric_refraction\": {apply_atmospheric_refraction},\n")
        file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
        file.write("        \"array_backend\": 'ARRAY_BACKEND_DEFAULT',\n")
        file.write("        \"verbose\": 0,\n")
        file.write("        \"log\": 0,\n")
        file.write("    },\n")
        file.write(f"     SolarAzimuth(value=numpy_array([{round(target,2)}], dtype='float32'), unit=RADIANS)),\n")
    file.write("]\n")

    file.write("cases_ids = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        latitude = float(row["LATITUDE [DEGREES]"])
        longitude = float(row["LONGITUDE [DEGREES]"])

        file.write(f"    'Input: Latitude,Longitude:{latitude:.2f}-{longitude:.2f}_{year}-{month}-{day}T{hour}:{minutes}:{seconds}',\n")
    file.write("]\n")


# Testing Solar Position
cases = "Solar Position NOAA"
print(f"-> Generating cases for module: {cases}")

with open("../algorithms/noaa/cases/cases_solar_azimuth.py", "w") as file:
    file.write("from pandas import DatetimeIndex, Timestamp\n")
    file.write("from numpy import array as numpy_array\n\n")
    file.write("from math import radians\n")
    file.write("from zoneinfo import ZoneInfo\n")
    file.write("from pvgisprototype import SolarAzimuth\n")
    file.write("from pvgisprototype.constants import DATA_TYPE_DEFAULT\n")
    file.write("from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT\n")
    file.write("from pvgisprototype import Latitude\n")
    file.write("from pvgisprototype import Longitude\n")
    file.write("from pvgisprototype.constants import RADIANS\n")
    file.write("from pvgisprototype.constants import MINUTES\n\n")

    file.write("cases = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        latitude = float(row["LATITUDE [RADIANS]"])
        longitude = float(row["LONGITUDE [RADIANS]"])
        apply_atmospheric_refraction = bool(row["APPLY ATMOSPHERIC REFRACTION"])
        timezone = str(row["TIMEZONE"])
        target = float(row["SOLAR AZIMUTH [RADIANS]"])

        file.write("    ({\n")
        file.write(f"        \"longitude\": Longitude(value={round(longitude,4)}, unit=RADIANS),\n")
        file.write(f"        \"latitude\": Latitude(value={round(latitude, 4)} , unit=RADIANS),\n")
        file.write(f"        \"timestamps\": DatetimeIndex([Timestamp(year={year}, month={month}, day={day}, hour={hour}, minute={minutes}, second={seconds})]),\n")
        file.write(f"        \"timezone\": ZoneInfo('{timezone}'),\n")
        file.write(f"        \"apply_atmospheric_refraction\": {apply_atmospheric_refraction},\n")
        file.write("        \"dtype\": DATA_TYPE_DEFAULT,\n")
        file.write("        \"array_backend\": 'ARRAY_BACKEND_DEFAULT',\n")
        file.write("        \"verbose\": 0,\n")
        file.write("        \"log\": 0,\n")
        file.write("    },\n")
        file.write(f"     SolarAzimuth(value=numpy_array([{round(target,2)}], dtype='float32'), unit=RADIANS)),\n")
    file.write("]\n")

    file.write("cases_ids = [\n")
    for _, row in data.iterrows():
        year = int(row["YEAR"])
        month = int(row["MONTH"])
        day = int(row["DAY"])
        hour = int(row["HOUR"])
        minutes = int(row["MINUTES"])
        seconds = int(row["SECONDS"])
        latitude = float(row["LATITUDE [DEGREES]"])
        longitude = float(row["LONGITUDE [DEGREES]"])

        file.write(f"    'Input: Latitude,Longitude:{latitude:.2f}-{longitude:.2f}_{year}-{month}-{day}T{hour}:{minutes}:{seconds}',\n")
    file.write("]\n")
