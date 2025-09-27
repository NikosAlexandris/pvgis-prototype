from typing import Annotated
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_fingerprint,
    fastapi_query_quick_response_code,
    fastapi_query_csv,
)


async def process_fingerprint(
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    fingerprint: Annotated[bool, fastapi_query_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    csv: Annotated[str | None, fastapi_query_csv] = None,
) -> bool:
    if quick_response_code.value != QuickResponseCode.NoneValue or csv:
        fingerprint = True

    return fingerprint
