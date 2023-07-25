from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import confloat
from typing import Optional
from zoneinfo import ZoneInfo
from datetime import datetime

from .geometry.solar_models import SolarPositionModels

class BaseTimestampInputModel(BaseModel):
    timestamp: datetime
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseTimeInputModel(BaseTimestampInputModel):
    timezone: Optional[ZoneInfo] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError("The `timezone` must be a valid `zoneinfo.ZoneInfo` object.")
        return v


class RandomTimeInputModel(BaseModel):
    random_time: bool

class TimeOffsetModel(BaseModel):
    time_offset_global: float = 0
    hour_offset: float = 0

class BaseTimeOutputUnitsModel(BaseModel):
    time_output_units: Optional[str] = None

    @field_validator('time_output_units')
    @classmethod
    def validate_time_output_units(cls, v):
        valid_units = ['minutes', 'seconds', 'hours']
        if v not in valid_units:
            raise ValueError(f"time_output_units must be one of {valid_units}")
        return v


class BaseAngleOutputUnitsModel(BaseModel):
    angle_output_units: str

    @field_validator('angle_output_units')
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = ['radians', 'degrees']
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v


class BaseAngleInternalUnitsModel(BaseModel):                                               # NOTE: Maybe deprecate
    angle_units: str
    model_config = ConfigDict(
        description="""Angular units for internal calculations (degrees).""",
    )

    @field_validator('angle_units')
    @classmethod
    def validate_angle_units(cls, v):
        valid_units = ['radians']
        if v not in valid_units:
            raise ValueError(f"angle_units must be {valid_units}")
        return v
class Longitude(BaseModel):
    longitude: confloat(ge=-pi, le=pi)
    model_config = ConfigDict(
        json_schema_extra = {
            "units": "radians",
        },
    )
    # @validator("longitude", always=True)                                 # TODO: Add me to manual
    # def longitude_to_radians(cls, v: float,) -> float:
    #     return math.radians(v)


class Latitude(BaseModel):
    latitude: confloat(ge=-pi/2, le=pi/2)
    model_config = ConfigDict(
        json_schema_extra = {
            "units": "radians",
        },
    )
    # @validator("latitude", always=True)                                 # TODO: Add me to manual
    # def latitude_to_radians(cls, v: float,) -> float:
    #     return math.radians(v)


class SolarPositionInputModel(BaseModel):
    model: SolarPositionModels
    apply_atmospheric_refraction: bool = True
class SolarTimeInputModel(SolarPositionInputModel):
    refracted_solar_zenith: float = 1.5853349194640094,  # radians
class BaseCoordinatesInputModel(Longitude, Latitude):
    pass


class SolarAltitudeInput(
    BaseCoordinatesInputModel,
    BaseTimeInputModel,
    BaseAngleOutputUnitsModel,
):
    pass


class SolarAzimuthInput(SolarAltitudeInput):
    pass


class EarthOrbitInputModel(BaseModel):
    days_in_a_year: float = 365.25
    orbital_eccentricity: float = 0.03344
    perigee_offset: float = 0.048869


class SolarDeclinationInput(
        # timestamp: Annotated[Optional[datetime], typer.Argument(
        #     help='Timestamp',
        #     default_factory=now_utc_datetimezone)],
        # timezone: Annotated[Optional[str], typer.Option(
        #     help='Timezone',
        #     callback=convert_to_timezone)] = None,
        BaseTimeInputModel,
        # days_in_a_year: float = 365.25,
        # orbital_eccentricity: float = 0.03344,
        # perigee_offset: float = 0.048869,
        EarthOrbitInputModel,
        # output_units: Annotated[str, typer.Option(
        #     '-o',
        #     '--output-units',
        #     show_default=True,
        #     case_sensitive=False,
        #     help="Output units for solar declination (degrees or radians)")] = 'radians',
        BaseAngleOutputUnitsModel,
        ):
    debug(locals())
    pass


class SolarTimeModel(BaseModel):
    solar_time: confloat(ge=0, le=86400)
    model_config = ConfigDict(
        description="""The solar time (ST) is a calculation of the passage of time based
        on the position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds.""",
        json_schema_extra = {
            "units": "seconds",
        },
    )

class SurfaceTilt(BaseModel):
    surface_tilt: Optional[confloat(ge=0, le=90)] = 0

class SolarDeclination(BaseModel):
    solar_declination: Optional[confloat(ge=-90, le=90)] = 0          # XXX: Default value changed from 180 to 0


class HourAngleInput(
        # solar_time: Annotated[float, typer.Argument(
        #     help='The solar time in decimal hours on a 24 hour base',
        #     callback=convert_hours_to_seconds)],
        SolarTime,
        # output_units: Annotated[str, typer.Option(
        #     '-u',
        #     '--units',
        #     show_default=True,
        #     case_sensitive=False,
        #     help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        BaseAngleOutputUnitsModel,
        ):
    pass


class HourAngleSunriseInput(
        # latitude: Annotated[Optional[float], typer.Argument(
        #     min=-90, max=90)],
        Latitude,
        # surface_tilt: Annotated[Optional[float], typer.Argument(
        #     min=0, max=90)] = 0,
        SurfaceTilt,
        # solar_declination: Annotated[Optional[float], typer.Argument(
        #     min=-90, max=90)] = 180,                                  # XXX: Default value changed from 180 to 0
        SolarDeclination,
        # output_units: Annotated[str, typer.Option(
        #     '-u',
        #     '--units',
        #     show_default=True,
        #     case_sensitive=False,
        #     help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        BaseAngleOutputUnitsModel,
        ):
    pass
