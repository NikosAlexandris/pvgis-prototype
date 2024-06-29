from pvgisprototype.log import log_function_call
from pvgisprototype.api.power.efficiency import calculate_pv_efficiency_series
from typing import Annotated
from typing import Optional
from typing import List
from pathlib import Path
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.cli.typer.irradiance import typer_argument_irradiance_series
from pvgisprototype import TemperatureSeries
from pvgisprototype.cli.typer.temperature import typer_option_temperature_series
from pvgisprototype.constants import TEMPERATURE_DEFAULT, UNITLESS
from pvgisprototype import WindSpeedSeries
from pvgisprototype.cli.typer.wind_speed import typer_option_wind_speed_series
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype import SpectralFactorSeries
from pvgisprototype.cli.typer.spectral_factor import typer_argument_spectral_factor_series
from pvgisprototype.cli.typer.efficiency import typer_option_pv_power_algorithm
from pvgisprototype.cli.typer.efficiency import typer_option_module_temperature_algorithm
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.cli.typer.statistics import typer_option_groupby
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.output import typer_option_index
from pvgisprototype.cli.typer.photovoltaic import typer_option_photovoltaic_module_model
from pvgisprototype.constants import PHOTOVOLTAIC_MODULE_DEFAULT
from pvgisprototype.constants import EFFICIENCY_COLUMN_NAME
from pvgisprototype.constants import SPECTRAL_FACTOR_DEFAULT
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
import typer
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import STATISTICS_FLAG_DEFAULT
from pvgisprototype.constants import GROUPBY_DEFAULT
from pvgisprototype.constants import CSV_PATH_DEFAULT
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT
from pvgisprototype.constants import QUIET_FLAG_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.cli.typer.output import typer_option_fingerprint
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.constants import UNIPLOT_FLAG_DEFAULT
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.cli.typer.output import typer_option_command_metadata


@log_function_call
def photovoltaic_efficiency_series(
    irradiance_series: Annotated[List[float], typer_argument_irradiance_series],
    spectral_factor_series: Annotated[Path|SpectralFactorSeries, typer_argument_spectral_factor_series] = SPECTRAL_FACTOR_DEFAULT,  # Accept also list of float values ?
    temperature_series: Annotated[TemperatureSeries, typer_option_temperature_series] = TEMPERATURE_DEFAULT,
    # temperature_series: Annotated[Path|TemperatureSeries, typer_argument_temperature_series] = TEMPERATURE_DEFAULT,
    photovoltaic_module: Annotated[PhotovoltaicModuleModel, typer_option_photovoltaic_module_model] = PHOTOVOLTAIC_MODULE_DEFAULT,
    standard_test_temperature: float = TEMPERATURE_DEFAULT,
    wind_speed_series: Annotated[WindSpeedSeries, typer_option_wind_speed_series] = WIND_SPEED_DEFAULT,
    # wind_speed_series: Annotated[Path|WindSpeedSeries, typer_argument_wind_speed_series] = WIND_SPEED_DEFAULT,
    power_model: Annotated[PhotovoltaicModulePerformanceModel, typer_option_pv_power_algorithm] = PhotovoltaicModulePerformanceModel.king,
    temperature_model: Annotated[ModuleTemperatureAlgorithm, typer_option_module_temperature_algorithm] = ModuleTemperatureAlgorithm.faiman,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[Optional[str], typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = False,
    ctx: typer.Context = typer.Context,
):
    photovoltaic_efficiency_series = calculate_pv_efficiency_series(
        irradiance_series=irradiance_series,
        spectral_factor_series=spectral_factor_series,
        temperature_series=temperature_series,
        photovoltaic_module=photovoltaic_module,
        standard_test_temperature=standard_test_temperature,
        wind_speed_series=wind_speed_series,
        power_model=power_model,
        temperature_model=temperature_model,
        verbose=verbose,
    )
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print import print_quantity_table
            print_quantity_table(
                dictionary=photovoltaic_efficiency_series,
                title=photovoltaic_efficiency_series['Title'],
                main_key=EFFICIENCY_COLUMN_NAME,
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        # else:
        #     flat_list = photovoltaic_efficiency_series.value.flatten().astype(str)
        #     csv_str = ','.join(flat_list)
        #     print(csv_str)

    # if statistics:
    #     print_series_statistics(
    #         data_array=photovoltaic_efficiency_series[GLOBAL_INCLINED_IRRADIANCE],
    #         timestamps=timestamps,
    #         title="Efficiency",
    #         rounding_places=rounding_places,
    #     )
    # if csv:
    #     write_irradiance_csv(
    #         longitude=None,
    #         latitude=None,
    #         timestamps=timestamps,
    #         dictionary=photovoltaic_efficiency_series,
    #         filename=csv,
    #     )
    #   
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_series
        uniplot_data_array_series(
            data_array=photovoltaic_efficiency_series.value,
            list_extra_data_arrays=None,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle = 'Efficiency Coefficients Series',
            title = 'Efficiency Coefficients Series',
            label = 'Efficiency Coefficients',
            extra_legend_labels=None,
            unit = UNITLESS,
            terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=photovoltaic_efficiency_series.components)
    if metadata:
        from pvgisprototype.cli.print import print_command_metadata
        import click
        print_command_metadata(context = click.get_current_context())
