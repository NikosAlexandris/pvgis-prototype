---
icon: material/format-vertical-align-bottom
title: Direct irradiance
tags:
  - How-To
  - CLI
  - Direct Solar Irradiance
hide:
  - toc
---

This page overviews how-to work with `irradiance` commands,
To begin with,
let's see the available subcommands by running

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct
```

## Direct inclined irradiance

Let's calculate the direct inclined irradiance over the location at 
(longitude, latitude, elevation) = $$8.627626 45.812233 200$$

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct inclined \
    8.627626 45.812233 200 \
    --start-time '2020-01-01' \
    --end-time '2020-01-02' \
    -r2 \
    -aou degrees \
    -vvv
```

## Direct horizontal irradiance

Let's calculate the direct horizontal irradiance over the location at 
(longitude, latitude, elevation) = $$8.627626 45.812233 200$$

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct horizontal \
    8.627626 45.812233 200 \
    --start-time '2020-01-01' \
    --end-time '2020-01-02' \
    -r2 \
    -aou degrees \
    -vvv
```
