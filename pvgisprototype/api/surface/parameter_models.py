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
    Tilt_and_Orientation = "Orientation & Tilt"
    NoneValue = "None"

class SurfacePositionOptimizerModeWithoutNone(str, Enum):
    Orientation = "Orientation"
    Tilt = "Tilt"
    Tilt_and_Orientation = "Orientation & Tilt"
