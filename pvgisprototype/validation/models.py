#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from enum import Enum
from math import pi
from typing import Tuple, List
from zoneinfo import ZoneInfo

from numpy import datetime64 as numpy_datetime64
from pandas import DatetimeIndex, Timestamp
from pydantic import BaseModel, ConfigDict, confloat, field_validator
from xarray import DataArray

from pvgisprototype import (
    Elevation,
    Latitude,
    Longitude,
    RefractedSolarAltitude,
    UnrefractedSolarZenith,
    SolarAltitude,
    SolarAzimuth,
    SolarDeclination,
    SolarHourAngle,
    SurfaceOrientation,
    SurfaceTilt,
    LocationShading,
)
from pvgisprototype.api.position.models import (
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
    ShadingModel,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEGREES,
    ECCENTRICITY_CORRECTION_FACTOR,
    ECCENTRICITY_PHASE_OFFSET,
    RADIANS,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SURFACE_TILT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.core.arrays import CUPY_ENABLED, NDArrayBackend

MESSAGE_UNSUPPORTED_TYPE = "Unsupported type provided for "


# Generic input/output


class VerbosityModel(BaseModel):
    verbose: int = VERBOSE_LEVEL_DEFAULT


class LoggingModel(BaseModel):
    log: int = VERBOSE_LEVEL_DEFAULT


class ArrayShapeModel(BaseModel):
    shape: Tuple[int, ...]


class ValidateOutputModel(BaseModel):
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT


class ArrayInitialisationModel(BaseModel):
    initialisation_method: str = "zeros"

    @field_validator("initialisation_method")
    def check_init_method(cls, v):
        valid_methods = ["zeros", "ones", "empty"]
        if v not in valid_methods:
            raise ValueError(
                f"Invalid initialisation method. Choose among {valid_methods}."
            )
        return v


class ArrayTypeModel(BaseModel):
    # dtype: ArrayDType = DATA_TYPE_DEFAULT
    dtype: str = DATA_TYPE_DEFAULT

    # @validator('dtype', pre=True)
    # def validate_dtype(cls, v):
    #     if isinstance(v, ArrayDType):
    #         return v
    #     try:
    #         return ArrayDType.from_string(v)
    #     except ValueError as e:
    #         raise ValueError(f"Validation error for dtype: {e}")


class ArrayBackendModel(BaseModel):
    array_backend: str = ARRAY_BACKEND_DEFAULT

    @field_validator("array_backend")
    def check_backend(cls, v, values, **kwargs):
        if values.get("use_gpu") and CUPY_ENABLED:
            return "CUPY"
        if v.upper() not in NDArrayBackend.__members__:
            raise ValueError(
                f"Invalid backend. Choose among {list(NDArrayBackend.__members__.keys())}."
            )
        return v.upper()

    class Config:
        use_enum_values = True


class ArrayModel(
    ArrayShapeModel,
    ArrayInitialisationModel,
    ArrayTypeModel,
    ArrayBackendModel,
):
    pass


# Where?


class LongitudeModel(BaseModel):
    longitude: confloat(ge=-pi, le=pi) | Longitude
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("longitude")
    def validate_longitude(cls, input) -> Longitude:
        if isinstance(input, Longitude):
            return input
        elif isinstance(input, float):
            return Longitude(value=input, unit=RADIANS)
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `longitude`")


class LatitudeModel(BaseModel):
    latitude: confloat(ge=-pi / 2, le=pi / 2) | Latitude
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("latitude")
    def validate_latitude(cls, input) -> Latitude:
        if isinstance(input, Latitude):
            return input
        elif isinstance(input, float):
            return Latitude(value=input, unit=RADIANS)
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `latitude`")


class BaseCoordinatesModel(
    LongitudeModel,
    LatitudeModel,
):
    pass


class LocationModel(
    BaseCoordinatesModel,
    Elevation,
):
    timezone: ZoneInfo | None = None
    name: str | None = None
    description: str | None = None


# When?


class BaseTimestampModel(BaseModel):
    timestamp: numpy_datetime64 | Timestamp | DatetimeIndex
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("timestamp")
    def check_timestamp_type(cls, value):
        if isinstance(value, np.ndarray):
            if value.dtype.type != numpy_datetime64:
                raise ValueError("NumPy array must be of dtype 'datetime64'")
        elif not isinstance(value, (numpy_datetime64, Timestamp, DatetimeIndex)):
            raise TypeError(
                "Timestamp must be a NumPy datetime64, a Pandas DatetimeIndex, or a Pandas Timestamp"
            )
        return value


class BaseTimestampSeriesModel(BaseModel):
    timestamps: DatetimeIndex | Timestamp
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("timestamps")
    def check_type(cls, value):
        if isinstance(value, Timestamp):
            return DatetimeIndex([value])
        elif isinstance(value, DatetimeIndex):
            return value
        else:
            raise TypeError(
                "Timestamps must be a Pandas object of either type DatetimeIndex or Timestamp"
            )


class BaseTimeModel(BaseTimestampModel):
    timezone: ZoneInfo | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError(
                "The `timezone` must be `None` or a valid `zoneinfo.ZoneInfo` object."
            )
        return v


class BaseTimeSeriesModel(BaseTimestampSeriesModel):
    timezone: ZoneInfo | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError(
                "The `timezone` must be `None` or a valid `zoneinfo.ZoneInfo` object."
            )
        return v


class TimeOffsetModel(BaseModel):
    time_offset_global: float = 0


class HourOffsetModel(BaseModel):
    hour_offset: float = 0


class RandomTimeModel(BaseModel):
    random_time: bool = False


class RandomTimeSeriesModel(BaseModel):
    random_time_series: bool = False


class BaseTimeOutputUnitsModel(BaseModel):
    time_output_units: str | None = None

    @field_validator("time_output_units")
    @classmethod
    def validate_time_output_units(cls, v):
        valid_units = ["minutes", "seconds", "hours"]
        if v not in valid_units:
            raise ValueError(f"time_output_units must be one of {valid_units}")
        return v


# Angular units


class BaseAngleUnitsModel(BaseModel):
    angle_units: str = RADIANS

    @field_validator("angle_units")
    @classmethod
    def validate_angle_units(cls, v):
        valid_units = [RADIANS, DEGREES]
        if v not in valid_units:
            raise ValueError(f"angle_units must be one of {valid_units}")
        return v


class BaseAngleInternalUnitsModel(BaseModel):  # NOTE: Maybe deprecate
    angle_units: str = RADIANS
    model_config = ConfigDict(
        description="""Angular units for internal calculations (degrees).""",
    )

    @field_validator("angle_units")
    @classmethod
    def validate_angle_units(cls, v):
        valid_units = [RADIANS]
        if v not in valid_units:
            raise ValueError(f"angle_units must be {valid_units}")
        return v


class BaseAngleOutputUnitsModel(BaseModel):
    angle_output_units: str
    model_config = ConfigDict(
        description="""Output units for solar geometry variables (degrees or radians).""",
    )

    @field_validator("angle_output_units")
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = [RADIANS, DEGREES]
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v


# Solar geometry


class SolarDeclinationModel(BaseModel):
    solar_declination: confloat(ge=0, le=pi) | SolarDeclination
    model_config = ConfigDict(
        description="""Solar declination (δ) is the angle between the equator and a
        line drawn from the centre of the Earth to the centre of the sun.""",
    )

    @field_validator("solar_declination")
    def validate_solar_declination(cls, input) -> SolarDeclination:
        if isinstance(input, SolarDeclination):
            return input
        elif isinstance(input, float):
            return SolarDeclination(value=input, unit=RADIANS)
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `solar_declination`")


class SolarPositionModelModel(BaseModel):
    """
    This Pydantic model defines the input parameter required by CLI and API
    functions for solar position that expect an SolarPositionModel item.

    Notes
    -----

    The suffix ModelModels is intentional !
    """

    solar_position_model: SolarPositionModel = SolarPositionModel.noaa

    @field_validator("solar_position_model")
    def validate_solar_position_model(cls, input) -> Enum:
        if isinstance(input, Enum):
            return input
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `solar_position_model`")



class SolarPositionModelModels(BaseModel):
    """
    This Pydantic model defines the input parameter required (mainly) in API
    functions for solar position that expect a list of SolarPositionModel
    items.

    Notes
    -----

    The suffix ModelModels is intentional !
    """
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.noaa]


