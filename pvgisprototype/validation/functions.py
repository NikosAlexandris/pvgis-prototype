# Generic input/output
from functools import wraps

# Validator
from typing import Callable, Type

from pydantic import BaseModel

# Output
# Incidence
# Solar Surface
# Solar geometry
# Solar time
# Earth orbit
# Atmospheric effects
# When?
# Where?
from pvgisprototype.validation.models import (
    ApplyAtmosphericRefractionModel,
    ArrayTypeModel,
    ArrayBackendModel,
    BaseAngleOutputUnitsModel,
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseTimeSeriesModel,
    BaseTimestampModel,
    BaseTimestampSeriesModel,
    ComplementaryIncidenceAngleModel,
    EarthOrbitModel,
    ElevationModel,
    HourOffsetModel,
    LatitudeModel,
    LoggingModel,
    LongitudeModel,
    RefractedSolarAltitudeModel,
    RefractedSolarAltitudeSeriesModel,
    RefractedSolarZenithModel,
    HorizonProfileModel,
    ShadingModelModel,
    ShadingModelsModel,
    SolarAltitudeSeriesModel,
    SolarAzimuthSeriesModel,
    SolarDeclinationModel,
    SolarHourAngleModel,
    SolarIncidenceModel,
    SolarPositionModelModel,
    SolarPositionModelModels,
    SolarTimeModel,
    SolarTimeModelModel,
    SurfaceInShadeModel,
    SurfaceOrientationModel,
    SurfaceTiltModel,
    TimeOffsetModel,
    VerbosityModel,
    ZeroNegativeSolarIncidenceAngleModel,
    ValidateOutputModel,
)


def validate_with_pydantic(input_model: Type[BaseModel]) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) == 1 and isinstance(args[0], input_model):
                # If the passed argument is already an instance of the expected model, skip validation
                validated_input = args[0]
            else:
                # input_data = {**kwargs,
                # **dict(zip(func.__annotations__.keys(), args))}  # Not supported by Numba's nonpython mode!
                input_data = {}  # an empty dictionary
                input_data.update(kwargs)  # update with kwargs
                input_data.update(
                    dict(zip(func.__annotations__.keys(), args))
                )  # update with zipped annotations and args
                validated_input = input_model(**input_data)
            dictionary_input = {}
            for k, v in validated_input:
                dictionary_input[k] = v
            return func(**dictionary_input)
            # return func(**validated_input.dict())  # Use .dict() to convert Pydantic model to dictionary

        return wrapper

    return decorator


class CalculateFractionalYearPVISInputModel(
    BaseTimestampModel,
):
    pass


class CalculateFractionalYearPVGISInputModel(
    BaseTimestampModel,
):
    pass


class CalculateSolarDeclinationPVISInputModel(
    BaseTimestampModel,
    EarthOrbitModel,
):
    pass


class CalculateSolarDeclinationHargreavesInputModel(
    BaseTimestampModel,
):
    pass


class CalculateSolarDeclinationNOAAInput(
    BaseTimestampModel,
):
    pass


class ModelSolarDeclinationInputModel(
    BaseTimeModel,
    EarthOrbitModel,
    VerbosityModel,
):
    pass


# Solar time


class ModelSolarTimeInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarTimeModelModel,
    VerbosityModel,
):
    pass


class ModelSolarTimeTimeSeriesInputModel(
    LongitudeModel,
    BaseTimeSeriesModel,
    SolarTimeModelModel,
    ArrayTypeModel,
    # ArrayBackendModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateSolarTimePVGISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    EarthOrbitModel,
    TimeOffsetModel,
    VerbosityModel,
):
    pass


class CalculateSolarTimeMilne1921InputModel(
    LongitudeModel,
    BaseTimestampModel,
    VerbosityModel,
):
    pass


class CalculateTrueSolarTimeNOAAInput(
    LongitudeModel,
    BaseTimeModel,
):
    pass


class CalculateTimeOffsetNOAAInput(
    LongitudeModel,
    BaseTimeModel,
):
    pass


class CalculateEquationOfTimeNOAAInput(
    BaseTimestampModel,
):
    pass


# Hour angle


class CalculateSolarHourAngleSeriesInputModel(
    LongitudeModel,
    BaseTimeSeriesModel,
    SolarPositionModelModels,
    SolarTimeModelModel,
    ArrayTypeModel,
    # ArrayBackendModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class SolarHourAnglePVISInput(
    SolarTimeModel,
):
    pass


class CalculateSolarHourAngleNOAAInput(
    LongitudeModel,
    BaseTimeModel,
):
    pass


class CalculateSolarHourAnglePVISInputModel(
    SolarTimeModel,  # Parameter
):
    pass


class CalculateEventHourAngleInputModel(
    LatitudeModel,
    SurfaceTiltModel,
    SolarDeclinationModel,
):
    pass


class CalculateEventHourAnglePVISInputModel(CalculateEventHourAngleInputModel):
    pass


class SolarHourAngleSeriesPVLIBInput(
    LongitudeModel,
    BaseTimestampSeriesModel,
):
    pass


class SolarHourAngleSkyfieldInput(
    BaseCoordinatesModel,
    BaseTimestampModel,
):
    pass


class CalculateSolarAltitudePVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    EarthOrbitModel,
    TimeOffsetModel,
    SolarTimeModelModel,
):
    pass


class CalculateSolarAltitudePVLIBInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
):
    pass


class CalculateSolarAltitudeNOAAInput(
    BaseCoordinatesModel,
    BaseTimeModel,
    ApplyAtmosphericRefractionModel,
):
    pass


