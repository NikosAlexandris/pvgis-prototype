import numpy as np

import typer
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from rich import print
# from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.constants import SOLAR_CONSTANT 
from pvgisprototype.constants import AU
from pvgisprototype.constants import STEPHAN_BOLTZMANN_CONSTANT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from rich.table import Table
from rich import box
from rich.console import Console
import numpy as np
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint


# ------------------------------------------------------------------ FixMe ---
LOWER_PHYSICALLY_POSSIBLE_LIMIT = -4
UPPER_PHYSICALLY_POSSIBLE_LIMIT = 2000  # Update-Me
# See : https://bsrn.awi.de/fileadmin/user_upload/bsrn.awi.de/Publications/BSRN_recommended_QC_tests_V2.pdf
# --- FixMe --- Use stuff below... ! -----------------------------------------

PHYSICALLY_POSSIBLE_LIMITS = {
    "Global SWdn": {
        "Min": -4,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 1.5 * mu0**1.2
        + 100,
    },
    "Global SW dn": {
        "Min": -4,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 1.5 * mu0**1.2
        + 100,
    },
    "Diffuse SW": {
        "Min": -4,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 0.95 * mu0**1.2
        + 50,
    },
    "Direct Normal SW": {
        "Min": -4,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance,
    },
    "Direct SW": {
        "Min": -4,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * mu0,
    },
    "SWup": {
        "Min": -4,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 1.2 * mu0**1.2
        + 50,
    },
    "LWdn": {"Min": 40, "Max": 700},
    "LWup": {"Min": 40, "Max": 900},
}
EXTREMELY_RARE_LIMITS = {
    "Global SWdn": {
        "Min": -2,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 1.2 * mu0**1.2
        + 50,
    },
    "Global SWdn": {
        "Min": -2,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 1.2 * mu0**1.2
        + 50,
    },
    "Diffuse SW": {
        "Min": -2,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 0.75 * mu0**1.2
        + 30,
    },
    "Direct Normal SW": {
        "Min": -2,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 0.95 * mu0**0.2
        + 10,
    },
    "SWup": {
        "Min": -2,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * mu0**1.2 + 50,
    },
    "LWdn": {"Min": 60, "Max": 500},
    "LWup": {"Min": 60, "Max": 700},
}


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    help=f"Calculate physically possible irradiance limits",
)


def round_float_values(obj, rounding_places=3):
    if isinstance(obj, float):
        return round(obj, rounding_places)
    elif isinstance(obj, list):
        return [round_float_values(x, rounding_places) for x in obj]
    elif isinstance(obj, dict):
        return {key: round_float_values(value, rounding_places) for key, value in obj.items()}
    elif isinstance(obj, np.ndarray):
        return np.around(obj, roundings=rounding_places)
    else:
        return obj


def print_limits_table(
    limits_dictionary,
    rounding_places=ROUNDING_PLACES_DEFAULT,
):
    limits_dictionary = round_float_values(limits_dictionary, rounding_places)
    console = Console()
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("Component")
    table.add_column("Min", justify="right")
    table.add_column("Max", justify="right")

    for component, limits in limits_dictionary.items():
        table.add_row(component, str(limits["Min"]), str(limits["Max"]))

    console.print(table)


@log_function_call
def calculate_limits(
    solar_zenith: float,
    air_temperature: float,
    limits_dictionary: dict,
):
    """Calculate physically possible and extremely rare limits

    Sum SW = [Diffuse SW + (Direct Normal SW) X µ0]
    Global SWdn: SW measured by unshaded pyranometer
    Diffuse SW: SW measured by shaded pyranometer
    Direct Normal SW: direct normal component of SW
    Direct SW: direct normal SW times the cosine of SZA; [(Direct Normal SW) x µ0]
    LWdn: downwelling LW measured by a pyrgeometer
    LWup: upwelling LW measured by a pyrgeometer

    Notes
    -----
    BSRN Global Network recommended QC tests, V2.0, C. N. Long and E. G. Dutton 
    See : https://bsrn.awi.de/fileadmin/user_upload/bsrn.awi.de/Publications/BSRN_recommended_QC_tests_V2.pdf
    """
    if not (170 < air_temperature < 350):
        raise ValueError("Air temperature must range in [170, 350] K")
    mu0 = np.array(np.cos(np.radians(solar_zenith)))
    mu0[solar_zenith > 90] = 0.0  # Set to 0 if solar_zenith > 90 degrees
    earth_sun_distance = SOLAR_CONSTANT / (AU**2)
    calculated_limits = {}
    for key, value in limits_dictionary.items():
        calculated_limits[key] = {"Min": value["Min"]}
        if callable(value["Max"]):
            calculated_limits[key]["Max"] = value["Max"](earth_sun_distance, mu0)
        else:
            calculated_limits[key]["Max"] = value["Max"]

    log_data_fingerprint(
            calculated_limits,
            verbosity_level = 7,
            hash_after_this_verbosity_level = HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    return calculated_limits


@app.command(
    'physical',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
def calculate_physical_limits(
    solar_zenith: float,
    air_temperature: float = 300,
    rounding_places: int = 5,
):
    """Calculate physically possible limits."""
    limits = calculate_limits(solar_zenith, air_temperature, PHYSICALLY_POSSIBLE_LIMITS)
    print_limits_table(limits_dictionary=limits, rounding_places=rounding_places)
    return limits


@app.command(
    'rare',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
def calculate_rare_limits(
    solar_zenith: float,
    air_temperature: float = 300,
    rounding_places: int = 5,
):
    """Calculate extremely rare limits."""
    limits = calculate_limits(solar_zenith, air_temperature, EXTREMELY_RARE_LIMITS)
    print_limits_table(limits_dictionary=limits, rounding_places=rounding_places)
    return limits
