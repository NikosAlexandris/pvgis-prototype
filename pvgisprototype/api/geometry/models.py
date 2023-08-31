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
    eot = 'EoT'
    ephem = 'ephem'
    noaa = 'NOAA'
    pvgis = 'PVGIS'
    skyfield = 'Skyfield'


# def _parse_model(
#         ctx: typer.Context,
#         model: List[SolarPositionModels],
#         param: typer.CallbackParam,
#     ) -> List[SolarPositionModels]:

#     print(f'ctx : {ctx}')
#     print(f'param : {param}')
#     print(f'model : {model}')
#     print()
#     if ctx.resilient_parsing:
#         return
#     if SolarPositionModels.all in model:
#         # Return all models except for the 'all' itself!
#         model = [model for model in SolarPositionModels if model != SolarPositionModels.all]
#     print(f"Return model: {model}")
#     return model


