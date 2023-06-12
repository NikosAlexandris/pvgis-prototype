import logging
from pvgisprototype.data_structures import SolarGeometryDayConstants
import typer
from typing import Annotated


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"PVGIS core CLI prototype",
)


# from :
# function : com_par_const()
@app.callback(invoke_without_command=True)
def calculate_solar_geometry_constants(
        latitude: Annotated[float, typer.Argument(
            help='Latitude in decimal degrees, south is negative',
            min=-90, max=90)],
        local_solar_time: float,
        cosine_of_declination: float,
        sine_of_declination: float,
        time_offset: float = 0,
        EPS: float = 1e-5,
) -> SolarGeometryDayConstants:
    """
    Compute solar geometry constants for the day.

    Parameters
    ----------
    local_solar_time : float
        Longitude time.
    cosine_of_declination : float
        Cosine of the solar declination.
    sine_of_declination : float
        Sine of the solar declination.

    Returns
    -------
    SolarGeometryDayConstants
        Solar geometry constants for the day.
    """
    solar_geometry_constants = SolarGeometryDayConstants.calculate_solar_geometry_constants(
            latitude,
            local_solar_time,
            cosine_of_declination,
            sine_of_declination,
            )
    typer.echo(solar_geometry_constants)
    return solar_geometry_constants

