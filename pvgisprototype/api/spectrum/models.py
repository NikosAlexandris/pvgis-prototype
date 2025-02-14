from enum import Enum


class PhotovoltaicModuleSpectralResponsivityModel(str, Enum):
    all = "all"
    cSi = "cSi"
    asi = "aSi"
    monosi = "monoSi"
    polysi = "polySi"
    fs3 = "FS3"
    fs6 = "FS6"
    cigs = "CIGS"


class SpectralMismatchModel(str, Enum):
    all = "all"
    pvlib = "pvlib"
    mihaylov = "Mihaylov"
    pelland = "Pelland"
    huld = "Huld"
