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
import numpy as np
from pandas.core.base import Shape
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
)
from pvgisprototype.core.arrays import create_array
from pvgisprototype.log import log_function_call, logger


@log_function_call
def identify_values_out_of_range(
    series: np.ndarray,
    shape: int | Shape,
    data_model: object | None = None,
    minimum: float | None = None,
    maximum: float | None = None,
    clip_to_physically_possible_limits: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
):
    """
    """
    if not minimum and not maximum:
        minimum = data_model.lower_physically_possible_limit
        maximum = data_model.upper_physically_possible_limit
    out_of_range = (series < minimum) | (series > maximum)
    # out_of_range = np.asarray(out_of_range, dtype=bool)  # Convert to array ?
    out_of_range = np.array(out_of_range, ndmin=1)  # Ensure it's at least 1D

    out_of_range_indices = create_array(
        shape, dtype=dtype, init_method=np.nan, backend=array_backend
    )
    if out_of_range.size:
        # warning = f"{WARNING_OUT_OF_RANGE_VALUES} in [code]diffuse_inclined_irradiance_series[/code] :\n{diffuse_inclined_irradiance_series[out_of_range]}"
        # warning_unstyled = (
        #     f"\n"
        #     f"{WARNING_OUT_OF_RANGE_VALUES} "
        #     f"[{DiffuseSkyReflectedInclinedIrradianceFromExternalData().lower_physically_possible_limit}, "
        #     f"{DiffuseSkyReflectedInclinedIrradianceFromExternalData().upper_physically_possible_limit}] "
        #     f" in diffuse_inclined_irradiance_series : "
        #     # f"{out_of_range_values}"
        #     f"\n"
        # )
        # warning = (
        #     f"\n"
        #     f"{WARNING_OUT_OF_RANGE_VALUES} "
        #     f"[{DiffuseSkyReflectedInclinedIrradianceFromExternalData().lower_physically_possible_limit}, "
        #     f"{DiffuseSkyReflectedInclinedIrradianceFromExternalData().upper_physically_possible_limit}] "
        #     f" in [code]diffuse_inclined_irradiance_series[/code] : "
        #     # f"{out_of_range_values}"
        #     f"\n"
        # )
        # logger.warning(warning_unstyled, alt=warning)
        logger.warning(
            f"{WARNING_OUT_OF_RANGE_VALUES} in `diffuse_horizontal_irradiance_series`!",
            alt=f"{WARNING_OUT_OF_RANGE_VALUES} in `diffuse_horizontal_irradiance_series`!",
        )
        stub_array = np.full(out_of_range.shape, -1, dtype=int)
        index_array = np.arange(len(out_of_range))
        out_of_range_indices = np.where(out_of_range, index_array, stub_array)

        # Clip irradiance values to the lower and upper
        # physically possible limits
        if clip_to_physically_possible_limits:
            series = np.clip(series, minimum, maximum)
        logger.warning(
            (
                f"\n"
                f"Out-of-Range values in [code]direct_normal_irradiance_series[/code]"
                f" clipped to physically possible limits "
                f"[{minimum}, {maximum}]"
                f"\n"
            ),
            alt=(
                f"\n"
                f"Out-of-Range values in direct_normal_irradiance_series"
                f" clipped to physically possible limits "
                f"[{minimum}, {maximum}]"
                f"\n"
            ),
        )

    return out_of_range, out_of_range_indices


@log_function_call
def identify_values_out_of_range_x(
    series: np.ndarray,
    shape: int | Shape,
    data_model: object | None = None,
    minimum: float | None = None,
    maximum: float | None = None,
    clip_to_predetermined_range: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
):
    """
    """
    if not minimum and not maximum:
        minimum = data_model.min_radians
        maximum = data_model.max_radians
    out_of_range = (series < minimum) | (series > maximum)
    # out_of_range = np.asarray(out_of_range, dtype=bool)  # Convert to array ?
    out_of_range = np.array(out_of_range, ndmin=1)  # Ensure it's at least 1D

    out_of_range_indices = create_array(
        shape, dtype=dtype, init_method=np.nan, backend=array_backend
    )
    if out_of_range.size:
        logger.warning(
            f"{WARNING_OUT_OF_RANGE_VALUES} in {data_model.name} series!",
            alt=f"{WARNING_OUT_OF_RANGE_VALUES} in {data_model.title} series!",
        )
        stub_array = np.full(out_of_range.shape, -1, dtype=int)
        index_array = np.arange(len(out_of_range))
        out_of_range_indices = np.where(out_of_range, index_array, stub_array)

        # Clip irradiance values to the lower and upper
        # physically possible limits
        if clip_to_predetermined_range:
            series = np.clip(series, minimum, maximum)
        logger.warning(
            (
                f"\n"
                f"Out-of-Range values in data_model.title"
                f" clipped to pre-determined range "
                f"[{minimum}, {maximum}]"
                f"\n"
            ),
            alt=(
                f"\n"
                f"Out-of-Range values in [code]data_model.title[/code]"
                f" clipped to pre-determined range "
                f"[{minimum}, {maximum}]"
                f"\n"
            ),
        )

    return out_of_range, out_of_range_indices
