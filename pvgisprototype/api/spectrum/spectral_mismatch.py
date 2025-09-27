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
from xarray import DataArray
from pvgisprototype.algorithms.pelland.spectral_mismatch import calculate_spectral_mismatch_pelland
from pvgisprototype import Latitude, Longitude, Elevation
from pvgisprototype.log import log_function_call, log_data_fingerprint
from devtools import debug
from typing import Dict, List
from zoneinfo import ZoneInfo
from pandas import DataFrame, DatetimeIndex, Series
# from pvlib.spectrum import calc_spectral_mismatch_field

from pvgisprototype import SpectralFactorSeries
from pvgisprototype.api.position.models import select_models
from pvgisprototype.api.spectrum.models import PhotovoltaicModuleSpectralResponsivityModel, SpectralMismatchModel
from pvgisprototype.api.spectrum.constants import (
    MAX_WAVELENGTH,
    MIN_WAVELENGTH,
)
from pvgisprototype.constants import (
        UNIT_NAME,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    IRRADIANCE_COLUMN_NAME,
    IRRADIANCE_SOURCE_COLUMN_NAME,
    LOG_LEVEL_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    UNITLESS,
    TITLE_KEY_NAME,
    SPECTRAL_FACTOR_NAME,
    SPECTRAL_FACTOR_COLUMN_NAME,
    TECHNOLOGY_NAME,
    SPECTRAL_MISMATCH_MODEL_COLUMN_NAME,
    NOT_AVAILABLE,
    FINGERPRINT_FLAG_DEFAULT,
    FINGERPRINT_COLUMN_NAME,
    REFERENCE_SPECTRUM_COLUMN_NAME,
    RESPONSIVITY_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    TOLERANCE_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
)
from pvgisprototype.core.hashing import generate_hash
from pvgisprototype.api.series.models import MethodForInexactMatches


