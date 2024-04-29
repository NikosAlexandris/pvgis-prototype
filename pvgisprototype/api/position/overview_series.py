from pvgisprototype.log import logger
from devtools import debug
from typing import List, Union, Sequence
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa
from pvgisprototype.api.position.incidence_series import model_solar_incidence_time_series
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarGeometryOverviewTimeSeriesInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype import SolarAltitude
from pvgisprototype import SurfaceOrientation
from pvgisprototype import SurfaceTilt
from datetime import datetime
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import DECLINATION_NAME
from pvgisprototype.constants import HOUR_ANGLE_NAME
from pvgisprototype.constants import POSITION_ALGORITHM_NAME
from pvgisprototype.constants import ZENITH_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import AZIMUTH_NAME
from pvgisprototype.constants import SURFACE_TILT_NAME
from pvgisprototype.constants import SURFACE_ORIENTATION_NAME
from pvgisprototype.constants import INCIDENCE_ALGORITHM_NAME
from pvgisprototype.constants import INCIDENCE_NAME
from pvgisprototype.constants import INCIDENCE_DEFINITION
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import UNITS_NAME
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.cli.messages import NOT_IMPLEMENTED
from pandas import DatetimeIndex


@validate_with_pydantic(ModelSolarGeometryOverviewTimeSeriesInputModel)
def model_solar_geometry_overview_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    surface_orientation: None | SurfaceOrientation,
    surface_tilt: None | SurfaceTilt,
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    apply_atmospheric_refraction: bool = True,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = VERBOSE_LEVEL_DEFAULT,
) -> List:
    """
    """
    solar_declination_series = None  # updated if applicable
    solar_hour_angle_series = None
    solar_zenith_series = None  # updated if applicable
    solar_altitude_series = None
    solar_azimuth_series = None
    solar_incidence_series = None
    debug(locals())

    if solar_position_model.value == SolarPositionModel.noaa:

        solar_declination_series = calculate_solar_declination_time_series_noaa(
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
        solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
            longitude=longitude,
            timestamps=timestamps,
            timezone=timezone,
            verbose=verbose,
            log=log,
        )
        solar_zenith_series = calculate_solar_zenith_time_series_noaa(
            latitude=latitude,
            timestamps=timestamps,
            solar_hour_angle_series=solar_hour_angle_series,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
            log=log,
        )
        solar_altitude_series = calculate_solar_altitude_time_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
            log=log,
        )
        solar_azimuth_series = calculate_solar_azimuth_time_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
            log=log,
        )
        solar_incidence_series = model_solar_incidence_time_series(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            solar_incidence_model=solar_incidence_model,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            complementary_incidence_angle=complementary_incidence_angle,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value == SolarPositionModel.skyfield:
        pass

    if solar_position_model.value == SolarPositionModel.suncalc:
        pass

    if solar_position_model.value == SolarPositionModel.pysolar:
        pass

    if solar_position_model.value == SolarPositionModel.pvis:
        pass

    if solar_position_model.value == SolarPositionModel.pvlib:
        pass

    position_series = (
        solar_declination_series if solar_declination_series is not None else None,
        solar_hour_angle_series if solar_hour_angle_series is not None else None,
        solar_zenith_series if solar_zenith_series is not None else None,
        solar_altitude_series if solar_altitude_series is not None else None,
        solar_azimuth_series if solar_azimuth_series is not None else None,
        surface_orientation if surface_orientation is not None else None,
        surface_tilt if surface_tilt is not None else None,
        solar_incidence_series if solar_incidence_series is not None else None,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return position_series


from typing import Optional
def calculate_solar_geometry_overview_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: datetime,
    timezone: ZoneInfo,
    surface_orientation: SurfaceOrientation,
    surface_tilt: SurfaceTilt,
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.skyfield],
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: SolarTimeModel = SolarTimeModel.skyfield,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = VERBOSE_LEVEL_DEFAULT,
) -> List:
    """Calculates the solar geometry overview for a time series

    Calculate the solar geometry overview for a geographic position over a
    series of timestamps for the user-requested solar position models (as in
    positioning algorithms) and one solar time model (as in solar timing
    algorithm).

    Notes
    -----
    While it is straightforward to report the solar geometry parameters for a
    series of solar position models (positioning algorithms), offering the
    option for multiple solar time models (timing algorithms), would mean to
    carefully craft the combinations for each solar time model and solar
    position models. Not impossible, yet something for expert users that would
    like to assess different combinations of algorithms to derive solar
    geometry parameters.

    """
    debug(locals())
    for solar_position_model in solar_position_models:
        # for the time being! ------------------------------------------------
        if solar_position_model != SolarPositionModel.noaa:
            logger.warning(f"Solar geometry overview series is not implemented for the requested solar position model: {solar_position_model}!")
        # --------------------------------------------------------------------
        if solar_position_model != SolarPositionModel.all:  # ignore 'all' in the enumeration
            (
                solar_declination_series,
                solar_hour_angle_series,
                solar_zenith_series,
                solar_altitude_series,
                solar_azimuth_series,
                surface_orientation,
                surface_tilt,
                solar_incidence_series,
            ) = model_solar_geometry_overview_time_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                solar_time_model=solar_time_model,
                solar_position_model=solar_position_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                solar_incidence_model=solar_incidence_model,
                complementary_incidence_angle=complementary_incidence_angle,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                backend=array_backend,
                dtype=dtype,
                verbose=verbose,
                log=log,
            )
            results = {
                    solar_position_model.name: {
                        TIME_ALGORITHM_NAME: solar_azimuth_series.timing_algorithm if solar_azimuth_series else NOT_AVAILABLE,
                        DECLINATION_NAME: getattr(solar_declination_series, angle_output_units, NOT_AVAILABLE) if solar_declination_series else NOT_AVAILABLE,
                        HOUR_ANGLE_NAME: getattr(solar_hour_angle_series, angle_output_units, NOT_AVAILABLE) if solar_hour_angle_series else NOT_AVAILABLE,
                        POSITION_ALGORITHM_NAME: solar_position_model.value,
                        ZENITH_NAME: getattr(solar_zenith_series, angle_output_units, NOT_AVAILABLE) if solar_zenith_series else NOT_AVAILABLE,
                        ALTITUDE_NAME: getattr(solar_altitude_series, angle_output_units, NOT_AVAILABLE) if solar_altitude_series else NOT_AVAILABLE,
                        AZIMUTH_NAME: getattr(solar_azimuth_series, angle_output_units, NOT_AVAILABLE) if solar_azimuth_series else NOT_AVAILABLE,
                        SURFACE_ORIENTATION_NAME: getattr(surface_orientation, angle_output_units, NOT_AVAILABLE) if surface_orientation else None,
                        SURFACE_TILT_NAME: getattr(surface_tilt, angle_output_units, NOT_AVAILABLE) if surface_tilt else None,
                        INCIDENCE_ALGORITHM_NAME: solar_incidence_series.incidence_algorithm,
                        INCIDENCE_NAME: getattr(solar_incidence_series, angle_output_units, NOT_AVAILABLE) if solar_incidence_series else NOT_AVAILABLE,
                        INCIDENCE_DEFINITION: solar_incidence_series.definition,
                        UNITS_NAME: angle_output_units,
                        }
                    }

    return results
