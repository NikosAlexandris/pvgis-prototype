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
from pvgisprototype.api.named_tuples import generate


class ModelToDict(BaseModel):
    def dict_with_namedtuple(self):
        d = {}
        for k, v in self:
            d[k] = v
        return d


class Longitude(BaseModel):
    longitude: Union[confloat(ge=-pi, le=pi), tuple]

    @validator("longitude", always=True)
    def longitude_named_tuple(cls, input) -> Union[confloat(ge=-pi, le=pi), tuple]:
        if isinstance(input, tuple):
            return generate('longitude', (input[0], input[1]))
        elif isinstance(input, float):
            return generate('longitude', (input, 'radians'))
        else:
            raise ValueError("Unsupported longitude type provided")


class Latitude(BaseModel):
    latitude: Union[confloat(ge=-pi/2, le=pi/2), tuple]

    @validator("latitude", always=True)
    def latitude_named_tuple(cls, input) -> Union[confloat(ge=-pi/2, le=pi/2), tuple]:
        if isinstance(input, tuple):
            return generate('latitude', (input[0], input[1]))
        elif isinstance(input, float):
            return generate('latitude', (input, 'radians'))
        else:
            raise ValueError("Unsupported latitude type provided")


class BaseCoordinatesInputModel(Longitude, Latitude):
    pass


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


    ModelToDict,




    pass


class CalculateTrueSolarTimeSkyfieldInputModel(
    BaseCoordinatesInputModel,
    BaseTimeInputModel,
):
    pass