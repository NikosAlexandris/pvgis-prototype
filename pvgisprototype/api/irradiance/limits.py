#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import numpy as np

from pvgisprototype.constants import (
    AU,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call

# ------------------------------------------------------------------ FixMe ---
LOWER_PHYSICALLY_POSSIBLE_LIMIT = -4
UPPER_PHYSICALLY_POSSIBLE_LIMIT = 2000  # Update-Me
# See : https://bsrn.awi.de/fileadmin/user_upload/bsrn.awi.de/Publications/BSRN_recommended_QC_tests_V2.pdf
# --- FixMe --- Use stuff below... ! -----------------------------------------

PHYSICALLY_POSSIBLE_LIMITS = {
    "Global SWdn": {
        "Min": LOWER_PHYSICALLY_POSSIBLE_LIMIT,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 1.5 * mu0**1.2
        + 100,
    },
    "Global SW dn": {
        "Min": LOWER_PHYSICALLY_POSSIBLE_LIMIT,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 1.5 * mu0**1.2
        + 100,
    },
    "Diffuse SW": {
        "Min": LOWER_PHYSICALLY_POSSIBLE_LIMIT,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 0.95 * mu0**1.2
        + 50,
    },
    "Direct Normal SW": {
        "Min": LOWER_PHYSICALLY_POSSIBLE_LIMIT,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance,
    },
    "Direct SW": {
        "Min": LOWER_PHYSICALLY_POSSIBLE_LIMIT,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * mu0,
    },
    "SWup": {
        "Min": LOWER_PHYSICALLY_POSSIBLE_LIMIT,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 1.2 * mu0**1.2 + 50,
    },
    "LWdn": {"Min": 40, "Max": 700},
    "LWup": {"Min": 40, "Max": 900},
}
EXTREMELY_RARE_LIMITS = {
    "Global SWdn": {
        "Min": -2,
        "Max": lambda earth_sun_distance, mu0: earth_sun_distance * 1.2 * mu0**1.2 + 50,
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


@log_function_call
def calculate_limits(
    solar_zenith: float,
    air_temperature: float,
    limits_dictionary: dict,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = VERBOSE_LEVEL_DEFAULT,
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
        data=calculated_limits,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return calculated_limits
