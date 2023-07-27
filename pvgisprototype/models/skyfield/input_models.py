from datetime import datetime
from math import pi
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import BaseModel
from pydantic import confloat
from typing import Optional
from zoneinfo import ZoneInfo


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


class Longitude(BaseModel):
    longitude: confloat(ge=-180, le=180)


class Latitude(BaseModel):
    latitude: confloat(ge=-90, le=90)


class BaseCoordinatesInputModel(Longitude, Latitude):
    pass


class CalculateTrueSolarTimeSkyfieldInputModel(
    BaseCoordinatesInputModel,
    BaseTimeInputModel,
):
    pass
