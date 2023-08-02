from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import confloat
from typing import Optional
from typing import Union
from zoneinfo import ZoneInfo
from datetime import datetime
from datetime import time
from math import pi
from pydantic import validator

from .geometry.solar_models import SolarPositionModels

from pvgisprototype.api.data_classes import OrbitalEccentricity
from pvgisprototype.api.data_classes import PerigeeOffset
from pvgisprototype.api.data_classes import RefractedSolarZenith
from pvgisprototype.api.data_classes import SurfaceTilt
from pvgisprototype.api.data_classes import SurfaceOrientation
from pvgisprototype.api.data_classes import Latitude
from pvgisprototype.api.data_classes import Longitude
from pvgisprototype.api.data_classes import HourAngleSunrise
from pvgisprototype.api.data_classes import SolarTime
from pvgisprototype.api.data_classes import TrueSolarTime
from pvgisprototype.api.data_classes import EquationOfTime
from pvgisprototype.api.data_classes import FractionalYear
from pvgisprototype.api.data_classes import TimeOffset
from pvgisprototype.api.data_classes import EventTime
from pvgisprototype.api.data_classes import HourAngle
from pvgisprototype.api.data_classes import SolarAltitude
from pvgisprototype.api.data_classes import SolarAzimuth
from pvgisprototype.api.data_classes import CompassSolarAzimuth
from pvgisprototype.api.data_classes import SolarDeclination
from pvgisprototype.api.data_classes import SolarIncidence
from pvgisprototype.api.data_classes import SolarHourAngle
from pvgisprototype.api.data_classes import SolarZenith
from pvgisprototype.api.data_classes import SolarPosition


class ValidatedInputToDict(BaseModel):
    def pydantic_model_to_dict(self):
        d = {}
        for k, v in self:
            d[k] = v
        return d


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


class BaseTimestampModel(BaseModel):
    timestamp: datetime
    model_config = ConfigDict(arbitrary_types_allowed=True)


class RandomTimeModel(BaseModel):
    random_time: bool


class TimeOffsetModel(BaseModel):
    time_offset_global: float = 0
    hour_offset: float = 0


class BaseTimeOutputUnitsModel(BaseModel):
    time_output_units: Optional[str] = None

    @field_validator('time_output_units')
    @classmethod
    def validate_time_output_units(cls, v):
        valid_units = ['minutes', 'seconds', 'hours']
        if v not in valid_units:
            raise ValueError(f"time_output_units must be one of {valid_units}")
        return v


class BaseAngleOutputUnitsModel(BaseModel):
    angle_output_units: str
    model_config = ConfigDict(
        description="""Output units for solar geometry variables (degrees or radians).""",
    )

    @field_validator('angle_output_units')
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = ['radians', 'degrees']
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v
    

class BaseAngleInternalUnitsModel(BaseModel):                                               # NOTE: Maybe deprecate
    angle_units: str = 'radians'
    model_config = ConfigDict(
        description="""Angular units for internal calculations (degrees).""",
    )

    @field_validator('angle_units')
    @classmethod
    def validate_angle_units(cls, v):
        valid_units = ['radians']
        if v not in valid_units:
            raise ValueError(f"angle_units must be {valid_units}")
        return v


class SolarPositionModel(BaseModel):
    model: SolarPositionModels = SolarPositionModels.skyfield
    apply_atmospheric_refraction: bool = True


class EarthOrbitModel(BaseModel):
    days_in_a_year: float = 365.25                                      # TODO: Validator for this value if never changes
    orbital_eccentricity: float = 0.03344
    perigee_offset: float = 0.048869
        

class SolarTimeModel(BaseModel):
    solar_time: time
    model_config = ConfigDict(
        description="""The solar time (ST) is a calculation of the passage of time based
        on the position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds.""",
    )


class SurfaceTiltModel(BaseModel):
    surface_tilt: Union[confloat(ge=-pi/2, le=pi/2), SurfaceTilt]
    model_config = ConfigDict(
        description="""Surface tilt (or slope) (β) is the angle between the inclined
        surface (slope) and the horizontal plane.""",
    )

    @field_validator("surface_tilt")
    def surface_tilt_named_tuple(cls, input) -> SurfaceTilt:
        if isinstance(input, type(SurfaceTilt)):
            return input
        elif isinstance(input, float):
            return SurfaceTilt(value=input, unit='radians')
        else:
            raise ValueError("Unsupported surface_tilt type provided")


class SurfaceOrientationModel(BaseModel):
    surface_orientation: confloat(ge=-pi/2, le=pi/2) = 0


