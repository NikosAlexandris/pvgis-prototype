from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import confloat
from typing import Optional
from zoneinfo import ZoneInfo
from datetime import datetime


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


class BaseTimeOutputUnitsModel(BaseModel):
    time_output_units: Optional[str] = None

    @field_validator('time_output_units')
    @classmethod
    def validate_time_output_units(cls, v):
        valid_units = ['minutes', 'seconds', 'hours']
        if v not in valid_units:
            raise ValueError(f"time_output_units must be one of {valid_units}")
        return v


# class BaseAngleOutputUnitsModel(BaseModel):  # Use this as in models/noaa/noaa_models.py
class BaseOutputUnitsModel(BaseModel):
    output_units: str

    @field_validator('output_units')
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = ['radians', 'degrees']
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
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


class Longitude(BaseModel):
    longitude: confloat(ge=-180, le=180)


class Latitude(BaseModel):
    latitude: confloat(ge=-90, le=90)


class BaseCoordinatesInputModel(Longitude, Latitude):
    pass


class SolarAltitudeInput(
    BaseCoordinatesInputModel,
    BaseTimeInputModel,
    BaseOutputUnitsModel,
):
    pass


class SolarAzimuthInput(SolarAltitudeInput):
    pass


class EarthOrbitInputModel(BaseModel):
    days_in_a_year: float = 365.25
    orbital_eccentricity: float = 0.03344
    perigee_offset: float = 0.048869


class SolarDeclinationInput(
    BaseTimeInputModel,
    EarthOrbitInputModel,
    BaseAngleOutputUnitsModel,
):
    pass