@log_function_call
def model_spectral_mismatch(
    # longitude: Longitude,
    # latitude: Latitude,
    # elevation: Elevation,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    responsivity: Series,
    irradiance: DataFrame | DataArray,
    average_irradiance_density: None | DataFrame | DataArray,
    # neighbor_lookup: MethodForInexactMatches = MethodForInexactMatches.nearest,
    # tolerance: None | float = TOLERANCE_DEFAULT,
    # mask_and_scale: bool = False,
    # in_memory: bool = False,
    min_wavelength: float = MIN_WAVELENGTH,
    max_wavelength: float = MAX_WAVELENGTH,
    reference_spectrum: None | Series = None,  # AM15G_IEC60904_3_ED4,
    integrate_reference_spectrum: bool = False,
    spectral_mismatch_model: SpectralMismatchModel = SpectralMismatchModel.pvlib,
    # dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    # array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    # multi_thread: Annotated[
    #     bool, typer_option_multi_thread
    # ] = MULTI_THREAD_FLAG_DEFAULT,
    resample_large_series: bool = False,
    # dtype: str = DATA_TYPE_DEFAULT,
    # array_backend: str = ARRAY_BACKEND_DEFAULT,
    # multi_thread=multi_thread,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """
    """
    spectral_mismatch = None

    if spectral_mismatch_model.value == SpectralMismatchModel.pvlib:

        pass
        # average_irradiance_density_without_geographic_coordinates = (
        #     average_irradiance_density.drop_vars(
        #         ["longitude", "latitude"], errors="ignore"
        #     )
        # )

        # spectral_mismatch = calc_spectral_mismatch_field(
        #     sr=responsivity.to_dataframe().T,  #T,  # for one PV module technology
        #     e_sun=average_irradiance_density_without_geographic_coordinates.to_dataframe().T,
        #     e_ref=reference_spectrum,
        # ).to_numpy()  # Very Important !

    if spectral_mismatch_model.value == SpectralMismatchModel.pelland:

        spectral_mismatch = calculate_spectral_mismatch_pelland(
            irradiance=irradiance,
            responsivity=responsivity.T,
            reference_spectrum=reference_spectrum,
        )

    return spectral_mismatch


def calculate_spectral_mismatch(
    longitude: Longitude,
    latitude: Latitude,
    elevation: Elevation,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    irradiance: DataFrame,
    average_irradiance_density: DataFrame,
    # neighbor_lookup: MethodForInexactMatches = MethodForInexactMatches.nearest,
    # tolerance: None | float = TOLERANCE_DEFAULT,
    # mask_and_scale: bool = False,
    # in_memory: bool = False,
    # responsivity: Series,
    responsivity: Dict[str, Series],  # Dictionary to hold responsivity for each type
    photovoltaic_module_type: List[PhotovoltaicModuleSpectralResponsivityModel] = [PhotovoltaicModuleSpectralResponsivityModel.cSi],
    reference_spectrum: Series = None,  # AM15G_IEC60904_3_ED4,
    integrate_reference_spectrum: bool = False,
    spectral_mismatch_models: List[SpectralMismatchModel] = [SpectralMismatchModel.pvlib],
    min_wavelength: float = MIN_WAVELENGTH,
    max_wavelength: float = MAX_WAVELENGTH,
    # dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    # array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    # multi_thread: Annotated[
    #     bool, typer_option_multi_thread
    # ] = MULTI_THREAD_FLAG_DEFAULT,
    resample_large_series: bool = False,
    # dtype: str = DATA_TYPE_DEFAULT,
    # array_backend: str = ARRAY_BACKEND_DEFAULT,
    # multi_thread=multi_thread,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> Dict:
    """Calculate an overview of solar position parameters for a time series.
    """
    results = {}
    # ctx.params.get() does not return a list !
    photovoltaic_module_types = select_models(
        PhotovoltaicModuleSpectralResponsivityModel, photovoltaic_module_type
        )# Using a callback fails!
    for spectral_mismatch_model in spectral_mismatch_models:
        if (
            spectral_mismatch_model != SpectralMismatchModel.all
        ):  # ignore 'all' in the enumeration

            model_results = {}  # store model output

            for module_type in photovoltaic_module_types:
                selected_responsivity = responsivity[module_type.value]
                spectral_mismatch_series = model_spectral_mismatch(
                    # longitude=longitude,
                    # latitude=latitude,
                    timestamps=timestamps,
                    timezone=timezone,
                    spectral_mismatch_model=spectral_mismatch_model,
                    responsivity=selected_responsivity,
                    # responsivity=responsivity,
                    irradiance=irradiance,
                    average_irradiance_density=average_irradiance_density,
                    reference_spectrum=reference_spectrum,
                    # dtype=dtype,
                    # array_backend=array_backend,
                    verbose=verbose,
                    log=log,
                )
                components_container = {
                    "Metadata": lambda: {
                        RESPONSIVITY_COLUMN_NAME: responsivity[module_type.value],
                        IRRADIANCE_COLUMN_NAME: irradiance,
                        IRRADIANCE_SOURCE_COLUMN_NAME: 'UpdateMe',
                        REFERENCE_SPECTRUM_COLUMN_NAME: 'See constant AM15G_IEC60904_3_ED4',
                    }
                    if verbose > 2
                    else {},
                    "Spectral factor": lambda: {
                        TITLE_KEY_NAME: SPECTRAL_FACTOR_NAME,
                        SPECTRAL_FACTOR_COLUMN_NAME: spectral_mismatch_series.value,
                        TECHNOLOGY_NAME: module_type.name,
                        SPECTRAL_MISMATCH_MODEL_COLUMN_NAME: (
                            spectral_mismatch_model
                            if spectral_mismatch_model
                            else NOT_AVAILABLE
                            ),
                        UNIT_NAME: UNITLESS,
                    },  # if verbose > 0 else {},
                    "fingerprint": lambda: {
                        FINGERPRINT_COLUMN_NAME: generate_hash(spectral_mismatch_series),
                    }
                    if fingerprint
                    else {},
                }

                components = {}
                for key, component in components_container.items():
                    components.update(component())

                components = components | spectral_mismatch_series.components
                model_results[module_type] = components
                results[spectral_mismatch_model] = model_results
                # results = results | spectral_mismatch_model_overview
    
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    # log_data_fingerprint(
    #     data=spectral_mismatch_series,
    #     log_level=log,
    #     hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    # )
    return SpectralFactorSeries(
            # value=spectral_mismatch_series,
            components=results,
            )
