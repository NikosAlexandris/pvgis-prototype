---
icon: material/solar-power-variant
title: Photovoltaic Performance
tags:
  - Development
  - Photovoltaic Performance
---

You might have followed the sections
for [solar position](solar_position.md) and [solar irradiance](solar_irradiance.md)
or maybe not.
Regardless,
this tutorial is both a stand-alone document and a building block
in the chain of calculations to estimate photovoltaic power output.

## Efficiency

!!! danger "To do"

    Add content!

## Photovoltaic power

We can _simulate_ the photovoltaic power output via

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 45 \
    '2010-01-27 12:00:00'
```

or _estimate_ it by reading external irradiance time series via

``` bash exec="true" result="ansi" source="material-block" hl_lines="4 5 6"
pvgis-prototype power broadband \
    8.628 45.812 214 180 45 \
    '2010-01-27 12:00:00' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --neighbor-lookup nearest
```

## Panel tilt

The default _tilt_ angle for a solar surface is `45` degrees.
In order to get the calculations done for a _horizontally flat_ panel,
we need to request this via the fifth positional parameter
with a value close to `0` like `0.0001`.

Let's add it to the power commands :

- simulating the photovoltaic power output

``` bash exec="true" result="ansi" source="material-block" hl_lines="2"
pvgis-prototype power broadband \
    8.628 45.812 214 180 0.0001 \
    '2010-01-27 12:00:00'
```

- using SARAH2 data

``` bash exec="true" result="ansi" source="material-block" hl_lines="4 5"
pvgis-prototype power broadband \
    8.628 45.812 214 180 0.0001 \
    '2010-01-27 12:00:00' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --neighbor-lookup nearest
```

We can request more details on the calculations

``` bash exec="true" result="ansi" source="material-block" hl_lines="7"
pvgis-prototype power broadband \
    8.628 45.812 214 180 0.0001 \
    '2010-01-27 12:00:00' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --neighbor-lookup nearest \
    -vvv
```

