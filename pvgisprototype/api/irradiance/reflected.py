from devtools import debug
from typing import Optional
from typing import List
from .loss import calculate_angular_loss_factor_for_nondirect_irradiance
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
from pvgisprototype.api.utilities.conversions import convert_to_radians
from datetime import datetime
from pathlib import Path
from math import sin
from math import cos
from pvgisprototype.api.geometry.altitude_series import model_solar_altitude_time_series
from pvgisprototype.api.irradiance.direct import calculate_direct_horizontal_irradiance_time_series
from pvgisprototype.api.irradiance.direct import calculate_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.api.irradiance.diffuse import diffuse_transmission_function_time_series
from pvgisprototype.api.irradiance.diffuse import diffuse_solar_altitude_function_time_series
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import MEAN_GROUND_ALBEDO_DEFAULT
from pvgisprototype.constants import ANGULAR_LOSS_FACTOR_FLAG_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import MINUTES
from pvgisprototype.constants import REFLECTED_INCLINED_IRRADIANCE
from pvgisprototype.constants import REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import ALBEDO_COLUMN_NAME
from pvgisprototype.constants import GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import VIEW_FRACTION_COLUMN_NAME
from pvgisprototype.constants import LOSS_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import ALTITUDE_COLUMN_NAME
from pvgisprototype import LinkeTurbidityFactor


def calculate_ground_reflected_inclined_irradiance_time_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: BaseTimestampSeriesModel = None,
    start_time: Optional[datetime] = None,
    frequency: Optional[str] = None,
    end_time: Optional[datetime] = None,
    timezone: Optional[str] = None,
    surface_tilt: Optional[float] = SURFACE_TILT_DEFAULT,
    surface_orientation: Optional[float] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Optional[bool] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: Optional[float] = MEAN_GROUND_ALBEDO_DEFAULT,
    direct_horizontal_component: Optional[Path] = None,
    apply_angular_loss_factor: Optional[bool] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModels = SolarPositionModels.noaa,
    solar_time_model: SolarTimeModels = SolarTimeModels.noaa,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_FLAG_DEFAULT,
    time_output_units: str = MINUTES,
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the clear-sky diffuse ground reflected irradiance on an inclined surface (Ri).

    The calculation relies on an isotropic assumption. The ground reflected
    clear-sky irradiance received on an inclined surface [W.m-2] is
    proportional to the global horizontal irradiance Ghc, to the mean ground
    albedo ρg and a fraction of the ground viewed by an inclined surface
    rg(γN).
    """
    # from the model
    direct_horizontal_irradiance_series = (
        calculate_direct_horizontal_irradiance_time_series(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            timestamps=timestamps,
            start_time=start_time,
            frequency=frequency,
            end_time=end_time,
            timezone=timezone,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            solar_time_model=solar_time_model,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            angle_output_units=angle_output_units,
            verbose=0,  # no verbosity here by choice!
        )
    )

    # G0
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_time_series(
            timestamps=timestamps,
            start_time=start_time,
            frequency=frequency,
            end_time=end_time,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            random_days=random_days,
            verbose=0,  # no verbosity here by choice!
        )
    )

    # extraterrestrial on a horizontal surface requires the solar altitude
    solar_altitude_series = model_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )

    # Dhc [W.m-2]
    diffuse_horizontal_irradiance_series = (
        extraterrestrial_normal_irradiance_series
        * diffuse_transmission_function_time_series(linke_turbidity_factor_series)
        * diffuse_solar_altitude_function_time_series(
            solar_altitude_series, linke_turbidity_factor_series
        )
    )
    global_horizontal_irradiance_series = (
        direct_horizontal_irradiance_series + diffuse_horizontal_irradiance_series
    )
    ground_view_fraction = (1 - cos(surface_tilt)) / 2

    # clear-sky ground reflected irradiance
    ground_reflected_inclined_irradiance_series = (
        albedo * global_horizontal_irradiance_series * ground_view_fraction
    )

    if apply_angular_loss_factor:
        ground_reflected_irradiance_angular_loss_coefficient = sin(surface_tilt) + (
            surface_tilt - sin(surface_tilt)
        ) / (1 - cos(surface_tilt))
        ground_reflected_irradiance_loss_factor_series = calculate_angular_loss_factor_for_nondirect_irradiance(
            indirect_angular_loss_coefficient=ground_reflected_irradiance_angular_loss_coefficient,
        )
        ground_reflected_inclined_irradiance_series *= (
            ground_reflected_irradiance_loss_factor_series
        )

    results = {
        "Title": REFLECTED_INCLINED_IRRADIANCE,
        REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: ground_reflected_inclined_irradiance_series,
    }

    if verbose > 1:
        extended_results = {
            ALBEDO_COLUMN_NAME: albedo,
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series,
            VIEW_FRACTION_COLUMN_NAME: ground_view_fraction,
        }
        results = results | extended_results

    if verbose > 2:
        more_extended_results = {
            LOSS_COLUMN_NAME: 1 - ground_reflected_irradiance_loss_factor_series,
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
            DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
        }
        results = results | more_extended_results
        results["Title"] += " & horizontal components"

    if verbose > 3:
        even_more_extended_results = {
            EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series,
            ALTITUDE_COLUMN_NAME: getattr(solar_altitude_series, angle_output_units),
        }
        results = results | even_more_extended_results

    if verbose > 5:
        debug(locals())

    if verbose > 0:
        return results

    return ground_reflected_inclined_irradiance_series
