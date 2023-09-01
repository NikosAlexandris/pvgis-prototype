from pydantic import field_validator
from typing import Optional

# When?
from pvgisprototype.validation.parameters import BaseTimestampModel
from pvgisprototype.validation.parameters import BaseTimestampSeriesModel
from pvgisprototype.validation.parameters import BaseTimeModel
from pvgisprototype.validation.parameters import BaseTimeSeriesModel
from pvgisprototype.validation.parameters import SolarHourAngleModel
from pvgisprototype.validation.parameters import SolarHourAngleSeriesModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseTimeEventModel

# Where?
from pvgisprototype.validation.parameters import LongitudeModel
from pvgisprototype.validation.parameters import LatitudeModel
from pvgisprototype.validation.parameters import BaseCoordinatesModel

# Units?

from pvgisprototype.algorithms.noaa.parameter_models import AngleInRadiansOutputUnitsModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseAngleUnitsModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseTimeOutputUnitsModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseAngleOutputUnitsModel

# What?
from pvgisprototype.algorithms.noaa.parameter_models import BaseApplyAtmosphericRefractionModel
from pvgisprototype.algorithms.noaa.parameter_models import SolarZenithModel
from pvgisprototype.algorithms.noaa.parameter_models import SolarZenithSeriesModel
from math import pi
import numpy as np

# In order of dependency:
# Fractional year  < Equation of time  < Time offset  < True solar time  < Solar hour angle 
# Solar declination  < Solar zenith  < Solar altitude  < Solar azimuth

class CalculateFractionalYearNOAAInput(
    BaseTimestampModel,
    AngleInRadiansOutputUnitsModel,
):
    pass


class CalculateFractionalYearTimeSeriesNOAAInput(  # merge above here-in!
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    AngleInRadiansOutputUnitsModel,
):
    pass


class CalculateEquationOfTimeNOAAInput(
    BaseTimestampModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateEquationOfTimeTimeSeriesNOAAInput(
    BaseTimestampSeriesModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateTimeOffsetNOAAInput(
    LongitudeModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateTimeOffsetTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateTrueSolarTimeNOAAInput(
    LongitudeModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateTrueSolarTimeTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateSolarHourAngleNOAAInput(
    LongitudeModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarHourAngleTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass



class CalculateSolarDeclinationNOAAInput(
    BaseTimestampModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarDeclinationTimeSeriesNOAAInput(  # merge above here-in
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    BaseAngleOutputUnitsModel,
):
    pass


class AdjustSolarZenithForAtmosphericRefractionNOAAInput(
    SolarZenithModel,
    BaseAngleOutputUnitsModel,
):
    @field_validator('solar_zenith')
    @classmethod
    def solar_zenith_range(cls, v):
        if not (0 <= v <= pi):
            raise ValueError('solar_zenith must range within [0, π]')
        return v


class AdjustSolarZenithForAtmosphericRefractionTimeSeriesNOAAInput(
    SolarZenithSeriesModel,
    BaseAngleOutputUnitsModel,
):
    @field_validator('solar_zenith_series')
    def solar_zenith_range(cls, v):
        v_array = np.atleast_1d(v)  # Ensure v is treated as an array
        if not np.all((0 <= v_array) & (v_array <= np.pi)):  # Adjust the condition to work with an array
            raise ValueError('solar_zenith must range within [0, π]')
        return v  # Return the original value or array


class CalculateSolarZenithNOAAInput(
    LatitudeModel,
    BaseTimestampModel,
    SolarHourAngleModel,
    BaseApplyAtmosphericRefractionModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarZenithTimeSeriesNOAAInput(
    LatitudeModel,
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    SolarHourAngleSeriesModel,
    BaseApplyAtmosphericRefractionModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAltitudeNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseApplyAtmosphericRefractionModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAltitudeTimeSeriesNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    BaseApplyAtmosphericRefractionModel,
    BaseTimeOutputUnitsModel,
    # BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAzimuthNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAzimuthTimeSeriesNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateEventHourAngleNOAAInput(
    LatitudeModel,
    BaseTimestampModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    refracted_solar_zenith: float

    @field_validator('refracted_solar_zenith')
    @classmethod
    def validate_refracted_solar_zenith(cls, v):
        target_zenith = 1.5853349194640094  # radias, approx. 90.833 degrees
        error_margin = 0.01
        if not (target_zenith - error_margin) <= v <= (target_zenith + error_margin):
            raise ValueError(
                f"`refracted_solar_zenith` must be approximately {target_zenith} radians (90.833 degrees), allowing an error margin of {error_margin}"
            )
        return v


class CalculateEventTimeNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseTimeEventModel,
    BaseApplyAtmosphericRefractionModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateLocalSolarTimeNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    verbose: Optional[bool] = False


class CalculateSolarPositionNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseApplyAtmosphericRefractionModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    refracted_solar_zenith: float

    @field_validator('refracted_solar_zenith')
    @classmethod
    def validate_refracted_solar_zenith(cls, v):
        target_zenith = 1.5853349194640094  # radias, approx. 90.833 degrees
        error_margin = 0.01
        if not (target_zenith - error_margin) <= v <= (target_zenith + error_margin):
            raise ValueError(
                f"`refracted_solar_zenith` must be approximately {target_zenith} radians (90.833 degrees), allowing an error margin of {error_margin}"
            )
        return v
    pass
