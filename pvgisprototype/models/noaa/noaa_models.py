from typing import List
from typing import Optional
from typing import Union
from typing import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo
from math import pi
from pydantic import field_validator
from pydantic import BaseModel
from pydantic import confloat
import numpy as np

# from pvgisprototype.api.data_classes import SolarZenith
from pvgisprototype.api.parameter_models import SolarHourAngleModel
from pvgisprototype.api.parameter_models import SolarHourAngleSeriesModel

# When?
from pvgisprototype.api.parameter_models import BaseTimestampModel
from pvgisprototype.api.parameter_models import BaseTimestampSeriesModel
from pvgisprototype.api.parameter_models import BaseTimeModel
from pvgisprototype.api.parameter_models import BaseTimeSeriesModel

# Where?
from pvgisprototype.api.parameter_models import LongitudeModel
from pvgisprototype.api.parameter_models import LatitudeModel
from pvgisprototype.api.parameter_models import BaseCoordinatesModel


class ValidatedInputToDict(BaseModel):
    def pydantic_model_to_dict(self):
        d = {}
        for k, v in self:
            d[k] = v
        return d
    

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


class CalculateFractionalYearNOAATimeSeriesInput(  # merge above here-in!
    ValidatedInputToDict,
    BaseTimestampSeriesModel,  # != BaseTimestampModel
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
    ValidatedInputToDict,
    BaseTimestampModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarDeclinationNOAATimeSeriesInput(  # merge above here-in
    ValidatedInputToDict,
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateTimeOffsetNOAAInput(
    ValidatedInputToDict,
    LongitudeModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
):
    pass


class CalculateTrueSolarTimeNOAAInput(
    ValidatedInputToDict,
    LongitudeModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateTrueSolarTimeNOAATimeSeriesInput(
    ValidatedInputToDict,
    LongitudeModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
):
    pass


class CalculateSolarHourAngleNOAAInput(
    ValidatedInputToDict,
    LongitudeModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarHourAngleNOAATimeSeriesInput(
    ValidatedInputToDict,
    LongitudeModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class SolarZenithModel(BaseModel):
    solar_zenith: Union[confloat(ge=0, le=pi+0.01745), List[confloat(ge=0, le=pi+0.01745)]]


class SolarZenithSeriesModel(BaseModel):  # merge above here-in
    solar_zenith_series: Union[confloat(ge=0, le=pi+0.01745), List[confloat(ge=0, le=pi+0.01745)]]


class AdjustSolarZenithForAtmosphericRefractionNOAAInput(
    ValidatedInputToDict,
    SolarZenithModel,
    BaseAngleOutputUnitsModel,
):
    @field_validator('solar_zenith')
    @classmethod
    def solar_zenith_range(cls, v):
        if not (0 <= v <= pi):
            raise ValueError('solar_zenith must range within [0, π]')
        return v


class AdjustSolarZenithForAtmosphericRefractionNOAATimeSeriesInput(
    ValidatedInputToDict,
    SolarZenithSeriesModel,
    BaseAngleOutputUnitsModel,
):
    @field_validator('solar_zenith_series')
    def solar_zenith_range(cls, v):
        v_array = np.atleast_1d(v)  # Ensure v is treated as an array
        if not np.all((0 <= v_array) & (v_array <= np.pi)):  # Adjust the condition to work with an array
            raise ValueError('solar_zenith must range within [0, π]')
        return v  # Return the original value or array


class BaseApplyAtmosphericRefractionModel(BaseModel):
    apply_atmospheric_refraction: bool


class CalculateSolarZenithNOAAInput(
    ValidatedInputToDict,
    LatitudeModel,
    BaseTimestampModel,
    SolarHourAngleModel,
    BaseApplyAtmosphericRefractionModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarZenithNOAATimeSeriesInput(
    ValidatedInputToDict,
    LatitudeModel,
    BaseTimestampSeriesModel,  # != BaseTimestampModel
    SolarHourAngleSeriesModel,
    BaseApplyAtmosphericRefractionModel,
    BaseAngleOutputUnitsModel,
):
    pass


class SolarAltitudeModel_in_Radians(BaseModel):
    solar_altitude: confloat(ge=-0.01745, le=pi/2)


class CalculateSolarAltitudeNOAAInput(
    ValidatedInputToDict,
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseApplyAtmosphericRefractionModel,
    BaseTimeOutputUnitsModel,
    # BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAltitudeNOAATimeSeriesInput(
    ValidatedInputToDict,
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    BaseApplyAtmosphericRefractionModel,
    BaseTimeOutputUnitsModel,
    # BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAzimuthNOAAInput(
    ValidatedInputToDict,
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateSolarAzimuthNOAATimeSeriesInput(
    ValidatedInputToDict,
    BaseCoordinatesModel,
    BaseTimeSeriesModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass




class CalculateEventHourAngleNOAAInput(
    ValidatedInputToDict,
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
    ValidatedInputToDict,
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseTimeEventModel,
    BaseApplyAtmosphericRefractionModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    pass


class CalculateLocalSolarTimeNOAAInput(
    ValidatedInputToDict,
    BaseCoordinatesModel,
    BaseTimeModel,
    BaseTimeOutputUnitsModel,
    BaseAngleUnitsModel,
    BaseAngleOutputUnitsModel,
):
    verbose: Optional[bool] = False


class CalculateSolarPositionNOAAInput(
    ValidatedInputToDict,
    BaseCoordinatesModel,
    BaseTimeModel,
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
