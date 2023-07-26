import typer
from typing_extensions import Annotated
from typing import Optional

from ..api.irradiance.extraterrestrial import app as extraterrestrial_irradiance
from ..api.irradiance.shortwave import app as global_irradiance
from ..api.irradiance.direct import app as direct_irradiance
from ..api.irradiance.diffuse import app as diffuse_irradiance
from ..api.irradiance.reflected import app as reflected_irradiance
from ..api.irradiance.loss import app as angular_loss_factor
from ..api.irradiance.effective import app as effective_irradiance


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":sun_with_face: Calculate solar irradiance",
)


app.add_typer(global_irradiance, name="global", help='Estimate the global (shortwave) irradiance', no_args_is_help=True)
app.add_typer(direct_irradiance, name="direct", help='Estimate the direct irradiance', no_args_is_help=True)
app.add_typer(diffuse_irradiance, name="diffuse", help='Calculate the diffuse irradiance', no_args_is_help=True)
app.add_typer(reflected_irradiance, name="reflected", help='Estimate the reflected radiation', no_args_is_help=True)
app.add_typer(extraterrestrial_irradiance, name="extraterrestrial", help='Compute the solar constant for a day of the year', no_args_is_help=True)
app.add_typer(angular_loss_factor, name="angular-loss", help='Calculate the angular loss factor for the direct horizontal irradiance', no_args_is_help=True)
app.add_typer(effective_irradiance, name="effective", help='Calculate the effective irradiance for a specific hour', no_args_is_help=True)
