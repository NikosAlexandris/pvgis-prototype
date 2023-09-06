from enum import Enum


class SolarIncidenceModels(str, Enum):
    all = 'all'
    jenco = 'Jenco'
    effective = 'effective'
    # pvis = 'pvis'


class SolarDeclinationModels(str, Enum):
    all = 'all'
    noaa = 'NOAA'
    pvis = 'pvis'
    hargreaves = 'Hargreaves'
    # pvgis = 'PVGIS'
    pvlib = 'pvlib'


class SolarPositionModels(str, Enum):
    all = 'all'
    noaa = 'NOAA'
    pysolar = 'pysolar'
    pvis = 'pvis'
    # pvgis = 'PVGIS'
    suncalc = 'suncalc'
    skyfield = 'Skyfield'
    pvlib = 'pvlib'


class SolarTimeModels(str, Enum):
    all = 'all'
    ephem = 'ephem'
    milne = 'Milne (1921)'
    noaa = 'NOAA'
    pvgis = 'PVGIS'
    skyfield = 'Skyfield'
