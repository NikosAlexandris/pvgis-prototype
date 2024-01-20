---
tags:
  - Core API
  - API
  - Reference
---

# API Reference

## Python API

This guide provides an introduction to the basic usage of the PVGIS API.

## Getting Started

[Include steps on how to get started with PVGIS API, such as installation instructions, setting up the environment, etc.]

## Examples

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

## Error Handling

[Discuss common errors and how to handle them.]

## Next Steps

...

## API Reference


### Solar position geometry

<!-- - Fractional year
       ⊂ Equation of time
       ⊂ Time offset
       ⊂ True solar time
       ⊂ Solar hour angle
     - Solar declination
       ⊂ Solar zenith
       ⊂ Solar altitude
       ⊂ Solar azimuth -->

::: pvgisprototype.api.geometry.fractional_year
::: pvgisprototype.api.geometry.solar_time
::: pvgisprototype.api.geometry.solar_time_series
::: pvgisprototype.api.geometry.hour_angle
::: pvgisprototype.api.geometry.declination
::: pvgisprototype.api.geometry.declination_series
::: pvgisprototype.api.geometry.zenith
::: pvgisprototype.api.geometry.altitude
::: pvgisprototype.api.geometry.altitude_series
::: pvgisprototype.api.geometry.azimuth
::: pvgisprototype.api.geometry.azimuth_series
::: pvgisprototype.api.geometry.overview
::: pvgisprototype.api.geometry.overview_series
::: pvgisprototype.api.geometry.incidence
::: pvgisprototype.api.geometry.incidence_series
::: pvgisprototype.api.geometry.models
