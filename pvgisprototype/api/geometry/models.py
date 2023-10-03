from enum import Enum


class SolarIncidenceModels(str, Enum):
    all = 'all'
    pvis = 'pvis'
    jenco = 'Jenco'


class SolarDeclinationModels(str, Enum):
    all = 'all'
    # pvgis = 'PVGIS'
    hargreaves = 'Hargreaves'
    noaa = 'NOAA'
    pvis = 'pvis'
    pvlib = 'pvlib'


class SolarPositionModels(str, Enum):
    all = 'all'
    noaa = 'NOAA'
    # pvgis = 'PVGIS'
    pvis = 'pvis'
    pvlib = 'pvlib'
    pysolar = 'pysolar'
    skyfield = 'Skyfield'
    suncalc = 'suncalc'


class SolarTimeModels(str, Enum):
    all = 'all'
    ephem = 'ephem'
    milne = 'Milne (1921)'
    noaa = 'NOAA'
    pvgis = 'PVGIS'
    skyfield = 'Skyfield'
