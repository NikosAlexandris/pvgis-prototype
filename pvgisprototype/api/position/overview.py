from devtools import debug
from typing import List
from math import isfinite
from datetime import datetime
from zoneinfo import ZoneInfo
import suncalc
import pysolar
from pvgisprototype.api.utilities.conversions import convert_south_to_north_radians_convention
from pvgisprototype.api.utilities.timestamp import attach_timezone
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarGeometryOverviewInputModel
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype import SolarAltitude
from pvgisprototype import SolarAzimuth
from pvgisprototype import SolarZenith
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_declination_noaa
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_hour_angle_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_noaa
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_altitude_noaa
from pvgisprototype.algorithms.noaa.solar_position import calculate_solar_azimuth_noaa
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.algorithms.milne1921.solar_time import calculate_apparent_solar_time_milne1921
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_pvis
from pvgisprototype.algorithms.pvis.solar_altitude import calculate_solar_altitude_pvis
from pvgisprototype.algorithms.pvis.solar_azimuth import calculate_solar_azimuth_pvis
from pvgisprototype.algorithms.pvis.solar_incidence import calculate_solar_incidence_pvis
from pvgisprototype.api.position.incidence import model_solar_incidence
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_hour_angle_declination_skyfield
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_altitude_azimuth_skyfield
from pvgisprototype.algorithms.pvlib.solar_declination import calculate_solar_declination_pvlib
from pvgisprototype.algorithms.pvlib.solar_hour_angle import calculate_solar_hour_angle_pvlib
from pvgisprototype.algorithms.pvlib.solar_zenith import calculate_solar_zenith_pvlib
from pvgisprototype.algorithms.pvlib.solar_altitude import calculate_solar_altitude_pvlib
from pvgisprototype.algorithms.pvlib.solar_azimuth import calculate_solar_azimuth_pvlib
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import DECLINATION_NAME
from pvgisprototype.constants import HOUR_ANGLE_NAME
from pvgisprototype.constants import POSITION_ALGORITHM_NAME
from pvgisprototype.constants import ZENITH_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import AZIMUTH_NAME
from pvgisprototype.constants import SURFACE_TILT_NAME
from pvgisprototype.constants import SURFACE_ORIENTATION_NAME
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import INCIDENCE_ALGORITHM_NAME
from pvgisprototype.constants import INCIDENCE_NAME
from pvgisprototype.constants import INCIDENCE_DEFINITION
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import UNITS_NAME
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import DEGREES
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.cli.messages import NOT_IMPLEMENTED


