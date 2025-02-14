from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo

from devtools import debug
import numpy
from pandas import DatetimeIndex, isna
from xarray import DataArray

from pvgisprototype import Latitude, Longitude, SurfaceOrientation, SurfaceTilt
from pvgisprototype.algorithms.iqbal.solar_incidence import (
    calculate_solar_incidence_series_iqbal,
)
from pvgisprototype.algorithms.jenco.solar_altitude import (
    calculate_solar_altitude_series_jenco,
)
from pvgisprototype.algorithms.jenco.solar_azimuth import (
    calculate_solar_azimuth_series_jenco,
)
from pvgisprototype.algorithms.jenco.solar_declination import (
    calculate_solar_declination_series_jenco,
)
from pvgisprototype.algorithms.jenco.solar_incidence import (
    calculate_solar_incidence_series_jenco,
)
from pvgisprototype.algorithms.noaa.solar_altitude import (
    calculate_solar_altitude_series_noaa,
)
from pvgisprototype.algorithms.noaa.solar_azimuth import (
    calculate_solar_azimuth_series_noaa,
)
from pvgisprototype.algorithms.noaa.solar_declination import (
    calculate_solar_declination_series_noaa,
)
from pvgisprototype.algorithms.noaa.solar_hour_angle import (
    calculate_solar_hour_angle_series_noaa,
)
from pvgisprototype.algorithms.noaa.solar_zenith import (
    calculate_solar_zenith_series_noaa,
)
from pvgisprototype.algorithms.pvis.solar_altitude import (
    calculate_solar_altitude_series_hofierka,
)
from pvgisprototype.algorithms.pvis.solar_azimuth import (
    calculate_solar_azimuth_series_hofierka,
)
from pvgisprototype.algorithms.pvis.solar_declination import (
    calculate_solar_declination_series_hofierka,
)
from pvgisprototype.algorithms.pvis.solar_hour_angle import (
    calculate_solar_hour_angle_series_hofierka,
)
from pvgisprototype.algorithms.pvis.solar_incidence import (
    calculate_solar_incidence_series_hofierka,
)
from pvgisprototype.algorithms.pvis.shading import(
    calculate_surface_in_shade_series_pvis
)
# from pvgisprototype.algorithms.pvlib.shade import calculate_surface_in_shade_series_pvlib
from pvgisprototype.algorithms.pvlib.solar_altitude import (
    calculate_solar_altitude_series_pvlib,
)
from pvgisprototype.algorithms.pvlib.solar_azimuth import (
    calculate_solar_azimuth_series_pvlib,
)
from pvgisprototype.algorithms.pvlib.solar_declination import (
    calculate_solar_declination_series_pvlib,
)
from pvgisprototype.algorithms.pvlib.solar_hour_angle import (
    calculate_solar_hour_angle_series_pvlib,
)
from pvgisprototype.algorithms.pvlib.solar_incidence import (
    calculate_solar_incidence_series_pvlib,
)
from pvgisprototype.algorithms.pvlib.solar_zenith import (
    calculate_solar_zenith_series_pvlib,
)
from pvgisprototype.api.position.conversions import (
    convert_north_to_south_radians_convention,
)
from pvgisprototype.api.position.event_time import model_solar_event_time_series
from pvgisprototype.api.position.models import (
    SUN_HORIZON_POSITION_DEFAULT,
    ShadingModel,
    SolarEvent,
    SolarIncidenceModel,
    SolarPositionModel,
    SunHorizonPositionModel,
    SolarTimeModel,
    SolarPositionParameter,
)
from pvgisprototype.api.position.shading import model_surface_in_shade_series
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    AZIMUTH_ORIGIN_NAME,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    INCIDENCE_ALGORITHM_NAME,
    INCIDENCE_DEFINITION,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    PERIGEE_OFFSET,
    RADIANS,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_EVENTS_NAME,
    SUN_HORIZON_POSITIONS_NAME,  # Requested Sun-Horizon Positions
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_NAME,
    UNIT_NAME,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.api.position.output import generate_dictionary_of_surface_in_shade_series
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.validation.functions import (
    ModelSolarPositionOverviewSeriesInputModel,
    validate_with_pydantic,
)
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT, FINGERPRINT_COLUMN_NAME
from pvgisprototype.core.hashing import generate_hash