class SolarDeclinationModel(BaseModel):
    solar_declination: Union[confloat(ge=-0.4092797096, le=0.4092797096), SolarDeclination]
    model_config = ConfigDict(
        description="""Solar declination (δ) is the angle between the equator and a
        line drawn from the centre of the Earth to the centre of the sun.""",
    )
    @field_validator("solar_declination")
    def solar_declination_named_tuple(cls, input) -> SolarDeclination:
        if isinstance(input, type(SolarDeclination)):
            return input
        elif isinstance(input, float):
            return SolarDeclination(value=input, unit='radians')
        else:
            raise ValueError("Unsupported solar_declination type provided")
        
# class HourAngleModel(BaseModel):
#     hour_angle: Union[confloat(ge=0, le=1), HourAngle]
#     model_config = ConfigDict(
#         description="""Solar hour angle.""",
#     )





class BaseCoordinatesInput(
    LongitudeModel,
    LatitudeModel,
):
    pass


class BaseTimeInput(BaseTimestampModel):
    timezone: Optional[ZoneInfo] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError("The `timezone` must be a valid `zoneinfo.ZoneInfo` object.")
        return v


class SolarTimeInput(SolarPositionModel):
    refracted_solar_zenith: Union[float, RefractedSolarZenith]

    @field_validator("refracted_solar_zenith")
    def refracted_solar_zenith_named_tuple(cls, input) -> RefractedSolarZenith:
        if isinstance(input, RefractedSolarZenith):
            return input
        elif isinstance(input, float):
            return RefractedSolarZenith(value=input, unit='radians')
        else:
            raise ValueError("Unsupported `refracted_solar_zenith` type provided")


class SolarAltitudeInput(
    ValidatedInputToDict,
    BaseCoordinatesInput,
    BaseTimeInput,
    BaseAngleOutputUnitsModel,
):
    pass


class SolarAzimuthInput(SolarAltitudeInput):
    pass


class SolarDeclinationInput(
        ValidatedInputToDict,
        # timestamp: Annotated[Optional[datetime], typer.Argument(
        #     help='Timestamp',
        #     default_factory=now_utc_datetimezone)],
        # timezone: Annotated[Optional[str], typer.Option(
        #     help='Timezone',
        #     callback=convert_to_timezone)] = None,
        BaseTimeInput,
        EarthOrbitModel,
        # output_units: Annotated[str, typer.Option(
        #     '-o',
        #     '--output-units',
        #     show_default=True,
        #     case_sensitive=False,
        #     help="Output units for solar declination (degrees or radians)")] = 'radians',
        BaseAngleOutputUnitsModel,
    ):
        pass


class HourAngleInput(
        ValidatedInputToDict,
        SolarTimeModel,
        # output_units: Annotated[str, typer.Option(
        #     '-u',
        #     '--units',
        #     show_default=True,
        #     case_sensitive=False,
        #     help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        BaseAngleOutputUnitsModel,
    ):
        pass


class HourAngleSunriseInput(
        ValidatedInputToDict,
        # latitude: Annotated[Optional[float], typer.Argument(
        #     min=-90, max=90)],
        LatitudeModel,
        # surface_tilt: Annotated[Optional[float], typer.Argument(
        #     min=0, max=90)] = 0,
        SurfaceTiltModel,
        SolarDeclinationModel,
        # solar_declination: Annotated[Optional[float], typer.Argument(
        #     min=-90, max=90)] = 180,                                  # XXX: Default value changed from 180 to 0
        # output_units: Annotated[str, typer.Option(
        #     '-u',
        #     '--units',
        #     show_default=True,
        #     case_sensitive=False,
        #     help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        BaseAngleOutputUnitsModel,
        ):
    pass


