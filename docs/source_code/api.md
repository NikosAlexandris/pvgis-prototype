---
icon: material/language-python
tags:
  - Core API
  - API
  - Reference
---

# Python API

This guide provides an introduction to the basic usage of the PVGIS API.

# Getting Started

[Include steps on how to get started with PVGIS API, such as installation instructions, setting up the environment, etc.]

# Examples

[Provide an example of making a basic API call, including code snippets and explanations.]

``` python
from pvgisprototype import Longitude, Latitude
```

or

``` pycon
>>> from pvgisprototype import Longitude
>>> Longitude()
Longitude(value=None, unit=None, symbol='Λ', desription="The angle between a point on the Earth's surface and the meridian plane, with its value ranging from 0° at the Prime Meridian in Greenwich, England, to 180° east or west.")
```

# Error Handling

[Discuss common errors and how to handle them.]

# Next Steps

...

# API Reference

## Solar position

<!-- - Fractional year
       ⊂ Equation of time
       ⊂ Time offset
       ⊂ True solar time
       ⊂ Solar hour angle
     - Solar declination
       ⊂ Solar zenith
       ⊂ Solar altitude
       ⊂ Solar azimuth -->

::: pvgisprototype.api.position.fractional_year
::: pvgisprototype.api.position.solar_time
::: pvgisprototype.api.position.solar_time_series
::: pvgisprototype.api.position.hour_angle
::: pvgisprototype.api.position.declination
::: pvgisprototype.api.position.declination_series
::: pvgisprototype.api.position.zenith
::: pvgisprototype.api.position.altitude
::: pvgisprototype.api.position.altitude_series
::: pvgisprototype.api.position.azimuth
::: pvgisprototype.api.position.azimuth_series
::: pvgisprototype.api.position.overview
::: pvgisprototype.api.position.overview_series
::: pvgisprototype.api.position.incidence
::: pvgisprototype.api.position.incidence_series
::: pvgisprototype.api.position.models
