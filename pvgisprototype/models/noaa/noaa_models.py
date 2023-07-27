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


class BaseTimeEventInputModel(BaseModel):
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


class Longitude(BaseModel):
    longitude: confloat(ge=-180, le=180)


class Longitude_in_Radians(BaseModel):
    longitude: confloat(ge=-pi, le=pi)  # -pi to pi


class Latitude(BaseModel):
    latitude: confloat(ge=-90, le=90)


class Latitude_in_Radians(BaseModel):
    latitude: confloat(ge=-pi/2, le=pi/2)  # -pi/2 to pi/2


class BaseCoordinatesInputModel(Longitude, Latitude):
    pass


class BaseAngleUnitsModel(BaseModel):
    angle_units: str

    @field_validator('angle_units')
    @classmethod
    def validate_angle_units(cls, v):
        valid_units = ['radians', 'degrees']
        if v not in valid_units:
            raise ValueError(f"angle_units must be one of {valid_units}")
        return v


class BaseAngleOutputUnitsModel(BaseModel):
    angle_output_units: Optional[str] = "radians"

    @field_validator('angle_output_units')
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = ['radians', 'degrees']
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v


class AngleInRadiansOutputUnitsModel(BaseModel):
    """
    The angle in radians output units argument is passed along with the
    returned value. This is not a real test. Hopefully, and however, it helps
    for clarity and understanding of what the function should return.
    """
    angle_output_units: str = "radians"

    @field_validator('angle_output_units')
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = ['radians']
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v


class CalculateFractionalYearNOAAInput(
    BaseTimestampInputModel,
    AngleInRadiansOutputUnitsModel,
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
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateTimeOffsetNOAAInput(
    Longitude,
    BaseTimestampInputModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
):
    pass


class CalculateTrueSolarTimeNOAAInput(
    Longitude,
    BaseTimeInputModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateSolarHourAngleNOAAInput(
    Longitude,
    BaseTimeInputModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class SolarZenith_in_Radians(BaseModel):
    solar_zenith: confloat(ge=0, le=pi+0.01745)


class AdjustSolarZenithForAtmosphericRefractionNOAAInput(
    SolarZenith_in_Radians,
    BaseAngleOutputUnitsModel,
):
    @field_validator('solar_zenith')
    @classmethod
    def solar_zenith_range(cls, v):
        if not (0 <= v <= pi):
            raise ValueError('solar_zenith must range within [0, π]')
        return v


class BaseApplyAtmosphericRefraction(BaseModel):
    apply_atmospheric_refraction: bool


class CalculateSolarZenithNOAAInput(
    Latitude,
    BaseTimestampInputModel,
    BaseApplyAtmosphericRefraction,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    solar_hour_angle: float


class SolarAltitude_in_Radians(BaseModel):
    solar_altitude: confloat(ge=-0.01745, le=pi/2)


class CalculateSolarAltitudeNOAAInput(
    BaseCoordinatesInputModel,
    BaseTimeInputModel,
    BaseApplyAtmosphericRefraction,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAzimuthNOAAInput(
    BaseCoordinatesInputModel,
    BaseTimeInputModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateEventHourAngleNOAAInput(
    Latitude,
    BaseTimestampInputModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    refracted_solar_zenith: float

    @field_validator('refracted_solar_zenith')
    @classmethod
    def validate_refracted_solar_zenith(cls, v):
        target_zenith = 1.5853349194640094  # radias, approx. 90.833 degrees
        error_margin = 0.01
        if not (target_zenith - error_margin) <= v <= (target_zenith + error_margin):
            raise ValueError(
                f"`refracted_solar_zenith` must be approximately {target_zenith} radians (90.833 degrees), allowing an error margin of {error_margin}"
            )
        return v


class CalculateEventTimeNOAAInput(
    BaseCoordinatesInputModel,
    BaseTimeInputModel,
    BaseApplyAtmosphericRefraction,
    BaseTimeEventInputModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateLocalSolarTimeNOAAInput(
    BaseCoordinatesInputModel,
    BaseTimeInputModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    verbose: Optional[bool] = False


class CalculateSolarPositionNOAA(
    BaseCoordinatesInputModel,
    BaseTimeInputModel,
    BaseApplyAtmosphericRefraction,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
        ):
    refracted_solar_zenith: float

    @field_validator('refracted_solar_zenith')
    @classmethod
    def validate_refracted_solar_zenith(cls, v):
        target_zenith = 1.5853349194640094  # radias, approx. 90.833 degrees
        error_margin = 0.01
        if not (target_zenith - error_margin) <= v <= (target_zenith + error_margin):
            raise ValueError(
                f"`refracted_solar_zenith` must be approximately {target_zenith} radians (90.833 degrees), allowing an error margin of {error_margin}"
            )
        return v
    pass
