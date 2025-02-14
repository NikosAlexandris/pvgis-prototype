---
icon: material/direct-irradiance
title: Direct irradiance
tags:
  - How-To
  - CLI
  - Direct Solar Irradiance
hide:
  - toc
---

This page overviews how-to work with the `irradiance direct` sub-commands
`inclined`, `horizontal` and `normal`.
To begin with,
let's see the available subcommands by running

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct
```

## Direct inclined

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

## Direct horizontal

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

We can repeat the same simulation
disabling this time the atmospheric refraction function
via the **`--no-apply-atmospheric-refraction`** option

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct horizontal \
    8.627626 45.812233 200 \
    --start-time '2020-01-01' \
    --end-time '2020-01-02' \
    -r2 \
    -aou degrees \
    -vvv \
    --no-apply-atmospheric-refraction
```

Notice the differences ?
Refraction has an impact on the apparent position of the sun in the sky.
Especially at low sun altitude angles.

??? info "Atmospheric refraction"

    We can get some information about the effects of atmospheric refraction by
    using the `manual info` command

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype manual info Refraction
    ```

## Direct normal

Let's calculate the hourly direct normal irradiance time series
at (longitude, latitude, elevation) = $$8.627626 45.812233 200$$
over the course of a year.
An hourly time series for a year is quite long to print out in the terminal.
We can **`--quiet`** the output and `--uniplot`** it instead.

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype irradiance direct normal \
    --start-time '2020-01-01' \
    --end-time '2021-01-01' \
    --quiet \
    --uniplot
```

??? hint "Still want to see some hourly figures ?"

    ``` bash exec="true" result="ansi" source="material-block"
    pvgis-prototype irradiance direct normal \
        --start-time '2020-01-01' \
        --end-time '2020-02-01' \
        -r2 \
        -vvv
    ```
