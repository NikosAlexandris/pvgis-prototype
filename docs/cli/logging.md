---
icon: material/notebook-edit-outline
title: Logging
description: PVGIS' unified logger
subtitle: Log details of a command execution
tags:
  - How-To
  - CLI
  - Logging
---

!!! danger

    Content under development !

    Explain :

    - `llllll`
    - `--log`
    - `--log-rich`
    - `--log-file`
    - Difference against debugging

Say we query a NetCDF file for a few timestamps

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype \
    series select \
    spectral_effect_cSi_over_esti_jrc.nc \
    8.6 45.8 \
    --neighbor-lookup nearest \
    '2005-12-31 12:00:00, 2006-12-31 12:00:00,2007-12-31 12:00:00,2008-12-31 12:00:00,2009-12-31 12:00:00'
```

and the output is _nothing_!

We can use some logging flags to get details around several steps of the
requested operation. In example, let's add `-l` to the same command

``` bash exec="true" result="ansi" source="material-block" hl_lines="6"
pvgis-prototype \
    series select \
    spectral_effect_cSi_over_esti_jrc.nc \
    8.6 45.8 \
    --neighbor-lookup nearest \
    '2005-12-31 12:00:00, 2006-12-31 12:00:00,2007-12-31 12:00:00,2008-12-31 12:00:00,2009-12-31 12:00:00' \
    -l
```

We can also try `--log`

``` bash exec="true" result="ansi" source="material-block" hl_lines="1"
pvgis-prototype --log \
    series select \
    spectral_effect_cSi_over_esti_jrc.nc \
    8.6 45.8 \
    --neighbor-lookup nearest \
    '2005-12-31 12:00:00, 2006-12-31 12:00:00,2007-12-31 12:00:00,2008-12-31 12:00:00,2009-12-31 12:00:00'
```

or even `--log-rich` for a colorful output

``` bash exec="true" result="ansi" source="material-block" hl_lines="1"
pvgis-prototype --log-rich \
    series select \
    spectral_effect_cSi_over_esti_jrc.nc \
    8.6 45.8 \
    --neighbor-lookup nearest \
    '2005-12-31 12:00:00, 2006-12-31 12:00:00,2007-12-31 12:00:00,2008-12-31 12:00:00,2009-12-31 12:00:00'
```

Finally, we can export to a log file via the `--log-file` option

``` bash exec="true" result="ansi" source="material-block" hl_lines="1"
pvgis-prototype --log-file series_select.log \
    series select \
    spectral_effect_cSi_over_esti_jrc.nc \
    8.6 45.8 \
    --neighbor-lookup nearest \
    '2005-12-31 12:00:00, 2006-12-31 12:00:00,2007-12-31 12:00:00,2008-12-31 12:00:00,2009-12-31 12:00:00'
```

??? note "The log file"

    --8<-- "series_select.log"
