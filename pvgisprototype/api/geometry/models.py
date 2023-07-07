from datetime import datetime
from pydantic import BaseModel
from pydantic import ConstrainedFloat
from pydantic import validator
from typing import Optional
from zoneinfo import ZoneInfo

class Latitude(ConstrainedFloat):
    ge = -90
    le = 90

class Longitude(ConstrainedFloat):
    ge = -180
    le = 180

class BaseInputModel(BaseModel):
    longitude: Longitude
    latitude: Latitude
    timestamp: datetime
    timezone: Optional[ZoneInfo]

    class Config:
        arbitrary_types_allowed = True

    @validator('timezone')
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError("The `timezone` must be a valid `zoneinfo.ZoneInfo` object.")
        return v
