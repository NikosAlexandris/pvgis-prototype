---
tags:
  - How-To
  - CLI
  - Solar Incidence Angle
hide:
  - toc
---

# Solar incidence angle

`#!bash pvgis-prototype`
can calculate the solar incidence angle for a givel location and moment in
time.

``` bash exec="true" result="ansi" source="above"
pvgis-prototype position incidence 8.627626 45.812233 '2020-01-01 15:00:00' -v
```

!!! hint "Looking for a time series ?"

    Currently,
    for a time series of solar geometry parameters over a location,
    you can use the `pvgis-prototype position overview-series` command.
    See [Solar Geometry Overview](how_to/solar_geometry_overview.md).
