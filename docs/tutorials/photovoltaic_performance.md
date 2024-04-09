---
icon: material/solar-power-variant
title: Photovoltaic Performance
tags:
  - Development
  - Photovoltaic Performance
---

## Efficiency

!!! danger "To do"

    Add content!

## Photovoltaic power

Finally, the photovoltaic power output is simulated via :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 45 \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 759.7145 -->

or estimated via :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 45 \
    '2010-01-27 12:00:00' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --neighbor-lookup nearest
```
<!-- returns -->
<!-- 588.5716 -->

## Panel tilt

The default _tilt_ angle for a solar surface is `45` degrees.
In order to get the calculations done for a _horizontally flat_ panel,
we need to request this via the fifth positional parameter
with a value close to `0` like `0.0001`.

Let's add it to the power commands :

- simulating the photovoltaic power output :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 0.0001 \
    '2010-01-27 12:00:00'
```
<!-- returns -->
<!-- 687.0622 -->

- using SARAH2 data :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 0.0001 \
    '2010-01-27 12:00:00' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --neighbor-lookup nearest
```
<!-- returns -->
<!-- 513.75525 -->
