import typer
from pvgisprototype.cli.typer.group import OrderCommands
from typing import Annotated
from typing import List
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.typer.position import typer_argument_solar_incidence
from pvgisprototype.cli.typer.position import typer_argument_solar_incidence_series
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import ANGULAR_LOSS_COEFFICIENT
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.api.irradiance.loss import calculate_angular_loss_factor_for_direct_irradiance_series


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    help=f"Angular loss factor {NOT_IMPLEMENTED_CLI}",
)


@app.command(
    'direct',
    no_args_is_help=True,
    help=f'⦟ Solar incidence angle modifier for direct inclined irradiance due to reflectivity by Martin & Ruiz, 2005 {NOT_IMPLEMENTED_CLI}',
    short_help=f'⦟ Solar incidence angle modifier for direct irradiance due to reflectivity {NOT_IMPLEMENTED_CLI}',
    rich_help_panel=rich_help_panel_toolbox,
)
def get_angular_loss_factor_for_direct_irradiance_series(
    solar_incidence_series: Annotated[List[float], typer_argument_solar_incidence_series],
    angular_loss_coefficient: float = ANGULAR_LOSS_COEFFICIENT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
):
    """
    Notes
    -----
    This function implements the solar incidence angle modifier as per Martin &
    Ruiz (2005). Expected is the angle between the sun-solar-surface vector and
    the vector normal to the reference solar surface. We call this the
    _typical_ incidence angle as opposed to the _complementary_ incidence angle
    defined by Jenco (1992).

    """
    angular_loss_factor_for_direct_irradiance_series = calculate_angular_loss_factor_for_direct_irradiance_series(
            solar_incidence_series=solar_incidence_series,
            angular_loss_coefficient=angular_loss_coefficient,
            verbose=verbose,
            log=log,
            )


@app.command(
    'indirect',
    no_args_is_help=True,
    help=f'⦟ Solar incidence angle modifier for non-direct inclined irradiance due to reflectivity by Martin & Ruiz, 2005 {NOT_IMPLEMENTED_CLI}',
    short_help=f'⦟ Solar incidence angle modifier for non-direct irradiance due to reflectivity {NOT_IMPLEMENTED_CLI}',
    rich_help_panel=rich_help_panel_toolbox,
)
def get_angular_loss_factor_for_nondirect_irradiance(
    indirect_angular_loss_coefficient,
    angular_loss_coefficient = ANGULAR_LOSS_COEFFICIENT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """
    """
    angular_loss_factor_for_nondirect_irradiance = calculate_angular_loss_factor_for_nondirect_irradiance(
    indirect_angular_loss_coefficient=indirect_angular_loss_coefficient,
    angular_loss_coefficient=angular_loss_coefficient,
    verbose=verbose,
    )
