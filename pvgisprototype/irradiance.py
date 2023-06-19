import typer
from typing_extensions import Annotated
from typing import Optional
from .direct_irradiance import app as direct_irradiance
# from .diffuse_irradiance import app as diffuse_irradiance
# from .reflected_irradiance import app as reflected_irradiance


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Calculate solar irradiance",
)

app.add_typer(direct_irradiance, name="direct", help='Estimate the direct direct radiation')
# app.add_typer(diffuse, name="diffuse", help='Estimate the direct diffuse radiation')
# app.add_typer(reflected, name="reflected", help='Estimate the direct reflected radiation')
