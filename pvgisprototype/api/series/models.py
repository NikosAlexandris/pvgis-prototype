from enum import Enum


class MethodForInexactMatches(str, Enum):
    none = None  # only exact matches
    pad = "pad"  # ffill: propagate last valid index value forward
    backfill = "backfill"  # bfill: propagate next valid index value backward
    nearest = "nearest"  # use nearest valid index value
