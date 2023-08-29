from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import confloat
from typing import Optional
from typing import Union
from typing import Sequence
from typing import List
from zoneinfo import ZoneInfo
from datetime import datetime
from datetime import time
from math import pi
from pydantic import validator
import numpy as np
from numpy import ndarray

from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels

from pvgisprototype.api.data_classes import EccentricityCorrectionFactor
from pvgisprototype.api.data_classes import PerigeeOffset
from pvgisprototype.api.data_classes import RefractedSolarAltitude
from pvgisprototype.api.data_classes import RefractedSolarZenith
from pvgisprototype.api.data_classes import SurfaceTilt
from pvgisprototype.api.data_classes import SurfaceOrientation
from pvgisprototype.api.data_classes import Latitude
from pvgisprototype.api.data_classes import Longitude
from pvgisprototype.api.data_classes import HourAngleSunrise
from pvgisprototype.api.data_classes import SolarTime
from pvgisprototype.api.data_classes import TrueSolarTime
from pvgisprototype.api.data_classes import EquationOfTime
from pvgisprototype.api.data_classes import FractionalYear
from pvgisprototype.api.data_classes import TimeOffset
from pvgisprototype.api.data_classes import EventTime
from pvgisprototype.api.data_classes import HourAngle
from pvgisprototype.api.data_classes import SolarAltitude
from pvgisprototype.api.data_classes import SolarAzimuth
from pvgisprototype.api.data_classes import CompassSolarAzimuth
from pvgisprototype.api.data_classes import SolarDeclination
from pvgisprototype.api.data_classes import SolarIncidence
from pvgisprototype.api.data_classes import SolarHourAngle
from pvgisprototype.api.data_classes import SolarZenith
from pvgisprototype.api.data_classes import SolarPosition
from pvgisprototype.api.data_classes import Elevation


# Where?

class LongitudeModel(BaseModel):
    longitude: Union[confloat(ge=-pi, le=pi), Longitude]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("longitude")
    def longitude_named_tuple(cls, input) -> Longitude:
        if isinstance(input, Longitude):
            return input
        elif isinstance(input, float):
            return Longitude(value=input, unit="radians")
        else:
            raise ValueError("Unsupported `longitude` type provided")


class LatitudeModel(BaseModel):
    latitude: Union[confloat(ge=-pi / 2, le=pi / 2), Latitude]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("latitude")
    def latitude_named_tuple(cls, input) -> Latitude:
        if isinstance(input, Latitude):
            return input
        elif isinstance(input, float):
            return Latitude(value=input, unit="radians")
        else:
            raise ValueError("Unsupported `latitude` type provided")


class BaseCoordinatesModel(
    LongitudeModel,
    LatitudeModel,
):
    pass


# When?

class BaseTimestampModel(BaseModel):
    timestamp: datetime
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseTimestampSeriesModel(BaseModel):
    timestamps: Union[datetime, Sequence[datetime]]
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseTimeModel(BaseTimestampModel):
    timezone: Optional[ZoneInfo] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError(
                "The `timezone` must be `None` or a valid `zoneinfo.ZoneInfo` object."
            )
        return v


class BaseTimeSeriesModel(BaseTimestampSeriesModel):
    timezone: Optional[ZoneInfo] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError(
                "The `timezone` must be `None` or a valid `zoneinfo.ZoneInfo` object."
            )
        return v


class TimeOffsetModel(BaseModel):
    time_offset_global: float = 0
    hour_offset: float = 0


class RandomTimeModel(BaseModel):
    random_time: bool


class BaseTimeOutputUnitsModel(BaseModel):
    time_output_units: Optional[str] = None

    @field_validator("time_output_units")
    @classmethod
    def validate_time_output_units(cls, v):
        valid_units = ["minutes", "seconds", "hours"]
        if v not in valid_units:
            raise ValueError(f"time_output_units must be one of {valid_units}")
        return v


# Angular units

