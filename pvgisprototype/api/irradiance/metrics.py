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
irradiance_metrics = {
    "Annual In-plane Irradiation": (
        "H(i)_y",
        "Annual global irradiation on the inclined plane",
        "kWh/m2/y",
    ),
    "Monthly In-plane Irradiation": (
        "H(i)_m",
        "Monthly global irradiation on the inclined plane",
        "kWh/m2/mo",
    ),
    "Daily In-plane Irradiation": (
        "H(i)_d",
        "Daily global irradiation on the inclined plane",
        "kWh/m2/d",
    ),
    "Monthly Optimal In-plane Irradiation": (
        "H(i_opt)_m",
        "Monthly global irradiation on an optimally-inclined plane",
        "kWh/m2/mo",
    ),
    "Monthly Horizontal Irradiation": (
        "H(h)_m",
        "Monthly global irradiation on the horizontal plane",
        "kWh/m2/mo",
    ),
    "Monthly Normal Beam Irradiation": (
        "Hb(n)_m",
        "Monthly beam (direct) irradiation on a plane always normal to sun rays",
        "kWh/m2/mo",
    ),
}
