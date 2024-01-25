---
tags:
  - Development
  - Roadmap
  - Progress
  - Solar Geometry
---

The following solar geometry _components_
are hard requirements
in order to derive the single most important angle of solar incidence
which is crucial for the estimation of the solar irradiance
incident on a solar surface.

| Quantity              | Implementation       | Requires                                                    | Required by                                 | Algorithm | Optimisation |
|-----------------------|----------------------|-------------------------------------------------------------|---------------------------------------------|-----------|--------------|
| - [x] Fractional year   | fractional_year.py   | Timestamp (+ time zone ? ) [^*]                             | Equation of time, solar declination         |           |              |
| - [x] Solar declination | solar_declination.py | Fractional year                                             | Solar zenith                                |           |              |
| - [x] Equation of time  | equation_of_time.py  | Fractional year                                             | Time offset                                 |           |              |
| - [x] Time offset       | time_offset.py       | Equation of time                                            | True solar time                             |           |              |
| - [x] True solar time   | solar_time.py        | Time offset                                                 | Solar hour angle                            |           |              |
| - [x] Solar hour angle  | solar_hour_angle.py  | True solar time                                             | Solar zenith, Solar altitude, Solar azimuth |           |              |
| - [x] Solar zenith      | solar_zenith.py      | Solar declination, Solar hour angle, Atmospheric refraction | Solar altitude                              |           |              |
| - [x] Solar altitude    | solar_altitude.py    | Solar hour angle, Solar zenith                              | Solar position                              |           |              |
| - [x] Solar azimuth     | solar_azimuth.py     | Solar declination, Solar hour angle, Solar zenith           | Solar position                              |           |              |

[^*]: Is the timezone is such that after conversion to UTC it changes the day, then this is indeed required ?

!!! tip

    PVGIS CLI offers a primer on the solar geometry parameters.
    Inform yourself using the `pvgis-prototype position intro` command.
    See [pvgis-prototype position into](how_to/solar_geometry_introduction.md)