class SolarIncidenceModel(BaseModel):
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal


class ComplementaryIncidenceAngleModel(BaseModel):
    complementary_incidence_angle: bool = False


class EarthOrbitModel(BaseModel):
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR


class SolarTimeModelModel(BaseModel):  # ModelModel is intentional !
    solar_time_model: SolarTimeModel = SolarTimeModel.skyfield
    @field_validator("solar_time_model")
    def validate_solar_time_model(cls, input) -> Enum:
        if isinstance(input, Enum):
            return input
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `solar_time_model`")


"""
FIXME: Decide if datetime.datetime or datetime.time, and also change the
callback function convert_hours_to_datetime_time() in typer_argument_true_solar_time()
"""


class SolarTimeModel(BaseModel):
    solar_time: Timestamp
    model_config = ConfigDict(
        description="""The solar time (ST) is a calculation of the passage of time based on the position of the Sun in the sky. It is expected to be decimal hours in a 24 hour format and measured internally in seconds.""",
        arbitrary_types_allowed=True,
    )


# Solar surface


class SurfaceTiltModel(BaseModel):
    # surface_tilt: confloat(ge=-pi / 2, le=pi / 2) | SurfaceTilt = (
    surface_tilt: float | SurfaceTilt = SURFACE_TILT_DEFAULT
    model_config = ConfigDict(
        description="""Surface tilt (or slope) (β) is the angle between the inclined surface (slope) and the horizontal plane.""",
    )

    @field_validator("surface_tilt")
    def validate_surface_tilt(cls, input) -> SurfaceTilt:
        if isinstance(input, SurfaceTilt):
            return input
        elif isinstance(input, float):
            return SurfaceTilt(value=input, unit=RADIANS)
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `surface_tilt`")


