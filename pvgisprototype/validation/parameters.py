from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import confloat
from typing import Union
from typing import Optional
from typing import Sequence
from zoneinfo import ZoneInfo
from datetime import datetime
from math import pi
from numpy import ndarray
from pvgisprototype import RefractedSolarAltitude
from pvgisprototype import RefractedSolarZenith
from pvgisprototype import SurfaceTilt
from pvgisprototype import SurfaceOrientation
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype import SolarDeclination
from pvgisprototype import SolarHourAngle
from pvgisprototype import Elevation
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.api.geometry.models import SolarTimeModels


MESSAGE_UNSUPPORTED_TYPE = "Unsupported type provided for "


# Generic input/output


class VerbosityModel(BaseModel):
    verbose: int = 0


# Where?

class LongitudeModel(BaseModel):
    longitude: Union[confloat(ge=-pi, le=pi), Longitude]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("longitude")
    def validate_longitude(cls, input) -> Longitude:
        if isinstance(input, Longitude):
            return input
        elif isinstance(input, float):
            return Longitude(value=input, unit="radians")
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `longitude`")


class LatitudeModel(BaseModel):
    latitude: Union[confloat(ge=-pi / 2, le=pi / 2), Latitude]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("latitude")
    def validate_latitude(cls, input) -> Latitude:
        if isinstance(input, Latitude):
            return input
        elif isinstance(input, float):
            return Latitude(value=input, unit="radians")
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `latitude`")


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

    @field_validator('timestamps')
    def check_empty_list(cls, value):
        if isinstance(value, list) and not value:
            raise ValueError('Empty list of timestamps provided')
        return value


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


class HourOffsetModel(BaseModel):
    hour_offset: float = 0


class RandomTimeModel(BaseModel):
    random_time: bool


class RandomTimeSeriesModel(BaseModel):
    random_time_series: bool


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
    angle_units: str = 'radians'

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
    solar_declination: Union[confloat(ge=0, le=pi), SolarDeclination]
    model_config = ConfigDict(
        description="""Solar declination (δ) is the angle between the equator and a
        line drawn from the centre of the Earth to the centre of the sun.""",
    )

    @field_validator("solar_declination")
    def validate_solar_declination(cls, input) -> SolarDeclination:
        if isinstance(input, SolarDeclination):
            return input
        elif isinstance(input, float):
            return SolarDeclination(value=input, unit="radians")
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `solar_declination`")


class SolarPositionModel(BaseModel):
    solar_position_model: SolarPositionModels = SolarPositionModels.skyfield
    apply_atmospheric_refraction: bool = True


class DaysInAYearModel(BaseModel):
    days_in_a_year: float = DAYS_IN_A_YEAR  # TODO: Validator


class EarthOrbitModel(DaysInAYearModel):
    perigee_offset: float = PERIGEE_OFFSET
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR


class SolarTimeModelModel(BaseModel):  # ModelModel is intentional!
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield


class SolarTimeModel(BaseModel):
    solar_time: datetime
    model_config = ConfigDict(
        description="""The solar time (ST) is a calculation of the passage of time based
        on the position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds.""",
    )



# Solar surface

class SurfaceTiltModel(BaseModel):
    surface_tilt: Union[confloat(ge=-pi / 2, le=pi / 2), SurfaceTilt] = SURFACE_TILT_DEFAULT
    model_config = ConfigDict(
        description="""Surface tilt (or slope) (β) is the angle between the inclined
        surface (slope) and the horizontal plane.""",
    )

    @field_validator("surface_tilt")
    def validate_surface_tilt(cls, input) -> SurfaceTilt:
        if isinstance(input, SurfaceTilt):
            return input
        elif isinstance(input, float):
            return SurfaceTilt(value=input, unit="radians")
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `surface_tilt`")


