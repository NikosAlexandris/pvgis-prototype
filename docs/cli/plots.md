---
icon: octicons/graph-16
description: Plotting time series data
title: Plots
subtitle: Plot time series data
tags:
  - How-To
  - CLI
  - Plots
---

## Time series

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype series plot \
    era5_t2m_over_esti_jrc.nc \
    8.628 45.812 \
    --neighbor-lookup nearest \
    --start-time '2001-01-01' \
    --end-time '2020-01-31' \
    --tufte-style \
    --output-filename 'example_series_plot' \
    --no-variable-name-as-suffix
```


<figure markdown="span">
  <!-- ![Example series plot](../../example_series_plot_20050101000000_20200131000000.png){ loading=lazy } -->
  ![Example series plot](example_series_plot_20050101000000_20200131000000.png){height=400px}
  <figcaption>Example ERA5 Temperature at 2m time series plot</figcaption>
</figure>

## Uniplot

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8 45 214 \
    --start-time '2000-01-01' \
    --end-time '2020-12-31' \
    --quiet \
    --uniplot
```

!!! attention "20 years of hourly time series!"

    Since we ask for 20 years of hourly time series,
    it is a good idea to use the `--quiet` flag!
    Else, it is going to take quite some time to print such a large times
    series in the terminal.

    The `--uniplot` will still work and this is the idea behind the `--quiet`
    flag.

### Multiple series

`uniplot` will also handle multiple series. This is useful for example in the
context of the `broadband-multi` command.

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband-multi \
    8 45 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    --surface-orientation "180,180,100" \
    --surface-tilt "45,0.1,33" \
    --quiet \
    --uniplot
```
