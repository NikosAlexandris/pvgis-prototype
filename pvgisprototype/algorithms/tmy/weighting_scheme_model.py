# Variables weight for the FS statistics under each methodology

# | Index of daily values         | ISO 15927-4_2005 | Sandia Method | NSRDB TMY |
# |-------------------------------+------------------+---------------+-----------|
# | Maximum Dry Bulb Temperature  | 0                | 1/24          | 1/20      |
# | Minimum Dry Bulb Temperature  | 0                | 1/24          | 1/20      |
# | Mean Dry Bulb Temperature     | 1                | 2/24          | 2/20      |
# | Maximum Dew Point Temperature | 0                | 1/24          | 1/20      |
# | Minimum Dew Point Temperature | 0                | 1/24          | 1/20      |
# | Mean Dew Point Temperature    | 0                | 2/24          | 2/20      |
# | Maximum Wind Velocity         | 0                | 2/24          | 1/20      |
# | Mean Wind Velocity            | 0*               | 2/24          | 1/20      |
# | Mean Relative Humidity        | 1                | 0             | 0         |
# | Global horizontal irradiance  | 1                | 12/24         | 5/20      |
# | Direct normal irradiance      | 0                | 0             | 5/20      |


# iso_15927_4 = "ISO 15927-4_2005"
# sandia = "Sandia Method"
# nsrdb = "NSRDB TMY"

from enum import Enum
from typing import Dict


class MeteorologicalVariable(str, Enum):
    all = "All"
    MAX_DRY_BULB_TEMPERATURE = "Maximum Dry Bulb Temperature"
    MIN_DRY_BULB_TEMPERATURE = "Minimum Dry Bulb Temperature"
    MEAN_DRY_BULB_TEMPERATURE = "Mean Dry Bulb Temperature"
    MAX_DEW_POINT_TEMPERATURE = "Maximum Dew Point Temperature"
    MIN_DEW_POINT_TEMPERATURE = "Minimum Dew Point Temperature"
    MEAN_DEW_POINT_TEMPERATURE = "Mean Dew Point Temperature"
    MAX_WIND_SPEED = "Maximum Wind Velocity"
    MEAN_WIND_SPEED = "Mean Wind Velocity"
    MEAN_RELATIVE_HUMIDITY = "Mean Relative Humidity"
    GLOBAL_HORIZONTAL_IRRADIANCE = "Global Horizontal Irradiance"
    DIRECT_NORMAL_IRRADIANCE = "Direct Normal Irradiance"


class TypicalMeteorologicalMonthWeightingScheme(Enum):
    all = "All"
    ISO_15927_4 = "ISO-15927-4"
    SANDIA = "Sandia"
    NSRDB = "NSRDB"
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


