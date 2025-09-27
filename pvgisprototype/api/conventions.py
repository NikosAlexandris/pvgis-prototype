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
ORIENATION_CONVENTIONS_AND_CONVERSIONS = """
[bold]Origin of Azimuth[/bold]

Solar azimuth is an important element in solar positioning. PVGIS follows the
[bold]North-Up = 0°[/bold] convention for azimuth angular measurements.

In overview :

- [bold]North-Based System (N=0)[/bold]: Default in PVGIS.
- [bold]East-Based System (E=0)[/bold]: Common in some literature and solar
  positioning models.
- [bold]South-Based System (S=0)[/bold]: Alternative system in specific
  applications.

Below is a visual representation of various azimuth angle conventions and
conversions, i.e. from a North-based system to either East- or South-based
systems :

             ┌─────────────┐  ┌────────────┐  ┌────────────┐
             │     N=0     │  │     N      │  │      N     │
             │      ▲      │  │     ▲      │  │      ▲     │
     Origin  │   W ◄┼► E   │  │  W ◄┼► E=0 │  │   W ◄┼► E  │
             │      ▼      │  │     ▼      │  │      ▼     │
             │      S      │  │     S      │  │     S=0    │
             └─────────────┘  └────────────┘  └────────────┘
             ┌─────────────┐  ┌────────────┐  ┌────────────┐
             │             │  │            │  │            │
             │             │  │            │  │            │
Input South  │     180     │  │     90     │  │     0      │
    (IS)     │             │  │            │  │            │
             │             │  │            │  │            │
             └─────────────┘  └────────────┘  └────────────┘
             ┌─────────────┐  ┌────────────┐  ┌────────────┐
             │             │  │            │  │            │
   Internal  │             │  │            │  │            │
             │      =      │  │  IS - 90   │  │  IS - 180  │
  Conversion │             │  │            │  │            │
             │             │  │            │  │            │
             └─────────────┘  └────────────┘  └────────────┘
"""

UNITS_IN_PVGIS = """
[bold]Units and Conversions[/bold] [yellow]Draft Text[/yellow]

Most angular calculations in PVGIS are performed in
[underline]radians[/underline] for consistency and precision. However, there is
an important exception : the [bold]atmospheric refraction[/bold] adjustments
use degrees.

The relevant API function in PVGIS is
calculate_refracted_solar_altitude_series() which requires input in degrees and
outputs adjusted values in degrees.

The refraction correction formula ensures accurate modeling of the sun's
observed position, especially near the horizon, where the refraction effect is
strongest.

"""

TIME_IN_PVGIS = """
[bold]UTC & Local Time Zones[/bold] [yellow]Draft Text[/yellow]

By default, all calculations in PVGIS are performed in [italics]UTC[/italics].
This ensures consistency across different geographic regions. Nonetheless,
local time support is under review. The goal is to:
    - [bold]translate local timestamps[/bold] to UTC
    - perform calculations
    - and [bold]convert them back[/bold] to local time for final output

[bold]Date & Time[/bold]

PVGIS respects input data timestamps and will then
[underline]filter[/underline] the data based on user-defined parameters such as
`start_time`, `end_time`, and `periods`.

If no data is provided, PVGIS generates a [code]DatetimeIndex[/code] using the
Pandas library and based on at least two or at most three out of the following
parameters :

- `start_time`
- `end_time`
- `frequency` : the default [bold]frequency[/bold] is set to hourly
  ([code]h[/code])
- or/and `periods`

┌─────────────┐  ┌────────────┐  ┌────────────┐
│  Input      │  │  Generated │  │  Filtered  │
│ Timestamps  │  │ Timestamps │  │ Timestamps │
└─────────────┘  └────────────┘  └────────────┘

┌─────────────┐  ┌────────────┐
│ Start Time  │  │  End Time  │
├─────────────┴──┴────────────┤
│     Frequency or Periods    │
└─────────────────────────────┘

"""

PHOTOVOLTAIC_EFFIENCY_COEFFICIENTS = """
[bold]Photovoltaic Efficiency and Spectral Data[/bold] [yellow]Draft Text[/yellow]

PVGIS integrates [bold]photovoltaic efficiency coefficients[/bold] derived from
research in the [bold]ESTI Lab[/bold], part of Unit C2 (JRC, European
Commission) alongside the PVGIS team. These coefficients are critical for
modeling the performance of PV modules under various conditions.

[bold]Concepts[/bold]

- [bold]Spectral Factor[/bold] : The ratio between the nominal reference
  spectrum (used for rating PV panels) and the real solar irradiance spectrum
  at the Earth's surface.

- [bold]Efficiency Curves[/bold] : Based on module types and are used to adjust
  performance predictions across different environmental conditions.

"""

SOLAR_INCIDENCE_ANGLE = """
[bold]Solar Incidence Angle[/bold] [yellow]Draft Text[/yellow]

The default definition of the [bold]solar incidence angle[/bold] in PVGIS
follows the "sun-vector to surface-normal" convention, specifically as modelled
by [italics]Iqbal[/italics].

[bold]Positioning Algorithm[/bold]

PVGIS uses the [bold]NOAA solar geometry equations[/bold] for solar
positioning. The system has undergone extensive testing, including hundreds of
thousands of automated tests to verify its accuracy. Comparisons with data from
the [bold]United States Naval Observatory (USNO)[/bold] further validate the
correctness of the calculated solar angles.

"""

ASSUMPTIONS_FOR_INPUT_DATA_IN_PVGIS = """
[bold]Assumptions for Input Data[/bold] [yellow]Draft Text[/yellow]

Solar irradiance input data must have a consistent [bold]temporal resolution
and extent[/bold]. PVGIS assumes all provided data adhere to these requirements
for accurate modeling.

"""

def generate_pvgis_conventions(docstring=ORIENATION_CONVENTIONS_AND_CONVERSIONS):
    return docstring