class SurfaceOrientationModel(BaseModel):
    surface_orientation: confloat(ge=0, le=2 * pi) | SurfaceOrientation = pi
    model_config = ConfigDict(
        description="""Surface orientation (also known as aspect or azimuth) is the projected angle measured clockwise from true north"""
    )

    @field_validator("surface_orientation")
    def validate_surface_orientation(cls, input) -> SurfaceOrientation:
        if isinstance(input, SurfaceOrientation):
            return input
        elif isinstance(input, float):
            return SurfaceOrientation(value=input, unit=RADIANS)
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `surface_orientation`")


class HorizonProfileModel(BaseModel):
    horizon_profile: DataArray | None = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    @field_validator("horizon_profile")
    def validate_horizon_profile(cls, input) -> DataArray:
        if isinstance(input, (DataArray | None)):
            return input
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `horizon_profile`")


class SurfaceInShadeModel(BaseModel):
    surface_in_shade_series: LocationShading
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class ShadingModelModel(BaseModel):
    shading_model: ShadingModel = ShadingModel.pvis
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class ShadingModelsModel(BaseModel):
    shading_models: List[ShadingModel]
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class SolarHourAngleModel(BaseModel):
    solar_hour_angle: confloat(ge=-pi, le=pi) | SolarHourAngle
    model_config = ConfigDict(
        description="""Solar hour angle""",
    )

    @field_validator("solar_hour_angle")
    def validate_solar_hour_angle(cls, input) -> SolarHourAngle:
        if isinstance(input, SolarHourAngle):
            return input
        elif isinstance(input, float):
            return SolarHourAngle(value=input, unit=RADIANS)
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `solar_hour_angle`")