class CalculateSolarAltitudeAzimuthSkyfieldInputModel(
    BaseCoordinatesModel,
    BaseTimestampModel,
):
    pass


class CalculateSolarAzimuthPVLIBInputModel(CalculateSolarAltitudePVLIBInputModel):
    pass


class CalculateSolarDeclinationSeriesPVLIBInput(
    BaseTimestampSeriesModel,
):
    pass


class CalculateSolarDeclinationSkyfieldInput(
    BaseTimestampModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarZenithPVLIBInputModel(CalculateSolarAltitudePVLIBInputModel):
    pass


class CalculateSolarZenithNOAAInput(
    LatitudeModel,
    BaseTimestampModel,
    SolarHourAngleModel,
    ApplyAtmosphericRefractionModel,
):
    pass


class CalculateSolarAzimuthPVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarTimeModelModel,
):
    pass


class ModelSolarAltitudeInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarPositionModelModel,
    SolarTimeModelModel,
    ApplyAtmosphericRefractionModel,
    EarthOrbitModel,
):
    pass


class ModelSolarAltitudeTimeSeriesInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    SolarPositionModelModel,
    ApplyAtmosphericRefractionModel,
    ArrayTypeModel,
    # ArrayBackendModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel,
):
    pass


class ModelSolarAzimuthInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarPositionModelModel,
    SolarTimeModelModel,
    ApplyAtmosphericRefractionModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class ModelSolarAzimuthTimeSeriesInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    SolarPositionModelModel,
    ApplyAtmosphericRefractionModel,
    ArrayTypeModel,
    # ArrayBackendModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel,
):
    pass


class ModelSolarPositionOverviewSeriesInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    HorizonProfileModel,
    SurfaceOrientationModel,
    SurfaceTiltModel,
    SolarPositionModelModel,
    SolarTimeModelModel,
    # SolarIncidenceModel,
    ShadingModelModel,
    ApplyAtmosphericRefractionModel,
    ZeroNegativeSolarIncidenceAngleModel,
    EarthOrbitModel,
    ComplementaryIncidenceAngleModel,
    VerbosityModel,
    LoggingModel,
):
    pass


# Solar incidence angle


class CalculateRelativeLongitudeInputModel(
    LatitudeModel,
    SurfaceOrientationModel,
    SurfaceTiltModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateSolarIncidenceInputModel(
    LatitudeModel,
    SolarDeclinationModel,
    SurfaceOrientationModel,
    SurfaceTiltModel,
    LoggingModel,
):
    pass


class CalculateSolarIncidencePVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SurfaceOrientationModel,
    SurfaceTiltModel,
    LoggingModel,
):
    pass


class CalculateSolarIncidenceTimeSeriesJencoInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    SurfaceOrientationModel,
    SurfaceTiltModel,
    SurfaceInShadeModel,
    ComplementaryIncidenceAngleModel,
    ZeroNegativeSolarIncidenceAngleModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class ModelSolarIncidenceInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarTimeModelModel,
    SolarIncidenceModel,
    ComplementaryIncidenceAngleModel,
    SurfaceOrientationModel,
    SurfaceTiltModel,
    ApplyAtmosphericRefractionModel,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class ModelSolarIncidenceTimeSeriesInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    SolarTimeModelModel,
    SolarIncidenceModel,
    ComplementaryIncidenceAngleModel,
    SurfaceOrientationModel,
    SurfaceTiltModel,
    EarthOrbitModel,
    ZeroNegativeSolarIncidenceAngleModel,
    ArrayTypeModel,
    VerbosityModel,
    LoggingModel,
):
    pass


# Direct irradiance


class AdjustElevationInputModel(
    ElevationModel,
    LoggingModel,
):
    pass


class ModelSurfaceInShadeSeriesInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    HorizonProfileModel,
    SolarTimeModelModel,
    SolarPositionModelModel,
    ShadingModelModel,
    ApplyAtmosphericRefractionModel,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    ArrayTypeModel,
    # ArrayBackendModel,
    ValidateOutputModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateSurfaceInShadePvisInputModel(
    SolarAltitudeSeriesModel,
    SolarAzimuthSeriesModel,
    HorizonProfileModel,
    ArrayTypeModel,
    # ArrayBackendModel,
    ValidateOutputModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateHorizonHeightSeriesInputModel(
    SolarAzimuthSeriesModel,
    HorizonProfileModel,
    ArrayTypeModel,
    # ArrayBackendModel,
    ValidateOutputModel,
    VerbosityModel,
    LoggingModel,
):
    pass


class CalculateSurfaceInShadeSeriesInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    HorizonProfileModel,
    ShadingModelsModel,
    SolarTimeModelModel,
    SolarPositionModelModel,
    ApplyAtmosphericRefractionModel,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    BaseAngleOutputUnitsModel,
    ArrayTypeModel,
    # ArrayBackendModel,
    VerbosityModel,
    LoggingModel,
    ValidateOutputModel,
):
    pass


class CalculateOpticalAirMassInputModel(
    ElevationModel,
    RefractedSolarAltitudeModel,
    VerbosityModel,
    LoggingModel,
):
    pass

    # @field_validator("angle_units")
    # @classmethod
    # def validate_angle_output_units(cls, v):
    #     valid_units = DEGREES
    #     if not v == valid_units:
    #         raise ValueError(f"angle_units must be {valid_units}")
    #     return v


class CalculateOpticalAirMassTimeSeriesInputModel(
    ElevationModel,
    RefractedSolarAltitudeSeriesModel,
    LoggingModel,
):
    pass
