from datetime import datetime
from math import pi
from pydantic import BaseModel
from pydantic import ConstrainedFloat
from pydantic import validator
from typing import Optional
from zoneinfo import ZoneInfo


class BaseTimestampInputModel(BaseModel):
    timestamp: datetime

    class Config:
        arbitrary_types_allowed = True


class BaseTimeInputModel(BaseTimestampInputModel):
    timezone: Optional[ZoneInfo]

    class Config:
        arbitrary_types_allowed = True

    @validator('timezone')
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError("The `timezone` must be a valid `zoneinfo.ZoneInfo` object.")
        return v


class BaseTimeEventInputModel(BaseModel):
    event: str

    @validator('event')
    def validate_event(cls, v):
        valid_events = ['noon', 'sunrise', 'sunset']
        if v not in valid_events:
            raise ValueError(f"`event` must be one of {valid_events}")
        return v


class BaseTimeOutputUnitsModel(BaseModel):
    time_output_units: Optional[str]

    @validator('time_output_units')
    def validate_time_output_units(cls, v):
        valid_units = ['minutes', 'seconds', 'hours']
        if v not in valid_units:
            raise ValueError(f"time_output_units must be one of {valid_units}")
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


class BaseAngleUnitsModel(BaseModel):
    angle_units: str

    @validator('angle_units')
    def validate_angle_units(cls, v):
        valid_units = ['radians', 'degrees']
        if v not in valid_units:
            raise ValueError(f"angle_units must be one of {valid_units}")
        return v


class BaseAngleOutputUnitsModel(BaseModel):
    angle_output_units: str

    @validator('angle_output_units')
    def validate_angle_output_units(cls, v):
        valid_units = ['radians', 'degrees']
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v


class CalculateFractionalYearNOAAInput(
    BaseTimestampInputModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateEquationOfTimeNOAAInput(
    BaseTimestampInputModel,
    BaseAngleUnitsModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateSolarDeclinationNOAAInput(
    BaseTimestampInputModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateTimeOffsetNOAAInput(
    BaseLongitudeInputModel,
    BaseTimestampInputModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
):
    pass


class CalculateTrueSolarTimeNOAAInput(
    BaseLongitudeInputModel,
    BaseTimeInputModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateSolarHourAngleNOAAInput(
    BaseLongitudeInputModel,
    BaseTimeInputModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class AdjustSolarZenithForAtmosphericRefractionNOAAInput(BaseAngleOutputUnitsModel):
    solar_zenith: float

    @validator('solar_zenith')
    def solar_zenith_range(cls, v):
        if not (0 <= v <= pi):
            raise ValueError('solar_zenith must range within [0, π]')
        return v


class BaseApplyAtmosphericRefraction(BaseModel):
    apply_atmospheric_refraction: bool


class CalculateSolarAltitudeNOAAInput(BaseCoordinatesInputModel,BaseTimeInputModel,BaseAngleOutputUnitsModel):
    pass


class CalculateSolarAzimuthNOAAInput(BaseCoordinatesInputModel,BaseTimeInputModel,BaseAngleOutputUnitsModel):
    pass


class CalculateEventTimeNOAAInput(BaseCoordinatesInputModel,BaseTimeInputModel,BaseTimeOutputUnitsModel):
    event: str

    @validator('event')
    def validate_event(cls, v):
        valid_events = ['noon', 'sunrise', 'sunset']
        if v not in valid_events:
            raise ValueError(f"event must be one of {valid_events}")
        return v


class CalculateLocalSolarTimeNOAAInput(BaseCoordinatesInputModel,BaseTimeInputModel,BaseTimeOutputUnitsModel):
    verbose: Optional[bool] = False
