import typer
from pvgisprototype.api.geometry.time_models import SolarTimeModels


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate reflected solar irradiance",
)


@app.command('reflected', no_args_is_help=True)
def calculate_reflected_irradiance():
    """
    solar_time_model: Annotated[SolarTimeModels, typer.Option(
        '-m',
        '--solar-time-model',
        help="Model to calculate solar position",
        show_default=True,
        show_choices=True,
        case_sensitive=False,
        rich_help_panel=rich_help_panel_advanced_options)] = SolarTimeModels.skyfield,
    """
    pass