class SolarHourAngleSeriesModel(BaseModel):
    solar_hour_angle_series: SolarHourAngle
    model_config = ConfigDict(
        description="Solar hour angle series.",
        arbitrary_types_allowed=True,
    )

    @field_validator("solar_hour_angle_series")
    def validate_solar_hour_angle(cls, input) -> SolarHourAngle:
        if isinstance(input, SolarHourAngle):
            return input
        # elif isinstance(input, ndarray) and all(                          # FIXME: What else could be?
        #     isinstance(item, SolarHourAngle) for item in input
        # ):
        #     return input
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `solar_hour_angle_series`")


class ApplyAtmosphericRefractionModel(BaseModel):
    adjust_for_atmospheric_refraction: bool = True


class ZeroNegativeSolarIncidenceAngleModel(BaseModel):
    zero_negative_solar_incidence_angle: bool = (
        ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT
    )


class RefractedSolarAltitudeModel(BaseModel):
    refracted_solar_altitude: float | RefractedSolarAltitude

    @field_validator("refracted_solar_altitude")
    def validate_refracted_solar_altitude(cls, input) -> RefractedSolarAltitude:
        if isinstance(input, RefractedSolarAltitude):
            return input
        elif isinstance(input, float):
            return RefractedSolarAltitude(value=input, unit=RADIANS)
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `refracted_solar_altitude`")


class RefractedSolarAltitudeSeriesModel(BaseModel):
    refracted_solar_altitude_series: RefractedSolarAltitude

    # @field_validator("refracted_solar_altitude")
    # def validate_refracted_solar_altitude(cls, input) -> RefractedSolarAltitude:
    #     if isinstance(input, RefractedSolarAltitude):
    #         return input
    #     elif isinstance(input, float):
    #         return RefractedSolarAltitude(value=input, unit=RADIANS)
    #     else:
    #         raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `refracted_solar_altitude`")

class SolarAltitudeSeriesModel(BaseModel):
    solar_altitude_series: SolarAltitude
    model_config = ConfigDict(
        description="Solar altitude series.",
        arbitrary_types_allowed=True,
    )
    @field_validator("solar_altitude_series")
    def validate_solar_hour_angle(cls, input) -> SolarAltitude:
        if isinstance(input, SolarAltitude):
            return input
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `solar_altitude_series`")

class SolarAzimuthSeriesModel(BaseModel):
    solar_azimuth_series: SolarAzimuth
    model_config = ConfigDict(
        description="Solar azimuth series.",
        arbitrary_types_allowed=True,
    )
    @field_validator("solar_azimuth_series")
    def validate_solar_hour_angle(cls, input) -> SolarAzimuth:
        if isinstance(input, SolarAzimuth):
            return input
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `solar_azimuth_series`")


class UnrefractedSolarZenithModel(BaseModel):
    unrefracted_solar_zenith: float | UnrefractedSolarZenith | None = (
        UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
    )

    @field_validator("unrefracted_solar_zenith")
    def validate_unrefracted_solar_zenith(cls, input) -> UnrefractedSolarZenith:
        if isinstance(input, UnrefractedSolarZenith):
            return input
        elif isinstance(input, float):
            return UnrefractedSolarZenith(value=input, unit=RADIANS)
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `unrefracted_solar_zenith`")


class ElevationModel(BaseModel):
    elevation: confloat(ge=0, le=8848) | Elevation
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        description="""Elevation""",
    )

    @field_validator("elevation")
    def validate_elevation(cls, input) -> Elevation:
        if isinstance(input, Elevation):
            return input
        elif isinstance(input, float):
            return Elevation(value=input, unit="meters")
        else:
            raise ValueError(f"{MESSAGE_UNSUPPORTED_TYPE} `elevation`")

        # valid_units = "meters"
        # if not unit == valid_units:
        #     raise ValueError(f"elevation must be given in {valid_units}")
        # return v


class IrradianceInputModel(BaseModel):
    linke_turbidity_factor: confloat(
        ge=0, le=8
    )  # help='A measure of atmospheric turbidity',
    optical_air_mass: float
    extraterrestial_irradiance: confloat(ge=1360) = (
        1360.8  # description="The average solar radiation at the top of the atmosphere ~1360.8 W/m^2 (Kopp, 2011)")
    )