class BaseAngleUnitsModel(BaseModel):
    angle_units: str

    @field_validator("angle_units")
    @classmethod
    def validate_angle_units(cls, v):
        valid_units = ["radians", "degrees"]
        if v not in valid_units:
            raise ValueError(f"angle_units must be one of {valid_units}")
        return v


class BaseAngleInternalUnitsModel(BaseModel):  # NOTE: Maybe deprecate
    angle_units: str = "radians"
    model_config = ConfigDict(
        description="""Angular units for internal calculations (degrees).""",
    )

    @field_validator("angle_units")
    @classmethod
    def validate_angle_units(cls, v):
        valid_units = ["radians"]
        if v not in valid_units:
            raise ValueError(f"angle_units must be {valid_units}")
        return v


# class BaseOutputUnitsModel(BaseModel):
#     output_units: str

#     @field_validator("output_units")
#     @classmethod
#     def validate_angle_output_units(cls, v):
#         valid_units = ["radians", "degrees"]
#         if v not in valid_units:
#             raise ValueError(f"angle_output_units must be one of {valid_units}")


class BaseAngleOutputUnitsModel(BaseModel):
    angle_output_units: str
    model_config = ConfigDict(
        description="""Output units for solar geometry variables (degrees or radians).""",
    )

    @field_validator("angle_output_units")
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = ["radians", "degrees"]
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v


# Solar geometry

class SolarDeclinationModel(BaseModel):
    solar_declination: Union[
        confloat(ge=0, le=pi), SolarDeclination
    ]
    model_config = ConfigDict(
        description="""Solar declination (δ) is the angle between the equator and a
        line drawn from the centre of the Earth to the centre of the sun.""",
    )

    @field_validator("solar_declination")
    def solar_declination_named_tuple(cls, input) -> SolarDeclination:
        if isinstance(input, SolarDeclination):
            return input
        elif isinstance(input, float):
            return SolarDeclination(value=input, unit="radians")
        else:
            raise ValueError("Unsupported solar_declination type provided")


class SolarPositionModel(BaseModel):
    model: SolarPositionModels = SolarPositionModels.skyfield
    apply_atmospheric_refraction: bool = True


class DaysInAYearModel(BaseModel):
    days_in_a_year: float = 365.25  # TODO: Validator for this value if never changes


class EarthOrbitModel(DaysInAYearModel):
    eccentricity_correction_factor: float = 0.03344
    perigee_offset: float = 0.048869


class SolarTimeModelModel(BaseModel):  # ModelModel is intentional!
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield


class SolarTimeModel(BaseModel):
    # solar_time: Union[confloat(ge=0, le=24), SolarTime]
    solar_time: Union[time, datetime]
    model_config = ConfigDict(
        description="""The solar time (ST) is a calculation of the passage of time based
        on the position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds.""",
    )


# Solar surface

class SurfaceTiltModel(BaseModel):
    surface_tilt: Union[confloat(ge=-pi / 2, le=pi / 2), SurfaceTilt]
    model_config = ConfigDict(
        description="""Surface tilt (or slope) (β) is the angle between the inclined
        surface (slope) and the horizontal plane.""",
    )

    @field_validator("surface_tilt")
    def surface_tilt_named_tuple(cls, input) -> SurfaceTilt:
        if isinstance(input, SurfaceTilt):
            return input
        elif isinstance(input, float):
            return SurfaceTilt(value=input, unit="radians")
        else:
            raise ValueError("Unsupported surface_tilt type provided")


class SurfaceOrientationModel(BaseModel):
    surface_orientation: Union[confloat(ge=0, le=2 * pi), SurfaceOrientation] = 180
    model_config = ConfigDict(
        description="""Surface orientation (also known as aspect or azimuth) is the projected angle measured clockwise from true north"""
    )

    @field_validator("surface_orientation")
    def surface_orientation_named_tuple(cls, input) -> SurfaceOrientation:
        if isinstance(input, SurfaceOrientation):
            return input
        elif isinstance(input, float):
            return SurfaceOrientation(value=input, unit="radians")
        else:
            raise ValueError("Unsupported surface_orientation type provided")


