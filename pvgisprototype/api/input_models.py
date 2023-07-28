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


class RandomTimeInputModel(BaseModel):
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





class SolarPositionInputModel(BaseModel):
    model: SolarPositionModels = SolarPositionModels.skyfield
    apply_atmospheric_refraction: bool = True

class SolarTimeInputModel(SolarPositionInputModel):
    refracted_solar_zenith: float = 1.5853349194640094,  # radians




class SolarAltitudeInput(
    ModelToDict,
    BaseCoordinatesInputModel,
    BaseTimeInputModel,
    BaseAngleOutputUnitsModel,
):
    pass


class SolarAzimuthInput(SolarAltitudeInput):
    pass


class EarthOrbitInputModel(BaseModel):
    days_in_a_year: float = 365.25
    orbital_eccentricity: float = 0.03344
    perigee_offset: float = 0.048869


class SolarDeclinationInput(
        ModelToDict,
        # timestamp: Annotated[Optional[datetime], typer.Argument(
        #     help='Timestamp',
        #     default_factory=now_utc_datetimezone)],
        # timezone: Annotated[Optional[str], typer.Option(
        #     help='Timezone',
        #     callback=convert_to_timezone)] = None,
        BaseTimeInputModel,
        # days_in_a_year: float = 365.25,
        # orbital_eccentricity: float = 0.03344,
        # perigee_offset: float = 0.048869,
        EarthOrbitInputModel,
        # output_units: Annotated[str, typer.Option(
        #     '-o',
        #     '--output-units',
        #     show_default=True,
        #     case_sensitive=False,
        #     help="Output units for solar declination (degrees or radians)")] = 'radians',
        BaseAngleOutputUnitsModel,
    ):
        # debug(locals())
        pass


class SolarTimeModel(BaseModel):
    solar_time: time     # confloat(ge=0, le=86400)
    model_config = ConfigDict(
        description="""The solar time (ST) is a calculation of the passage of time based
        on the position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds.""",
        json_schema_extra = {
            "units": "seconds",
        },
    )

class SurfaceTilt(BaseModel):
    surface_tilt: confloat(ge=-pi/2, le=pi/2) = 0
    model_config = ConfigDict(
        description="""Surface tilt (or slope) (β) is the angle between the inclined
        surface (slope) and the horizontal plane.""",
        json_schema_extra = {
            "units": "radians",
        },
    )

class SurfaceOrientation(BaseModel):
    surface_orientation: confloat(ge=-pi/2, le=pi/2) = 0


class SolarDeclinationModel(BaseModel):
    solar_declination: confloat(ge=-0.4092797096, le=0.4092797096) = 0
    model_config = ConfigDict(
        description="""Solar declination (δ) is the angle between the equator and a
        line drawn from the centre of the Earth to the centre of the sun.""",
        json_schema_extra = {
            "units": "radians",
        },
    )

class HourAngleInput(
        ModelToDict,
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
        ModelToDict,
        # latitude: Annotated[Optional[float], typer.Argument(
        #     min=-90, max=90)],
        Latitude,
        # surface_tilt: Annotated[Optional[float], typer.Argument(
        #     min=0, max=90)] = 0,
        SurfaceTilt,
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
    ModelToDict,
    # longitude: Annotated[float, typer.Argument(
    #     callback=convert_to_radians,
    #     min=-180, max=180)],
    # latitude: Annotated[float, typer.Argument(
    #     callback=convert_to_radians,
    #     min=-90, max=90)],
    BaseCoordinatesInputModel,
    # timestamp: Annotated[Optional[datetime.datetime], typer.Argument(
    #     help='Timestamp',
    #     default_factory=now_utc_datetimezone)],
    # timezone: Annotated[Optional[str], typer.Option(
    #     help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
    #     callback=ctx_convert_to_timezone)] = None,
    BaseTimeInputModel,
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
    SolarPositionInputModel,
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
    ModelToDict,
    # longitude: Annotated[float, typer.Argument(
    #     callback=convert_to_radians,
    #     min=-180, max=180)],
    # latitude: Annotated[float, typer.Argument(
    #     callback=convert_to_radians,
    #     min=-90, max=90)],
    BaseCoordinatesInputModel,
    # timestamp: Annotated[Optional[datetime], typer.Argument(
    #     help='Timestamp',
    #     default_factory=now_utc_datetimezone)],
    # timezone: Annotated[Optional[str], typer.Option(
    #     help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
    #     callback=ctx_convert_to_timezone)] = None,
    BaseTimeInputModel,
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
    SolarTimeInputModel,
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
    EarthOrbitInputModel,
    # time_offset_global: Annotated[float, typer.Option(
    #     help='Global time offset')] = 0,
    # hour_offset: Annotated[float, typer.Option(
    #     help='Hour offset')] = 0,
    TimeOffsetModel,
):
    pass


class SolarIncidenceStandarInput(
    Latitude,
    SolarDeclinationModel,
    BaseAngleOutputUnitsModel,
):
    surface_orientation: float = 0
    hour_angle: float


class SolarIncidenceInput(SolarTimeInput):
    random_time: bool = False
    hour_angle: float
    surface_tilt: float = 0
    surface_orientation: float = 0
    rounding_places: int = 5
    verbose: bool = False


class FractionalYearInput(
    ModelToDict,
    BaseTimestampInputModel,
    BaseAngleInternalUnitsModel,
):
    pass


class RelativeLongitudeInput(
    Latitude,
    SurfaceTilt,
    SurfaceOrientation,
):
    angle_output_units: str = 'radians'
