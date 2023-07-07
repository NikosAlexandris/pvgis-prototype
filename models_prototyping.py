from datetime import datetime
from datetime import timezone
from math import pi
from pydantic import BaseModel
from pydantic import ConstrainedFloat
from pydantic import validator
from typing import Optional
from zoneinfo import ZoneInfo


class BaseTimeInputModel(BaseModel):
    timestamp: datetime
    timezone: Optional[ZoneInfo]

    class Config:
        arbitrary_types_allowed = True

    @validator('timezone')
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError("The `timezone` must be a valid `zoneinfo.ZoneInfo` object.")
        return v


class BaseTimeOutputUnitsModel(BaseModel):
    output_units: Optional[str]

    @validator('output_units')
    def validate_output_units(cls, v):
        valid_units = ['minutes', 'seconds', 'hours']
        if v not in valid_units:
            raise ValueError(f"output_units must be one of {valid_units}")
        return v


class Longitude(ConstrainedFloat):
    ge = -180
    le = 180


class Latitude(ConstrainedFloat):
    ge = -90
    le = 90


class BaseLongitudeInputModel(BaseModel):
    longitude: Longitude


class BaseLatitudeInputModel(BaseModel):
    latitude: Latitude


class BaseCoordinatesInputModel(BaseLongitudeInputModel, BaseLatitudeInputModel):
    pass


class BaseAngleOutputUnitsModel(BaseModel):
    output_units: Optional[str]

    @validator('output_units')
    def validate_output_units(cls, v):
        valid_units = ['radians', 'degrees']
        if v not in valid_units:
            raise ValueError(f"output_units must be one of {valid_units}")
        return v
