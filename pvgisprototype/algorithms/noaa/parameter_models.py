#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from math import pi
from typing import List, Optional

import numpy as np
from pydantic import BaseModel, confloat, field_validator

from pvgisprototype import SolarZenith
from pvgisprototype.constants import DEGREES, RADIANS
from pvgisprototype.api.position.models import SolarEvent


class BaseTimeEventModel(BaseModel):
    event: List[Optional[SolarEvent]] = [None]

    @field_validator("event")
    @classmethod
    def validate_event(cls, v):
        if v is not None:
            if not all(isinstance(event, SolarEvent) or event is None for event in v):
                raise ValueError(f"All items in `event` must be instances of {list(SolarEvent)} or None")
        return v


class BaseTimeOutputUnitsModel(BaseModel):
    time_output_units: str | None = None

    @field_validator("time_output_units")
    @classmethod
    def validate_time_output_units(cls, v):
        valid_units = ["minutes", "seconds", "hours"]
        if v not in valid_units:
            raise ValueError(f"time_output_units must be one of {valid_units}")
        return v


class BaseAngleUnitsModel(BaseModel):
    angle_units: str

    @field_validator("angle_units")
    @classmethod
    def validate_angle_units(cls, v):
        valid_units = [RADIANS, DEGREES]
        if v not in valid_units:
            raise ValueError(f"angle_units must be one of {valid_units}")
        return v


class BaseAngleOutputUnitsModel(BaseModel):
    angle_output_units: str | None = RADIANS

    @field_validator("angle_output_units")
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = [RADIANS, DEGREES]
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v


class AngleInRadiansOutputUnitsModel(BaseModel):
    """
    The angle in radians output units argument is passed along with the
    returned value. This is not a real test. Hopefully, and however, it helps
    for clarity and understanding of what the function should return.
    """

    angle_output_units: str = RADIANS

    @field_validator("angle_output_units")
    @classmethod
    def validate_angle_output_units(cls, v):
        valid_units = [RADIANS]
        if v not in valid_units:
            raise ValueError(f"angle_output_units must be one of {valid_units}")
        return v


class SolarZenithModel(BaseModel):
    solar_zenith: confloat(ge=0, le=pi + 0.01745) | List[confloat(ge=0, le=pi + 0.01745)] | SolarZenith


class SolarZenithSeriesModel(BaseModel):  # merge above here-in
    solar_zenith_series: SolarZenith

    @field_validator("solar_zenith_series")
    def solar_zenith_range(cls, v):
        if not np.all(
            (0 <= v.radians) & (v.radians <= np.pi)
        ):  # Adjust the condition to work with an array
            raise ValueError("The solar zenith angle must be between 0 and pi radians.")
        return v
