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
from zoneinfo import ZoneInfo

from numpy import array
from pandas import DatetimeIndex

from pvgisprototype import SpectralFactorSeries
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode
from pvgisprototype.constants import (
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import logger


def build_location_dictionary(
    longitude: float,
    latitude: float,
    elevation: float,
    # timestamps: DatetimeIndex,
    # timezone: ZoneInfo,
    # surface_orientation: float,
    # surface_tilt: float,
    # mode: SurfacePositionOptimizerMode,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """
    Build a dictionary containing location parameters.

    Parameters
    ----------
    longitude : float
        The longitude of the location.
    latitude : float
        The latitude of the location.
    elevation : float
        The elevation of the location.
    verbose : int, optional
        The verbosity level. Defaults to VERBOSE_LEVEL_DEFAULT.

    Returns
    -------
    location_arguments : dict
        A dictionary containing the location arguments.
    """
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.debug(
            f"i Collect location arguments",
            alt=f"i [bold]Collect[/bold] the [magenta]location arguments[/magenta]",
        )
    location_arguments = {
        "longitude": longitude,
        "latitude": latitude,
        "elevation": elevation,
    }

    return location_arguments


def build_other_input_arguments_dictionary(
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    **kwargs,
) -> dict:
    """
    Build a dictionary of input arguments for the photovoltaic model.

    This function collects all keyword arguments into a single dictionary
    and optionally logs a message if the verbosity level is high enough.

    Parameters
    ----------
    verbose : int, optional
        Verbosity level used for logging. If greater than the configured
        threshold (`HASH_AFTER_THIS_VERBOSITY_LEVEL`), a logging message is printed.
        Default is 0.
    **kwargs : dict
        Arbitrary keyword arguments representing input parameters. These include,
        but are not limited to:

        - global_horizontal_irradiance : array
        - direct_horizontal_irradiance : array
        - spectral_factor_series : array | SpectralFactorSeries
        - photovoltaic_module : PhotovoltaicModuleModel
        - temperature_series : array | TemperatureSeries
        - wind_speed_series : array | WindspeedSeries
        - horizon_profile : DataArray | None
        - shading_model : ShadingModel
        - linke_turbidity_factor_series :  array | LinkeTurbidityFactor
        - shading_states : ShadingState
        - adjust_for_atmospheric_refraction : bool
        - refracted_solar_zenith : float | None
        - albedo : float | None
        - apply_reflectivity_factor : bool
        - solar_position_model : SolarPositionModel
        - sun_horizon_position : SunHorizonPositionModel
        - solar_incidence_model : SolarIncidenceModel
        - zero_negative_solar_incidence_angle : bool
        - solar_time_model : SolarTimeModel
        - solar_constant : float
        - perigee_offset : float
        - eccentricity_correction_factor : float
        - peak_power : float | None
        - system_efficiency : float | None
        - power_model : PhotovoltaicModulePerformanceModel
        - temperature_model : ModuleTemperatureAlgorithm
        - efficiency : float | None

    Returns
    -------
    dict
        A dictionary containing all keyword arguments and the `verbose` flag.

    Notes
    -----
    The function uses `**kwargs` to dynamically accept and return a flexible set
    of arguments.

    """
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.debug(
            "i Collect the rest input arguments",
            alt="i [bold]Collect[/bold] the [magenta]rest input arguments[/magenta]",
        )

    return dict(kwargs, verbose=verbose)
