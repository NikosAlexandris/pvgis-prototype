import typer
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND
from pvgisprototype.api.irradiance.direct import calculate_direct_normal_irradiance_time_series
from pvgisprototype.api.irradiance.direct import calculate_direct_horizontal_irradiance_time_series
from pvgisprototype.api.irradiance.direct import calculate_direct_inclined_irradiance_time_series_pvgis
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from typing import Annotated
from typing import Optional
from datetime import datetime
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
from pvgisprototype.api.position.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_INCIDENCE_ALGORITHM_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_convert_longitude_360
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_optical_air_mass_series
from pvgisprototype import OpticalAirMass
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.constants import RADIANS
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_index
from pathlib import Path
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_uniplot
from pvgisprototype.cli.typer_parameters import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
import numpy as np
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.progress import progress
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE
from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
from pandas import DatetimeIndex
from rich import print
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call


@log_function_call
def get_direct_normal_irradiance_time_series(
    timestamps: Annotated[Optional[DatetimeIndex], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT, # REVIEW-ME + Typer Parser
    optical_air_mass_series: Annotated[OpticalAirMass, typer_option_optical_air_mass_series] = [OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT], # REVIEW-ME + ?
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_SERIES_FLAG_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    uniplot: Annotated[bool, typer_option_uniplot] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = False,
    fingerprint: Annotated[bool, typer.Option('--fingerprint', '--fp', help='Fingerprint the photovoltaic power output time series')] = False,
    log: Annotated[int, typer.Option('--log', help='Log internal operations')] = 0,
    quiet: Annotated[bool, typer.Option('--quiet', help='Do not print out the output')] = False,
) -> None:
    # with progress:
    direct_normal_irradiance_series = calculate_direct_normal_irradiance_time_series(
        timestamps=timestamps,
        start_time=start_time,
        frequency=frequency,
        end_time=end_time,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        optical_air_mass_series=optical_air_mass_series,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        random_days=random_days,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    # Reporting =============================================================
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print import print_irradiance_table_2
            from pvgisprototype.constants import TITLE_KEY_NAME
            print_irradiance_table_2(
                timestamps=timestamps,
                dictionary=direct_normal_irradiance_series.components,
                title = (
                    direct_normal_irradiance_series.components[TITLE_KEY_NAME]
                    + f" normal irradiance series {IRRADIANCE_UNITS}"
                ),
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = direct_normal_irradiance_series.value.flatten().astype(str)
            csv_str = ','.join(flat_list)
            print(csv_str)

    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics
        print_series_statistics(
            data_array=direct_normal_irradiance_series[DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME],
            timestamps=timestamps,
            title=f"Direct normal irradiance series {IRRADIANCE_UNITS}",
            rounding_places=rounding_places,
        )
    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv
        write_irradiance_csv(
            longitude=None,
            latitude=None,
            timestamps=timestamps,
            dictionary=direct_normal_irradiance_series.components,
            filename=csv,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_time_series
        uniplot_data_array_time_series(
            data_array=direct_normal_irradiance_series.value,
            data_array_2=None,
            lines=True,
            supertitle = 'Direct Normal Irradiance Series',
            title = 'Direct Normal Irradiance Series',
            label = 'Direct Normal Irradiance',
            label_2 = None,
            unit = IRRADIANCE_UNITS,
            # terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=direct_normal_irradiance_series.components)



