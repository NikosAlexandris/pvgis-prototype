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
from pvgisprototype.validation.parameters import ApplyAtmosphericRefraction
from pvgisprototype.validation.parameters import RefractedSolarZenithModel

# Earth orbit
from pvgisprototype.validation.parameters import DaysInAYearModel
from pvgisprototype.validation.parameters import EarthOrbitModel

# Solar time
from pvgisprototype.validation.parameters import SolarTimeModelModel
from pvgisprototype.validation.parameters import SolarTimeModel
from pvgisprototype.validation.parameters import TimeOffsetModel
from pvgisprototype.validation.parameters import HourOffsetModel
from pvgisprototype.validation.parameters import BaseTimeOutputUnitsModel
from pvgisprototype.validation.parameters import RandomTimeModel
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
    BaseAngleInternalUnitsModel,
):
    pass


class CalculateSolarDeclinationPVISInputModel(
    BaseTimeModel,
    EarthOrbitModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarDeclinationHargreavesInputModel(
    BaseTimestampModel,
    DaysInAYearModel,
    BaseAngleOutputUnitsModel,
):
    pass


# Solar time

class ModelSolarTimeInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    SolarTimeModelModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
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
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
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
 

class CalculateSolarTimeEoTInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    EarthOrbitModel,
    TimeOffsetModel,
    VerbosityModel,
):
    pass


class CalculateSolarTimeEphemInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    VerbosityModel,
):
    pass


# Hour angle

class CalculateHourAngleInputModel(
    SolarTimeModel,  # Parameter
    BaseAngleOutputUnitsModel,
):
    pass

class SolarHourAnglePvisInput(
    SolarTimeModel,  # Parameter
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarHourAnglePVISInputModel(
    SolarTimeModel,  # Parameter
    BaseAngleOutputUnitsModel,
):
    pass


# rename to : CalculateEventHourAngleInputModel
class CalculateHourAngleSunriseInputModel(
    LatitudeModel,
    SurfaceTiltModel,
    SolarDeclinationModel,
    BaseAngleOutputUnitsModel,
):
    pass


class SolarHourAngleSunrisePvisInput(
    CalculateHourAngleSunriseInputModel
):
    pass


class SolarHourAnglePVLIBInput(
    LongitudeModel,
    BaseTimestampModel,
    BaseAngleOutputUnitsModel,
):
    pass


class SolarHourAngleSkyfieldInput(
    BaseCoordinatesModel,
    BaseTimestampModel,
    BaseAngleOutputUnitsModel,
):
    pass


# Solar geometry

class CalculateSolarAltitudePVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    ApplyAtmosphericRefraction,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    SolarTimeModelModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAltitudePVLIBInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAzimuthPVLIBInputModel(
    CalculateSolarAltitudePVLIBInputModel
):
    pass

class CalculateSolarDeclinationPVLIBInput(
    BaseTimestampModel,
    BaseAngleOutputUnitsModel,
):
    pass

class CalculateSolarDeclinationSkyfieldInput(
    BaseTimestampModel,
    BaseAngleOutputUnitsModel,
):
    pass

class CalculateSolarZenithPVLIBInputModel(
    CalculateSolarAltitudePVLIBInputModel
):
    pass


class CalculateSolarAzimuthPVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    ApplyAtmosphericRefraction,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    SolarTimeModelModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class ModelSolarAltitudeInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarPositionModel,
    SolarTimeModelModel,
    ApplyAtmosphericRefraction,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class ModelSolarAltitudeTimeSeriesInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    SolarPositionModel,
    SolarTimeModelModel,
    ApplyAtmosphericRefraction,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class ModelSolarAzimuthInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarPositionModel,
    SolarTimeModelModel,
    ApplyAtmosphericRefraction,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
    VerbosityModel,
):
    pass


class ModelSolarPositionInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarPositionModel,
    SolarTimeModelModel,
    ApplyAtmosphericRefraction,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
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
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarIncidencePVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarIncidenceJencoInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarHourAngleModel,
    RandomTimeModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    EarthOrbitModel,
    BaseTimeOutputUnitsModel,
    BaseAngleInternalUnitsModel,
    BaseAngleOutputUnitsModel,
    VerbosityModel,
):
    pass


class CalculateSolarIncidenceTimeSeriesJencoInputModel(
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    RandomTimeSeriesModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    EarthOrbitModel,
    BaseTimeOutputUnitsModel,
    BaseAngleInternalUnitsModel,
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
