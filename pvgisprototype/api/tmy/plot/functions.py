from typing import Dict, Callable
from pvgisprototype.api.tmy.models import (
    EmpiricalCumulativeDistributionFunction,
    FinkelsteinSchaferStatisticModel,
    TMYStatisticModel,
)
from pvgisprototype.api.tmy.plot.tmy import plot_tmy
from pvgisprototype.api.tmy.plot.finkelstein_schafer import (
    plot_ranked_finkelstein_schafer_statistic,
    plot_finkelstein_schafer_statistic,
)
from pvgisprototype.api.tmy.plot.distribution import (
    plot_long_term_monthly_ecdfs,
    plot_yearly_monthly_ecdfs,
)


PLOT_FUNCTIONS: Dict[TMYStatisticModel, Callable] = {
    TMYStatisticModel.tmy: plot_tmy,
    FinkelsteinSchaferStatisticModel.ranked: plot_ranked_finkelstein_schafer_statistic,
    FinkelsteinSchaferStatisticModel.weighted: plot_finkelstein_schafer_statistic,
    FinkelsteinSchaferStatisticModel.finkelsteinschafer: plot_finkelstein_schafer_statistic,
    EmpiricalCumulativeDistributionFunction.long_term_ecdf: plot_long_term_monthly_ecdfs,
    EmpiricalCumulativeDistributionFunction.yearly_ecdf: plot_yearly_monthly_ecdfs,
}
