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
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex
from xarray import DataArray

from pvgisprototype import (
    Latitude,
    Longitude,
    SurfaceOrientation,
    SurfaceTilt,
    SolarPositionOverview,
)
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
from pvgisprototype.algorithms.hofierka.position.solar_altitude import (
    calculate_solar_altitude_series_hofierka,
)
from pvgisprototype.algorithms.hofierka.position.solar_azimuth import (
    calculate_solar_azimuth_series_hofierka,
)
from pvgisprototype.algorithms.hofierka.position.solar_declination import (
    calculate_solar_declination_series_hofierka,
)
from pvgisprototype.algorithms.hofierka.position.solar_hour_angle import (
    calculate_solar_hour_angle_series_hofierka,
)
from pvgisprototype.algorithms.hofierka.position.solar_incidence import (
    calculate_solar_incidence_series_hofierka,
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
)
from pvgisprototype.api.position.shading import model_surface_in_shade_series
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    ECCENTRICITY_PHASE_OFFSET,
    RADIANS,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.validation.functions import (
    ModelSolarPositionOverviewSeriesInputModel,
    validate_with_pydantic,
)
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT


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
    shading_model: ShadingModel = ShadingModel.pvgis,
    adjust_for_atmospheric_refraction: bool = True,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    # solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
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
    - sun-to-horizon position

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
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
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
    solar_event_type_series = solar_event_series.event_type
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
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
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
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
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
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
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
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
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
        #     solar_positioning_algorithm=solar_azimuth.solar_positioning_algorithm,
        #     solar_timing_algorithm=solar_azimuth.timing_algorithm,
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
        #     solar_positioning_algorithm='suncalc',
        #     solar_timing_algorithm='suncalc',
        # )
        # solar_altitude = SolarAltitude(
        #     value=solar_altitude,
        #     unit=RADIANS,
        #     solar_positioning_algorithm='suncalc',
        #     solar_timing_algorithm='suncalc',
        # )
        # solar_zenith = SolarZenith(
        #     value = 90 - solar_altitude.degrees,
        #     unit = DEGREES,
        #     solar_positioning_algorithm='suncalc',
        #     solar_timing_algorithm='suncalc',
        # )

    if solar_position_model.value == SolarPositionModel.jenco:
        solar_declination_series = calculate_solar_declination_series_jenco(
            timestamps=timestamps,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
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
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
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
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
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
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            surface_in_shade_series=surface_in_shade_series,
            complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
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
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
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
            # adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
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
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            # unrefracted_solar_zenith=unrefracted_solar_zenith,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
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
        solar_event_type_series if solar_event_series.event_type is not None else None,
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
    # solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvgis,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
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
                sun_horizon_position_series,  # time series of relative position
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
                sun_horizon_position=sun_horizon_position,  # positions for which to perform calculations !
                horizon_profile=horizon_profile,
                shading_model=shading_model,
                adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                # solar_incidence_model=solar_incidence_model,
                complementary_incidence_angle=complementary_incidence_angle,
                zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                validate_output=validate_output,
            )
            solar_position_overview = SolarPositionOverview(
                #
                solar_position_model=solar_position_model,
                # Positioning
                solar_timing_algorithm=solar_time_model,
                solar_declination=solar_declination_series,
                solar_hour_angle=solar_hour_angle_series,
                solar_positioning_algorithm=solar_position_model,
                adjusted_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                solar_zenith=solar_zenith_series,
                adjust_for_atmospheric_refraction=solar_zenith_series.adjusted_for_atmospheric_refraction,
                solar_altitude=solar_altitude_series,
                refracted_solar_altitude=solar_altitude_series.refracted_value,
                solar_azimuth=solar_azimuth_series,
                solar_azimuth_origin=solar_azimuth_series.origin,
                # Incidence
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                solar_incidence=solar_incidence_series,
                solar_incidence_model=solar_incidence_series.algorithm,
                solar_incidence_definition=solar_incidence_series.definition,
                # Sun-to-Horizon  -- ** Rethink parameters naming here ! **
                sun_horizon_position=sun_horizon_position_series,  # time series of relative sun position !
                sun_horizon_positions=sun_horizon_position,  # positions for which calculations were performed !
                horizon_height=surface_in_shade_series.horizon_height,
                surface_in_shade=surface_in_shade_series,
                shading_algorithm=shading_model,
                # shading_states=shading_states,
                # visible=~surface_in_shade_series.value if surface_in_shade_series else NOT_AVAILABLE,
                visible=surface_in_shade_series.visible,
                # Solar events
                event=event,
                event_type=solar_event_type_series,
                event_time=solar_event_time_series,
                #
                angle_output_units=solar_incidence_series.unit,
            )
            solar_position_overview.build_output(verbose=verbose, fingerprint=fingerprint)
            results = {
                solar_position_model.name: solar_position_overview.output
            }

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return results
