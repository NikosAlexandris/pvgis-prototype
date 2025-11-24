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
from pvgisprototype.log import logger
from pvgisprototype.api.tmy.weighting_scheme_model import MeteorologicalVariable
from pvgisprototype.api.tmy.models import (
    TMYStatisticModel,
)
from typing import Dict, List, Sequence
from typing import List
from pvgisprototype.api.tmy.helpers import (
    retrieve_nested_value,
)
from pvgisprototype.api.tmy.plot.functions import PLOT_FUNCTIONS
from pvgisprototype.api.tmy.models import (
    TMYStatisticModel,
)


def plot_requested_tmy_statistics(
    tmy_series: dict,
    variable: str,
    statistics: List[TMYStatisticModel],
    meteorological_variables: Sequence[MeteorologicalVariable],
    temperature_series,  #: numpy.ndarray = numpy.array(TEMPERATURE_DEFAULT),
    relative_humidity_series,
    wind_speed_series,  #: numpy.ndarray = numpy.array(WIND_SPEED_DEFAULT),
    global_horizontal_irradiance,  #: ndarray | None = None,
    direct_normal_irradiance,  #: ndarray | None = None,
    weighting_scheme: str = "",
    limit_x_axis_to_tmy_extent: bool = True,
    fingerprint: bool = False,
):
    """Plot the selected models based on the Enum to function mapping."""

    # Map variables to their data series
    variable_series_map: Dict[MeteorologicalVariable, any] = {
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: temperature_series,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: temperature_series,
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: temperature_series,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: relative_humidity_series,
        MeteorologicalVariable.MEAN_WIND_SPEED: wind_speed_series,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: global_horizontal_irradiance,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: direct_normal_irradiance,
    }

    # Filter map to only variables requested
    filtered_variable_map = {
        var: data
        for var, data in variable_series_map.items()
        if var in meteorological_variables
    }

    # for meteorological_variable in meteorological_variables:
    logger.info("Plotting")
    for meteorological_variable, time_series in filtered_variable_map.items():
        logger.info(
                f"- Processing series of {meteorological_variable} based on {time_series.name}",
                alt=f"- Processing series of [bold]{meteorological_variable}[/bold] based on [bold]{time_series.name}[/bold]",
                )

        meteorological_variable_statistics = tmy_series.get(meteorological_variable)
        if meteorological_variable_statistics is None:
            logger.warning(f"No TMY output for {meteorological_variable}")
            continue
        
        for statistic in statistics:
            logger.info(f"Statistic {statistic}\n")

            if statistic == TMYStatisticModel.tmy:
                plot_function = PLOT_FUNCTIONS.get(statistic)
                logger.info(
                    f"- Selected plotting function {plot_function}",
                    alt=f"- Selected plotting function [code]{plot_function}[/code]"
                )

                if plot_function is not None:
                                            # Extract the RAW TMY DataArray (not the output dict)
                    # tmy_dataarray = meteorological_variable_statistics.get(TMYStatisticModel.tmy)
                    tmy_dataarray = retrieve_nested_value(meteorological_variable_statistics, TMYStatisticModel.tmy.value)
                    if tmy_dataarray is None:
                        logger.warning(
                                f"Warning: TMY data not found for {meteorological_variable}",
                                alt=f"[red]Warning: TMY data not found for {meteorological_variable}[/red]"
                                )
                        continue
                    typical_months = retrieve_nested_value(meteorological_variable_statistics, 'Typical months')

                    plot_function(
                        tmy_series=tmy_dataarray,
                        variable=variable,
                        meteorological_variable=meteorological_variable,
                        finkelstein_schafer_statistic=meteorological_variable_statistics.get(
                            "Finkelstein-Schafer"
                        ),
                        typical_months=typical_months,
                        input_series=time_series,
                        limit_x_axis_to_tmy_extent=limit_x_axis_to_tmy_extent,
                        # title=TMYStatisticModel.tmy.name,
                        title="Typical Meteorological Year",
                        y_label=meteorological_variable.value,
                        weighting_scheme=weighting_scheme,
                        fingerprint=fingerprint,
                    )
                else:
                    raise ValueError(
                        f"Plot function for statistic {statistic} not found."
                    )

            elif statistic == TMYStatisticModel.ranked:
                plot_function = PLOT_FUNCTIONS.get(statistic.value)
                if plot_function is not None:
                    plot_function(
                        ranked_finkelstein_schafer_statistic=tmy_series.get(
                            statistic.value
                        ),
                        weighting_scheme=weighting_scheme,
                    )
                else:
                    raise ValueError(
                        f"Plot function for statistic {statistic} not found."
                    )
            else:
                plot_function = PLOT_FUNCTIONS.get(statistic)
                if plot_function is not None:
                    plot_function(tmy_series.get(statistic.value, None))
                else:
                    raise ValueError(
                        f"Plot function for statistic {statistic} not found."
                    )
