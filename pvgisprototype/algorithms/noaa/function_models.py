from pydantic import field_validator

# Generic input/output
from pvgisprototype.validation.pvis_data_classes import VerbosityModel
from pvgisprototype.validation.pvis_data_classes import LoggingModel
from pvgisprototype.validation.pvis_data_classes import ArrayTypeModel
from pvgisprototype.validation.pvis_data_classes import ArrayBackendModel

# When?
from pvgisprototype.validation.pvis_data_classes import BaseTimestampModel
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
from pvgisprototype.validation.pvis_data_classes import BaseTimeModel
from pvgisprototype.validation.pvis_data_classes import BaseTimeSeriesModel
from pvgisprototype.validation.pvis_data_classes import SolarHourAngleModel
from pvgisprototype.validation.pvis_data_classes import SolarHourAngleSeriesModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseTimeEventModel

# Where?
from pvgisprototype.validation.pvis_data_classes import LongitudeModel
from pvgisprototype.validation.pvis_data_classes import LatitudeModel
from pvgisprototype.validation.pvis_data_classes import BaseCoordinatesModel

# Units?
from pvgisprototype.algorithms.noaa.parameter_models import AngleInRadiansOutputUnitsModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseAngleOutputUnitsModel

# What?
from pvgisprototype.validation.pvis_data_classes import ApplyAtmosphericRefractionModel
from pvgisprototype.algorithms.noaa.parameter_models import SolarZenithModel
from pvgisprototype.algorithms.noaa.parameter_models import SolarZenithSeriesModel
from pvgisprototype.validation.pvis_data_classes import RefractedSolarZenithModel
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
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateEquationOfTimeTimeSeriesNOAAInput(
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateTimeOffsetTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateTrueSolarTimeTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateSolarHourAngleTimeSeriesNOAAInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateSolarDeclinationTimeSeriesNOAAInput(  # merge above here-in
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
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
):
    pass


class CalculateEventHourAngleNOAAInput(
    LatitudeModel,
    BaseTimestampModel,
    RefractedSolarZenithModel,
    VerbosityModel,
    LoggingModel,
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


class CalculateEventHourAngleTimeSeriesNOAAInput(
    LatitudeModel,
    BaseTimestampSeriesModel,
    RefractedSolarZenithModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateEventTimeNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    RefractedSolarZenithModel,
    BaseTimeEventModel,
    ApplyAtmosphericRefractionModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateEventTimeTimeSeriesNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    RefractedSolarZenithModel,
    BaseTimeEventModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateLocalSolarTimeNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    RefractedSolarZenithModel,
    VerbosityModel,
    LoggingModel,
):
    verbose: int = 0


class CalculateSolarPositionNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    RefractedSolarZenithModel,
    ApplyAtmosphericRefractionModel,
    VerbosityModel,
    LoggingModel,
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


class CalculateTimeserieSolarPositionNOAAInput(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    RefractedSolarZenithModel,
    ApplyAtmosphericRefractionModel,
    VerbosityModel,
    LoggingModel,
):
    pass
