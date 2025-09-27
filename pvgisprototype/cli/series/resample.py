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
def resample(
    indexer: str | None = None,  # The offset string or object representing target conversion.
    # or : Mapping from a date-time dimension to resample frequency [1]
):
    """Time-based groupby of solar radiation and PV output power time series over a location.

    For example:
    - solar radiation on horizontal and inclined planes
    - Direct Normal Irradiation (DNI) and more in various
    - the daily variation in the clear-sky radiation

    - hourly
    - daily
    - monthly

    Parameters
    ----------
    indexer: str
    """
    pass



