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
from .cases_solar_azimuth import cases, cases_ids
from .cases_solar_azimuth_usno import cases as cases_usno
from .cases_solar_azimuth_usno import cases_ids as cases_usno_ids
from .cases_solar_azimuth_noaa_pvlib import cases as cases_pvlib
from .cases_solar_azimuth_noaa_pvlib import cases_ids as cases_pvlib_ids

cases_solar_azimuth_noaa = cases
cases_solar_azimuth_noaa_ids = cases_ids

cases_solar_azimuth_noaa_usno = cases_usno
cases_solar_azimuth_noaa_usno_ids = cases_usno_ids

cases_solar_azimuth_noaa_pvlib = cases_pvlib
cases_solar_azimuth_noaa_pvlib_ids = cases_pvlib_ids