#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from enum import Enum
from typing import List, Type

import typer

from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ALTITUDE_NAME,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_NAME,
    DECLINATION_COLUMN_NAME,
    DECLINATION_NAME,
    HORIZON_HEIGHT_COLUMN_NAME,
    HORIZON_HEIGHT_NAME,
    HOUR_ANGLE_COLUMN_NAME,
    HOUR_ANGLE_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_NAME,
    POSITION_ALGORITHM_NAME,
    SOLAR_EVENT_COLUMN_NAME,
    SOLAR_EVENT_NAME,
    SOLAR_EVENT_TIME_COLUMN_NAME,
    SOLAR_EVENT_TIME_NAME,
    SUN_HORIZON_POSITION_NAME,
    SUN_HORIZON_POSITION_COLUMN_NAME,
    TIME_ALGORITHM_NAME,
    VISIBLE_COLUMN_NAME,
    VISIBLE_NAME,
    ZENITH_COLUMN_NAME,
    ZENITH_NAME,
)


def select_models(enum_type: Type[Enum], models: List[str]) -> List[Enum]:
    """Select models from an enum list."""
    if enum_type.all in models:
        return [model for model in enum_type if model != enum_type.all]

    return [enum_type(model) for model in models]


def validate_model(enum_type: Type[Enum], model: List[Enum]) -> Enum:
    """Check that one and only one model from an Enum class is selected"""
    if model == enum_type.all:  # or len(model) > 1: will not work! -- ReviewMe
        raise typer.BadParameter(
            "You can select only one model for [code]solar_time_model[/code]. Multiple or all are not meaningful nor possible."
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
    horizon = HORIZON_HEIGHT_NAME
    sun_horizon = SUN_HORIZON_POSITION_NAME
    visible = VISIBLE_NAME
    event_type = SOLAR_EVENT_NAME
    event_time = SOLAR_EVENT_TIME_NAME
    overview = "Overview"


class SolarPositionParameterColumnName(str, Enum):
    all = "all"
    timing = TIME_ALGORITHM_NAME
    declination = DECLINATION_COLUMN_NAME
    hour_angle = HOUR_ANGLE_COLUMN_NAME
    positioning = POSITION_ALGORITHM_NAME
    zenith = ZENITH_COLUMN_NAME
    altitude = ALTITUDE_COLUMN_NAME
    azimuth = AZIMUTH_COLUMN_NAME
    incidence = INCIDENCE_COLUMN_NAME
    horizon = HORIZON_HEIGHT_COLUMN_NAME
    sun_horizon = SUN_HORIZON_POSITION_COLUMN_NAME
    visible = VISIBLE_COLUMN_NAME
    event_type = SOLAR_EVENT_COLUMN_NAME
    event_time = SOLAR_EVENT_TIME_COLUMN_NAME


# Following, the "algorithms" are commented out. On purpose so !
# The parameters defined here will appear as columns in some tabular context.
# We _don't_ want columns with a single value repeated throughout all rows.
# If we "use" the "algorithms" here, this is what will happen !

SOLAR_POSITION_PARAMETER_COLUMN_NAMES = {
    # SolarPositionParameter.timing: TIMING_ALGORITHM_COLUMN_NAME,
    SolarPositionParameter.declination: DECLINATION_COLUMN_NAME,
    SolarPositionParameter.hour_angle: HOUR_ANGLE_COLUMN_NAME,
    # SolarPositionParameter.positioning: POSITIONING_ALGORITHM_COLUMN_NAME,
    SolarPositionParameter.zenith: ZENITH_COLUMN_NAME,
    SolarPositionParameter.altitude: ALTITUDE_COLUMN_NAME,
    SolarPositionParameter.azimuth: AZIMUTH_COLUMN_NAME,
    SolarPositionParameter.incidence: INCIDENCE_COLUMN_NAME,
    SolarPositionParameter.horizon: HORIZON_HEIGHT_COLUMN_NAME,
    SolarPositionParameter.sun_horizon: SUN_HORIZON_POSITION_COLUMN_NAME,
    SolarPositionParameter.visible: VISIBLE_COLUMN_NAME,
    SolarPositionParameter.event_type: SOLAR_EVENT_COLUMN_NAME,
    SolarPositionParameter.event_time: SOLAR_EVENT_TIME_COLUMN_NAME,
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
    skyfield = "Skyfield"  # FIXME This isn't working
    suncalc = "suncalc"  # FIXME This isn't working


class SolarIncidenceModel(str, Enum):
    all = "all"
    hofierka = "Hofierka"
    jenco = "Jenco"
    iqbal = "Iqbal"  # NREL
    pvis = "PVIS"  # FIXME This isn't working
    pvlib = "pvlib"


class SunHorizonPositionModel(str, Enum):
    all = "all"
    above = "Above"
    low_angle = "Low angle"
    below = "Below"


class ShadingModel(str, Enum):
    all = "all"
    pvis = "PVGIS"
    pvlib = "pvlib"


class ShadingState(str, Enum):
    all = "all"
    sunlit = "Sunlit"
    potentially_sunlit = "Potentially-sunlit"
    in_shade = "In-shade"


class SolarEvent(str, Enum):
    all = "all"
    astronomical_twilight = "Astronomical Twilight"
    nautical_twilight = "Nautical Twilight"
    civil_twilight = "Civil Twilight"
    sunrise = "Sunrise"
    noon = "Noon"
    sunset = "Sunset"
    daylength = "Daylength"
    perihelion = "Perihelion"
    first_minimum_point = "1st Minimum Point"
    vernal_equinox = "Vernal Point"
    first_zero_point = "1st Zero Point"
    first_maximum_point = "1st Maximum Point"
    second_zero_point = "2nd Zero Point"
    solstice_summer_to_winter = "Summer Solstice / Winter Solstice"
    aphelion = "Aphelion"
    third_zero_point = "3rd Zero Point"
    autumnal_equinox = "Autumnal Equinox"
    second_maximum_point = "2nd Maximum Point"
    fourth_zero_point = "4th Zero Point"
    winter_to_summer_solstice = "Winter Solstice / Summer Solstice"


SOLAR_TIME_ALGORITHM_DEFAULT = SolarTimeModel.milne
SOLAR_DECLINATION_ALGORITHM_DEFAULT = SolarDeclinationModel.noaa
SOLAR_POSITION_ALGORITHM_DEFAULT = SolarPositionModel.noaa
SHADE_ALGORITHM_DEFAULT = ShadingModel.pvis
SHADING_STATE_DEFAULT = [ShadingState.all]
SOLAR_INCIDENCE_ALGORITHM_DEFAULT = SolarIncidenceModel.iqbal
SUN_HORIZON_POSITION_DEFAULT = [SunHorizonPositionModel.all]
