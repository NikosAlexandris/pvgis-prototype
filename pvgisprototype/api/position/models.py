from enum import Enum
from typing import Type
from typing import List
from typing import Union
import typer


def select_models(enum_type: Type[Enum], models: List[Enum]) -> List[Enum]:
    """Select models from an enum list."""
    if enum_type.all in models:
        return [model for model in enum_type if model != enum_type.all]

    return models


def validate_model(enum_type: Type[Enum], model: List[Enum]) -> Enum:
    """Check that one and only one model from an Enum class is selected"""
    if model == enum_type.all:  # or len(model) > 1: will not work! -- ReviewMe
        raise typer.BadParameter(f"You can select only one model for [code]solar_time_model[/code]. Multiple or all are not a meaningful option.")

    return model


class SolarTimeModel(str, Enum):
    all = 'all'
    ephem = 'ephem'
    milne = 'Milne1921'
    noaa = 'NOAA'
    pvgis = 'PVGIS'
    skyfield = 'Skyfield'


class SolarDeclinationModel(str, Enum):
    all = 'all'
    # pvgis = 'PVGIS'
    hargreaves = 'Hargreaves'
    noaa = 'NOAA'
    pvis = 'PVIS'
    pvlib = 'pvlib'


class SolarPositionModel(str, Enum):
    all = 'all'
    noaa = 'NOAA'
    # pvgis = 'PVGIS'
    pvis = 'PVIS'
    jenco = 'Jenco'
    pvlib = 'pvlib'
    pysolar = 'pysolar'
    skyfield = 'Skyfield'
    suncalc = 'suncalc'


class SolarIncidenceModel(str, Enum):
    all = 'all'
    jenco = 'Jenco'
    iqbal = 'Iqbal'  # NREL
    pvis = 'PVIS'


SOLAR_TIME_ALGORITHM_DEFAULT = SolarTimeModel.milne
SOLAR_DECLINATION_ALGORITHM_DEFAULT = SolarDeclinationModel.noaa
SOLAR_POSITION_ALGORITHM_DEFAULT = SolarPositionModel.noaa
SOLAR_INCIDENCE_ALGORITHM_DEFAULT = SolarIncidenceModel.iqbal
