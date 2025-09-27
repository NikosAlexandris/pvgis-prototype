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
from math import cos
from devtools import debug
from numpy import ndarray, asarray
from pandas import DatetimeIndex, Timestamp

from pvgisprototype import (
    ClearSkyDiffuseGroundReflectedInclinedIrradiance,
    DiffuseGroundReflectedInclinedIrradiance,
)
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_ground_reflected_inclined_irradiance_series_pvgis(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex = DatetimeIndex([Timestamp.now(tz='UTC')]),
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_tilt_threshold = SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    albedo: float | None = ALBEDO_DEFAULT,
    global_horizontal_irradiance: ndarray | None = None,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """Calculate the clear-sky diffuse ground reflected irradiance on an inclined surface (Ri).

    The calculation assumes isotropy. The ground reflected clear-sky irradiance
    received on an inclined surface [W.m-2] is proportional to the global
    horizontal irradiance Ghc, to the mean ground albedo ρg and a fraction of
    the ground viewed by an inclined surface rg(γN).

    Parameters
    ----------
    longitude : float
        longitude
    latitude : float
        latitude
    elevation : float
        elevation
    timestamps : DatetimeIndex
        timestamps
    surface_orientation : float
        surface_orientation
    surface_tilt : float
        surface_tilt
    surface_tilt_threshold :
        surface_tilt_threshold
    albedo : float | None
        albedo
    global_horizontal_irradiance : ndarray | None
        global_horizontal_irradiance
    dtype : str
        dtype
    array_backend : str
        array_backend
    verbose : int
        verbose
    log : int
        log

    """
    if surface_tilt <= surface_tilt_threshold:  # No ground reflection for a flat or nearly flat surface
        ground_view_fraction = 0
        # in order to avoid 'NameError's
        flat_surface_array_parameters = {
            "shape": timestamps.shape,
            "dtype": dtype,
            "init_method": "zeros",
            "backend": array_backend,
        }  # Borrow shape from timestamps
        global_horizontal_irradiance = create_array(**flat_surface_array_parameters)
    else:
        ground_view_fraction = (1 - cos(surface_tilt)) / 2

    ground_reflected_inclined_irradiance_series = asarray(
        global_horizontal_irradiance * ground_view_fraction * albedo,
        dtype=dtype
    ).reshape(-1)

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=ground_reflected_inclined_irradiance_series,
        shape=timestamps.shape,
        data_model=DiffuseGroundReflectedInclinedIrradiance(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=ground_reflected_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    # Common output structure
    function_output = {
        "value": ground_reflected_inclined_irradiance_series,
        "out_of_range": out_of_range,
        "out_of_range_index": out_of_range_index,
        "ground_view_fraction": ground_view_fraction,
        "albedo": albedo,
        "global_horizontal_irradiance": global_horizontal_irradiance,
        "location": (longitude, latitude),
        "elevation": elevation,
        "surface_orientation": surface_orientation,
        "surface_tilt": surface_tilt,
        "surface_tilt_threshold": surface_tilt_threshold,
    }
    return DiffuseGroundReflectedInclinedIrradiance(**function_output)
