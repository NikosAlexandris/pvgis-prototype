from devtools import debug
import logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('error.log'),  # Save log to a file
        logging.StreamHandler()  # Print log to the console
    ]
)
import typer
from typing_extensions import Annotated
import math
from math import exp
from math import pi


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"Angular loss factor",
)


AOIConstants = []
AOIConstants.append(-0.074)
AOIConstants.append(0.155)


@app.callback(invoke_without_command=True)
def calculate_angular_loss_factor_for_direct_irradiance(
        sine_solar_incidence_angle: Annotated[float, typer.Argument(
            help='Solar altitude in degrees °',
            min=0, max=90)],
        angle_of_incidence_constant: float = 0.155,
    ):
    """Calculate the angular loss factor for the direct horizontal radiation based
    on the solar altitude and declination

    The adjustment factor represents the fraction of the original
    `direct_radiation` that is retained after accounting for the loss of
    radiation due to the angle of incidence or the orientation of the surface
    with respect to the sun.

    Parameters
    ----------

    angle_of_incidence_constant: float
        In degrees (°).
    sine_solar_incidence_angle: float
        sine of solar incidence angle in degrees (°).

    Returns
    -------
    angular_loss_factor: float

    Notes
    -----

    The adjustment involves:

    1. computes the fraction of radiation that is _not_ lost due to
    the `solar_incidence_angle` angle divided by the `solar_declination` ranging between
    0 (complete loss) and 1 (no loss):

        `( 1 - exp( -solar_incidence_angle / angle_of_incidence_constant ) )`

        - The exponential function `exp`, raises the mathematical constant `e`
          (approximately 2.71828) to the power of the given argument.

        - The negative exponential term of the fraction `solar_altitude /
          solar_declination` calculates the exponential decay or attenuation
          factor based on the ratio of `solar_altitude` to the `solar_declination`. 
    
    2. rescales the adjusted value to bring it within a suitable range,
    by multiplying it by the reciprocal of the exponential term with the
    reciprocal of the `solar_declination`:

        `1 / ( 1 - exp( - 1 / solar_declination) )`

    ensuring no excessive amplification or diminishing the effect
    (over-amplification or under-amplification).
    """
    try:
        # The `-` in `-sine_solar_incidence_angle` is maybe the _workaround_ for the trigonometry error!
        angular_loss = 1 - exp( - sine_solar_incidence_angle / angle_of_incidence_constant )
        # --------------------------------------------------------------------
        normalisation_term =  1 / ( 1 - exp( -1 / angle_of_incidence_constant))
        angular_loss_factor = angular_loss / normalisation_term
        typer.echo(f'Angular loss factor : {angular_loss_factor}')
        return angular_loss_factor

    except ZeroDivisionError as e:
        logging.error(f"Zero Division Error: {e}")
        typer.echo("Error: Division by zero in calculating the angular loss factor.")
        return 1


def calculate_angular_loss_factor_for_nondirect_irradiance(
    angular_loss_coefficient,
    solar_incidence_angle_1 = AOIConstants[0],
    solar_incidence_angle_2 = AOIConstants[1],
):
    """
    Here,
    - solar_incidence_angle_1 == AOIConstants[0]
    - solar_incidence_angle_2 == AOIConstants[1]
    """
    c1 = 4 / (3 * pi)
    loss_factor = 1 - exp(
        -(
            c1 * angular_loss_coefficient
            + solar_incidence_angle_1 * angular_loss_coefficient ** 2
        )
        / solar_incidence_angle_2
    )
        
    return loss_factor
