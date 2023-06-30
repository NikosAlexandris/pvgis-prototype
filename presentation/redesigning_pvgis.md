# PVGIS

..


# Current state

..


# Redesign

## Why?

- We cannot know unless we try.
- Transparency
- Reproducibility


## Approach

> Premature optimization is the root of all evil

[Donald Knuth](https://en.wikipedia.org/wiki/Donald_Knuth)

- KIS~~S~~
- DRY


## Structure

_Core_ **API**  +  **CLI**  +  _Web_ **API**


### Application Programming Interface

    : Python  Numpy  Numba
    : Dask
    : ..


### Command Line Interface

    : Typer  (Click)


### Web API

    : FastAPI


- Plotting

    : Holoviz


## User Interface

..


# Examples


## Solar `time`

Based on _Skyfield_

``` bash
pvgis-prototype time -m Skyfield 6.6327 46.5218 2023-06-26T12:04:25
```

Based on _NOAA's Equation of Time_

``` bash
pvgis-prototype time -m NOAA 6.6327 46.5218 2023-06-26T12:04:25
```


## Web API 

First, run the server:

``` bash
uvicorn pvgisprototype.webapi:app --reload
```

Then, demonstration of an endpoint


### Solar `time` again

- [`http://localhost:8000/calculate_solar_time_skyfield/?longitude=-70&latitude=40&timestamp=2023-06-26T12:00:00&timezone=America/New_York`](http://localhost:8000/calculate_solar_time_skyfield/?longitude=-70&latitude=40&timestamp=2023-06-26T12:00:00&timezone=America/New_York)

    - functin   : `calculate_solar_time_skyfield`
    - longitude : -70
    - latitude  : 40
    - timestamp : 2023-06-26T12:00:00
    - timezone  : 'America/New_York'


- [`http://localhost:8000/calculate_solar_time_skyfield/?longitude=6.6327&latitude=46.5218&timestamp=2023-06-26T12:04:25&timezone=CET`](http://localhost:8000/calculate_solar_time_skyfield/?longitude=6.6327&latitude=46.5218&timestamp=2023-06-26T12:04:25&timezone=CET)


### Direct inclined irradiance

- API endpoint to calculate the direct inclined irradiance:

```
..
```

### Plot solar declination

- [Plot solar declination for 2023](http://localhost:8000/plot_solar_declination_one_year_bokeh?year=2023)


## Diagnostic tools

```
plot-data outliers --sensitivity-factor 1.25 /spacetime/pvgis/from_jeodpp_nextcloud/raster/era5/2009_01_cds_era5_surface_net_solar_radiation.nc 0.2 0.2 && tycat outliers_iqr_with_sensitivity_125_on_surface_net_solar_radiation.png
```

# Concerns of speed


- **Tested?** Not yet!  However,

    - renewables.ninja
    - 

# Progress


## `rsun_standalone_hourly_opt.cpp`

Functions :

|       | Function                                | start line | end  | name in Python                                             | Remakrs                                                   |
|-------|-----------------------------------------|------------|------|------------------------------------------------------------|-----------------------------------------------------------|
| - [ ] | systemEfficiency()                      | 75         | 78   |                                                            |                                                           |
| - [ ] | setSystemEfficiency()                   | 79         | 82   |                                                            |                                                           |
| - [ ] | useTimeOffset()                         | 85         | 88   |                                                            |                                                           |
| - [ ] | setUseTimeOffset()                      | 89         | 92   |                                                            |                                                           |
| - [x] | ~~joules2~~ Not used!                   | 98         | 189  |                                                            |                                                           |
| - [x] | joules_onetime()                        | 192        | 284  | to calculate_hourly_radiation.py                           |                                                           |
| - [x] | EnergyContributionPerformanceModelMPP() | 286        | 396  | energy_contribution_performance_model_mpp.py               |                                                           |
| - [x] | optimizeSlope()                         | 400        | 532  | optimise_slope.py                                          |                                                           |
| - [x] | optimizeSlopeAspect()                   | 535        | 868  |                                                            |                                                           |
| - [ ] | main()                                  | 889        | 2013 |                                                            |                                                           |
| - [ ] | joules_with_unshadowed()                | 2025       | 2147 |                                                            |                                                           |
| - [x] | dateFromHour()                          | 2158       | 2205 | get_day_from_hour_of_year() in solar_geometry_variables.py |                                                           |
| - [ ] | updateGeometryYear()                    | 2208       | 2454 |                                                            |                                                           |
| - [x] | calculateGeometryYear()                 | 2456       | 2708 | solar_declination.py                                       | Among others, calculates solar declination based on Jenco |
| - [x] | calculateTotal()                        | 2711       | 2802 |                                                            |                                                           |
| - [x] | calculate()                             | 2805       | 3128 |                                                            |                                                           |

average_SD() -> average_standard_deviation.py

## rsun_base.c

| Function                                                           | Start line | End | Notes
|--------------------------------------------------------------------|------------|-----|---------------------------------------------------------------------------------------------------------------------|
| - [ ] brad.c                                                       |            |     | Not used                                                                                                            |
| - [x] brad_angle_irradiance.c                                      |            |     | Defines s0, uses sh : s0 == sh. sh stands for 'solar height/declination' != altitude ?                              |
| - [ ] brad_angle_loss.c                                            |            |     |                                                                                                                     |
| - [ ] brad_angle_loss_with_cs.c                                    |            |     |                                                                                                                     |
| - [ ] drad.c                                                       |            |     |                                                                                                                     |
| - [x] drad.cpp                                                     |            |     |                                                                                                                     |
| - [ ] drad_angle_irradiance.c                                      |            |     |                                                                                                                     |
| - [ ] drad_angle_loss.c                                            |            |     |                                                                                                                     |
| - [x] drad_angle_loss.cpp                                          |            |     |                                                                                                                     |
| - [ ] drad_angle_loss_with_cs.c                                    |            |     |                                                                                                                     |
| - [ ] efficiency.c                                                 |            |     |                                                                                                                     |
| - [ ] efficiency_ww.c                                              |            |     |                                                                                                                     |
| - [ ] initEfficiencyCoeffs.c                                       |            |     |                                                                                                                     |
| - [ ] initEfficiencyCoeffsWind.c                                   |            |     |                                                                                                                     |
| - [ ] SplinesMonthlyTemperature.c                                  |            |     |                                                                                                                     |
| - [x] calculateAngleLoss.c                                         |            |     | Calculates loss to direct horizontal irradiance due to solar declination. Hardcodes incidence angle (AOIConstants)! |
| - [x] calculate_angle_loss.c                                       |            |     | Variable                                                                                                            |
| - [x] com_declin.c                                                 |            |     | Inverts sign of calculated declination due to trigonometry mathematical error!                                      |
| - [x] com_par.c                                                    |            |     | Simpler approximations. How do they compare with others?                                                            |
| - [x] com_par_const.c                                              |            |     |                                                                                                                     |
| - [x] com_sol_const.c                                              |            |     |                                                                                                                     |
| - [ ] correctTemperatureElevation.c                                |            |     |                                                                                                                     |
| - [x] dateFromHour.c                                               |            |     | Complex, not needed                                                                                                 |
| - [ ] dni_rad.c                                                    |            |     |                                                                                                                     |
| - [ ] imageTimeOffset.c                                            |            |     |                                                                                                                     |
| - [x] lumcline2.c                                                  |            |     | Calculates the solar declination based on Jenco                                                                     |
| - [ ] rearrangeHorizon.c                                           |            |     |                                                                                                                     |
| - [ ] satgeo.c                                                     |            |     |                                                                                                                     |
| - [ ] satgeomsgnew.c                                               |            |     |                                                                                                                     |
| - [ ] slotHourOffset.c                                             |            |     |                                                                                                                     |
| - [ ] small_functions_from_start_and_before_calculate_angle_loss.c |            |     |                                                                                                                     |
| - [ ] temperature.c                                                |            |     |                                                                                                                     |


# Links

- [Python]: https://www.python.org/
- [Numpy]: https://numpy.org/
- [Numba]: https://numba.pydata.org/
- [Mojo]: 
- [Holoviz]: https://holoviz.org/#
- 
- [Skyfield]:
- [SPA]:
- [NOAA's Equation of Time]:
