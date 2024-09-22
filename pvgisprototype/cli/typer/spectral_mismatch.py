from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_spectral_mismatch,
)
import typer


spectral_mismatch_model_typer_help = "Spectral mismatch model"


typer_option_spectral_mismatch_model = typer.Option(
    help=spectral_mismatch_model_typer_help,
    is_eager=True,
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_spectral_mismatch,
)