@log_function_call
@validate_with_pydantic(ModelSolarPositionOverviewSeriesInputModel)
def model_solar_position_overview_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    event: List[SolarEvent | None] = [None],
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    # solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> Tuple:
    """Model solar position parameters for a position and moment in time.

    Model essential solar position parameters for a solar surface
    orientation and tilt at a given geographic position for a time series based
    on a given solar position model (as in positioning algorithm, see class
    `SolarPositionModel`) and solar time model (as in solar timing algorithm,
    see class `SolarTimeModel`) :

    - solar declination
    - solar hour angle
    - solar zenith
    - solar altitude
    - solar azimuth
    - solar incidence
    - behind horizon

    Notes
    -----
    The solar altitude angle measures from the horizon up towards the zenith
    (positive, and down towards the nadir (negative)). The altitude is zero all
    along the great circle between zenith and nadir.

    The solar azimuth angle measures horizontally around the horizon from north
    through east, south, and west.

    In order to avoid confusion, the solar incidence angle series are derived
    using specific functions for each "algorithm". For example, the NOAA solar
    positioning set of equations are "bound" to the
    `calculate_solar_incidence_series_iqbal()`. However, thinking of more
    flexibility, for example to facilitate a cross-comparison
    between different implementations of the Equation of Time and their impact
    on different solar incidence angle definitions, we can refactor the source
    code to allow for combinations of different "blocks" of solar timing and
    positioning algorithms.

    The following combinations are currently the default ones to derive the
    solar incidence angle : 

    - SolarPositionModel.noaa + SolarIncidenceModel.iqbal

    - SolarPositionModel.jenco + SolarIncidenceModel.jenco
    
    - SolarPositionModel.hofierka + SolarIncidenceModel.hofierka

    """
    solar_declination_series = None  # updated if applicable
    solar_hour_angle_series = None
    solar_zenith_series = None  # updated if applicable
    solar_altitude_series = None
    solar_azimuth_series = None
    solar_incidence_series = None
    sun_horizon_position_series = None
    surface_in_shade_series = model_surface_in_shade_series(
        horizon_profile=horizon_profile,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_time_model=solar_time_model,
        solar_position_model=solar_position_model,
        shading_model=shading_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
    solar_event_series = model_solar_event_time_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                event=event,
                timezone=timezone,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
        )
    solar_event_type_series = solar_event_series.event
    solar_event_time_series = solar_event_series.value

    if solar_position_model.value == SolarPositionModel.noaa:
        solar_declination_series = calculate_solar_declination_series_noaa(
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )
        solar_hour_angle_series = calculate_solar_hour_angle_series_noaa(
            longitude=longitude,
            timestamps=timestamps,
            timezone=timezone,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )
        solar_zenith_series = calculate_solar_zenith_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )
        solar_altitude_series = calculate_solar_altitude_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )
        solar_azimuth_series = calculate_solar_azimuth_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )
        # Iqbal (1983) measures azimuthal angles from South !
        surface_orientation_south_convention = SurfaceOrientation(
            value=convert_north_to_south_radians_convention(
                north_based_angle=surface_orientation
            ),
            unit=RADIANS,
        )
        solar_incidence_series = calculate_solar_incidence_series_iqbal(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation_south_convention,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            sun_horizon_position=sun_horizon_position,
            surface_in_shade_series=surface_in_shade_series,
            complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output
        )

    if solar_position_model.value == SolarPositionModel.skyfield:
        pass
        # solar_hour_angle, solar_declination = calculate_solar_hour_angle_declination_skyfield(
        #     longitude=longitude,
        #     latitude=latitude,
        #     timestamp=timestamp,
        #     timezone=timezone,
        # )
        # solar_altitude, solar_azimuth = calculate_solar_altitude_azimuth_skyfield(
        #         longitude=longitude,
        #         latitude=latitude,
        #         timestamp=timestamp,
        #         )
        # solar_zenith = SolarZenith(
        #     value = 90 - solar_altitude.degrees,
        #     unit = DEGREES,
        #     position_algorithm=solar_azimuth.position_algorithm,
        #     timing_algorithm=solar_azimuth.timing_algorithm,
        # )

    if solar_position_model.value == SolarPositionModel.suncalc:
        pass
        # # note : first azimuth, then altitude
        # solar_azimuth_south_radians_convention, solar_altitude = suncalc.get_position(
        #     date=timestamp,  # this comes first here!
        #     lng=longitude.degrees,
        #     lat=latitude.degrees,
        # ).values()  # zero points to south
        # solar_azimuth = convert_south_to_north_radians_convention(
        #     solar_azimuth_south_radians_convention
        # )
        # solar_azimuth = SolarAzimuth(
        #     value=solar_azimuth,
        #     unit=RADIANS,
        #     position_algorithm='suncalc',
        #     timing_algorithm='suncalc',
        # )
        # solar_altitude = SolarAltitude(
        #     value=solar_altitude,
        #     unit=RADIANS,
        #     position_algorithm='suncalc',
        #     timing_algorithm='suncalc',
        # )
        # solar_zenith = SolarZenith(
        #     value = 90 - solar_altitude.degrees,
        #     unit = DEGREES,
        #     position_algorithm='suncalc',
        #     timing_algorithm='suncalc',
        # )

    if solar_position_model.value == SolarPositionModel.pysolar:
        pass
        # timestamp = attach_timezone(timestamp, timezone)

        # solar_altitude = pysolar.solar.get_altitude(
        #     latitude_deg=latitude.degrees,  # this comes first
        #     longitude_deg=longitude.degrees,
        #     when=timestamp,
        # )  # returns degrees by default
        # # required by output function
        # solar_altitude = SolarAltitude(
        #     value=solar_altitude,
        #     unit=DEGREES,
        #     position_algorithm='pysolar',
        #     timing_algorithm='pysolar',
        # )
        # solar_zenith = SolarZenith(
        #     value = 90 - solar_altitude.degrees,
        #     unit = DEGREES,
        #     position_algorithm=solar_altitude.position_algorithm,
        #     timing_algorithm=solar_altitude.timing_algorithm,
        # )
        # solar_azimuth = pysolar.solar.get_azimuth(
        #     latitude_deg=latitude.degrees,  # this comes first
        #     longitude_deg=longitude.degrees,
        #     when=timestamp,
        # )  # returns degrees by default
        # # required by output function
        # solar_azimuth = SolarAzimuth(
        #     value=solar_azimuth,
        #     unit=DEGREES,
        #     position_algorithm='pysolar',
        #     timing_algorithm='pysolar',
        # )

    if solar_position_model.value == SolarPositionModel.jenco:
        solar_declination_series = calculate_solar_declination_series_jenco(
            timestamps=timestamps,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
        solar_altitude_series = calculate_solar_altitude_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=0,
            log=log,
        )
        solar_azimuth_series = calculate_solar_azimuth_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=0,
            log=log,
        )  # North = 0
        surface_orientation_south_convention = SurfaceOrientation(
            value=convert_north_to_south_radians_convention(
                north_based_angle=surface_orientation
            ),
            unit=RADIANS,
        )
        # And apparently, defined the complementary surface tilt angle too!
        # from math import pi
        # surface_tilt = SurfaceTilt(
        #         value=(pi/2 - surface_tilt.radians),
        #         unit=RADIANS,
        #         )
        # ---------------------------------------------------------- Update-Me
        solar_incidence_series = calculate_solar_incidence_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            # surface_orientation=surface_orientation,
            # surface_orientation=surface_orientation_east_convention,
            surface_orientation=surface_orientation_south_convention,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            surface_in_shade_series=surface_in_shade_series,
            complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value == SolarPositionModel.hofierka:
        solar_declination_series = calculate_solar_declination_series_hofierka(
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
        solar_hour_angle_series = calculate_solar_hour_angle_series_hofierka(
            longitude=longitude,
            timestamps=timestamps,
            timezone=timezone,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
        solar_altitude_series = calculate_solar_altitude_series_hofierka(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
        solar_azimuth_series = calculate_solar_azimuth_series_hofierka(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            # apply_atmospheric_refraction=apply_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )  # East = 0 !
        surface_orientation_south_convention = SurfaceOrientation(
            value=convert_north_to_south_radians_convention(
                north_based_angle=surface_orientation
            ),
            unit=RADIANS,
        )
        solar_incidence_series = calculate_solar_incidence_series_hofierka(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            # surface_orientation=surface_orientation,
            surface_orientation=surface_orientation_south_convention,
            surface_tilt=surface_tilt,
            complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value == SolarPositionModel.pvlib:

        solar_declination_series = calculate_solar_declination_series_pvlib(
            timestamps=timestamps,
            # dtype=dtype,
            # array_backend=array_backend,
            # verbose=verbose,
            # log=log,
        )
        solar_hour_angle_series = calculate_solar_hour_angle_series_pvlib(
            longitude=longitude,
            timestamps=timestamps,
            # timezone=timezone,
            # dtype=dtype,
            # array_backend=array_backend,
            # verbose=verbose,
            # log=log,
        )
        solar_zenith_series = calculate_solar_zenith_series_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
        solar_altitude_series = calculate_solar_altitude_series_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
        solar_azimuth_series = calculate_solar_azimuth_series_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
        solar_incidence_series = calculate_solar_incidence_series_pvlib(
            longitude=longitude,
            latitude=latitude,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            timestamps=timestamps,
            complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_incidence_series.sun_horizon_position is not None:
        sun_horizon_position_series = solar_incidence_series.sun_horizon_position
    else:
        sun_horizon_position = NOT_AVAILABLE

    if shading_model:

        surface_in_shade_series = model_surface_in_shade_series(
            horizon_profile=horizon_profile,
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            solar_time_model=solar_time_model,
            solar_position_model=solar_position_model,
            shading_model=shading_model,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )

    position_series = (
        solar_declination_series if solar_declination_series is not None else None,
        solar_hour_angle_series if solar_hour_angle_series is not None else None,
        solar_zenith_series if solar_zenith_series is not None else None,
        solar_altitude_series if solar_altitude_series is not None else None,
        solar_azimuth_series if solar_azimuth_series is not None else None,
        surface_orientation if surface_orientation is not None else None,
        surface_tilt if surface_tilt is not None else None,
        solar_incidence_series if solar_incidence_series is not None else None,
        sun_horizon_position_series if sun_horizon_position_series is not None else None,
        surface_in_shade_series if surface_in_shade_series is not None else None,
        solar_event_type_series if solar_event_series.event is not None else None,
        solar_event_time_series if solar_event_series.value is not None else None,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return position_series


def calculate_solar_position_overview_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    event: List[SolarEvent | None] = [None],
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.noaa],
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = VERBOSE_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> Dict:
    """Calculate an overview of solar position parameters for a time series.

    Calculate an overview of solar position parameters for a solar surface
    orientation and tilt at a given geographic position for a time series and
    for the user-requested solar position models (as in positioning algorithms)
    and one solar time model (as in solar timing algorithm).

    Notes
    -----
    While it is straightforward to report the solar position parameters for a
    series of solar position models (positioning algorithms), offering the
    option for multiple solar time models (timing algorithms), would mean to
    carefully craft the combinations for each solar time model and solar
    position models. Not impossible, yet something for expert users that would
    like to assess different combinations of algorithms to explore and assess
    solar position parameters.

    """
    results = {}
    for solar_position_model in solar_position_models:
        # for the time being! ------------------------------------------------
        if solar_position_model != SolarPositionModel.noaa:
            logger.warning(
                f"Solar geometry overview series is not implemented for the requested solar position model: {solar_position_model}!"
            )
        # --------------------------------------------------------------------
        if (
            solar_position_model != SolarPositionModel.all
        ):  # ignore 'all' in the enumeration
            (
                solar_declination_series,
                solar_hour_angle_series,
                solar_zenith_series,
                solar_altitude_series,
                solar_azimuth_series,
                surface_orientation,
                surface_tilt,
                solar_incidence_series,
                sun_horizon_position_series,
                surface_in_shade_series,
                solar_event_type_series,
                solar_event_time_series,
            ) = model_solar_position_overview_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                event=event,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                solar_time_model=solar_time_model,
                solar_position_model=solar_position_model,
                sun_horizon_position=sun_horizon_position,
                horizon_profile=horizon_profile,
                shading_model=shading_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                # solar_incidence_model=solar_incidence_model,
                complementary_incidence_angle=complementary_incidence_angle,
                zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                validate_output=validate_output,
            )
            solar_position_model_overview = {
                solar_position_model.name: {
                    SolarPositionParameter.timing: (
                        solar_hour_angle_series.timing_algorithm
                        if solar_hour_angle_series
                        else NOT_AVAILABLE
                    ),
                    SolarPositionParameter.declination: (
                        getattr(
                            solar_declination_series, angle_output_units, NOT_AVAILABLE
                        )
                        if solar_declination_series
                        else NOT_AVAILABLE
                    ),
                    SolarPositionParameter.hour_angle: (
                        getattr(
                            solar_hour_angle_series, angle_output_units, NOT_AVAILABLE
                        )
                        if solar_hour_angle_series
                        else NOT_AVAILABLE
                    ),
                    SolarPositionParameter.positioning: solar_position_model.value,
                    SolarPositionParameter.zenith: (
                        getattr(solar_zenith_series, angle_output_units, NOT_AVAILABLE)
                        if solar_zenith_series
                        else NOT_AVAILABLE
                    ),
                    SolarPositionParameter.altitude: (
                        getattr(
                            solar_altitude_series, angle_output_units, NOT_AVAILABLE
                        )
                        if solar_altitude_series
                        else NOT_AVAILABLE
                    ),
                    SolarPositionParameter.azimuth: (
                        getattr(solar_azimuth_series, angle_output_units, NOT_AVAILABLE)
                        if solar_azimuth_series
                        else NOT_AVAILABLE
                    ),
                    AZIMUTH_ORIGIN_NAME: (  # Not meant as a column name !
                        solar_azimuth_series.origin
                        if solar_azimuth_series
                        else NOT_AVAILABLE
                    ),
                    SURFACE_ORIENTATION_NAME: (
                        getattr(surface_orientation, angle_output_units, NOT_AVAILABLE)
                        if surface_orientation
                        else None
                    ),
                    SURFACE_TILT_NAME: (
                        getattr(surface_tilt, angle_output_units, NOT_AVAILABLE)
                        if surface_tilt
                        else None
                    ),
                    SolarPositionParameter.incidence: (
                        getattr(
                            solar_incidence_series, angle_output_units, NOT_AVAILABLE
                        )
                        if solar_incidence_series
                        else NOT_AVAILABLE
                    ),
                    INCIDENCE_ALGORITHM_NAME: (
                        solar_incidence_series.incidence_algorithm
                        if solar_incidence_series
                        else NOT_AVAILABLE
                    ),
                    INCIDENCE_DEFINITION: (
                        solar_incidence_series.definition
                        if solar_incidence_series
                        else NOT_AVAILABLE
                    ),
                    SUN_HORIZON_POSITIONS_NAME: (  # Requested positions
                        sun_horizon_position
                        if sun_horizon_position
                        else NOT_AVAILABLE
                    ),
                    SolarPositionParameter.sun_horizon: (  # Series of sun-horizon position
                        sun_horizon_position_series
                        if sun_horizon_position_series is not None
                        else NOT_AVAILABLE
                    ),
                    **generate_dictionary_of_surface_in_shade_series(
                            surface_in_shade_series,
                            angle_output_units,
                    ),  # This is the horizon height profile !
                    SOLAR_EVENTS_NAME: (  # Requested solar events
                        event
                        if event
                        else NOT_AVAILABLE
                    ),
                    **(
                        {SolarPositionParameter.event_type: solar_event_type_series}
                        if solar_event_type_series is not None and not (
                            isinstance(solar_event_type_series,
                                       (list, numpy.ndarray)) and
                            all(x is None for x in solar_event_type_series)
                        )
                        else {}
                    ),
                    **(
                        {SolarPositionParameter.event_time: solar_event_time_series}
                        if solar_event_time_series is not None and not (
                            isinstance(solar_event_time_series, DatetimeIndex) and
                            all(isna(x) for x in solar_event_time_series)
                        )
                        else {}
                    ),
                    UNIT_NAME: angle_output_units,
                    FINGERPRINT_COLUMN_NAME: (
                        generate_hash(solar_incidence_series)
                        if fingerprint
                        else NOT_AVAILABLE
                    ),
                }
            }
            results = results | solar_position_model_overview

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return results
