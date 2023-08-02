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

from pvgisprototype.api.data_classes import Latitude
from pvgisprototype.api.data_classes import Longitude


class ValidatedInputToDict(BaseModel):
    def pydantic_model_to_dict(self):
        d = {}
        for k, v in self:
            d[k] = v
        return d
    

class BaseTimestampModel(BaseModel):
    timestamp: datetime
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseTimeInput(BaseTimestampModel):
    timezone: Optional[ZoneInfo] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError("The `timezone` must be a valid `zoneinfo.ZoneInfo` object.")
        return v


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


# class LongitudeModel_in_Radians(BaseModel):
#     longitude: confloat(ge=-pi, le=pi)  # -pi to pi


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



# class LatitudeModel_in_Radians(BaseModel):
#     latitude: confloat(ge=-pi/2, le=pi/2)  # -pi/2 to pi/2


class BaseCoordinatesInput(LongitudeModel, LatitudeModel):
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
    ValidatedInputToDict,
    BaseTimestampModel,
    AngleInRadiansOutputUnitsModel,
):
    pass


class CalculateEquationOfTimeNOAAInput(
    ValidatedInputToDict,
    BaseTimestampModel,
    BaseAngleUnitsModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateSolarDeclinationNOAAInput(
    BaseTimestampModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateTimeOffsetNOAAInput(
    ValidatedInputToDict,
    LongitudeModel,
    BaseTimestampModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
):
    pass


class CalculateTrueSolarTimeNOAAInput(
    ValidatedInputToDict,
    LongitudeModel,
    BaseTimeInput,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateSolarHourAngleNOAAInput(
    ValidatedInputToDict,
    LongitudeModel,
    BaseTimeInput,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class SolarZenithModel_in_Radians(BaseModel):
    solar_zenith: confloat(ge=0, le=pi+0.01745)


class AdjustSolarZenithForAtmosphericRefractionNOAAInput(
    SolarZenithModel_in_Radians,
    BaseAngleOutputUnitsModel,
):
    @field_validator('solar_zenith')
    @classmethod
    def solar_zenith_range(cls, v):
        if not (0 <= v <= pi):
            raise ValueError('solar_zenith must range within [0, π]')
        return v


class BaseApplyAtmosphericRefractionModel(BaseModel):
    apply_atmospheric_refraction: bool


class CalculateSolarZenithNOAAInput(
    LatitudeModel,
    BaseTimestampModel,
    BaseApplyAtmosphericRefractionModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    solar_hour_angle: float


class SolarAltitudeModel_in_Radians(BaseModel):
    solar_altitude: confloat(ge=-0.01745, le=pi/2)


class CalculateSolarAltitudeNOAAInput(
    ValidatedInputToDict,
    BaseCoordinatesInput,
    BaseTimeInput,
    BaseApplyAtmosphericRefractionModel,
    BaseTimeOutputUnitsModel,
    # BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAzimuthNOAAInput(
    BaseCoordinatesInput,
    BaseTimeInput,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateEventHourAngleNOAAInput(
    LatitudeModel,
    BaseTimestampModel,
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
    BaseCoordinatesInput,
    BaseTimeInput,
    BaseApplyAtmosphericRefractionModel,
    BaseTimeEventModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateLocalSolarTimeNOAAInput(
    BaseCoordinatesInput,
    BaseTimeInput,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    verbose: Optional[bool] = False


class CalculateSolarPositionNOAAInput(
    BaseCoordinatesInput,
    BaseTimeInput,
    BaseApplyAtmosphericRefractionModel,
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
