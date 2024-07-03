from pvgisprototype import (TemperatureSeries, WindSpeedSeries, SpectralFactorSeries, LinkeTurbidityFactor,
                             Longitude, Latitude, SurfaceTilt,
                            )
from pvgisprototype.api.utilities.timestamp import generate_datetime_series
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from zoneinfo import ZoneInfo
import random
from pvgisprototype.api.surface.optimize_angles import optimize_angles
from pvgisprototype.api.surface.helper_functions import (OptimizerMethod, OptimizerMode)
#from tests.algorithms.optimization.helper_functions import generate_random_date
import datetime

def generate_random_date():
    date = datetime.datetime(
        random.randrange(2010, 2023),
        random.randrange(1, 12),
        random.randrange(1, 28),
        00,00)
    return date              

def write_header_cases():

    header =("import random \n")
    header +=("import datetime \n")
    header +=("from zoneinfo import ZoneInfo\n")
    header +=("from pvgisprototype.api.utilities.timestamp import generate_datetime_series \n")
    header +=("from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel\n")
    header +=("from pvgisprototype import (\n")
    header +=("    Longitude, Latitude, Elevation,\n")
    header +=("    TemperatureSeries, WindSpeedSeries,\n")
    header +=("    LinkeTurbidityFactor, SpectralFactorSeries,\n")
    header +=("    SurfaceOrientation, SurfaceTilt,\n")
    header +=("    )\n")
    header +=("from pvgisprototype.api.surface.optimize_angles import optimize_angles \n")
    header +=("from pvgisprototype.api.surface.helper_functions import OptimizerMethod, OptimizerMode\n\n")

    with open('cases_optimizer_orientation.py', 'w') as fp:
        fp.write(header)


def write_cases_optimizer_orientation(number_of_cases):

    cases = ("cases = [ \n")

    for i in range(0,number_of_cases):
        longitude_value = random.uniform(-180,180)
        latitude_value = random.uniform(-90,90)
        elevation_value = random.randrange(0,100)
        start_time,end_time=generate_random_date(),generate_random_date()
        if start_time > end_time:
           start_time, end_time = end_time, start_time
        temperature_value=random.uniform(0,35)
        wind_value=random.uniform(0,15)
        surface_tilt_value=random.uniform(0,SurfaceTilt().max_radians)
        sampling_method_shgo = 'sobol'

        result=optimize_angles(longitude = Longitude(value=longitude_value, unit='degrees'),
                                latitude = Latitude(value=latitude_value, unit='degrees'),
                                elevation = elevation_value, #Elevation(value=random.randrange(0,100), unit = 'meters'),
                                timestamps = generate_datetime_series(start_time=str(start_time), end_time=str(end_time), frequency="h"),
                                timezone = ZoneInfo("UTC"),
                                spectral_factor_series = SpectralFactorSeries(value=1),
                                photovoltaic_module = PhotovoltaicModuleModel.CIS_FREE_STANDING,
                                temperature_series = TemperatureSeries(value=temperature_value),
                                wind_speed_series = WindSpeedSeries(value=wind_value),
                                linke_turbidity_factor_series = LinkeTurbidityFactor(value=1),
                                method=OptimizerMethod.brute, 
                                mode = OptimizerMode.orientation,
                                surface_tilt = SurfaceTilt(value=(surface_tilt_value), unit='radians'),
                                workers=-1,
                                )
        cases +=("({")
        cases +=("'longitude': Longitude(value="+str(longitude_value)+", unit='degrees'),\n")
        cases +=("'latitude': Latitude(value="+str(latitude_value)+", unit='degrees'),\n")
        cases +=("'elevation':"+str(elevation_value)+",\n")
        cases +=("'timestamps': generate_datetime_series(start_time='"+str(start_time)+"', end_time='"+str(end_time)+"', frequency='h'),")
        cases +=("'timezone': ZoneInfo('UTC'),\n")
        cases +=("'spectral_factor_series': SpectralFactorSeries(value=1),\n")
        cases +=("'photovoltaic_module': PhotovoltaicModuleModel.CIS_FREE_STANDING,\n")
        cases +=("'temperature_series': TemperatureSeries(value="+str(temperature_value)+"),\n")
        cases +=("'wind_speed_series': WindSpeedSeries(value="+str(wind_value)+"),\n")
        cases +=("'linke_turbidity_factor_series': LinkeTurbidityFactor(value=1),\n")
        cases +=("'method': OptimizerMethod.shgo, \n")
        cases +=("'mode':OptimizerMode.orientation, \n")
        cases +=("'surface_tilt': SurfaceTilt(value="+str(surface_tilt_value)+", unit='radians'),\n")
        cases +=("'workers': -1,\n")
        cases +=("'sampling_method_shgo':'"+str(sampling_method_shgo)+"',\n")
        cases +=("},\n")
        cases +=(str(result)+"),\n")

    cases += ("]\n")
    with open('cases_optimizer_orientation.py', 'a') as fp:
        fp.write(cases)

write_header_cases()
write_cases_optimizer_orientation(2)


