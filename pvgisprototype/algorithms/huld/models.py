from enum import Enum


class PhotovoltaicModulePerformanceModel(str, Enum):
    none = None
    iv = "IV"
    king = "Huld 2011"
