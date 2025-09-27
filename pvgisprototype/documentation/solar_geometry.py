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
A_PRIMER_ON_SOLAR_GEOMETRY = """
    The amount of solar irradiance incident on a solar surface at a location
    and a moment in time, depends on the [blue]Solar Incidence[/blue] angle.

    To calculcate the critical [cyan]Solar Incidence[/cyan] angle, PVGIS requires :
    - the relative [cyan]Latitude[/cyan] and [cyan]Longitude[/cyan] coordinates
      of the surface in question
    - the [cyan]Surface Orientation[/cyan] and [cyan]Surface Tilt[/cyan] angles
    - the [cyan]Solar Declination[/cyan] and the [cyan]Solar Hour[/cyan] angles
    - a [cyan]Timestamp[/cyan] from which to derive the latter two

    [bold]First in order is[/bold] the calculation of the position of the Earth
    in its orbit around the sun expressed through the angle [cyan]Fractional Year[/cyan]
    measured in radians based on a moment in time (timestamp).

    [bold]Second is the[/bold] [cyan]Equation of Time[/cyan] measured in minutes
    that corrects for the eccentricity of the Earth's orbit and axial tilt.

    [bold]Third is the[/bold] [cyan]Time Offset[/cyan] measured in minutes,
    incorporates the [italic]Equation of Time[/italic] and accounts for
    the variation of the Local Solar Time (LST) within a given time zone
    due to the longitude variations within the time zone.

    [bold]Fourth is the[/bold] [cyan]True solar time[/cyan], also known as
    the [cyan]Apparent solar time[/cyan] upon which depends the calculation of
    the [cyan]Solar hour angle[/cyan].

    [bold]Next is the[/bold] [cyan]Solar Hour angle[/cyan] measures
    the Earth's rotation and indicates the time of the day relative to
    the position of the sun. It bases on the longitude and timestamp and
    by definition, the solar hour angle is :

        - 0° at solar noon
        - negative in the morning
        - positive in the afternoon

    The [underline]order of dependency[/underline] is :

    - [cyan]Fractional year[/cyan] ⊂ [cyan]Equation of time[/cyan] ⊂ [cyan]Time offset[/cyan] ⊂ [cyan]True solar time[/cyan] ⊂ [cyan]Solar hour angle[/cyan]
    - Solar declination ⊂ Solar zenith ⊂ Solar altitude ⊂ Solar azimuth

    The [cyan]Solar Declination[/cyan] angle, depending on the algorithm,
    requires only the [cyan]Fractional Year[/cyan] or in addition the
    [cyan]Eccentricity correction factor[/cyan] and the [cyan]Perigee
    offset[/cyan]) ⊂ [cyan]Solar declination[/cyan].

    The order of dependency is :

    - [cyan]Fractional year[/cyan] ⊂ [cyan]Solar declination[/cyan] ([reverse]NOAA[/reverse])

    or

    - ([cyan]Fractional year[/cyan], [cyan]Eccentricity correction[/cyan], [cyan]Perigee offset[/cyan]) ⊂ [cyan]Solar declination[/cyan] ([reverse]Need Reference Here![/reverse])
"""

