---
icon: material/sun-wireless
title: Global irradiance
tags:
  - How-To
  - CLI
  - Global Solar Irradiance
hide:
  - toc
---

This page overviews how-to work with
the `irradiance global` sub-commands `inclined`, `horizontal` and `spectral`.

!!! help "`irradiance global`"

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype irradiance global
    ```

## Global inclined

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global inclined \
    8.628 45.812 214 180 35 \
    '2010-01-01 12:00:00' \
    -vvvv
```

## Global horizontal

!!! warning "Horizontal components"

    Horizontal components
    are independent of the positional setup of a solar surface.
    Hence,
    we only need to provide a location and define a series of timestamps.

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance global horizontal \
    8.628 45.812 214 \
    '2010-01-01 12:00:00' \
    -vvv
```

## Global spectral

!!! danger "Incomplete"

    This section is yet to be completed.
