ORIENATION_CONVENTIONS_AND_CONVERSIONS = """
[bold]Origin of Azimuth[/bold]

Important part of solar positioning, is the origin of solar azimuth angular
measurements. PVGIS follows the [bold]North-Up[/bold] = 0 deg definition.

See also the following overview diagram of conventions and conversions
from a North-based system to either East- or South-based systems :

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


def generate_pvgis_conventions(docstring=ORIENATION_CONVENTIONS_AND_CONVERSIONS):
    return docstring
