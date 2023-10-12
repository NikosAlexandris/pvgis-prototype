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
    BaseTimeModel,
    EarthOrbitModel,
):
    pass


class CalculateSolarDeclinationHargreavesInputModel(
    BaseTimestampModel,
    DaysInAYearModel,
):
    pass


class CalculateSolarDeclinationNOAAInput(
    BaseTimestampModel,
):
    pass


class ModelSolarDeclinationInputModel(
    BaseTimeModel,
    EarthOrbitModel,
    DaysInAYearModel,
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
 

class CalculateSolarTimeEoTInputModel(
    LongitudeModel,
    BaseTimeModel,
    VerbosityModel,
):
    pass


class CalculateSolarTimeEphemInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    VerbosityModel,
):
    verbose: int = 0


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

class CalculateHourAngleInputModel(
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


# rename to : CalculateEventHourAngleInputModel
class CalculateHourAngleSunriseInputModel(
    LatitudeModel,
    SurfaceTiltModel,
    SolarDeclinationModel,
):
    pass


class CalculateHourAngleSunrisePVISInputModel(
    CalculateHourAngleSunriseInputModel
):
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



# Solar geometry

class CalculateSolarAltitudePVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    EarthOrbitModel,
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
    SolarTimeModelModel,
    ApplyAtmosphericRefractionModel,
    RefractedSolarZenithModel,
    EarthOrbitModel,
    TimeOffsetModel,
    HourOffsetModel,
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
    DaysInAYearModel,
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
    RandomTimeModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    EarthOrbitModel,
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


class CalculateOpticalAirMassTimeSeriesInputModel(
    ElevationModel,
    RefractedSolarAltitudeSeriesModel,
):
    pass
