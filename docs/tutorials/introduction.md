---
icon: material/location-enter
title: Introduction
subtitle: A gentle introduction to elements of photovoltaic performance using PVGIS
tags:
  - Tutorial
  - CLI
  - Introduction
  - Photovoltaic Performance
  - Broadband Irradiance
---

# Overview

Curious about photovoltaic performance ?
This is an introduction into the estimation of photovoltaic power
over a location and a moment or period in time.

We will explore _solar radiation components_
and _photovoltaic power estimates_,
by stepping through :

- the calculation of **the position of the sun in the sky**
- the measurement of **sun-to-surface angles**
- the analysis of **solar irradiance components**
- and the derivation of the **_effective_ amount of global irradiance**.

!!! note

    The aim of this tutorial
    is to explain the calculations
    that lead to the estimation of the photovoltaic power output
    for a given location and period of time.

    Alright,
    let's go through this step-by-step
    and overview some theoretical concepts too.

# Example

Before we walk through the tutorial,
let's get straight a/the result we are aiming at !
We want to _estimate the photovoltaic power output
for a specific location and a short period of time_.
Along with the result,

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --neighbor-lookup nearest \
    --quiet
```

!!! tip

    Just copy-and-paste the commands and follow along.
    This is one way to practice through this tutorial!

Let's see a plot for this output time series 

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --neighbor-lookup nearest \
    --uniplot \
    --quiet
```

# Analysis

Let's break-down the result :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 0.0001 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --neighbor-lookup nearest \
    -vv
```

For each hour during the period in question,
we calculated the photovoltaic power output
based on satellite-based observations of the terrestrial radiation
and a predefined efficiency and other parameters.

!!! seealso "Symbols"

    The `Power ⌁` column is the results of the 
    `Global ∡` inclined irradiance
    multiplied by the overall `Efficiency %`.
    In fact,
    the global inclined irradiance can be broken down in
    its _inclined_ irradiance components
    `Direct ∡`, `Diffuse ∡` and `Reflected ∡`.
    See the complete list at [Symbols](../cli/symbols.md)
