from typing import Dict, List, Callable, Sequence, Type
from enum import Enum
from pvgisprototype.api.tmy.plot import plot_tmy
from pvgisprototype.api.tmy.plot import (
    plot_long_term_monthly_ecdfs,
    # plot_yearly_monthly_ecdfs_with_seaborn,
)
from pvgisprototype.api.tmy.plot import plot_ranked_finkelstein_schafer_statistic
from pvgisprototype.api.tmy.plot import plot_finkelstein_schafer_statistic
from pvgisprototype.api.tmy.plot import plot_long_term_monthly_ecdfs
from pvgisprototype.api.tmy.plot import plot_yearly_monthly_ecdfs
from pvgisprototype.algorithms.tmy.weighting_scheme_model import MeteorologicalVariable

YEARLY_MONTHLY_ECDFs_COLUMN_NAME = 'Yearly-Monthly-ECDFs'
LONG_TERM_MONTHLY_ECDFs_COLUMN_NAME = 'Long-term-Monthly-ECDFs'
UNALIGNED_LONG_TERM_MONTHLY_ECDFs_COLUMN_NAME = 'Unaligned-Long-term-Monthly-ECDFs'


class EmpiricalCumulativeDistributionFunction(str, Enum):
    all = "all"
    yearly_ecdf = YEARLY_MONTHLY_ECDFs_COLUMN_NAME
    long_term_ecdf = LONG_TERM_MONTHLY_ECDFs_COLUMN_NAME


class FinkelsteinSchaferStatisticModel(str, Enum):
    all = "all"
    ranked = "Ranked"
    weighted = "Weighted"
    # weights = "Weights"
    # weighting = "Weighting scheme"
    # weightor = "Weighting variable"
    finkelsteinschafer = "Finkelstein-Schafer"


def create_combined_enum(name, bases, additional_members=None):
    """
    Create a combined Enum from multiple bases and add any additional members.
    
    Parameters:
    - name: The name of the enum to create.
    - bases: Tuple of base enums to combine.
    - additional_members: Dict of additional members to add to the combined enum.
    
    Returns:
    - Enum: The newly created enum with combined members.
    """
    combined_members = {**bases[0].__members__, **bases[1].__members__}
    
    # If we have additional members, we add them to the combined members
    if additional_members:
        combined_members.update(additional_members)
    
    return Enum(name, combined_members)


# Create the combined enum dynamically
TMYStatisticModel = create_combined_enum(
    "TMYStatisticModel", 
    (EmpiricalCumulativeDistributionFunction, FinkelsteinSchaferStatisticModel), 
    additional_members={"tmy": "TMY"}
)


def select_tmy_models(
    enum_type: Type[TMYStatisticModel],
    models: List[TMYStatisticModel],
) -> Sequence[TMYStatisticModel]:
    """Select models from an enum list."""
    if enum_type.all in models:
        return [model for model in enum_type if model != enum_type.all]
    # return list(models)
    # return models
    return [enum_type(model) for model in models]


def select_meteorological_variables(
    enum_type: Type[MeteorologicalVariable],
    meteorological_variables: List[MeteorologicalVariable],
) -> Sequence[MeteorologicalVariable]:
    """Select models from an enum list."""
    if enum_type.all in meteorological_variables:
        return [variable for variable in enum_type if variable != enum_type.all]
    return [enum_type(variable) for variable in meteorological_variables]


PLOT_FUNCTIONS: Dict[TMYStatisticModel, Callable] = {
    TMYStatisticModel.tmy: plot_tmy,
    FinkelsteinSchaferStatisticModel.ranked: plot_ranked_finkelstein_schafer_statistic,
    FinkelsteinSchaferStatisticModel.weighted: plot_finkelstein_schafer_statistic,
    FinkelsteinSchaferStatisticModel.finkelsteinschafer: plot_finkelstein_schafer_statistic,
    EmpiricalCumulativeDistributionFunction.long_term_ecdf: plot_long_term_monthly_ecdfs,
    EmpiricalCumulativeDistributionFunction.yearly_ecdf: plot_yearly_monthly_ecdfs,
}
