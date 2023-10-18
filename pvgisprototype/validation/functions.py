# Generic input/output
from pvgisprototype.validation.parameters import VerbosityModel

# Where?
from pvgisprototype.validation.parameters import LatitudeModel
from pvgisprototype.validation.parameters import LongitudeModel
from pvgisprototype.validation.parameters import BaseCoordinatesModel
from pvgisprototype.validation.parameters import ElevationModel

# When?
from pvgisprototype.validation.parameters import BaseTimestampModel
from pvgisprototype.validation.parameters import BaseTimeModel
from pvgisprototype.validation.parameters import BaseTimeSeriesModel

# Atmospheric effects
from pvgisprototype.validation.parameters import ApplyAtmosphericRefractionModel
from pvgisprototype.validation.parameters import RefractedSolarZenithModel

# Earth orbit
from pvgisprototype.validation.parameters import EarthOrbitModel

# Solar time
from pvgisprototype.validation.parameters import SolarTimeModelModel
from pvgisprototype.validation.parameters import SolarTimeModel
from pvgisprototype.validation.parameters import TimeOffsetModel
from pvgisprototype.validation.parameters import HourOffsetModel
from pvgisprototype.validation.parameters import BaseTimeOutputUnitsModel
from pvgisprototype.validation.parameters import RandomTimeSeriesModel

# Solar geometry
from pvgisprototype.validation.parameters import RefractedSolarAltitudeModel
from pvgisprototype.validation.parameters import RefractedSolarAltitudeSeriesModel
from pvgisprototype.validation.parameters import SolarDeclinationModel
from pvgisprototype.validation.parameters import SolarPositionModel
from pvgisprototype.validation.parameters import SolarHourAngleModel

# Solar Surface
from pvgisprototype.validation.parameters import SurfaceTiltModel
from pvgisprototype.validation.parameters import SurfaceOrientationModel

# Incidence
from pvgisprototype.validation.parameters import SolarIncidenceModel

# Output
from pvgisprototype.validation.parameters import BaseAngleUnitsModel
from pvgisprototype.validation.parameters import BaseAngleInternalUnitsModel
from pvgisprototype.validation.parameters import BaseAngleOutputUnitsModel

# Validator
from typing import Type
from pydantic import BaseModel
from typing import Callable
from functools import wraps


def validate_with_pydantic(input_model: Type[BaseModel]) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) == 1 and isinstance(args[0], input_model):
                # If the passed argument is already an instance of the expected model, skip validation
                validated_input = args[0]
            else:
                input_data = {**kwargs, **dict(zip(func.__annotations__.keys(), args))}
                validated_input = input_model(**input_data)
            dictionary_input = {}
            for k, v in validated_input:
                dictionary_input[k] = v
            return func(**dictionary_input)

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
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    SolarTimeModelModel,
    VerbosityModel,
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


class CalculateSolarTimeEphemInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
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

class CalculateSolarHourAngleInputModel(
    SolarTimeModel,
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


class SolarHourAnglePVLIBInput(
    LongitudeModel,
    BaseTimestampModel,
):
    pass


class SolarHourAngleSkyfieldInput(
    BaseCoordinatesModel,
    BaseTimestampModel,
):
    pass


class SolarHourAngleSkyfieldInput(
    BaseCoordinatesModel,
    BaseTimestampModel,
):
    pass


# Solar geometry

class CalculateSolarAltitudePVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    ApplyAtmosphericRefractionModel,
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
    BaseTimeModel,
):
    pass


class CalculateSolarAzimuthPVLIBInputModel(
    CalculateSolarAltitudePVLIBInputModel
):
    pass


class CalculateSolarDeclinationPVLIBInput(
    BaseTimestampModel,
):
    pass


class CalculateSolarDeclinationSkyfieldInput(
    BaseTimestampModel,
    BaseAngleOutputUnitsModel,
):
    pass

class CalculateSolarDeclinationSkyfieldInput(
    BaseTimestampModel,
):
    pass

class CalculateSolarZenithPVLIBInputModel(
    CalculateSolarAltitudePVLIBInputModel
):
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
    ApplyAtmosphericRefractionModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    SolarTimeModelModel,
):
    pass


class ModelSolarAltitudeInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarPositionModel,
    SolarTimeModelModel,
    ApplyAtmosphericRefractionModel,
    EarthOrbitModel,
):
    pass


class ModelSolarAltitudeTimeSeriesInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    SolarPositionModel,
    ApplyAtmosphericRefractionModel,
):
    pass


class ModelSolarAzimuthInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarPositionModel,
    SolarTimeModelModel,
    ApplyAtmosphericRefractionModel,
    VerbosityModel,
):
    pass


class ModelSolarPositionInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarPositionModel,
    SolarTimeModelModel,
    ApplyAtmosphericRefractionModel,
    EarthOrbitModel,
    VerbosityModel,
):
    pass


# Solar incidence angle

class CalculateRelativeLongitudeInputModel(
    LatitudeModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
):
    pass


class CalculateSolarIncidenceInputModel(
    LatitudeModel,
    SolarDeclinationModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
):
    pass


class CalculateSolarIncidencePVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
):
    pass


class CalculateSolarIncidenceJencoInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    EarthOrbitModel,
    VerbosityModel,
):
    pass


class CalculateSolarIncidenceTimeSeriesJencoInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
    VerbosityModel,
):
    pass


class ModelSolarIncidenceInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarTimeModelModel,
    SolarIncidenceModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    ApplyAtmosphericRefractionModel,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    VerbosityModel,
):
    pass


class ModelSolarIncidenceTimeSeriesInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    SolarTimeModelModel,
    SolarIncidenceModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    EarthOrbitModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
    VerbosityModel,
):
    pass


# Direct irradiance

class AdjustElevationInputModel(
    ElevationModel
):
    pass


class CalculateOpticalAirMassInputModel(
    ElevationModel,
    RefractedSolarAltitudeModel,
):
    pass

    # @field_validator("angle_units")
    # @classmethod
    # def validate_angle_output_units(cls, v):
    #     valid_units = "degrees"
    #     if not v == valid_units:
    #         raise ValueError(f"angle_units must be {valid_units}")
    #     return v


class CalculateOpticalAirMassTimeSeriesInputModel(
    ElevationModel,
    RefractedSolarAltitudeSeriesModel,
):
    pass
