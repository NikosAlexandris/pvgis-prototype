from pydantic import field_validator
# from typing import Optional

# Generic input/output
from pvgisprototype.validation.parameters import VerbosityModel

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
# from pvgisprototype.validation.parameters import BaseAngleUnitsModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseTimeOutputUnitsModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseAngleOutputUnitsModel

# What?
from pvgisprototype.validation.parameters import ApplyAtmosphericRefractionModel
from pvgisprototype.algorithms.noaa.parameter_models import SolarZenithModel
from pvgisprototype.algorithms.noaa.parameter_models import SolarZenithSeriesModel
from pvgisprototype.validation.parameters import RefractedSolarZenithModel
from math import pi
import numpy as np

# In order of dependency:
# Fractional year  < Equation of time  < Time offset  < True solar time  < Solar hour angle 
# Solar declination  < Solar zenith  < Solar altitude  < Solar azimuth

class CalculateFractionalYearNOAAInput(
    BaseTimestampModel,
):
    pass


class CalculateFractionalYearTimeSeriesNOAAInput(  # merge above here-in!
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    AngleInRadiansOutputUnitsModel,
):
    pass


class CalculateEquationOfTimeTimeSeriesNOAAInput(
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    BaseTimeOutputUnitsModel,
):
    pass



class CalculateTimeOffsetTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
):
    pass



class CalculateTrueSolarTimeTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
):
    pass





class CalculateSolarHourAngleTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
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
    VerbosityModel,
):
    @field_validator('solar_zenith')
    @classmethod
    def solar_zenith_range(cls, v):
        if not (0 <= v.radians <= pi):
            raise ValueError('solar_zenith must range within [0, π]')
        return v


class AdjustSolarZenithForAtmosphericRefractionTimeSeriesNOAAInput(
    SolarZenithSeriesModel,
    BaseAngleOutputUnitsModel,
    VerbosityModel,
):
    # @field_validator('solar_zenith_series')
    # def solar_zenith_range(cls, v):
    #     v_array = np.atleast_1d(v)  # Ensure v is treated as an array
    #     if not np.all((0 <= v_array) & (v_array <= np.pi)):  # Adjust the condition to work with an array
    #         raise ValueError('solar_zenith must range within [0, π]')
    #     return v  # Return the original value or array
    @field_validator('solar_zenith_series')
    def solar_zenith_range(cls, v):
        v_values = np.array([zenith.value for zenith in np.atleast_1d(v)])  # Extract numerical values
        if not np.all((0 <= v_values) & (v_values <= np.pi)):  # Adjust the condition to work with an array
            raise ValueError("The solar zenith angle must be between 0 and pi radians.")
        return v


class CalculateSolarZenithNOAAInput(                # FIXME: Move this to function models, keep VerbosityModel
    LatitudeModel,
    BaseTimestampModel,
    SolarHourAngleModel,
    ApplyAtmosphericRefractionModel,
    BaseAngleOutputUnitsModel,
    VerbosityModel,
):
    pass


class CalculateSolarZenithTimeSeriesNOAAInput(
    LatitudeModel,
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    SolarHourAngleSeriesModel,
    ApplyAtmosphericRefractionModel,
    BaseAngleOutputUnitsModel,
    VerbosityModel,
):
    pass


class CalculateSolarAltitudeTimeSeriesNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    ApplyAtmosphericRefractionModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
    VerbosityModel,
):
    pass


class CalculateSolarAzimuthNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    # BaseTimeOutputUnitsModel,
    # BaseAngleUnitsModel,
    # BaseAngleOutputUnitsModel,
    VerbosityModel,
):
    pass


class CalculateSolarAzimuthTimeSeriesNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateEventHourAngleNOAAInput(
    LatitudeModel,
    BaseTimestampModel,
    RefractedSolarZenithModel,
):

    @field_validator('refracted_solar_zenith')
    @classmethod
    def validate_refracted_solar_zenith(cls, v):
        target_zenith = 1.5853349194640094  # radias, approx. 90.833 degrees
        error_margin = 0.01
        if not (target_zenith - error_margin) <= v.radians <= (target_zenith + error_margin):
            raise ValueError(
                f"`refracted_solar_zenith` must be approximately {target_zenith} radians (90.833 degrees), allowing an error margin of {error_margin}"
            )
        return v


class CalculateEventTimeNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    RefractedSolarZenithModel,
    BaseTimeEventModel,
    ApplyAtmosphericRefractionModel,
):
    pass


class CalculateLocalSolarTimeNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    RefractedSolarZenithModel,
):
    verbose: int = 0


class CalculateSolarPositionNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    RefractedSolarZenithModel,
    ApplyAtmosphericRefractionModel,
):

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
