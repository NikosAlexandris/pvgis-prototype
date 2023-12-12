from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarIncidencePVISInputModel
from pvgisprototype import SolarIncidence
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RADIANS
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.api.geometry.solar_time import model_solar_time
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_pvis
from math import sin
from math import cos
from math import acos


@validate_with_pydantic(CalculateSolarIncidencePVISInputModel)
def calculate_solar_incidence_pvis(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    surface_tilt: float = 0,
    surface_orientation: float = 180,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
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
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
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

    return SolarIncidence(value=solar_incidence, unit=RADIANS)
