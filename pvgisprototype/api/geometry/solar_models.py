from enum import Enum


class SolarPositionModels(str, Enum):
    all = 'all'
    noaa = 'NOAA'
    pysolar = 'pysolar'
    pvis = 'pvis'
    # pvgis = 'PVGIS'
    suncalc = 'suncalc'
    skyfield = 'Skyfield'
