import typer
from pvgisprototype.api.irradiance.efficiency import calculate_pv_efficiency_time_series
from typing import Annotated
from typing import Optional
from typing import List
from pathlib import Path
from rich import print
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.api.irradiance.efficiency_coefficients import STANDARD_EFFICIENCY_MODEL_COEFFICIENTS
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithm
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.cli.typer_parameters import typer_argument_irradiance_series
from pvgisprototype import TemperatureSeries
from pvgisprototype.cli.typer_parameters import typer_option_temperature_series
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype import WindSpeedSeries
from pvgisprototype.cli.typer_parameters import typer_option_wind_speed_series
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_pv_power_algorithm
from pvgisprototype.cli.typer_parameters import typer_option_module_temperature_algorithm
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_log
from pvgisprototype.cli.typer_parameters import typer_option_index
from pvgisprototype.cli.typer_parameters import typer_option_photovoltaic_module_model
from pvgisprototype.constants import PHOTOVOLTAIC_MODULE_DEFAULT
from pvgisprototype.constants import EFFICIENCY
from pvgisprototype.constants import EFFICIENCY_COLUMN_NAME
from pvgisprototype.cli.print import print_quantity_table
from pvgisprototype.api.irradiance.photovoltaic_module import PhotovoltaicModuleModel


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Calculate the efficiency of a photovoltaic system",
)


from typing import Any
import numpy as np
@app.command(
    'efficiency',
    no_args_is_help=True,
    help=f"Calculate the efficiency of a photovoltaic system",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def get_pv_efficiency_time_series(
    irradiance_series: Annotated[List[float], typer_argument_irradiance_series],
    spectral_factor=None,
    temperature_series: Annotated[TemperatureSeries, typer_option_temperature_series] = TEMPERATURE_DEFAULT,
    photovoltaic_module: Annotated[PhotovoltaicModuleModel, typer_option_photovoltaic_module_model] = PHOTOVOLTAIC_MODULE_DEFAULT, #PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    # model_constants: List[float] = EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT,
    standard_test_temperature: float = TEMPERATURE_DEFAULT,
    wind_speed_series: Annotated[WindSpeedSeries, typer_option_wind_speed_series] = WIND_SPEED_DEFAULT,
    power_model: Annotated[PVModuleEfficiencyAlgorithm, typer_option_pv_power_algorithm] = PVModuleEfficiencyAlgorithm.king,
    temperature_model: Annotated[ModuleTemperatureAlgorithm, typer_option_module_temperature_algorithm] = ModuleTemperatureAlgorithm.faiman,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = 'series_in',
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[Optional[int], typer_option_log] = 0,
    index: Annotated[bool, typer_option_index] = False,
    ctx: typer.Context = typer.Context,
):
    print(f'Context: {ctx.params}')
    print(f'photovoltaic_module : {type(photovoltaic_module)}')
    # print(f"Invoked subcommand: {ctx.invoked_subcommand}")
    results = calculate_pv_efficiency_time_series(
        irradiance_series=irradiance_series,
        spectral_factor=spectral_factor,
        temperature_series=temperature_series,
        photovoltaic_module=photovoltaic_module,
        # model_constants=model_constants,
        standard_test_temperature=standard_test_temperature,
        wind_speed_series=wind_speed_series,
        power_model=power_model,
        temperature_model=temperature_model,
        verbose=verbose,
    )
    if verbose > 0:
        print_quantity_table(
            dictionary=results,
            title=results['Title'],
            main_key = EFFICIENCY_COLUMN_NAME,
            rounding_places=rounding_places,
            index=index,
            verbose=verbose,
        )
        # if statistics:
        #     print_series_statistics(
        #         data_array=results[GLOBAL_INCLINED_IRRADIANCE],
        #         timestamps=timestamps,
        #         title="Efficiency",
        #         rounding_places=rounding_places,
        #     )
        # if csv:
        #     write_irradiance_csv(
        #         longitude=None,
        #         latitude=None,
        #         timestamps=timestamps,
        #         dictionary=results,
        #         filename=csv,
        #     )
    else:
        print(results)
