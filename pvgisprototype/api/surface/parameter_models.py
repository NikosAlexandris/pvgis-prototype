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
from enum import Enum


class SurfacePositionOptimizerMethod(str, Enum):
    brute = "Brute"
    shgo = "SHGO"
    cg = "CG"
    powell = "Powell"
    nelder_mead = "Nelder-Mead"  # Not working properly right now
    bfgs = "BFGS"  # Not working properly right now
    l_bfgs_b = "L-BFGS-B"  # Not working properly right now
    direct = "DIRECT"


class SurfacePositionOptimizerMethodSHGOSamplingMethod(str, Enum):
    halton = "halton"
    sobol = "sobol"
    simplicial = "simplicial"


class SurfacePositionOptimizerMode(str, Enum):
    Orientation = "Orientation"
    Tilt = "Tilt"
    Orientation_and_Tilt = "Orientation & Tilt"
    NoneValue = "None"


class SurfacePositionOptimizerModeWithoutNone(str, Enum):
    Orientation = "Orientation"
    Tilt = "Tilt"
    Orientation_and_Tilt = "Orientation & Tilt"


MINIMIZE_METHODS = [
    SurfacePositionOptimizerMethod.bfgs,
    SurfacePositionOptimizerMethod.cg,
    SurfacePositionOptimizerMethod.l_bfgs_b,
]
