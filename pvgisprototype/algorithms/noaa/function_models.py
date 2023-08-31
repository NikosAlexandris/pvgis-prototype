from pydantic import field_validator
from typing import Optional
from pvgisprototype.algorithms.noaa.parameter_models import BaseTimestampModel
from pvgisprototype.algorithms.noaa.parameter_models import AngleInRadiansOutputUnitsModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseTimestampSeriesModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseAngleUnitsModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseTimeOutputUnitsModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseAngleOutputUnitsModel
from pvgisprototype.algorithms.noaa.parameter_models import LongitudeModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseTimeModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseTimeSeriesModel
from pvgisprototype.algorithms.noaa.parameter_models import SolarZenithModel
from pvgisprototype.algorithms.noaa.parameter_models import SolarZenithSeriesModel
from pvgisprototype.algorithms.noaa.parameter_models import LatitudeModel
from pvgisprototype.algorithms.noaa.parameter_models import SolarHourAngleModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseApplyAtmosphericRefractionModel
from pvgisprototype.algorithms.noaa.parameter_models import SolarHourAngleSeriesModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseCoordinatesModel
from pvgisprototype.algorithms.noaa.parameter_models import BaseTimeEventModel
from math import pi


class CalculateFractionalYearNOAAInput(
    BaseTimestampModel,
    AngleInRadiansOutputUnitsModel,
):
    pass


class CalculateFractionalYearNOAATimeSeriesInput(  # merge above here-in!
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    AngleInRadiansOutputUnitsModel,
):
    pass


class CalculateEquationOfTimeNOAAInput(
    BaseTimestampModel,
    BaseAngleUnitsModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateSolarDeclinationNOAAInput(
    BaseTimestampModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarDeclinationNOAATimeSeriesInput(  # merge above here-in
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateTimeOffsetNOAAInput(
    LongitudeModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
):
    pass


class CalculateTrueSolarTimeNOAAInput(
    LongitudeModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateTrueSolarTimeNOAATimeSeriesInput(
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


class CalculateSolarHourAngleNOAATimeSeriesInput(
    LongitudeModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
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


class AdjustSolarZenithForAtmosphericRefractionNOAATimeSeriesInput(
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


class CalculateSolarZenithNOAATimeSeriesInput(
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


class CalculateSolarAltitudeNOAATimeSeriesInput(
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


class CalculateSolarAzimuthNOAATimeSeriesInput(
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
