---
icon: fontawesome/solid/file-csv
description: CSV output
title: CSV
subtitle: Export output as CSV
tags:
  - How-To
  - CLI
  - CSV
---

PVGIS can export results as Comma-Separated-Values (CSV)
via the `--csv` option for various commands, including
the photovoltaic `power`,
the photovoltaic `performance`
and the solar `position`.

## Photovoltaic Power

The following example generates some photovoltaic power time series

``` bash exec="true" result="ansi" source="above" hl_lines="6"
pvgis-prototype power broadband \
7.9672 45.9684 2000 180 33 \
--start-time '2010-06-01 04:00:00' \
--end-time '2010-06-01 19:00:00' \
-v \
--csv power_broadband_example.csv
```

This command will generate the requested file `power_broadband_example.csv`.

??? note "power_broadband_example.csv"

    {{ read_csv('power_broadband_example.csv') }}

A companion metadata file `power_broadband_example_metadata.yaml`
is generated too.

??? note "power_broadband_example_metadata.yaml"

    {{ read_yaml('power_broadband_example_metadata.yaml') }}


Of course we can add more `-v`s for a _richer_ output

``` bash exec="true" result="ansi" source="above" hl_lines="5"
pvgis-prototype power broadband \
7.9672 45.9684 2000 180 33 \
--start-time '2010-06-01 04:00:00' \
--end-time '2010-06-01 19:00:00' \
-vvv \
--csv power_broadband_example_vvv.csv
```

??? note "power_broadband_example_vvv.csv"

    {{ read_csv('power_broadband_example_vvv.csv') }}

!!! info

    [Verbosity](../cli/verbosity.md)

## Fingerprinted

If we request for a fingerprint, however,
it becomes part of the CSV filename

``` bash exec="true" result="ansi" source="above" hl_lines="7"
pvgis-prototype power broadband \
7.9672 45.9684 2000 180 33 \
--start-time '2010-06-01 04:00:00' \
--end-time '2010-06-01 19:00:00' \
-vvv \
--csv power_broadband_example_vvv.csv \
--fingerprint

```

We can list all CSV files generated in this session

``` bash exec="true" result="ansi" source="above"
ls power_broadband_example_vvv_*.csv
```

!!! note 

    You can check for the output along with its unique fingerprint
    in the current working directory.

## Photovoltaic Performance

An example of photovoltaic performance analysis.
Here, the CSV output is practically the same as in the `power` command
yet with more details.

``` bash exec="true" result="ansi" source="above" hl_lines="12"
pvgis-prototype performance broadband \
    8.628 45.812 214 180 44 \
    --start-time '2010-01-01' \
    --end-time '2010-12-31' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --spectral-factor-series spectral_effect_cSi_over_esti_jrc.nc \
    --temperature-series era5_t2m_over_esti_jrc.nc \
    --wind-speed-series era5_ws2m_over_esti_jrc.nc \
    --neighbor-lookup nearest \
    -aou degrees \
    --csv performance_broadband_example.csv
```

??? note "performance_broadband_example.csv"

    {{ read_csv('performance_broadband_example.csv') }}

## Solar Position Overview

``` bash exec="true" result="ansi" source="above" hl_lines="7"
pvgis-prototype position overview \
8.610 45.815 \
--start-time 2010-01-01 \
--end-time "2010-12-31 23:00:00" \
--rounding-places 2 \
--quiet \
--csv pvgis6_solar_position_overview_8.610_45.815_2010.csv
```
