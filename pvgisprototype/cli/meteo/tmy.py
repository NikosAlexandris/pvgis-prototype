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
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
import typer
from typing_extensions import Annotated
from typing import List, Tuple
from pathlib import Path

from pandas import DatetimeIndex
from datetime import datetime

from xarray import DataArray
from pvgisprototype.api.irradiance.direct.normal_from_horizontal import calculate_direct_normal_from_horizontal_irradiance_series
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT, SolarPositionModel
from pvgisprototype.api.tmy.models import (
    TMYStatisticModel,
    select_meteorological_variables,
    select_tmy_models,
)
from pvgisprototype import (
    EccentricityPhaseOffset,
    EccentricityAmplitude,
    TemperatureSeries,
    RelativeHumiditySeries,
    WindSpeedSeries,
)
from pvgisprototype.api.tmy.weighting_scheme_model import MeteorologicalVariable, get_typical_meteorological_month_weighting_scheme
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.tmy.helpers import retrieve_nested_value
from pvgisprototype.api.tmy.plot.statistics import plot_requested_tmy_statistics
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.cli.typer.temperature import typer_option_temperature_series_for_tmy
from pvgisprototype.cli.typer.relative_humidity import typer_option_relative_humidity_series_for_tmy
from pvgisprototype.cli.typer.wind_speed import typer_option_wind_speed_series_for_tmy
from pvgisprototype.cli.typer.irradiance import (
    typer_option_direct_horizontal_irradiance,
    typer_option_global_horizontal_irradiance,
)
from pvgisprototype.cli.typer.location import typer_argument_longitude_in_degrees
from pvgisprototype.cli.typer.location import typer_argument_latitude_in_degrees
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_naive_timestamps,
    typer_option_timezone,
)
from pvgisprototype.api.datetime.now import now_datetime
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.helpers import typer_option_convert_longitude_360
from pvgisprototype.cli.typer.time_series import typer_option_data_variable
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.cli.typer.time_series import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer.time_series import typer_option_tolerance
from pvgisprototype.cli.typer.time_series import typer_option_mask_and_scale
from pvgisprototype.cli.typer.time_series import typer_option_in_memory
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.cli.typer.statistics import typer_option_groupby
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.output import typer_option_output_filename
from pvgisprototype.cli.typer.output import typer_option_variable_name_as_suffix
from pvgisprototype.cli.typer.output import (
    typer_option_angle_output_units,
    typer_option_command_metadata,
    typer_option_csv,
    typer_option_fingerprint,
    typer_option_index,
    typer_option_quick_response,
    typer_option_rounding_places,
)
from pvgisprototype.cli.typer.plot import (
    typer_option_uniplot,
    typer_option_uniplot_terminal_width,
)
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
    typer_option_multi_thread,
)
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    FINGERPRINT_FLAG_DEFAULT,
    GROUPBY_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    QUIET_FLAG_DEFAULT,
    RADIANS,
    ROUNDING_PLACES_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TOLERANCE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.api.tmy.tmy import calculate_tmy
from pvgisprototype.api.tmy.weighting_scheme_model import (
    TypicalMeteorologicalMonthWeightingScheme,
)


def calculate_degree_days(
    location: Annotated[
        Tuple[float, float], typer.Argument(..., help="Latitude, longitude [°]")
    ],
    years: Annotated[
        Tuple[float, float],
        typer.Argument(
            ..., min=2005, max=2020, help="First and last year of calculations"
        ),
    ],
    meteo: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="Directory containing the meteorological data",
        ),
    ],
    elevation: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="Directory containing the digital elevation data",
        ),
    ],
    monthly: bool = typer.Option(False, is_flag=True, help="Print monthly averages"),
):
    """Calculate the cooling/heating degree days

    Args:

    Returns:
        None

    Raises:
        AssertionError: If the command exit code or output doesn't match the expected values.

    Example:

    Notes:
    - Refactored from the original C program `degreedays_hourly` as follows:\n
      - New flag, Old flag, Type, Old Variable, Description\n
      - monthly   , r    , Flag         , -                   , Print monthly averages \n
      - meteo     , g    , str          , dailyPrefix         , Directory containing the meteo files\n
      - elevation , f    , str          , elevationFilename   , Directory prefix of the DEM files\n
      - location  , d    , float, float , latitude, longitude , Latitude, longitude [°]\n
      - years     , y    , float, float , yearStart, yearEnd  , First year, last year of calculations
    """
    pass


