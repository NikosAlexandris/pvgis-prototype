---
icon: simple/spectrum
title: Photovoltaic performance based on broadband irradiance
subtitle: Estimate photovoltaic performance over a time series based on broadband irradiance
tags:
  - How-To
  - CLI
  - Photovoltaic Performance
  - Broadband Irradiance
---

PVGIS can estimate the photovoltaic power over a time series
or an arbitrarily aggregated energy production of a PV system
based on broadband irradiance, ambient temperature and wind speed.

## Example

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.627626 45.81223 200 \
    --start-time '2000-01-01' \
    --end-time '2000-01-02'
```

### Verbosity levels

The command above returned the PV power output
at hourly frequency for the requested period of time.
Eventually we want to know more about the calculated figures.
We can ask for more details via the _verbosity_ flag `-v` :

!!! note "On the structure of the command"

    To improve readability,
    many example commands are broken in multiple lines.
    Each line, _except of the last one_,
    is suffixed with the `\` (back-slash) character.
    This allows to continue a command in the next line.
    Copy-pasting such commands from here and to a terminal is safe!

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.627626 45.81223 200 \
    --start-time '2000-01-01' \
    --end-time '2000-01-02' \
    -v
```

In fact,
we can ask for more by adding more `v`s, i.e. `-vv` as in

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.627626 45.81223 200 \
    --start-time '2000-01-01' \
    --end-time '2000-01-02' \
    -vv
```

or even more via `-vvv`, `-vvvv` and so on. 

!!! warning "On the number of verbosity levels"

    The number of available detail levels is not the same for all commands in
    PVGIS. At the moment, it takes for some exploration to discover what useful
    information each commad can reveal!

### Statistics

We can also ask from PVGIS to generate a statistical overview.
Following, we repeat the same calculations however extented over a year's
period, like so :


``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8.627626 45.81223 200 --start-time '2000-01-01' --end-time '2000-01-02' --statistics -v
```

#### Group by

We can do better and ask for a 2-hours aggregation :

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.627626 45.81223 200 \
    --start-time '2000-01-01' \
    --end-time '2000-01-02' \
    --statistics \
    --groupby 2h \
    -v 
```

### Plots in the command line

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.627626 45.81223 200 177 43 \
    --start-time '2005-06-01' \
    --end-time '2005-06-02' \
    -aou degrees \
    --uniplot \
    -vvv
```

### Reading from external solar irradiance time series

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.627626 45.81223 200 166 35 \
    --start-time '2005-06-01'\
    --end-time '2005-06-02'\
    -aou degrees\
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc\
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc\
    --neighbor-lookup nearest\
    -vv \
    --uniplot\
    --terminal-width-fraction 0.46
```

## Analysis of Performance

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 0.1 \
    --start-time '2013-01-01' \
    --end-time '2013-12-31' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --spectral-factor-series spectral_effect_cSi_over_esti_jrc.nc \
    --temperature-series era5_t2m_over_esti_jrc.nc \
    --wind-speed-series era5_ws2m_over_esti_jrc.nc
```

