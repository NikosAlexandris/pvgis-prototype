from datetime import datetime
from datetime import timezone
from pydantic import BaseModel
from pydantic import validator
from typing import Optional
from zoneinfo import ZoneInfo


class BaseTimeInputModel(BaseModel):
    timestamp: datetime
    timezone: Optional[ZoneInfo]

    class Config:
        arbitrary_types_allowed = True

    @validator('timezone')
    def validate_timezone(cls, v):
        if v is not None and not isinstance(v, ZoneInfo):
            raise ValueError("The `timezone` must be a valid `zoneinfo.ZoneInfo` object.")
        return v


class BaseTimeOutputUnitsModel(BaseModel):
    output_units: Optional[str]

    @validator('output_units')
    def validate_output_units(cls, v):
        valid_units = ['minutes', 'seconds', 'hours']
        if v not in valid_units:
            raise ValueError(f"output_units must be one of {valid_units}")
        return v
