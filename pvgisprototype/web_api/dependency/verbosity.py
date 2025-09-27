from typing import Annotated
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.constants import (
    QUIET_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_analysis,
    fastapi_query_quick_response_code,
    fastapi_query_quiet,
    fastapi_query_verbose,
)
from pvgisprototype.web_api.schemas import (
    AnalysisLevel,
)


async def process_verbose_for_performance_analysis(
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    analysis: Annotated[AnalysisLevel, fastapi_query_analysis] = AnalysisLevel.Simple,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
):
    """ """
    if analysis.value != AnalysisLevel.NoneValue:
        if verbose < 7:
            verbose = 9

    return await process_verbose(
        verbose=verbose, quick_response_code=quick_response_code
    )


async def process_verbose(
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
) -> int:
    """ """
    if quick_response_code.value != QuickResponseCode.NoneValue:
        verbose = 9

    return verbose


async def process_quiet_for_performance_analysis(
    quiet: Annotated[bool, fastapi_query_quiet] = QUIET_FLAG_DEFAULT,
    analysis: Annotated[AnalysisLevel, fastapi_query_analysis] = AnalysisLevel.Simple,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
) -> bool:
    """ """
    if analysis.value != AnalysisLevel.NoneValue:
        quiet = True

    return await process_quiet(quiet=quiet, quick_response_code=quick_response_code)


async def process_quiet(
    quiet: Annotated[bool, fastapi_query_quiet] = QUIET_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
) -> bool:
    """ """
    if quick_response_code.value != QuickResponseCode.NoneValue:
        quiet = True

    return quiet
