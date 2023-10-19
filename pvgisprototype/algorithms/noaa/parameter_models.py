from typing import List
from typing import Optional
from typing import Union
from typing import Sequence
from math import pi
from pydantic import field_validator
from pydantic import BaseModel
from pydantic import confloat
from pvgisprototype import SolarZenith
from pvgisprototype.constants import RADIANS, DEGREES


class BaseTimeEventModel(BaseModel):
    event: str

    @field_validator('event')
    @classmethod
    def validate_event(cls, v):
        valid_events = ['noon', 'sunrise', 'sunset']
        if v not in valid_events:
            raise ValueError(f"`event` must be one of {valid_events}")
        return v


class BaseTimeOutputUnitsModel(BaseModel):
    time_output_units: Optional[str] = None

    @field_validator('time_output_units')
    @classmethod
    def validate_time_output_units(cls, v):
        valid_units = ['minutes', 'seconds', 'hours']
        if v not in valid_units:
            raise ValueError(f"time_output_units must be one of {valid_units}")
        return v


class BaseAngleUnitsModel(BaseModel):
    angle_units: str

    @field_validator('angle_units')
    @classmethod
    def validate_angle_units(cls, v):
        valid_units = [RADIANS, DEGREES]
        if v not in valid_units:
            raise ValueError(f"angle_units must be one of {valid_units}")
        return v


class BaseAngleOutputUnitsModel(BaseModel):
    angle_output_units: Optional[str] = RADIANS

    @field_validator('angle_output_units')
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = [RADIANS, DEGREES]
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v


class AngleInRadiansOutputUnitsModel(BaseModel):
    """
    The angle in radians output units argument is passed along with the
    returned value. This is not a real test. Hopefully, and however, it helps
    for clarity and understanding of what the function should return.
    """
    angle_output_units: str = RADIANS

    @field_validator('angle_output_units')
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = [RADIANS]
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v


class SolarZenithModel(BaseModel):
    solar_zenith: Union[confloat(ge=0, le=pi+0.01745), List[confloat(ge=0, le=pi+0.01745)], SolarZenith]


class SolarZenithSeriesModel(BaseModel):  # merge above here-in
    # solar_zenith_series: Union[confloat(ge=0, le=pi+0.01745), List[confloat(ge=0, le=pi+0.01745)]]
    solar_zenith_series: Union[SolarZenith, Sequence[SolarZenith]]

