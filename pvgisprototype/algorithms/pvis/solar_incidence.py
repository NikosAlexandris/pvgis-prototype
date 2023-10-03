from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarIncidencePVISInputModel
from pvgisprototype import SolarIncidence
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.api.geometry.solar_time import model_solar_time
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_pvis
from math import sin
from math import cos
from math import acos


@validate_with_pydantic(CalculateSolarIncidencePVISInputModel)      # NOTE gounaol: Renamed from CalculateSolarIncidenceInputModel
def calculate_solar_incidence_pvis(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_time_model: SolarTimeModels = SolarTimeModels.milne,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    surface_tilt: float = 0,
    surface_orientation: float = 180,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float = 1.5853349194640094,
    days_in_a_year: float = DAYS_IN_A_YEAR,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    # time_output_units: str = 'minutes',
    # angle_units: str = 'radians',
) -> SolarIncidence:
    """Calculate the angle of incidence (θ) between the direction of the sun
    ray and the line normal to the surface measured in radian.

    θ =
    acos(
         sin(Φ)
         * (
           sin(δ) * cos(β) + cos(δ) * cos(γ) * cos(ω) * sin(β)
           )
         + cos(Φ) * (cos(δ) * cos(ω) * cos(β) - sin(δ) * cos(γ) * sin(β))
         + cos(δ)
         * sin(γ)
         * sin(ω)
         * sin(β)
        )

    Parameters
    ----------

    latitude: float
        Latitude is the angle (Φ) between the sun's rays and its projection on
        the horizontal surface measured in radian.

    surface_tilt: float 
        Surface tilt or slope is the angle (β) between the inclined slope and
        the horizontal plane measured in radian.

    surface_orientiation: float
        Surface orientation or azimuth is the angle (γ) in the horizontal plane
        between the line due south and the horizontal projection of the normal
        to the inclined plane surface measured in radian.

    Returns
    -------
    solar_incidence: float
        The angle of incidence (θ) is the angle between the direction of the
        sun ray and the line normal to the surface measured in radian.
    """
    solar_declination = calculate_solar_declination_pvis(
        timestamp=timestamp,
        timezone=timezone,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        # angle_output_units=angle_output_units,
    )
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_time_model=solar_time_model,
    )
    hour_angle = calculate_solar_hour_angle_pvis(
        solar_time=solar_time,
    )
    solar_incidence = acos(
        sin(latitude.radians)
        * (
            sin(solar_declination.radians)
            * cos(surface_tilt.radians)
            + cos(solar_declination.radians)
            * cos(surface_orientation.radians)
            * cos(hour_angle.radians)
            * sin(surface_tilt.radians)
        )
        + cos(latitude.radians)
        * (
            cos(solar_declination.radians)
            * cos(hour_angle.radians)
            * cos(surface_tilt.radians)
            - sin(solar_declination.radians)
            * cos(surface_orientation.radians)
            * sin(surface_tilt.radians)
        )
        + cos(solar_declination.radians)
        * sin(surface_orientation.radians)
        * sin(hour_angle.radians)
        * sin(surface_tilt.radians)
    )

    return SolarIncidence(value=solar_incidence, unit='radians')
