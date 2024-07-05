from enum import Enum


class DirectIrradianceComponents(str, Enum):
    normal = "normal"
    on_horizontal_surface = "horizontal"
    on_inclined_surface = "inclined"


class MethodForInexactMatches(str, Enum):
    none = None  # only exact matches
    pad = "pad"  # ffill: propagate last valid index value forward
    backfill = "backfill"  # bfill: propagate next valid index value backward
    nearest = "nearest"  # use nearest valid index value


class SolarPanelTechnology(str, Enum):
    none = None
    cSi = "cSi"
    old_cSi = "Old cSi"
    CIS = "CIS"
    CdTe = "CdTe"


class ModuleTemperatureAlgorithm(str, Enum):
    none = None
    faiman = "Faiman"