class SolarPositionInput(
    ValidatedInputToDict,
    # longitude: Annotated[float, typer.Argument(
    #     callback=convert_to_radians,
    #     min=-180, max=180)],
    # latitude: Annotated[float, typer.Argument(
    #     callback=convert_to_radians,
    #     min=-90, max=90)],
    BaseCoordinatesInput,
    # timestamp: Annotated[Optional[datetime.datetime], typer.Argument(
    #     help='Timestamp',
    #     default_factory=now_utc_datetimezone)],
    # timezone: Annotated[Optional[str], typer.Option(
    #     help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
    #     callback=ctx_convert_to_timezone)] = None,
    BaseTimeInput,
    # model: Annotated[SolarPositionModels, typer.Option(
    #     '-m',
    #     '--model',
    #     show_default=True,
    #     show_choices=True,
    #     case_sensitive=False,
    #     help="Model to calculate solar position")] = SolarPositionModels.skyfield,
    # apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
    #     '-a',
    #     '--atmospheric-refraction',
    #     help='Apply atmospheric refraction functions',
    #     )] = True,
    SolarPositionModel,
    # time_output_units: Annotated[str, typer.Option(
    #     '-u',
    #     '--output-units',
    #     show_default=True,
    #     case_sensitive=False,
    #     help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
    # BaseTimeOutputUnitsModel,
    # angle_units: Annotated[str, typer.Option(
    #     '-u',
    #     '--units',
    #     show_default=True,
    #     case_sensitive=False,
    #     help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
    # BaseAngleInternalUnitsModel,
    # angle_output_units: Annotated[str, typer.Option(
    #     '-u',
    #     '--units',
    #     show_default=True,
    #     case_sensitive=False,
    #     help="Angular units for solar position calculations output (degrees or radians)")] = 'radians',
    BaseAngleOutputUnitsModel,
):
    pass


class SolarTimeInput(
    ValidatedInputToDict,
    # longitude: Annotated[float, typer.Argument(
    #     callback=convert_to_radians,
    #     min=-180, max=180)],
    # latitude: Annotated[float, typer.Argument(
    #     callback=convert_to_radians,
    #     min=-90, max=90)],
    BaseCoordinatesInput,
    # timestamp: Annotated[Optional[datetime], typer.Argument(
    #     help='Timestamp',
    #     default_factory=now_utc_datetimezone)],
    # timezone: Annotated[Optional[str], typer.Option(
    #     help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
    #     callback=ctx_convert_to_timezone)] = None,
    BaseTimeInput,
    # model: Annotated[SolarTimeModels, typer.Option(
    #     '-m',
    #     '--model',
    #     help="Model to calculate solar position",
    #     show_default=True,
    #     show_choices=True,
    #     case_sensitive=False)] = SolarTimeModels.skyfield,
    # refracted_solar_zenith: float = 1.5853349194640094,  # radians
    # apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
    #     '-a',
    #     '--atmospheric-refraction',
    #     help='Apply atmospheric refraction functions',
    #     )] = True,
    SolarTimeInput,
    # time_output_units: Annotated[str, typer.Option(
    #     '-u',
    #     '--output-units',
    #     show_default=True,
    #     case_sensitive=False,
    #     help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
    BaseTimeOutputUnitsModel,
    # angle_units: Annotated[str, typer.Option(
    #     '-u',
    #     '--units',
    #     show_default=True,
    #     case_sensitive=False,
    #     help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
    # BaseAngleInternalUnitsModel,
    # angle_output_units: Annotated[str, typer.Option(
    #     '-u',
    #     '--units',
    #     show_default=True,
    #     case_sensitive=False,
    #     help="Angular units for solar position calculations output (degrees or radians)")] = 'radians',
    BaseAngleOutputUnitsModel,
    # days_in_a_year: Annotated[float, typer.Option(
    #     help='Days in a year')] = 365.25,
    # perigee_offset: Annotated[float, typer.Option(
    #     help='Perigee offset')] = 0.048869,
    # orbital_eccentricity: Annotated[float, typer.Option(
    #     help='Eccentricity')] = 0.01672,
    EarthOrbitModel,
    # time_offset_global: Annotated[float, typer.Option(
    #     help='Global time offset')] = 0,
    # hour_offset: Annotated[float, typer.Option(
    #     help='Hour offset')] = 0,
    TimeOffsetModel,
):
    pass


class SolarIncidenceStandardInput(
    LatitudeModel,
    SolarDeclinationModel,
    BaseAngleOutputUnitsModel,
    SurfaceOrientationModel,
):
    hour_angle: float

class SolarIncidenceJencoInput(
    BaseCoordinatesInput,
    BaseTimeInput,
    RandomTimeModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    EarthOrbitModel,
    BaseTimeOutputUnitsModel,
    BaseAngleInternalUnitsModel,
    BaseAngleOutputUnitsModel,
):
    hour_angle: float



class SolarIncidenceInput(
    SolarTimeInput,
    SurfaceTiltModel,
    SurfaceOrientationModel,
):
    random_time: bool = False
    hour_angle: float
    rounding_places: int = 5
    verbose: bool = False




class FractionalYearInput(
    ValidatedInputToDict,
    BaseTimestampModel,
    BaseAngleInternalUnitsModel,
):
    pass


class RelativeLongitudeInput(
    LatitudeModel,
    SurfaceTiltModel,
    SurfaceOrientationModel,
    BaseAngleOutputUnitsModel,
):
    pass
