from enum import Enum


class DirectIrradianceComponents(str, Enum):
    normal = 'normal'
    on_horizontal_surface = 'horizontal'
    on_inclined_surface = 'inclined'


class MethodsForInexactMatches(str, Enum):
    none = None # only exact matches
    pad = 'pad' # ffill: propagate last valid index value forward
    backfill = 'backfill' # bfill: propagate next valid index value backward
    nearest = 'nearest' # use nearest valid index value


class PVModuleEfficiencyAlgorithms(str, Enum):
    none = None
    linear = 'Linear'
    faiman = 'Faiman'
