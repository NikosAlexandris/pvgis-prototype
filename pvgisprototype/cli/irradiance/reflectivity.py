from typing import Annotated, List

import typer

from pvgisprototype.algorithms.martin_ruiz.reflectivity import (
    calculate_reflectivity_factor_for_direct_irradiance_series,
    calculate_reflectivity_factor_for_nondirect_irradiance,
)
from pvgisprototype.cli.messages import NOT_COMPLETE_CLI
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.position import typer_argument_solar_incidence_series
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.constants import (
    ANGULAR_LOSS_COEFFICIENT,
    LOG_LEVEL_DEFAULT,
    QUIET_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)

app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    help=f"Reflectivity effect as a function of the solar incidence angle {NOT_COMPLETE_CLI}",
)


@app.command(
    "direct",
    no_args_is_help=True,
    help=f"⦟ Solar incidence angle modifier for direct inclined irradiance due to reflectivity by Martin & Ruiz, 2005 {NOT_COMPLETE_CLI}",
    short_help=f"⦟ Solar incidence angle modifier for direct irradiance due to reflectivity {NOT_COMPLETE_CLI}",
    rich_help_panel=rich_help_panel_toolbox,
)
def get_reflectivity_factor_for_direct_irradiance_series(
    solar_incidence_series: Annotated[
        List[float], typer_argument_solar_incidence_series
    ],
    angular_loss_coefficient: float = ANGULAR_LOSS_COEFFICIENT,
    # csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    # dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    # array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    # uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    # resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    # terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    # fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    # metadata: Annotated[bool, typer_option_command_metadata] = False,
    # panels: Annotated[bool, typer_option_panels_output] = False,
    # index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
):
    """
    Notes
    -----
    This CLI function uses an implementation of the solar incidence angle
    modifier as per Martin & Ruiz (2005). Expected is the angle between the
    sun-solar-surface vector and the vector normal to the reference solar
    surface. We call this the _typical_ incidence angle as opposed to the
    _complementary_ incidence angle defined by Jenčo (1992).

    """
    reflectivity_factor_for_direct_irradiance_series = (
        calculate_reflectivity_factor_for_direct_irradiance_series(
            solar_incidence_series=solar_incidence_series,
            angular_loss_coefficient=angular_loss_coefficient,
            verbose=verbose,
            log=log,
        )
    )
    if not quiet:
        if verbose > 0:
            pass
        else:
            flat_list = (
                reflectivity_factor_for_direct_irradiance_series.flatten().astype(str)
            )
            csv_str = ",".join(flat_list)
            print(csv_str)


@app.command(
    "indirect",
    no_args_is_help=True,
    help=f"⦟ Solar incidence angle modifier for non-direct inclined irradiance due to reflectivity by Martin & Ruiz, 2005 {NOT_COMPLETE_CLI}",
    short_help=f"⦟ Solar incidence angle modifier for non-direct irradiance due to reflectivity {NOT_COMPLETE_CLI}",
    rich_help_panel=rich_help_panel_toolbox,
)
def get_reflectivity_factor_for_nondirect_irradiance(
    indirect_angular_loss_coefficient: float,
    angular_loss_coefficient: float = ANGULAR_LOSS_COEFFICIENT,
    # csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    # dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    # array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    # uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    # resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    # terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    # fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    # metadata: Annotated[bool, typer_option_command_metadata] = False,
    # panels: Annotated[bool, typer_option_panels_output] = False,
    # index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
):
    """ """
    reflectivity_factor_for_nondirect_irradiance = (
        calculate_reflectivity_factor_for_nondirect_irradiance(
            indirect_angular_loss_coefficient=indirect_angular_loss_coefficient,
            angular_loss_coefficient=angular_loss_coefficient,
            verbose=verbose,
        )
    )
    if not quiet:
        if verbose > 0:
            pass
        else:
            print(reflectivity_factor_for_nondirect_irradiance)
