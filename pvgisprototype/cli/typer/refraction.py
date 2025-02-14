"""
Atmospheric refraction

The calculation of the solar declination angle may not include the effects of
the refraction of light in the atmosphere, which causes the apparent angle of
elevation of the Sun as seen by an observer to be higher than the actual angle
of elevation, especially at low Sun elevations.[0]
For example,
when the Sun is at an elevation of 10°, it appears to be at 10.1°.
The Sun's declination can be used, along with its right ascension,
to calculate its azimuth and also its true elevation,
which can then be corrected for refraction to give its apparent
position.[0][1][2]

[0] Jenkins, Alejandro (2013). "The Sun's position in the sky". European
Journal of Physics. 34 (3): 633–652. arXiv:1208.1043.
Bibcode:2013EJPh...34..633J. doi:10.1088/0143-0807/34/3/633. S2CID 119282288.

[1] https://gml.noaa.gov/grad/solcalc/calcdetails.html
[2] https://gml.noaa.gov/grad/solcalc/atmosrefr.gif
"""

import typer

from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_advanced_options,
    rich_help_panel_atmospheric_properties,
)

typer_option_apply_atmospheric_refraction = typer.Option(
    help="Correct solar azimuth and altitude angles for atmospheric refraction",
    rich_help_panel=rich_help_panel_atmospheric_properties,
)
typer_option_refracted_solar_zenith = typer.Option(
    help="Refracted solar zenith angle (in radians) for sun -rise and -set events",
    rich_help_panel=rich_help_panel_atmospheric_properties,
)
typer_option_albedo = typer.Option(
    min=0,
    help="Mean ground albedo",
    rich_help_panel=rich_help_panel_advanced_options,
)