def tmy_weighting(
    meteorological_variable: Annotated[
        MeteorologicalVariable,
        typer.Argument(help="Standard name of meteorological variable for Finkelstein-Schafer statistics"),
    ] = None,
    weighting_scheme: Annotated[
    TypicalMeteorologicalMonthWeightingScheme,
    typer.Option(help="Weighting scheme"),
    ] = TypicalMeteorologicalMonthWeightingScheme.ISO_15927_4.value,
):
    """Print the available weightings for a meteorological variable or full scheme."""
    if meteorological_variable:
        meteorological_variables = select_meteorological_variables(
            MeteorologicalVariable, [meteorological_variable]
        )
    else:
        print(f"{weighting_scheme} :")
        meteorological_variables = [None]  # To handle printing the full scheme

    for meteorological_variable in meteorological_variables:
        print(
            get_typical_meteorological_month_weighting_scheme(
                weighting_scheme=weighting_scheme,
                meteorological_variable=meteorological_variable,
            )
        )


def tmy(
    longitude: Annotated[float, typer_argument_longitude_in_degrees] = float(),
    latitude: Annotated[float, typer_argument_latitude_in_degrees] = float(),
    # time_series_2: Annotated[Path, typer_option_time_series] = None,
    timestamps: Annotated[DatetimeIndex, typer_argument_naive_timestamps] = str(
        now_datetime()
    ),
    timezone: Annotated[ZoneInfo | None, typer_option_timezone] = None,
    start_time: Annotated[
        datetime | None, typer_option_start_time
    ] = None,  # Used by a callback function
    periods: Annotated[
        int | None, typer_option_periods
    ] = None,  # Used by a callback function
    frequency: Annotated[
        str | None, typer_option_frequency
    ] = None,  # Used by a callback function
    end_time: Annotated[
        datetime | None, typer_option_end_time
    ] = None,  # Used by a callback function
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,

    # Required variables
    # time_series: Annotated[Path, typer_argument_time_series],
    variable: Annotated[str | None, typer_option_data_variable] = None,
    meteorological_variable: Annotated[
        List[MeteorologicalVariable],
        typer.Option(
            help="Standard name of meteorological variable for Finkelstein-Schafer statistics"
        ),
    ] = [MeteorologicalVariable.all],
    global_horizontal_irradiance: Annotated[
        Path | None, typer_option_global_horizontal_irradiance
    ] = None,
    direct_horizontal_irradiance: Annotated[
        Path | None, typer_option_direct_horizontal_irradiance
    ] = None,
    temperature_series: Annotated[
        TemperatureSeries, typer_option_temperature_series_for_tmy
    ] = TemperatureSeries().average_air_temperature,
    relative_humidity_series: Annotated[
        RelativeHumiditySeries, typer_option_relative_humidity_series_for_tmy,
    ] = RelativeHumiditySeries().average_relative_humidity,
    wind_speed_series: Annotated[
        WindSpeedSeries, typer_option_wind_speed_series_for_tmy
    ] = WindSpeedSeries().average_wind_speed,
    # wind_speed_variable: Annotated[str | None, typer_option_data_variable] = None,

    # Solar positioning, required for the direct normal irradiance
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    eccentricity_phase_offset: float = EccentricityPhaseOffset().value,
    eccentricity_amplitude: float = EccentricityAmplitude().value,

    # Series selection options
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = MethodForInexactMatches.nearest,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    
    # Output options
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[str | None, typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    output_filename: Annotated[
        Path, typer_option_output_filename
    ] = "series_in",  # Path(),
    variable_name_as_suffix: Annotated[
        bool, typer_option_variable_name_as_suffix
    ] = True,

    # Optios for internal calculations
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    multi_thread: Annotated[
        bool, typer_option_multi_thread
    ] = MULTI_THREAD_FLAG_DEFAULT,

    # More output options
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    rounding_places: Annotated[
        int | None, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme = TypicalMeteorologicalMonthWeightingScheme.ISO_15927_4.value,
    plot_statistic: Annotated[
        list[TMYStatisticModel],
        typer.Option(help="Select which Finkelstein-Schafer statistics to plot"),
    ] = None,  # [TMYStatisticModel.tmy.value],
    limit_x_axis_to_tmy_extent: Annotated[
        bool, "Limit plot of input time series to temporal extent of TMY"
    ] = True,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, typer_option_quick_response
    ] = QuickResponseCode.NoneValue,
    metadata: Annotated[bool, typer_option_command_metadata] = False,
):
    """Generate the Typical Meteorological Year (TMY)

    A typical meteorological year (TMY) is a set of meteorological data with
    data values for every hour in a year for a given geographical location. The
    data are selected from hourly data in a longer time period (normally 10
    years or more). 
    
    An overview of the algorithm for calculating the TMY :

    1. **Input data** : Read _at least_ 10 years of hourly time series over a
    location

    2. **Daily Statistics** : Compute daily maximum, minimum, and mean for
    selected variables.

    3. **Cumulative Distribution Function** (CDF) : Compute the CDF of each
    variable for each month :

       3.1 one CDF for each variable, month, and year. For example, for the
       Global Horizontal Irradiance (GHI) : one for January 2011, one for
       January 2012 and so on, _and_ for each month the same for the ambient
       Temperature or other variables.
       
       3.2 one long-term CDF for each variable across all years for each month.

    4. **Finkelstein-Schafer Statistic** :

       4.1 Compute the absolute difference between the long-term CDF and the
       candidate month's CDF. 4.2 Compute the weighted sum (WS) of these
       differences for each month and year.

    5. **Typical Months** : Rank months by the lowest WS for each month (e.g.,
    rank all Januaries).

    6. **Month Selection** : 

       - ISO method: Select months based on wind speed similarity to the
         long-term average.

       - Sandia/NREL methods : Re-rank top months by their closeness to
         long-term averages, filtering based on extreme values.

    7. **TMY** : Combine the selected months into a continuous year, smoothing
    variable transitions at month boundaries.

    Notes
    -----

    Pay attention to the default _return_ modus of this function ! Without any
    `--verbose` asked, is to print all TMY variable values as one CSV string.
    In the case of a TMY dataset, this is likely very long.

    """
    direct_normal_irradiance_series = None
    direct_normal_irradiance = None

    # Map variables to their data series
    variable_series_map: Dict[MeteorologicalVariable, any] = {
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: temperature_series,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: relative_humidity_series,
        MeteorologicalVariable.MEAN_WIND_SPEED: wind_speed_series,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: global_horizontal_irradiance,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: direct_normal_irradiance,
    }

    # meteorological_variable = MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE
    meteorological_variables = select_meteorological_variables(
        MeteorologicalVariable, meteorological_variable
    )  # Using a callback fails!

    # Filter map to only variables requested

    filtered_variable_map = {
        var: data
        for var, data in variable_series_map.items()
        if var in meteorological_variables
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Calculating the TMY...", total=None)
        if isinstance(global_horizontal_irradiance, (str, Path)) and isinstance(
            direct_horizontal_irradiance, (str, Path)
        ):
            global_horizontal_irradiance = select_time_series(
                    time_series=global_horizontal_irradiance,
                    # longitude=longitude_for_selection,
                    # latitude=latitude_for_selection,
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    # convert_longitude_360=convert_longitude_360,
                    neighbor_lookup=neighbor_lookup,
                    tolerance=tolerance,
                    mask_and_scale=mask_and_scale,
                    in_memory=in_memory,
                    verbose=0,  # no verbosity here by choice!
                    log=log,
                )
            direct_horizontal_irradiance = select_time_series(
                    time_series=direct_horizontal_irradiance,
                    # longitude=longitude_for_selection,
                    # latitude=latitude_for_selection,
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    # convert_longitude_360=convert_longitude_360,
                    neighbor_lookup=neighbor_lookup,
                    tolerance=tolerance,
                    mask_and_scale=mask_and_scale,
                    in_memory=in_memory,
                    verbose=0,  # no verbosity here by choice!
                    log=log,
                )
            direct_normal_irradiance_series = calculate_direct_normal_from_horizontal_irradiance_series(
                direct_horizontal_irradiance=direct_horizontal_irradiance.values,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                # timezone=timezone,
                solar_position_model=solar_position_model,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                # angle_output_units=angle_output_units,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                fingerprint=fingerprint,
            )
            direct_normal_irradiance_series = DataArray(
                direct_normal_irradiance_series.value,
                coords=[("time", timestamps)],
                name=direct_normal_irradiance_series.title,
            )
            # direct_normal_irradiance_series.attrs["units"] = "W/m^2"
            # direct_normal_irradiance_series.load()
        if isinstance(temperature_series, Path):
            temperature_series = select_time_series(
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    time_series=temperature_series,
                    neighbor_lookup=neighbor_lookup,
                    tolerance=tolerance,
                    mask_and_scale=mask_and_scale,
                    in_memory=in_memory,
                    # dtype=dtype,
                    # array_backend=array_backend,
                    # multi_thread=multi_thread,
                    verbose=verbose,
                    log=log,
                )
        if isinstance(relative_humidity_series, Path):
            # relative_humidity_series = get_relative_humidity_series(
            relative_humidity_series = select_time_series(
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    time_series=relative_humidity_series,
                    neighbor_lookup=neighbor_lookup,
                    tolerance=tolerance,
                    mask_and_scale=mask_and_scale,
                    in_memory=in_memory,
                    # dtype=dtype,
                    # array_backend=array_backend,
                    # multi_thread=multi_thread,
                    verbose=verbose,
                    log=log,
                )
        if isinstance(wind_speed_series, Path):
            # wind_speed_series = get_wind_speed_series(
            wind_speed_series = select_time_series(
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    time_series=wind_speed_series,
                    neighbor_lookup=neighbor_lookup,
                    tolerance=tolerance,
                    mask_and_scale=mask_and_scale,
                    in_memory=in_memory,
                    # dtype=dtype,
                    # array_backend=array_backend,
                    # multi_thread=multi_thread,
                    verbose=verbose,
                    log=log,
                )

        tmy = calculate_tmy(
            meteorological_variables=meteorological_variables,
            temperature_series=temperature_series,
            relative_humidity_series=relative_humidity_series,
            wind_speed_series=wind_speed_series,
            # wind_speed_variable=wind_speed_variable,
            global_horizontal_irradiance=global_horizontal_irradiance,
            direct_normal_irradiance=direct_normal_irradiance_series,
            timestamps=timestamps,
            weighting_scheme=weighting_scheme,
            verbose=verbose,
            fingerprint=fingerprint,
        )
        if plot_statistic:

            tmy_statistics = select_tmy_models(
                enum_type=TMYStatisticModel,
                models=plot_statistic,
            )
            plot_requested_tmy_statistics(
                tmy_series=tmy,
                variable=variable,
                statistics=tmy_statistics,
                meteorological_variables=meteorological_variables,
                temperature_series=temperature_series,
                relative_humidity_series=relative_humidity_series,
                wind_speed_series=wind_speed_series,
                global_horizontal_irradiance=global_horizontal_irradiance,
                direct_normal_irradiance=direct_normal_irradiance_series,
                weighting_scheme=weighting_scheme.name,
                limit_x_axis_to_tmy_extent=limit_x_axis_to_tmy_extent,
            )

    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if quick_response_code.value != QuickResponseCode.NoneValue:
        print(f"[code]quick_response_code[/code] {NOT_IMPLEMENTED_CLI}")
        # from pvgisprototype.cli.print.qr import print_quick_response_code

        # print_quick_response_code(
        #     dictionary=tmy,
        #     longitude=longitude,
        #     latitude=latitude,
        #     elevation=False,
        #     surface_orientation=False,
        #     surface_tilt=False,
        #     timestamps=timestamps,
        #     rounding_places=rounding_places,
        # )
    if not quiet:
        if verbose > 0:
            print(f"[code]verbose[/code] {NOT_IMPLEMENTED_CLI}")
            for meteorological_variable, output in tmy.items():
                continue
        else:
            # When verbose=0, print TMY data as CSV
            for meteorological_variable in meteorological_variables:
                variable_output = tmy.get(meteorological_variable)
                if variable_output is None:
                    continue
                
                # Get the actual TMY DataArray, not the FS statistic
                tmy_dataarray = retrieve_nested_value(variable_output, TMYStatisticModel.tmy.value)
                if tmy_dataarray is not None:
                    # Flatten and print as CSV
                    flat_values = tmy_dataarray.values.flatten().astype(str)
                    csv_str = ",".join(flat_values)
                    print(csv_str)
    # if not quiet:
    #     if verbose > 0:
    #         print(f"[code]verbose[/code] {NOT_IMPLEMENTED_CLI}")
    #         for meteorological_variable, output in tmy.items():
    #             continue
    #         # from pvgisprototype.cli.print.irradiance import print_irradiance_table_2

    #         # print_irradiance_table_2(
    #         #     longitude=longitude,
    #         #     latitude=latitude,
    #         #     timestamps=timestamps,
    #         #     dictionary=tmy,
    #         #     # title=photovoltaic_power_output_series['Title'] + f" series {POWER_UNIT}",
    #         #     rounding_places=rounding_places,
    #         #     index=index,
    #         #     surface_orientation=True,
    #         #     surface_tilt=True,
    #         #     verbose=verbose,
    #         # )
    #     else:
    #         flat_list = []
    #         for meteorological_variable in meteorological_variables:
    #             statistics = tmy.get(meteorological_variable)
    #             for data_array in statistics.get(
    #                 FinkelsteinSchaferStatisticModel.ranked, NOT_AVAILABLE
    #             ):
    #                 flat_list.extend(data_array.values.flatten().astype(str))
    #             csv_str = ",".join(flat_list)
    #             print(csv_str)
    if statistics:
        print(f"[code]statistics[/code] {NOT_IMPLEMENTED_CLI}")
        # from pvgisprototype.api.series.statistics import print_series_statistics

        # print_series_statistics(
        #     data_array=tmy,
        #     timestamps=timestamps,
        #     groupby=groupby,
        #     title="Typical Meteorological Year",
        # )
    if uniplot:
        print(f"[code]uniplot[/code] {NOT_IMPLEMENTED_CLI}")
        # from pvgisprototype.api.plot import uniplot_data_array_series

        # uniplot_data_array_series(
        #     data_array=tmy[list(tmy.data_vars)[0]],
        #     # list_extra_data_arrays=individual_series,
        #     timestamps=timestamps,
        #     resample_large_series=resample_large_series,
        #     lines=True,
        #     supertitle="Typical Meteorological Year",
        #     title="Typical Meteorological Year",
        #     label="TMY",
        #     # extra_legend_labels=individual_labels,
        #     unit="?",
        #     terminal_width_fraction=terminal_width_fraction,
        # )
    if fingerprint:
        print(f"[code]fingerprint[/code] {NOT_IMPLEMENTED_CLI}")
        # from pvgisprototype.cli.print.fingerprint import print_finger_hash

        # print_finger_hash(dictionary=tmy[list(tmy.data_vars)[0]])
    if metadata:
        import click

        from pvgisprototype.cli.print.metadata import print_command_metadata

        print_command_metadata(context=click.get_current_context())
    # Call write_irradiance_csv() last : it modifies the input dictionary !
    if csv:
        print(f"[code]csv[/code] {NOT_IMPLEMENTED_CLI}")
        # from pvgisprototype.cli.write import write_irradiance_csv

        # write_irradiance_csv(
        #     longitude=longitude,
        #     latitude=latitude,
        #     timestamps=timestamps,
        #     dictionary=tmy,
        #     filename=csv,
        #     index=index,
        # )
