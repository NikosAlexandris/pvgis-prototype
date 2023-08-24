from .parameter_models import ValidatedInputToDict

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
    ValidatedInputToDict,
    BaseTimestampModel,
    BaseAngleInternalUnitsModel,
):
    pass


class CalculateSolarDeclinationPVISInputModel(
    ValidatedInputToDict,
    BaseTimeModel,
    EarthOrbitModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarDeclinationHargreavesInputModel(
    ValidatedInputToDict,
    BaseTimestampModel,
    DaysInAYearModel,
    BaseAngleOutputUnitsModel,
):
    pass


# Solar time

class ModelSolarTimeInputModel(
    ValidatedInputToDict,
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
    ValidatedInputToDict,
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
    ValidatedInputToDict,
    BaseCoordinatesModel,
    BaseTimeModel,
):
    verbose: bool


# Hour angle

class CalculateHourAngleInputModel(
    ValidatedInputToDict,
    SolarTimeModel,  # Parameter
    BaseAngleOutputUnitsModel,
):
    pass


# rename to : CalculateEventHourAngleInputModel
class CalculateHourAngleSunriseInputModel(
    ValidatedInputToDict,
    LatitudeModel,
    SurfaceTiltModel,
    SolarDeclinationModel,
    BaseAngleOutputUnitsModel,
):
    pass


# Solar geometry

class CalculateSolarAltitudePVISInputModel(
    ValidatedInputToDict,
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
    ValidatedInputToDict,
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
    ValidatedInputToDict,
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
    ValidatedInputToDict,
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
    ValidatedInputToDict,
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
    ValidatedInputToDict,
    LatitudeModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
):
    pass


class CalculateSolarIncidenceInputModel(
    ValidatedInputToDict,
    LatitudeModel,
    SolarDeclinationModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    BaseAngleOutputUnitsModel,
):
    hour_angle: float


class CalculateSolarIncidenceJencoInputModel(
    ValidatedInputToDict,
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
    ValidatedInputToDict,
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
