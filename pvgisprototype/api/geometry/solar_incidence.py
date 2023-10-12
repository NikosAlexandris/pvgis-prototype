from devtools import debug
from pvgisprototype.algorithms.jenco.solar_incidence import calculate_solar_incidence_jenco
from pvgisprototype.algorithms.pvis.solar_incidence import calculate_solar_incidence_pvis
from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype import RefractedSolarZenith
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.geometry.models import SolarIncidenceModels
from pathlib import Path
from typing import List
from pvgisprototype import SolarIncidence
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import POSITION_ALGORITHM_NAME
from pvgisprototype.constants import INCIDENCE_NAME
from pvgisprototype.constants import UNITS_NAME


def model_solar_incidence(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
    solar_time_model: SolarTimeModels = SolarTimeModels.milne,
    random_time: bool = RANDOM_DAY_FLAG_DEFAULT,
    solar_incidence_model: SolarIncidenceModels = SolarIncidenceModels.jenco,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    shadow_indicator: Path = None,
    horizon_heights: List = None,
    horizon_interval: float = None,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: RefractedSolarZenith = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_offset_global: float = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: float = HOUR_OFFSET_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> SolarIncidence:
    """ """
    if solar_incidence_model.value == SolarIncidenceModels.jenco:

        solar_incidence = calculate_solar_incidence_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            random_time=random_time,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            eccentricity_correction_factor=eccentricity_correction_factor,
            perigee_offset=perigee_offset,
            verbose=verbose,
        )

    if solar_incidence_model.value == SolarIncidenceModels.pvis:

        solar_incidence = calculate_solar_incidence_pvis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            solar_time_model=solar_time_model,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
        )

    return solar_incidence


def calculate_solar_incidence(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
    random_time: bool = RANDOM_DAY_FLAG_DEFAULT,
    solar_incidence_models: List[SolarIncidenceModels] = [SolarIncidenceModels.jenco],
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    # shadow_indicator: Path = None,
    horizon_heights: List[float] = None,
    horizon_interval: float = None,
    solar_time_model: SolarTimeModels = SolarTimeModels.milne,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_offset_global: float = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: float = HOUR_OFFSET_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> List:
    """Calculates the solar Incidence angle for the selected models and returns the results in a table"""
    results = []
    for solar_incidence_model in solar_incidence_models:
        if solar_incidence_model != SolarIncidenceModels.all:  # ignore 'all' in the enumeration
            solar_incidence = model_solar_incidence(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                random_time=random_time,
                solar_time_model=solar_time_model,
                solar_incidence_model=solar_incidence_model,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                surface_tilt=surface_tilt,
                surface_orientation=surface_orientation,
                # shadow_indicator=shadow_indicator,
                horizon_heights=horizon_heights,
                horizon_interval=horizon_interval,
                eccentricity_correction_factor=eccentricity_correction_factor,
                perigee_offset=perigee_offset,
                verbose=verbose,
            )
            results.append(
                {
                    TIME_ALGORITHM_NAME: solar_time_model,
                    POSITION_ALGORITHM_NAME: solar_incidence_model.value,
                    INCIDENCE_NAME: solar_incidence.value,
                    UNITS_NAME: solar_incidence.unit,
                }
            )
    return results
