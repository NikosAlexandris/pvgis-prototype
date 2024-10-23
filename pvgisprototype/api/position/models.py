from enum import Enum
from typing import List, Sequence, Type

import typer

from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ALTITUDE_NAME,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_NAME,
    DECLINATION_COLUMN_NAME,
    DECLINATION_NAME,
    HOUR_ANGLE_COLUMN_NAME,
    HOUR_ANGLE_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_NAME,
    POSITION_ALGORITHM_NAME,
    TIME_ALGORITHM_NAME,
    ZENITH_COLUMN_NAME,
    ZENITH_NAME,
)


def select_models(enum_type: Type[Enum], models: List[str]) -> List[Enum]:
    """Select models from an enum list."""
    if enum_type.all in models:
        return [model for model in enum_type if model != enum_type.all]
    # return list(models)
    return [enum_type(model) for model in models]


def validate_model(enum_type: Type[Enum], model: List[Enum]) -> Enum:
    """Check that one and only one model from an Enum class is selected"""
    if model == enum_type.all:  # or len(model) > 1: will not work! -- ReviewMe
        raise typer.BadParameter(
            "You can select only one model for [code]solar_time_model[/code]. Multiple or all are not a meaningful option."
        )

    return model


class SolarPositionParameter(str, Enum):
    all = "all"
    timing = TIME_ALGORITHM_NAME
    declination = DECLINATION_NAME
    hour_angle = HOUR_ANGLE_NAME
    positioning = POSITION_ALGORITHM_NAME
    zenith = ZENITH_NAME
    altitude = ALTITUDE_NAME
    azimuth = AZIMUTH_NAME
    incidence = INCIDENCE_NAME
    overview = "Overview"


SOLAR_POSITION_PARAMETER_COLUMN_NAMES = {
    # SolarPositionParameter.timing: TIME_ALGORITHM_COLUMN_NAME,
    SolarPositionParameter.declination: DECLINATION_COLUMN_NAME,
    SolarPositionParameter.hour_angle: HOUR_ANGLE_COLUMN_NAME,
    # SolarPositionParameter.positioning: POSITIONING_ALGORITHM_COLUMN_NAME,
    SolarPositionParameter.zenith: ZENITH_COLUMN_NAME,
    SolarPositionParameter.altitude: ALTITUDE_COLUMN_NAME,
    SolarPositionParameter.azimuth: AZIMUTH_COLUMN_NAME,
    SolarPositionParameter.incidence: INCIDENCE_COLUMN_NAME,
}


class SolarTimeModel(str, Enum):
    all = "all"
    milne = "Milne1921"
    noaa = "NOAA"
    pvgis = "PVGIS"
    pvlib = "pvlib"
    skyfield = "Skyfield"


class SolarDeclinationModel(str, Enum):
    all = "all"
    hargreaves = "Hargreaves"
    noaa = "NOAA"
    pvis = "PVIS"
    pvlib = "pvlib"


class SolarPositionModel(str, Enum):
    all = "all"  # FIXME This isn't working
    noaa = "NOAA"  # Works
    hofierka = "Hofierka"  # FIXME This isn't working
    jenco = "Jenco"  # Works
    pvlib = "pvlib"  # FIXME This isn't working
    pysolar = "pysolar"  # FIXME This isn't working
    skyfield = "Skyfield"  # FIXME This isn't working
    suncalc = "suncalc"  # FIXME This isn't working


class SolarIncidenceModel(str, Enum):
    all = "all"
    hofierka = "Hofierka"
    jenco = "Jenco"
    iqbal = "Iqbal"  # NREL
    pvis = "PVIS"  # FIXME This isn't working
    pvlib = "pvlib"

class ShadingModel(str, Enum):
    all = "all"
    pvlib = "pvlib"
SHADE_ALGORITHM_DEFAULT = ShadingModel.pvlib


SOLAR_TIME_ALGORITHM_DEFAULT = SolarTimeModel.milne
SOLAR_DECLINATION_ALGORITHM_DEFAULT = SolarDeclinationModel.noaa
SOLAR_POSITION_ALGORITHM_DEFAULT = SolarPositionModel.noaa
SOLAR_INCIDENCE_ALGORITHM_DEFAULT = SolarIncidenceModel.iqbal
