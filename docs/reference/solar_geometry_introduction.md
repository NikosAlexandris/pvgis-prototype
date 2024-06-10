---
title: Solar Position
tags:
  - Reference
  - Solar Position
  - Introduction
hide:
  - toc
---

The amount of solar irradiance incident on a solar surface
at a location and a moment in time,
depends primarily on the ==Solar Incidence== angle.

!!! tip

    PVGIS CLI offers a primer on the solar position parameters.
    Inform yourself using the `pvgis-prototype position intro` command.
    See [pvgis-prototype position intro](../cli/position/intro.md)

To calculcate the critical ==solar incidence== angle,
PVGIS requires the relative Latitude and Longitude coordinates
of the surface in question,
the ==Surface Tilt== and ==Surface Orientation== angles,
the ==Solar Declination== and the ==Solar Hour== angles
both of which are derived from the _Timestamp_ of interest.

!!! hint 

    Practically speaking,
    _solar position_
    consists of a series of angular measurements
    between the position of the sun in the sky
    and a location on the surface of the earth
    for a moment or series of moments in time.

First in order
is the calculation of the position of the Earth in its orbit around the sun
expressed through the angle ==Fractional Year==
measured in radians based solely on a moment in time (timestamp).

Second is
the ==Equation of Time== measured in minutes that
corrects for the eccentricity of the Earth's orbit and axial tilt.

The ==Time Offset== measured in minutes,
incorporates the ==Equation of Time==
and accounts for the variation of the ==Local Solar Time== (LST)
within a given time zone
due to the longitude variations within the time zone.

Next is
the ==True solar time==,
also known as the _Apparent solar time_
upon which depends the calculation of the ==Solar hour== angle.

The ==Solar Hour== angle
measures the Earth's rotation
and indicates the time of the day relative to the position of the sun.
It bases on the longitude and timestamp and by definition,
the solar hour angle is :

    - 0° at solar noon
    - negative in the morning
    - positive in the afternoon

!!! hint "Order of dependent calculations"

    - Fractional year ⊂ Equation of time ⊂ Time offset ⊂ True solar time ⊂ Solar hour angle
    - Solar declination ⊂ Solar zenith ⊂ Solar altitude ⊂ Solar azimuth

The ==Solar Declination== angle,
depending on the algorithm,
requires only the ==Fractional Year==
_or in addition_
the _Eccentricity correction factor_
and the _Perigee offset_.

!!! hint "Alternative algorithm and Order of dependency"

    - Fractional year ⊂ Solar declination  **NOAA**
    or
    - (Fractional year, Eccentricity correction, Perigee offset) ⊂ Solar declination  **Jenčo/Hofierka**
