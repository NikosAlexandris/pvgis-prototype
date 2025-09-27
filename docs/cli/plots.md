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

## Overview

With `pvgis-prototype` we can generate plots : images that we can re-use or
plot directly in the terminal for uninterrupted interactive work.

<div class="grid cards" markdown>

- :octicons-graph-16: __Plot__

    ---

    - use the command `series` + subcommand `plot`

    - arbitrary single or multiple time series
    
    - user defined output filename
    
    - support for Tufte styled output


- :material-console-line::octicons-graph-16: __Uniplot in the terminal !__

    ---

    - Use the `--uniplot` flag
    - Support for single and multiple series
    - Adjust output width via the `--terminal-width-fraction` flag

</div>

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

You can find the newly generated plot in your current working directory.

<figure markdown="span">
  ![Example series plot](../../example_series_plot_20050101000000_20200131000000.png){height=400px}
  <figcaption>Example ERA5 Temperature at 2m time series plot</figcaption>
</figure>

## Uniplot

### A day of power output

We can plot in the terminal the photovoltaic power for a single day

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    --uniplot
```

### A year of power output

For a horizontally flat panel, we get

``` bash exec="true" result="ansi" source="material-block" hl_lines="5"
pvgis-prototype power broadband \
    8.628 45.812 214 180 0.001 \
    --start-time '2010-01-01' \
    --end-time '2010-12-31' \
    --quiet \
    --uniplot
```

!!! tip "Use the `--quiet` option"

    Large time series will take some time to print in the command line. It's
    really useful to use the `--quiet` flag.


Let's change the tilt to 30 degrees

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 30 \
    --start-time '2010-01-01' \
    --end-time '2010-12-31' \
    --quiet \
    --uniplot
```

and then to 45 -- at the same time, we can ask for a simplification of the plot
via the `--resample-large-series` option

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 45 \
    --start-time '2010-01-01' \
    --end-time '2010-12-31' \
    --quiet \
    --uniplot \
    --resample-large-series
```

### A day of solar incidence angles

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype position overview \
    8.628 45.812 \
    --start-time '2010-01-17' \
    --end-time '2010-01-18' \
    -aou degrees \
    --quiet \
    --uniplot
```
### Reading external time series data

We can repeat the same task
by using SARAH2/3 products
for the global and direct horizontal irradiance components

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 35 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --neighbor-lookup nearest \
    --uniplot
```

or indeed use also ERA5 time series data for ambient temperature and wind speed

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband \
    8.628 45.812 214 180 35 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    --global-horizontal-irradiance sarah2_sis_over_esti_jrc.nc \
    --direct-horizontal-irradiance sarah2_sid_over_esti_jrc.nc \
    --temperature-series era5_t2m_over_esti_jrc.nc \
    --wind-speed-series era5_ws2m_over_esti_jrc.nc \
    --neighbor-lookup nearest \
    --uniplot
```

!!! hint "Neighbor lookup ?"

    When reading data from external time series data,
    it is rather rare that the requested location coordinates truely exist as a
    data record.  Most likely, we need to ask for the location in the data that
    is nearest to the coordinates of our interest. There are also other methods
    for inexact location lookups available through the `--neighbor-lookup`
    option.

### Multi-year series

Or for 20 years

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
    Otherwise, it is going to take quite some time
    to print such a large times series in the terminal.

    The `--uniplot` will still work and this is the idea behind the `--quiet`
    flag.

### Multiple series

`uniplot` will also handle multiple series.
This is useful for example in the context of the `broadband-multi` command.

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
