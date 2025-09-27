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
from pydantic import field_validator

from pvgisprototype.algorithms.noaa.parameter_models import (
    BaseTimeEventModel,
    SolarZenithModel,
    SolarZenithSeriesModel,
)

# What?
# Where?
# When?
# Generic input/output
from pvgisprototype.validation.models import (
    ApplyAtmosphericRefractionModel,
    ArrayTypeModel,
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseTimeSeriesModel,
    BaseTimestampModel,
    BaseTimestampSeriesModel,
    LatitudeModel,
    LoggingModel,
    LongitudeModel,
    UnrefractedSolarZenithModel,
    VerbosityModel,
    ValidateOutputModel,
)

# Units?


# In order of dependency:
# Fractional year  < Equation of time  < Time offset  < True solar time  < Solar hour angle
# Solar declination  < Solar zenith  < Solar altitude  < Solar azimuth


class CalculateFractionalYearNOAAInput(
    BaseTimestampModel,
):
    pass


class CalculateFractionalYearTimeSeriesNOAAInput(  # merge above here-in!
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel
):
    pass


class CalculateEquationOfTimeTimeSeriesNOAAInput(
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel,
):
    pass


class CalculateTimeOffsetTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel
):
    pass


class CalculateTrueSolarTimeTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel,
):
    pass


class CalculateSolarHourAngleTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel,
):
    pass


class CalculateSolarDeclinationTimeSeriesNOAAInput(  # merge above here-in
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel,
):
    pass


class AdjustSolarZenithForAtmosphericRefractionNOAAInput(
    SolarZenithModel,
    VerbosityModel,
    LoggingModel,
):
    # @field_validator('solar_zenith')
    # @classmethod
    # def solar_zenith_range(cls, v):
    #     if not (0 <= v.radians <= pi):
    #         raise ValueError('solar_zenith must range within [0, π]')
    #     return v
    pass


class AdjustSolarZenithForAtmosphericRefractionTimeSeriesNOAAInput(
    SolarZenithSeriesModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateSolarZenithTimeSeriesNOAAInput(
    LongitudeModel,
    LatitudeModel,
    BaseTimeSeriesModel,  # != BaseTimestampModel
    # SolarHourAngleSeriesModel,
    ApplyAtmosphericRefractionModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel,
):
    pass


class CalculateSolarAltitudeTimeSeriesNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    ApplyAtmosphericRefractionModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateSolarAzimuthTimeSeriesNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    ApplyAtmosphericRefractionModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel,
):
    pass


class CalculateEventHourAngleNOAAInput(
    LatitudeModel,
    BaseTimestampModel,
    UnrefractedSolarZenithModel,
    VerbosityModel,
    LoggingModel,
):
    @field_validator("unrefracted_solar_zenith")
    @classmethod
    def validate_unrefracted_solar_zenith(cls, v):
        target_zenith = 1.5853349194640094  # radians, approx. 90.833 degrees
        error_margin = 0.01
        if (
            not (target_zenith - error_margin)
            <= v.radians
            <= (target_zenith + error_margin)
        ):
            raise ValueError(
                f"`unrefracted_solar_zenith` must be approximately {target_zenith} radians (90.833 degrees), allowing an error margin of {error_margin}"
            )
        return v


class CalculateEventHourAngleTimeSeriesNOAAInput(
    LatitudeModel,
    BaseTimestampSeriesModel,
    UnrefractedSolarZenithModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateEventTimeNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    UnrefractedSolarZenithModel,
    BaseTimeEventModel,
    ApplyAtmosphericRefractionModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateEventTimeTimeSeriesNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    UnrefractedSolarZenithModel,
    BaseTimeEventModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateLocalSolarTimeNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    UnrefractedSolarZenithModel,
    VerbosityModel,
    LoggingModel,
):
    verbose: int = 0


class CalculateSolarPositionNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    UnrefractedSolarZenithModel,
    ApplyAtmosphericRefractionModel,
    VerbosityModel,
    LoggingModel,
):
    @field_validator("unrefracted_solar_zenith")
    @classmethod
    def validate_unrefracted_solar_zenith(cls, v):
        target_zenith = 1.5853349194640094  # radias, approx. 90.833 degrees
        error_margin = 0.01
        if not (target_zenith - error_margin) <= v <= (target_zenith + error_margin):
            raise ValueError(
                f"`unrefracted_solar_zenith` must be approximately {target_zenith} radians (90.833 degrees), allowing an error margin of {error_margin}"
            )
        return v

    pass


class CalculateTimeserieSolarPositionNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    UnrefractedSolarZenithModel,
    ApplyAtmosphericRefractionModel,
    VerbosityModel,
    LoggingModel,
):
    pass
