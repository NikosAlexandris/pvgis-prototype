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
from pydantic import ValidationError

from .cases_equation_of_time import cases
from .cases_equation_of_time import cases_ids

cases_equation_of_time_noaa = cases

cases_equation_of_time_noaa_ids = cases_ids

# INPUT NOT OK

string_datetime = "2020-01-01:12:00:00"
random_number = 34.223424252423
cases_equation_of_time_noaa_invalid = [
    ({"timestamps": string_datetime}, ValidationError),
    ({"timestamps": random_number}, ValidationError),
]

cases_equation_of_time_noaa_invalid_ids = [
    f"Timestamp from string: {string_datetime}->{ValidationError}",
    f"Timestamp from random number: {random_number:.2f}->{ValidationError}",
]