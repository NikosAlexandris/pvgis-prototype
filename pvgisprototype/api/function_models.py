# Where?
from .parameter_models import LatitudeModel
from .parameter_models import BaseCoordinatesModel

# When?
from .parameter_models import BaseTimestampModel
from .parameter_models import BaseTimeModel

# Atmospheric effects
from .parameter_models import ApplyAtmosphericRefraction
from .parameter_models import RefractedSolarZenithInput

# Earth orbit
from .parameter_models import DaysInAYearModel
from .parameter_models import EarthOrbitModel

# Time
from .parameter_models import SolarTimeModelModel
from .parameter_models import SolarTimeModel
from .parameter_models import TimeOffsetModel
from .parameter_models import BaseTimeOutputUnitsModel
from .parameter_models import RandomTimeModel


from .parameter_models import ElevationModel

# Solar geometry

from .parameter_models import RefractedSolarAltitudeInput
from .parameter_models import SolarDeclinationModel
from .parameter_models import SolarPositionModel

# Solar Surface

from .parameter_models import SurfaceTiltModel
from .parameter_models import SurfaceOrientationModel

# Output

from .parameter_models import BaseAngleUnitsModel
from .parameter_models import BaseAngleInternalUnitsModel
from .parameter_models import BaseAngleOutputUnitsModel


# Solar declination

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
    EarthOrbitModel,
    TimeOffsetModel,
    SolarTimeModelModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarTimePVGISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    EarthOrbitModel,
    TimeOffsetModel,
):
    pass
 

class CalculateSolarTimeEoTInputModel(
    ModelSolarTimeInputModel
):
    pass


class CalculateSolarTimeEphemInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
):
    verbose: bool


# Hour angle

class CalculateHourAngleInputModel(
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


# Solar geometry

class CalculateSolarAltitudePVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    ApplyAtmosphericRefraction,
    RefractedSolarZenithInput,
    EarthOrbitModel,
    TimeOffsetModel,
    SolarTimeModelModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAzimuthPVISInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    ApplyAtmosphericRefraction,
    RefractedSolarZenithInput,
    EarthOrbitModel,
    TimeOffsetModel,
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
    RefractedSolarZenithInput,
    EarthOrbitModel,
    TimeOffsetModel,
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
    RefractedSolarZenithInput,
    EarthOrbitModel,
    TimeOffsetModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class ModelSolarPositionInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    SolarPositionModel,
    SolarTimeModelModel,
    ApplyAtmosphericRefraction,
    RefractedSolarZenithInput,
    EarthOrbitModel,
    TimeOffsetModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
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
    hour_angle: float


class CalculateSolarIncidenceJencoInputModel(
    BaseCoordinatesModel,
    BaseTimeModel,
    RandomTimeModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    EarthOrbitModel,
    BaseTimeOutputUnitsModel,
    BaseAngleInternalUnitsModel,
    BaseAngleOutputUnitsModel,
):
    hour_angle: float


# Direct irradiance

class CalculateOpticalAirMassInputModel(
    ElevationModel,
    RefractedSolarAltitudeInput,
    BaseAngleUnitsModel
):
    pass

    # @field_validator("angle_units")
    # @classmethod
    # def validate_angle_output_units(cls, v):
    #     valid_units = "degrees"
    #     if not v == valid_units:
    #         raise ValueError(f"angle_units must be {valid_units}")
    #     return v
