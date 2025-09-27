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
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
)
from pvgisprototype.api.conventions import ORIENATION_CONVENTIONS_AND_CONVERSIONS


A_PRIMER_ON_PHOTOVOLTAIC_PERFORMANCE = f"""
A key metric for evaluating the overall performance of a photovoltaic (PV)
system is the cumulative [yellow]Energy[/yellow] produced over a time period
(e.g., daily, monthly, or annually). In other words, energy production is an
aggregate of the [italic]instantaneous[/italic] power estimations over a time series.

Instantaneous power values reflect the [italic]current[/italic] output of the PV
system at each moment in time, which in turn depends on the effective irradiance.

[bold]How does PVGIS calculate photovoltaic power output ?[/bold]

First, it calculates [italic]the position of the sun[/italic] relative to the
solar surface over the user requested period of time. This boils down to one
key trigonometric parameter : the [cyan]solar incidence[/cyan] angle. The
incidence angle depends on the [cyan]solar altitude[/cyan] and
[cyan]azimuth[/cyan] angles at any given time, combined with the
[cyan]location[/cyan], [cyan]orientation[/cyan], and [cyan]tilt[/cyan] of the
solar surface.

Important consideration is the various conventions or angular measurements of
orientation. PVGIS 6 follows the North-Up = 0 deg definition. See also the
following diagram :

    {ORIENATION_CONVENTIONS_AND_CONVERSIONS}

Second and based on the incidence angle, it estimates the [cyan]direct[/cyan]
and [cyan]diffuse[/cyan] [yellow]irradiance[/yellow] components.
Following is a step by step analysis of the calculations.

### Step by Step

Analytically the algorithm performs the following steps :

1. Define an arbitrary period of time

   The user selects a time period over which the energy production will be
   evaluated.

2. Calculate the [cyan]solar altitude[/cyan] angle series
   
   - The solar altitude angle is the elevation of the sun above the horizon.

   - The default algorithm for solar time is
     [code]solar_time_model[/code] is set to [code]{SOLAR_TIME_ALGORITHM_DEFAULT}[/code]
     (see: [code]pvgisprototype.constants.SOLAR_TIME_ALGORITHM_DEFAULT[/code]).
     This calculates the apparent solar time based on the Equation of Time (Milne, 1921).

   - The default solar positioning algorithm is
     [code]solar_position_model[/code] is set to [code]{SOLAR_POSITION_ALGORITHM_DEFAULT}[/code]
     (see: [code]pvgisprototype.constants.SOLAR_POSITION_ALGORITHM_DEFAULT[/code]).

   - The default model to calculate the solar incidence angle is
     [code]solar_incidence_model[/code] is set to [code]{SolarIncidenceModel.iqbal}[/code]
     (see: [code]SolarIncidenceModel.iqbal[/code]).

3. Calculate the [cyan]solar azimuth[/cyan] angle series
   
   - The solar azimuth is the compass direction from which the sunlight is
     coming, calculated using the NOAA solar position algorithm.

4. Derive masks for solar position
   
   - Create masks for different solar positions

     i. Above the horizon and not in shade.
     ii. Low sun angles (for example, near sunrise or sunset).
     iii. Below the horizon (nighttime).

5. Calculate the direct horizontal irradiance component
   
   - Compute the direct irradiance component that reaches the PV surface from
     the sun without scattering.

6. Calculate the diffuse and ground-reflected irradiance components
   
   - For times when the sun is above the horizon, calculate the diffuse
     irradiance (scattered light) and reflected irradiance (from nearby
     surfaces).

7. Sum the individual irradiance components
   
   - Combine the direct, diffuse, and reflected components to derive the global
     inclined irradiance on the solar panel.

8. Read time series of ambient conditions
   
   - Input data such as ambient temperature, wind speed, and spectral factors
     are read from time series, which affect panel performance.

9. Derive the conversion efficiency coefficients
   
   - Conversion efficiency is calculated based on the temperature, wind speed,
     and other factors influencing the PV panel's ability to convert irradiance
     into power.

10. Estimate the photovoltaic power output
   
   - Photovoltaic power is estimated as the product of the global inclined
     irradiance and the conversion efficiency coefficients. This gives the
     instantaneous power output, which is then integrated over time to
     calculate the total energy produced.
"""

