from enum import Enum
from typing import Dict
from pvgisprototype.algorithms.tmy.weighting_schemes import (
    iso_15927_4,
    sandia,
    nsrdb,
    weights_24_32,
    weights_18,
    weights_33,
    weights_16_17,
    weights_34,
    weights_35,
    weights_36,
    weights_37e39,
    weights_40,
    weights_41,
    weights_42,
    weights_43,
    weights_44_45,
    weights_46,
    weights_47,
    weights_48,
    weights_49,
    weights_50,
)


class TypicalMeteorologicalMonthWeightingScheme(Enum):
    ISO_15927_4 = 'ISO-15927-4'
    SANDIA = 'Sandia'
    NSRDB = 'NSRDB'
    REF_24_32 = "[24,32]"
    REF_18 = "[18]"
    REF_33 = "[33]"
    REF_16_17 = "[16,17]"
    REF_34 = "[34]"
    REF_35 = "[35]"
    REF_36 = "[36]"
    REF_37e39 = "[37e39]"
    REF_40 = "[40]"
    REF_41 = "[41]"
    REF_42 = "[42]"
    REF_43 = "[43]"
    REF_44_45 = "[44,45]"
    REF_46 = "[46]"
    REF_47 = "[47]"
    REF_48 = "[48]"
    REF_49 = "[49]"
    REF_50 = "[50]"


WEIGHTING_SCHEMES: Dict[TypicalMeteorologicalMonthWeightingScheme, Dict] = {
    TypicalMeteorologicalMonthWeightingScheme.ISO_15927_4: iso_15927_4,
    TypicalMeteorologicalMonthWeightingScheme.SANDIA: sandia,
    TypicalMeteorologicalMonthWeightingScheme.NSRDB: nsrdb,
    TypicalMeteorologicalMonthWeightingScheme.REF_24_32: weights_24_32,
    TypicalMeteorologicalMonthWeightingScheme.REF_18: weights_18,
    TypicalMeteorologicalMonthWeightingScheme.REF_33: weights_33,
    TypicalMeteorologicalMonthWeightingScheme.REF_16_17: weights_16_17,
    TypicalMeteorologicalMonthWeightingScheme.REF_34: weights_34,
    TypicalMeteorologicalMonthWeightingScheme.REF_35: weights_35,
    TypicalMeteorologicalMonthWeightingScheme.REF_36: weights_36,
    TypicalMeteorologicalMonthWeightingScheme.REF_37e39: weights_37e39,
    TypicalMeteorologicalMonthWeightingScheme.REF_40: weights_40,
    TypicalMeteorologicalMonthWeightingScheme.REF_41: weights_41,
    TypicalMeteorologicalMonthWeightingScheme.REF_42: weights_42,
    TypicalMeteorologicalMonthWeightingScheme.REF_43: weights_43,
    TypicalMeteorologicalMonthWeightingScheme.REF_44_45: weights_44_45,
    TypicalMeteorologicalMonthWeightingScheme.REF_46: weights_46,
    TypicalMeteorologicalMonthWeightingScheme.REF_47: weights_47,
    TypicalMeteorologicalMonthWeightingScheme.REF_48: weights_48,
    TypicalMeteorologicalMonthWeightingScheme.REF_49: weights_49,
    TypicalMeteorologicalMonthWeightingScheme.REF_50: weights_50
}


def get_typical_meteorological_month_weighting_scheme(
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme,
    variable: str,
) -> float:
    """Retrieve the specific weight for a given variable under a chosen meteorological month weighting scheme."""
    scheme_weights = WEIGHTING_SCHEMES.get(weighting_scheme)

    if scheme_weights is None:
        return "No weighting scheme available for this method"
    weight = scheme_weights.get(variable)

    if weight is None:
        return f"No weight defined for the variable '{variable}' under this weighting scheme."

    return weight


TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT = "ISO-15927-4"
