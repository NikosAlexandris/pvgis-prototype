---
tags:
  - How-To
  - CLI
  - Solar Incidence Angle
hide:
  - toc
---

# Solar Geometry Overview

## Time series

To get a time series of solar geometry parameters over a location,
you can use the `pvgis-prototype position overview-series` command.

``` bash exec="true" result="ansi" source="above"
export COLUMNS=1000  # markdown-exec: hide
pvgis-prototype position overview-series 8.627626 45.812233 --start-time '2020-01-01' --end-time '2020-01-02' -r2 -aou degrees
```

### CSV

We can export the results in widely known and machine readable CSV format

``` bash exec="true" result="ansi" source="above"
pvgis-prototype position overview-series 8.627626 45.812233 --start-time '2020-01-01' --end-time '2020-01-02' -r2 -aou degrees --csv solar_incidence_angle_sample.csv
```

Let's verify it worked well

``` bash exec="true" result="ansi" source="above"
file solar_incidence_angle_sample.csv
```

??? note "solar_incidence_angle_sample.csv"

    {{ read_csv('docs/data/solar_incidence_angle_sample.csv') }}
