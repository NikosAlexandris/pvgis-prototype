from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from pvgisprototype import Latitude
from pvgisprototype import Longitude
from pvgisprototype import RefractedSolarZenith
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.geometry.solar_altitude import calculate_solar_altitude

# NOTE: Not used !

# def calculate_solar_zenith(
#     longitude: Longitude,
#     latitude: Latitude,
#     timestamp: datetime,
#     timezone: ZoneInfo,
#     # refracted_solar_zenith: RefractedSolarZenith,
#     solar_position_models: List[SolarPositionModels] = [SolarPositionModels.skyfield],
#     solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
#     apply_atmospheric_refraction: bool = True,
#     days_in_a_year: float = 365.25,
#     perigee_offset: float = 0.048869,
#     eccentricity_correction_factor: float = 0.01672,
#     # time_offset_global: float = 0,
#     # hour_offset: float = 0,
#     angle_output_units: str = 'radians',
# ) -> List:
    
#     results = calculate_solar_altitude(
#         longitude=longitude,
#         latitude=latitude,
#         timestamp=timestamp,
#         timezone=timezone,
#         solar_position_models=solar_position_models,
#         solar_time_model=solar_time_model,
#         apply_atmospheric_refraction=apply_atmospheric_refraction,
#         days_in_a_year=days_in_a_year,
#         perigee_offset=perigee_offset,
#         eccentricity_correction_factor=eccentricity_correction_factor,
#         angle_output_units=angle_output_units,
#     )

#     return results      # FIXME: This contains info about altitude and NOT ZENITH
