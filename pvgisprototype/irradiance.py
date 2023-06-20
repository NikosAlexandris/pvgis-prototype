import typer
from typing_extensions import Annotated
from typing import Optional
from .direct_irradiance import app as direct_irradiance
from .diffuse_irradiance import app as diffuse_irradiance
from .reflected_irradiance import app as reflected_irradiance
from .extraterrestrial_irradiance import app as extraterrestrial_irradiance
from .angular_loss_factor import app as angular_loss_factor


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate solar irradiance",
)

app.add_typer(direct_irradiance, name="direct", help='Estimate the direct irradiance', no_args_is_help=True)
app.add_typer(diffuse_irradiance, name="diffuse", help='Estimate the diffuse irradiance', no_args_is_help=True)
app.add_typer(reflected_irradiance, name="reflected", help='Estimate the direct reflected radiation', no_args_is_help=True)
app.add_typer(extraterrestrial_irradiance, name="extraterrestrial-irradiance", help='Compute the solar constant for a day of the year', no_args_is_help=True)
app.add_typer(angular_loss_factor, name="angular-loss", help='Calculate the angular loss factor for the direct horizontal irradiance', no_args_is_help=True)
