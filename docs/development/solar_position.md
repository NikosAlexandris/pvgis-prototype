---
icon: material/sun-angle
tags:
  - Development
  - Roadmap
  - Progress
  - Solar Position
---

<style>
.twemoji.checked svg {
    color: #00e676;
}
.twemoji.blank svg {
    color: rgba(0, 0, 0, 0.07);
}
</style>

The following solar position _components_
are hard requirements
in order to derive the single most important angle of _solar incidence_
which is crucial for the estimation of the solar irradiance
incident on a solar surface.

!!! tip

    PVGIS CLI offers a primer on the solar position parameters.
    Inform yourself using the `pvgis-prototype position intro` command.
    See [pvgis-prototype position into](../how_to/solar_position_introduction.md)

The implementations concern NOAA's solar position equations, listed _in dependency order_ : 

| Status                                      | Quantity              | Implementation         | Requires                                                      | Required by                                   | Support a Moment | Support Time series                         | Optimisation   |
| -----------------------------------         | -------------------   | ---------------------- | ------------------------------------------------------------- | --------------------------------------------- | -----------      | -------------                               | -------------- |
| :material-checkbox-marked-circle:{.checked} | Fractional year       | fractional_year.py     | Timestamp (+ time zone ? ) [^*]                               | Equation of time, solar declination           |                  | :material-checkbox-marked-circle:{.checked} |                |
| :material-checkbox-marked-circle:{.checked} | Equation of time      | equation_of_time.py    | Fractional year                                               | Time offset                                   |                  | :material-checkbox-marked-circle:{.checked} |                |
| :material-checkbox-marked-circle:{.checked} | Time offset           | time_offset.py         | Equation of time                                              | True solar time                               |                  | :material-checkbox-marked-circle:{.checked} |                |
| :material-checkbox-marked-circle:{.checked} | True solar time | solar_time.py          | Time offset                                                   | Solar hour angle                              |                  | :material-checkbox-marked-circle:{.checked} |                |
| :material-checkbox-marked-circle:{.checked} | Solar hour angle      | solar_hour_angle.py    | True solar time                                               | Solar zenith, Solar altitude, Solar azimuth   |                  | :material-checkbox-marked-circle:{.checked} |                |
| :material-checkbox-marked-circle:{.checked} | Solar declination     | solar_declination.py   | Fractional year                                               | Solar zenith                                  |                  | :material-checkbox-marked-circle:{.checked} |                |
| :material-checkbox-marked-circle:{.checked} | Solar zenith          | solar_zenith.py        | Solar declination, Solar hour angle, Atmospheric refraction   | Solar altitude                                |                  | :material-checkbox-marked-circle:{.checked} |                |
| :material-checkbox-marked-circle:{.checked} | Solar altitude        | solar_altitude.py      | Solar hour angle, Solar zenith                                | Solar position                                |                  | :material-checkbox-marked-circle:{.checked} |                |
| :material-checkbox-marked-circle:{.checked} | Solar azimuth         | solar_azimuth.py       | Solar declination, Solar hour angle, Solar zenith             | Solar position                                |                  | :material-checkbox-marked-circle:{.checked} |                |

Further are listed more _quantities_
which are, however, not _hard-requirements_
for the calculations of photovoltaic performance.

Also to support ?

| Status | Quantity         | Implementation      | Requires | Required by | Algorithm | Time series | Optimisation |
|--------|------------------|---------------------|----------|-------------|-----------|-------------|--------------|
|        | Events           | events.py           |          |             |           |             |              |
|        | Event hour angle | event_hour_angle.py |          |             |           |             |              |
|        | Event time       | event_time.py       |          |             |           |             |              |
|        | Local time       | local_time.py       |          |             |           |             |              |


[^*]: If the timezone is such that after conversion to UTC it changes the day, then is this required ?