@validate_with_pydantic(ModelSolarGeometryOverviewInputModel)
def model_solar_geometry_overview(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    surface_orientation: float,
    surface_tilt: float,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    apply_atmospheric_refraction: bool = True,
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = VERBOSE_LEVEL_DEFAULT,
) -> List:
    """Model solar geometry parameters for a position and moment in time.

    Model the following solar geometry parameters for a position and moment in
    time and for a given solar position model (as in positioning algorithm, see
    class `SolarPositionModel`) and solar time model (as in solar timing
    algorithm, see class `SolarTimeModel`) :

    - solar declination 
    - solar hour angle 
    - solar zenith 
    - solar altitude 
    - solar azimuth 
    - solar incidence 

    Notes
    -----

    The solar altitude angle measures from the horizon up towards the zenith
    (positive, and down towards the nadir (negative)). The altitude is zero all
    along the great circle between zenith and nadir.

    The solar azimuth angle measures horizontally around the horizon from north
    through east, south, and west.

    - All solar calculation functions return floating angular measurements in
      radians.

    pysolar :

    From https://pysolar.readthedocs.io:

    - Altitude is reckoned with zero at the horizon. The altitude is positive
      when the sun is above the horizon.

    - Azimuth is reckoned with zero corresponding to north. Positive azimuth
      estimates correspond to estimates east of north; negative estimates, or
      estimates larger than 180 are west of north. In the northern hemisphere,
      if we speak in terms of (altitude, azimuth), the sun comes up around
      (0, 90), reaches (70, 180) around noon, and sets around (0, 270).

    - The result is returned with units.
    """
    solar_declination = None  # updated if applicable
    solar_hour_angle = None
    solar_zenith = None  # updated if applicable
    solar_altitude = None
    solar_azimuth = None
    solar_incidence = None

    if solar_position_model.value == SolarPositionModel.noaa:

        solar_declination = calculate_solar_declination_noaa(
            timestamp=timestamp,
        )
        solar_hour_angle = calculate_solar_hour_angle_noaa(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )
        solar_zenith = calculate_solar_zenith_noaa(
            latitude=latitude,
            timestamp=timestamp,
            solar_hour_angle=solar_hour_angle,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
        )
        solar_altitude = calculate_solar_altitude_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
        )
        solar_azimuth = calculate_solar_azimuth_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
        )
    
    if solar_position_model.value == SolarPositionModel.skyfield:

        solar_hour_angle, solar_declination = calculate_solar_hour_angle_declination_skyfield(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
        )
        solar_altitude, solar_azimuth = calculate_solar_altitude_azimuth_skyfield(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                )
        solar_zenith = SolarZenith(
            value = 90 - solar_altitude.degrees,
            unit = DEGREES,
            position_algorithm=solar_azimuth.position_algorithm,
            timing_algorithm=solar_azimuth.timing_algorithm,
        )

    if solar_position_model.value == SolarPositionModel.suncalc:
        # note : first azimuth, then altitude
        solar_azimuth_south_radians_convention, solar_altitude = suncalc.get_position(
            date=timestamp,  # this comes first here!
            lng=longitude.degrees,
            lat=latitude.degrees,
        ).values()  # zero points to south
        solar_azimuth = convert_south_to_north_radians_convention(
            solar_azimuth_south_radians_convention
        )
        solar_azimuth = SolarAzimuth(
            value=solar_azimuth,
            unit=RADIANS,
            position_algorithm='suncalc',
            timing_algorithm='suncalc',
        )
        solar_altitude = SolarAltitude(
            value=solar_altitude,
            unit=RADIANS,
            position_algorithm='suncalc',
            timing_algorithm='suncalc',
        )
        solar_zenith = SolarZenith(
            value = 90 - solar_altitude.degrees,
            unit = DEGREES,
            position_algorithm='suncalc',
            timing_algorithm='suncalc',
        )

    if solar_position_model.value == SolarPositionModel.pysolar:

        timestamp = attach_timezone(timestamp, timezone)

        solar_altitude = pysolar.solar.get_altitude(
            latitude_deg=latitude.degrees,  # this comes first
            longitude_deg=longitude.degrees,
            when=timestamp,
        )  # returns degrees by default
        # required by output function
        solar_altitude = SolarAltitude(
            value=solar_altitude,
            unit=DEGREES,
            position_algorithm='pysolar',
            timing_algorithm='pysolar',
        )
        solar_zenith = SolarZenith(
            value = 90 - solar_altitude.degrees,
            unit = DEGREES,
            position_algorithm=solar_altitude.position_algorithm,
            timing_algorithm=solar_altitude.timing_algorithm,
        )
        solar_azimuth = pysolar.solar.get_azimuth(
            latitude_deg=latitude.degrees,  # this comes first
            longitude_deg=longitude.degrees,
            when=timestamp,
        )  # returns degrees by default
        # required by output function
        solar_azimuth = SolarAzimuth(
            value=solar_azimuth,
            unit=DEGREES,
            position_algorithm='pysolar',
            timing_algorithm='pysolar',
        )

    if solar_position_model.value  == SolarPositionModel.pvis:

        solar_declination = calculate_solar_declination_pvis(
            timestamp=timestamp,
            eccentricity_correction_factor=eccentricity_correction_factor,
            perigee_offset=perigee_offset,
        )
        solar_time_milne1921 = calculate_apparent_solar_time_milne1921(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )
        solar_hour_angle = calculate_solar_hour_angle_pvis(
            solar_time=solar_time_milne1921,
        )
        solar_altitude = calculate_solar_altitude_pvis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            solar_time_model=solar_time_model,
            verbose=verbose,
        )
        solar_zenith = SolarZenith(
            value = 90 - solar_altitude.degrees,
            unit = DEGREES,
            position_algorithm=solar_altitude.position_algorithm,
            timing_algorithm=solar_altitude.timing_algorithm,
        )
        solar_azimuth = calculate_solar_azimuth_pvis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            solar_time_model=solar_time_model,
        )
        solar_incidence = calculate_solar_incidence_pvis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            verbose=verbose,
        )

    if solar_position_model.value == SolarPositionModel.pvlib:

        solar_declination = calculate_solar_declination_pvlib(
            timestamp=timestamp,
        )
        solar_hour_angle = calculate_solar_hour_angle_pvlib(
            longitude=longitude,
            timestamp=timestamp,
        )
        solar_zenith = calculate_solar_zenith_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
        )
        solar_altitude = calculate_solar_altitude_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            )
        solar_azimuth = calculate_solar_azimuth_pvlib(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
        )

    if not solar_incidence:  # get through the API
        solar_incidence = model_solar_incidence(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            solar_incidence_model=solar_incidence_model,
            verbose=verbose,
        )

    position = (
            solar_declination if solar_declination is not None else None,
            solar_hour_angle if solar_hour_angle is not None else None,
            solar_zenith if solar_zenith is not None else None,
            solar_altitude if solar_altitude is not None else None,
            solar_azimuth if solar_azimuth is not None else None,
            surface_orientation if surface_orientation is not None else None,
            surface_tilt if surface_tilt is not None else None,
            solar_incidence if solar_incidence is not None else None,
    )
    if verbose == DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return position


