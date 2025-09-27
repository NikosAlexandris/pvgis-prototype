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

MINIMUM_SPECTRAL_MISMATCH = 1.0e20
SCALING_FACTOR = 150.0
INVERSE_SCALE = 1 / SCALING_FACTOR
STANDARD_CONDITIONS_EFFECTIVE_IRRADIANCE = 975.99
STANDARD_CONDITIONS_EFFECTIVE_IRRADIANCE_DNI = 874.8
ELECTRON_CHARGE = 1.602e-19
PHOTON_ENERGIES = np.array(
    [
        6.26034705700271e-19,
        5.75554472228137e-19,
        5.15959917732287e-19,
        4.62208115276972e-19,
        4.09692157015343e-19,
        3.75623190997145e-19,
        3.64619251701414e-19,
        3.55961953815841e-19,
        3.39099638659833e-19,
        3.2299929809257e-19,
        3.07570749132043e-19,
        2.94096977413105e-19,
        2.8610233184015e-19,
        2.74548800710585e-19,
        2.58973475289527e-19,
        2.42851270865034e-19,
        2.29192753696064e-19,
        2.13152128496671e-19,
        1.96615496404041e-19,
        1.77365972594739e-19,
        1.46594666160119e-19,
        1.26953772817109e-19,
        1.11029203366421e-19,
        9.64701443458792e-20,
    ]
)

BAND_LIMITS = np.array(
    [
        306.8408,
        327.7722,
        362.5000,
        407.5000,
        452.0458,
        517.6806,
        540.0000,
        549.5000,
        566.6000,
        605.0000,
        625.0000,
        666.7000,
        684.1772,
        704.4486,
        742.6139,
        791.4788,
        844.4581,
        888.9693,
        974.9063,
        1045.7440,
        1194.1880,
        1515.9400,
        1613.4510,
        1964.7980,
        2153.4640,
    ]
)

EXTRATERRESTRIAL_NORMAL_IRRADIANCE = np.array(
    [
        15.281005,
        34.00431,
        54.97951,
        7.92e001,
        1.29e002,
        4.11e001,
        1.67e001,
        3.32e001,
        6.85e001,
        3.41e001,
        6.69e001,
        2.56e001,
        2.89e001,
        5.11e001,
        6.03e001,
        5.78e001,
        4.35e001,
        7.36e001,
        5.13e001,
        8.52e001,
        1.22e002,
        2.56e001,
        61.61056,
        19.78135,
        9.56295,
        31.47585,
        11.32165,
        3.71585,
    ]
)
