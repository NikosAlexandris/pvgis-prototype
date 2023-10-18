from enum import Enum


class SolarIncidenceModels(str, Enum):
    all = 'all'
    pvis = 'PVIS'
    jenco = 'Jenco'


class SolarDeclinationModels(str, Enum):
    all = 'all'
    # pvgis = 'PVGIS'
    hargreaves = 'Hargreaves'
    noaa = 'NOAA'
    pvis = 'PVIS'
    pvlib = 'pvlib'


class SolarTimeModels(str, Enum):
    all = 'all'
    ephem = 'ephem'
    milne = 'Milne (1921)'
    noaa = 'NOAA'
    pvgis = 'PVGIS'
    skyfield = 'Skyfield'


class SolarPositionModels(str, Enum):
    all = 'all'
    noaa = 'NOAA'
    # pvgis = 'PVGIS'
    pvis = 'PVIS'
    pvlib = 'pvlib'
    pysolar = 'pysolar'
    skyfield = 'Skyfield'
    suncalc = 'suncalc'


SOLAR_INCIDENCE_ALGORITHM_DEFAULT = SolarIncidenceModels.jenco
SOLAR_DECLINATION_ALGORITHM_DEFAULT = SolarDeclinationModels.noaa
SOLAR_TIME_ALGORITHM_DEFAULT = SolarTimeModels.milne
SOLAR_POSITION_ALGORITHM_DEFAULT = SolarPositionModels.noaa
