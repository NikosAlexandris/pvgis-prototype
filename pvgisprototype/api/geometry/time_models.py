from enum import Enum

class SolarTimeModels(str, Enum):
    all = 'all'
    eot = 'EoT'
    ephem = 'ephem'
    noaa = 'NOAA'
    pvgis = 'PVGIS'
    skyfield = 'Skyfield'