# class HourAngleModel(BaseModel):
#     hour_angle: Union[confloat(ge=0, le=1), HourAngle]
#     model_config = ConfigDict(
#         description="""Solar hour angle.""",
#     )

class SolarHourAngleModel(BaseModel):
    solar_hour_angle: Union[confloat(ge=0, le=2*pi), SolarHourAngle]
    model_config = ConfigDict(
        description="""Solar hour angle.""",
    )

    @field_validator("solar_hour_angle")
    def solar_hour_angle_named_tuple(cls, input) -> SolarHourAngle:
        if isinstance(input, SolarHourAngle):
            return input
        elif isinstance(input, float):
            return SolarHourAngle(value=input, unit="radians")
        else:
            raise ValueError("Unsupported solar_hour_angle type provided")


class SolarHourAngleSeriesModel(BaseModel):
    solar_hour_angle_series: Union[Sequence[SolarHourAngle], ndarray]
    model_config = ConfigDict(
        description="Solar hour angle series.",
        arbitrary_types_allowed=True,
    )

    @field_validator("solar_hour_angle_series")
    def solar_hour_angle_named_tuple(cls, input) -> Union[Sequence[SolarHourAngle], ndarray]:
        if isinstance(input, list) and all(isinstance(item, SolarHourAngle) for item in input):
            return input
        elif isinstance(input, ndarray) and all(isinstance(item, SolarHourAngle) for item in input):
            return input
        else:
            raise ValueError("Unsupported solar_hour_angle_series type provided")


class ApplyAtmosphericRefraction(BaseModel):
    apply_atmospheric_refraction: bool


class RefractedSolarAltitudeInput(BaseModel):
    refracted_solar_altitude: float

    @field_validator("refracted_solar_altitude")
    def refracted_solar_altitude_named_tuple(cls, input) -> RefractedSolarAltitude:
        if isinstance(input, RefractedSolarAltitude):
            return input
        elif isinstance(input, float):
            return RefractedSolarAltitude(value=input, unit="radians")
        else:
            raise ValueError("Unsupported `refracted_solar_altitude` type provided")


class RefractedSolarZenithInput(BaseModel):
    refracted_solar_zenith: Optional[float]

    @field_validator("refracted_solar_zenith")
    def refracted_solar_zenith_named_tuple(cls, input) -> RefractedSolarZenith:
        if isinstance(input, RefractedSolarZenith):
            return input
        elif isinstance(input, float):
            return RefractedSolarZenith(value=input, unit="radians")
        else:
            raise ValueError("Unsupported `refracted_solar_zenith` type provided")


# class SolarTimeInput(
#         ValidatedInputToDict,
#         SolarPositionModel
# ):
#     pass


# class SolarIncidenceInput(
#     SolarTimeInput,
#     SurfaceTiltModel,
#     SurfaceOrientationModel,
# ):
#     random_time: bool = False
#     hour_angle: float
#     rounding_places: int = 5
#     verbose: bool = False


class ElevationModel(BaseModel):
    elevation: Union[confloat(ge=0, le=8848), Elevation]
    model_config = ConfigDict(
            arbitrary_types_allowed=True,
            description="""Elevation""",
        )

    @field_validator('elevation')
    def elevation_named_tuple(cls, input) -> Elevation:
        if isinstance(input, Elevation):
            return input
        elif isinstance(input, float):
            return Elevation(value=input, unit='meters')
        else:
            raise ValueError("Unsupported type provided for `elevation`")

        # valid_units = "meters"
        # if not unit == valid_units:
        #     raise ValueError(f"elevation must be given in {valid_units}")
        # return v

class IrradianceInputModel(BaseModel):
    linke_turbidity_factor: confloat(ge=0, le=8)  # help='A measure of atmospheric turbidity',
    optical_air_mass: float
    extraterrestial_irradiance: confloat(ge=1360) = 1360.8 # description="The average solar radiation at the top of the atmosphere ~1360.8 W/m^2 (Kopp, 2011)")
