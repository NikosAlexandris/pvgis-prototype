from datetime import datetime
from math import pi
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import BaseModel
from pydantic import confloat
from typing import Optional
from typing import Union
from zoneinfo import ZoneInfo
from pydantic import validator

from pvgisprototype.api.data_classes.models import Latitude
from pvgisprototype.api.data_classes.models import Longitude


class LongitudeModel(BaseModel):
    longitude: Union[confloat(ge=-pi, le=pi), Longitude]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("longitude")
    def longitude_named_tuple(cls, input) -> Longitude:
        if isinstance(input, Longitude):
            return input
        elif isinstance(input, float):
            return Longitude(value=input, unit='radians')
        else:
            raise ValueError("Unsupported `longitude` type provided")


class LatitudeModel(BaseModel):
    latitude: Union[confloat(ge=-pi/2, le=pi/2), Latitude]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("latitude")
    def latitude_named_tuple(cls, input) -> Latitude:
        if isinstance(input, Latitude):
            return input
        elif isinstance(input, float):
            return Latitude(value=input, unit='radians')
        else:
            raise ValueError("Unsupported `latitude` type provided")


class BaseCoordinates(LongitudeModel, LatitudeModel):
    pass


class BaseTimestamp(BaseModel):
    timestamp: datetime
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseTime(BaseTimestamp):
    timezone: Optional[ZoneInfo] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError("The `timezone` must be a valid `zoneinfo.ZoneInfo` object.")
        return v
