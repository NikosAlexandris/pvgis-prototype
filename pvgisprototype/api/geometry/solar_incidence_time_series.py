from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarIncidenceTimeSeriesInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from typing import Optional
from typing import List
from zoneinfo import ZoneInfo
from pvgisprototype import SurfaceTilt
from pvgisprototype import SurfaceOrientation
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.geometry.models import SolarIncidenceModels
from pvgisprototype import RefractedSolarZenith
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import HORIZON_HEIGHT_UNIT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import NO_SOLAR_INCIDENCE
from pvgisprototype.constants import RADIANS
from pvgisprototype import SolarIncidence
from pvgisprototype.algorithms.jenco.solar_incidence import calculate_solar_incidence_time_series_jenco
import numpy as np


@validate_with_pydantic(ModelSolarIncidenceTimeSeriesInputModel)
def model_solar_incidence_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: np.array,
    timezone: Optional[ZoneInfo] = None,
    solar_time_model: SolarTimeModels = SolarTimeModels.milne,
    solar_incidence_model: SolarIncidenceModels = SolarIncidenceModels.jenco,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: str = TIME_OUTPUT_UNITS_DEFAULT,
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> SolarIncidence:

    if solar_incidence_model.value == SolarIncidenceModels.jenco:

        solar_incidence_series = calculate_solar_incidence_time_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            time_output_units=time_output_units,
            angle_output_units=angle_output_units,
            verbose=verbose,
        )

    if solar_incidence_model.value == SolarIncidenceModels.pvis:
        pass

    return solar_incidence_series