class SurfaceOrientationModel(BaseModel):
    surface_orientation: Union[confloat(ge=0, le=2 * pi), SurfaceOrientation] = 180
    model_config = ConfigDict(
        description="""Surface orientation (also known as aspect or azimuth) is the projected angle measured clockwise from true north"""
    )

    @field_validator("surface_orientation")
    def validate_surface_orientation(cls, input) -> SurfaceOrientation:
        if isinstance(input, SurfaceOrientation):
            return input
        elif isinstance(input, float):
            return SurfaceOrientation(value=input, unit="radians")
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `surface_orientation`")


class SolarHourAngleModel(BaseModel):
    solar_hour_angle: Union[confloat(ge=-pi, le=pi), SolarHourAngle]
    model_config = ConfigDict(
        description="""Solar hour angle""",
    )

    @field_validator("solar_hour_angle")
    def validate_solar_hour_angle(cls, input) -> SolarHourAngle:
        if isinstance(input, SolarHourAngle):
            return input
        elif isinstance(input, float):
            return SolarHourAngle(value=input, unit="radians")
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `solar_hour_angle`")


class SolarHourAngleSeriesModel(BaseModel):
    solar_hour_angle_series: Union[Sequence[SolarHourAngle], ndarray]
    model_config = ConfigDict(
        description="Solar hour angle series.",
        arbitrary_types_allowed=True,
    )

    @field_validator("solar_hour_angle_series")
    def validate_solar_hour_angle(
        cls, input
    ) -> Union[Sequence[SolarHourAngle], ndarray]:
        if isinstance(input, list) and all(
            isinstance(item, SolarHourAngle) for item in input
        ):
            return input
        elif isinstance(input, ndarray) and all(
            isinstance(item, SolarHourAngle) for item in input
        ):
            return input
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `solar_hour_angle_series`")


class ApplyAtmosphericRefractionModel(BaseModel):
    apply_atmospheric_refraction: bool


class RefractedSolarAltitudeModel(BaseModel):
    refracted_solar_altitude: Union[float, RefractedSolarAltitude]

    @field_validator("refracted_solar_altitude")
    def validate_refracted_solar_altitude(cls, input) -> RefractedSolarAltitude:
        if isinstance(input, RefractedSolarAltitude):
            return input
        elif isinstance(input, float):
            return RefractedSolarAltitude(value=input, unit="radians")
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `refracted_solar_altitude`")


class RefractedSolarAltitudeSeriesModel(BaseModel):
    refracted_solar_altitude_series: Union[RefractedSolarAltitude, Sequence[RefractedSolarAltitude]]

    # @field_validator("refracted_solar_altitude")
    # def validate_refracted_solar_altitude(cls, input) -> RefractedSolarAltitude:
    #     if isinstance(input, RefractedSolarAltitude):
    #         return input
    #     elif isinstance(input, float):
    #         return RefractedSolarAltitude(value=input, unit="radians")
    #     else:
    #         raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `refracted_solar_altitude`")


class RefractedSolarZenithModel(BaseModel):
    refracted_solar_zenith: Union[Optional[float], RefractedSolarZenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT

    @field_validator("refracted_solar_zenith")
    def validate_refracted_solar_zenith(cls, input) -> RefractedSolarZenith:
        if isinstance(input, RefractedSolarZenith):
            return input
        elif isinstance(input, float):
            return RefractedSolarZenith(value=input, unit="radians")
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `refracted_solar_zenith`")



class ElevationModel(BaseModel):
    elevation: Union[confloat(ge=0, le=8848), Elevation]
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        description="""Elevation""",
    )

    @field_validator("elevation")
    def validate_elevation(cls, input) -> Elevation:
        if isinstance(input, Elevation):
            return input
        elif isinstance(input, float):
            return Elevation(value=input, unit="meters")
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `elevation`")

        # valid_units = "meters"
        # if not unit == valid_units:
        #     raise ValueError(f"elevation must be given in {valid_units}")
        # return v


class IrradianceInputModel(BaseModel):
    linke_turbidity_factor: confloat(
        ge=0, le=8
    )  # help='A measure of atmospheric turbidity',
    optical_air_mass: float
    extraterrestial_irradiance: confloat(
        ge=1360
    ) = 1360.8  # description="The average solar radiation at the top of the atmosphere ~1360.8 W/m^2 (Kopp, 2011)")
