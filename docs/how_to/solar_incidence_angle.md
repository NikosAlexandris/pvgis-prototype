---
tags:
  - How-To
  - CLI
  - Solar Incidence Angle
hide:
  - toc
---

# Solar incidence angle

## For a moment in time

`#!bash pvgis-prototype`
can calculate the solar incidence angle for a givel location and moment in
time.

``` bash exec="true" result="ansi" source="above"
pvgis-prototype position incidence 8.627626 45.812233 '2020-01-01 15:00:00' -v
```

## For a time series

Currently,
to get a time series of solar geometry parameters over a location,
you can use the `pvgis-prototype position overview-series` command.

``` bash exec="true" result="ansi" source="above"
pvgis-prototype position overview-series 8.627626 45.812233 --start-time '2020-01-01' --end-time '2020-01-02' -r2 -aou degrees
```
