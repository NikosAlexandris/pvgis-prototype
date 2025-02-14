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

## Analysis of Performance

We start right away with an analysis of the photovoltaic performance for our
sample location behind the ESTI facilities in the JRC, Ispra.

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 0.1 \
    --start-time '2013-01-01' \
    --end-time '2013-12-31' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --spectral-factor-series spectral_effect_cSi_2013_over_esti_jrc.nc \
    --temperature-series era5_t2m_over_esti_jrc.nc \
    --wind-speed-series era5_ws2m_over_esti_jrc.nc \
    --neighbor-lookup nearest \
    -aou degrees \
    --analysis \
    --quiet
```

PVGIS
provides a compact overview
of the calculations that generate the final power output.

Nonetheless,
in order to make better sense of the reported figures,
we can go through the algorithmic structure of the power-rating model
implemented in PVGIS.

The flow of calculations is :


```python exec="true" html="true"
```


## Efficiency

!!! danger "To do"

    Add content!

## Photovoltaic power

PVGIS uses a modified version of the power-rating model by King.

??? seealso "Huld, 2011"

    Thomas Huld, Gabi Friesen, Artur Skoczek, Robert P. Kenny, Tony Sample, Michael Field, Ewan D. Dunlop, A power-rating model for crystalline silicon PV modules, Solar Energy Materials and Solar Cells, Volume 95, Issue 12, 2011, Pages 3359-3369, ISSN 0927-0248, [doi.org/10.1016/j.solmat.2011.07.026](https://doi.org/10.1016/j.solmat.2011.07.026) (https://www.sciencedirect.com/science/article/pii/S0927024811004442)

    **Abstract**

    A model for the performance of generic crystalline silicon photovoltaic (PV) modules is proposed. The model represents the output power of the module as a function of module temperature and in-plane irradiance, with a number of coefficients to be determined by fitting to measured performance data from indoor or outdoor measurements. The model has been validated using data from 3 different modules characterized through extensive measurements in outdoor conditions over several seasons. The model was then applied to indoor measurement data for 18 different PV modules to investigate the variability in modeled output from different module types. It was found that for a Central European climate the modeled output of the 18 modules varies with a standard deviation (SD) of 1.22%, but that the between-module variation is higher at low irradiance (SD of 3.8%). The variability between modules of different types is thus smaller than the uncertainty normally found in the total solar irradiation per year for a given site. We conclude that the model can therefore be used for generalized estimates of PV performance with only a relatively small impact on the overall uncertainty of such estimates resulting from different module types.

    **Keywords** Crystalline silicon; PV energy rating; PV performance; Performance rating


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