WEIGHTING_SCHEMES: Dict[
    TypicalMeteorologicalMonthWeightingScheme, Dict[MeteorologicalVariable, float]
] = {
    TypicalMeteorologicalMonthWeightingScheme.ISO_15927_4: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 0,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 0,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 1,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: 0,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: 0,
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: 0,
        MeteorologicalVariable.MAX_WIND_SPEED: 0,
        MeteorologicalVariable.MEAN_WIND_SPEED: 0,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: 1,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 1,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 0,
    },
    TypicalMeteorologicalMonthWeightingScheme.SANDIA: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 2 / 24,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: 2 / 24,
        MeteorologicalVariable.MAX_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.MEAN_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: 0,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 12 / 24,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 0,
    },
    TypicalMeteorologicalMonthWeightingScheme.NSRDB: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 2 / 20,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: 2 / 20,
        MeteorologicalVariable.MAX_WIND_SPEED: 1 / 20,
        MeteorologicalVariable.MEAN_WIND_SPEED: 1 / 20,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: 0,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 5 / 20,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 5 / 20,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_24_32: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 2 / 24,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: 2 / 24,
        MeteorologicalVariable.MAX_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.MEAN_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 12 / 24,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_18: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 5 / 100,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 5 / 100,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 30 / 100,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: 2.5 / 100,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: 2.5 / 100,
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: 5 / 100,
        MeteorologicalVariable.MAX_WIND_SPEED: 5 / 100,
        MeteorologicalVariable.MEAN_WIND_SPEED: 5 / 100,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 40 / 100,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_33: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MAX_WIND_SPEED: 1 / 24,
        MeteorologicalVariable.MEAN_WIND_SPEED: 1 / 24,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 12 / 24,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 5 / 20,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_16_17: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 2 / 20,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: 2 / 20,
        MeteorologicalVariable.MAX_WIND_SPEED: 1 / 20,
        MeteorologicalVariable.MEAN_WIND_SPEED: 1 / 20,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 5 / 20,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 8 / 32,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_34: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 10,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 10,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 2 / 10,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: 1 / 10,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: 1 / 10,
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: 2 / 10,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: None,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 8 / 32,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_35: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 32,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 32,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 2 / 32,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: 1 / 32,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: 1 / 32,
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: 2 / 32,
        MeteorologicalVariable.MAX_WIND_SPEED: 1 / 32,
        MeteorologicalVariable.MEAN_WIND_SPEED: 2 / 32,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 8 / 32,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 8 / 32,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_36: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 3 / 24,
        MeteorologicalVariable.MAX_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.MEAN_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 12 / 24,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_37e39: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 2 / 24,
        MeteorologicalVariable.MAX_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.MEAN_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: None,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_40: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 22,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 22,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 1 / 22,
        MeteorologicalVariable.MAX_WIND_SPEED: 1 / 22,
        MeteorologicalVariable.MEAN_WIND_SPEED: 1 / 22,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 11 / 22,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 12 / 24,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_41: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 3 / 20,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: 2 / 20,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 5 / 20,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 5 / 20,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_42: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: 1 / 24,
        MeteorologicalVariable.MAX_WIND_SPEED: 11 / 24,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 11 / 24,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_43: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 20,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 6 / 20,
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: 4 / 24,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: 1 / 20,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 8 / 20,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_44_45: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 2 / 24,
        MeteorologicalVariable.MAX_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.MEAN_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 12 / 24,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_46: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 100,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 2 / 100,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 1 / 100,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: 2 / 100,
        MeteorologicalVariable.MAX_WIND_SPEED: 4 / 100,
        MeteorologicalVariable.MEAN_WIND_SPEED: 2 / 100,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 85 / 100,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_47: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 24,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 3 / 24,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: 2 / 24,
        MeteorologicalVariable.MAX_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.MEAN_WIND_SPEED: 2 / 24,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 12 / 24,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 8 / 32,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_48: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 2 / 16,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 16,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 1 / 16,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: None,
        MeteorologicalVariable.MEAN_WIND_SPEED: 1 / 16,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 8 / 16,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_49: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 1 / 32,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 1 / 32,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 2 / 32,
        MeteorologicalVariable.MAX_WIND_SPEED: 1 / 32,
        MeteorologicalVariable.MEAN_WIND_SPEED: 2 / 32,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 8 / 32,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: 8 / 32,
    },
    TypicalMeteorologicalMonthWeightingScheme.REF_50: {
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: 5 / 100,
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: 5 / 100,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: 30 / 100,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: 10 / 100,
        MeteorologicalVariable.MAX_WIND_SPEED: 5 / 100,
        MeteorologicalVariable.MEAN_WIND_SPEED: 5 / 100,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: 40 / 100,
    },
}


def get_typical_meteorological_month_weighting_scheme(
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme,
    meteorological_variable: MeteorologicalVariable | None = None,
) -> float | str:
    """Retrieve the specific weight or full scheme for a variable under a meteorological month weighting scheme."""    
    if weighting_scheme == TypicalMeteorologicalMonthWeightingScheme.all:
        output = []
        for scheme_name, scheme_weights in WEIGHTING_SCHEMES.items():
            if meteorological_variable:
                weight = scheme_weights.get(meteorological_variable)
                output.append(
                    f"{scheme_name.value}: {weight if weight is not None else f'No weight for {meteorological_variable.name}'}"
                )
            else:
                output.append(f"{scheme_name}: {scheme_weights}")
        return "\n".join(output)

    scheme_weights = WEIGHTING_SCHEMES.get(weighting_scheme)

    if not scheme_weights:
        raise ValueError(f"No weighting scheme available for {weighting_scheme.name}")

    if meteorological_variable:
        weight = scheme_weights.get(meteorological_variable)
        if weight is None:
            raise ValueError(f"No weight defined for '{meteorological_variable.name}' in scheme {weighting_scheme.name}.")
        return weight
    
    return scheme_weights  # Return the full scheme if no specific variable is requested


TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT = (
    TypicalMeteorologicalMonthWeightingScheme.ISO_15927_4.value
)
