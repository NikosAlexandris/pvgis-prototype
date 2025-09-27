---
icon: material/sun-angle
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
PVGIS requires the relative _Latitude_ and _Longitude_ coordinates
of the surface in question,
its ==Surface Tilt== and ==Surface Orientation== angles,
as well as the ==Solar Declination== and the ==Solar Hour== angles
both of which are derived from the _Timestamp_ of interest.

!!! hint

    Practically speaking,
    _solar position_
    consists of a series of angular measurements
    between the position of the sun in the sky
    and a location on the surface of the earth
    for a moment or series of moments in time.


```python exec="true" html="true"
--8<-- "docs/reference/solar_position_diagram.py"
```

### Fractional Year

![Fractional year]

First in order
is the calculation of the position of the Earth in its orbit around the sun
expressed through the angle ==Fractional Year==
measured in radians based solely on a moment in time (timestamp).

!!! Notes

    - The function that calculates the fractional year considers leap years and converts the timestamps into fractional values.
    - Other solar positioning algorithms name this variable "the day angle"

### Equation of Time

![Equation of time]

Second is
the ==Equation of Time== measured in minutes that
corrects for the eccentricity of the Earth's orbit and axial tilt.

### Time Offset

![Time Offset]

The ==Time Offset== measured in minutes,
incorporates the ==Equation of Time==
and accounts for the variation of the ==Local Solar Time== (LST)
within a given time zone
due to the longitude variations within the time zone.

### True Solar Time

![True solar time]

Next is
the ==True solar time==,
also known as the _Apparent solar time_
upon which depends the calculation of the ==Solar hour== angle.

### Solar Hour

![Solar Hour Angle]

The ==Solar Hour== angle
measures the Earth's rotation
and indicates the time of the day relative to the position of the sun.
It bases on the longitude and timestamp and by definition,
the solar hour angle is :

    - 0° at solar noon
    - negative in the morning
    - positive in the afternoon

!!! note "Useful to know"

    Since the Earth rotates 15° per hour (or pi / 12 in radians),
    each hour away from solar noon
    corresponds to an angular motion of the sun in the sky of 15°.
    Practically, the calculation converts a timestamp into a solar time.

!!! hint "Order of dependent calculations"

    - Fractional year ⊂ Equation of time ⊂ Time offset ⊂ True solar time ⊂ Solar hour angle
    - Solar declination ⊂ Solar zenith ⊂ Solar altitude ⊂ Solar azimuth

### Solar Declination

![Solar Declination]

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

## Solar Zenith

![Solar Zenith]

## Solar Altitude

![Solar Altitude]

## Solar Azimuth

![Solar Azimuth]

## Solar Incidence

![Solar Incidence]

## Default algoriths

The default algoriths for
solar timing,
positioning
and the definition of the incidence angle
are :

- `solar_time_model` is set to Milne1921 (see in pvgisprototype.constants: SOLAR_TIME_ALGORITHM_DEFAULT).
    - Calculate the apparent solar time based on the equation of time by Milne 1921

- `solar_position_model` is set to NOAA's equation for .. (see : SOLAR_POSITION_ALGORITHM_DEFAULT).
- `solar_incidence_model` is set to Iqbal (see : SolarIncidenceModel.iqbal).


## Atmospheric refraction

!!! warning "Review Me" 

Following the NOAA solar geometry equations,
the calculation of the solar incidence anlge
requires all of the following angular quantities :

- altitude which in turn requires the hour angle and the zenith angle
- zenith which in turn requires the solar declination angle (sun-earth)
- azimuth
- surface tilt
- latitude
- hour angle
- relative longitude

Mathematicall speaking,
the point where refraction plays a role is the solar zenith angle.
The zenith angle is adjusted based on some method of atmospheric refraction
and the solar altitude angle
(high altitude above horizon, low altitude above horizon and altitude below horizon).
While the adjustment isn't large in absolute terms,
it is part of the solar geometry system and may impact the analysis,
especially when it comes to the amount of irradiance
close to sun- rise and set.

[Fractional year]: icons/fractional-year.svg
[Equation of time]: icons/noun-clock.svg
[Time Offset]: icons/map-clock.svg
[True solar time]: icons/solar-time.svg
[Solar Hour Angle]: icons/solar-hour-angle.svg
[Solar Declination]: icons/earth_to_sun_angle.svg
[Solar Zenith]: icons/solar-zenith.svg
[Solar Altitude]: icons/sun-angle-outline.svg
[Solar Azimuth]: icons/sun-compass.svg
[Solar Incidence]: icons/noun_global_horizontal_irradiance_new.svg
