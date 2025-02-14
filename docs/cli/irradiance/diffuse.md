---
icon: simple/liberadotchat
title: Diffuse irradiance
tags:
  - How-To
  - CLI
  - Diffuse Solar Irradiance
hide:
  - toc
---

This page overviews how-to work with the `irradiance diffuse` sub-commands
`inclined`, `horizontal` and `from-global-and-direct-irradiance`
which supports reading the global and direct irradiance components
from external time series.

To begin with,
let's see the available subcommands by running

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse
```

## Diffuse inclined

Let's calculate the direct inclined irradiance over the location at 
(longitude, latitude, elevation) = $$8.627626 45.812233 200$$


``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse inclined \
    8.628 45.812 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28'
```

or indeed a bit more detailed

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse inclined \
    8.628 45.812 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    -v
```

We can do this for 2 years, for example, and add a quick plot along with a
fingerprint which can be handy to verify the output in case we want to
reproduce it

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse inclined \
    8.628 45.812 214 \
    --start-time '2010-01-01' \
    --end-time '2011-12-31' \
    --fingerprint \
    --uniplot \
    --quiet
```

## Diffuse horizontal

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse horizontal \
    8.628 45.812 214 \
    --start-time '2013-06-01' \
    --end-time '2013-06-02' \
    -vvvvv
```


## Reading external time series of global and direct irradiance

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance diffuse from-global-and-direct-irradiance \
    sarah2_sis_over_esti_jrc.nc \
    sarah2_sid_over_esti_jrc.nc \
    8.628 45.812 \
    --start-time '2010-01-01' \
    --end-time '2010-12-31' \
    --quiet \
    --uniplot
```