def calculate_solar_geometry_overview(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    surface_orientation: float,
    surface_tilt: float,
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.skyfield],
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    apply_atmospheric_refraction: bool = True,
    solar_time_model: SolarTimeModel = SolarTimeModel.skyfield,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.iqbal,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = VERBOSE_LEVEL_DEFAULT,
) -> List:
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = []
    for solar_position_model in solar_position_models:
        if solar_position_model != SolarPositionModel.all:  # ignore 'all' in the enumeration
            (
                solar_declination,
                solar_hour_angle,
                solar_zenith,
                solar_altitude,
                solar_azimuth,
                surface_orientation,
                surface_tilt,
                solar_incidence,
            ) = model_solar_geometry_overview(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                solar_position_model=solar_position_model,
                complementary_incidence_angle=complementary_incidence_angle,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                solar_time_model=solar_time_model,
                solar_incidence_model=solar_incidence_model,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                dtype=dtype,
                backend=array_backend,
                verbose=verbose,
                log=log,
            )
            results.append({
                TIME_ALGORITHM_NAME: solar_azimuth.timing_algorithm if solar_altitude.timing_algorithm == solar_azimuth.timing_algorithm else NOT_AVAILABLE,
                DECLINATION_NAME: getattr(solar_declination, angle_output_units, NOT_AVAILABLE) if solar_declination else None,
                HOUR_ANGLE_NAME: getattr(solar_hour_angle, angle_output_units, NOT_AVAILABLE) if solar_hour_angle else None,
                POSITION_ALGORITHM_NAME: solar_position_model.value,
                ZENITH_NAME: getattr(solar_zenith, angle_output_units, NOT_AVAILABLE) if solar_zenith else None,
                ALTITUDE_NAME: getattr(solar_altitude, angle_output_units, NOT_AVAILABLE) if solar_altitude else None,
                AZIMUTH_NAME: getattr(solar_azimuth, angle_output_units, NOT_AVAILABLE) if solar_azimuth else None,
                SURFACE_ORIENTATION_NAME: getattr(surface_orientation, angle_output_units, NOT_AVAILABLE) if surface_tilt else None,
                SURFACE_TILT_NAME: getattr(surface_tilt, angle_output_units, NOT_AVAILABLE) if surface_tilt else None,
                INCIDENCE_ALGORITHM_NAME: solar_incidence.incidence_algorithm,
                INCIDENCE_NAME: getattr(solar_incidence, angle_output_units, NOT_AVAILABLE) if solar_incidence else NOT_IMPLEMENTED,
                INCIDENCE_DEFINITION: solar_incidence.definition,
                UNITS_NAME: angle_output_units,
            })

    return results
