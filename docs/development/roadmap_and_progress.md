---
tags:
  - Development
  - Roadmap
  - Progress
---

# Roadmap

| Item | Planning | Design | Develop & Test | Beta | Release |
|------|----------|--------|----------------|------|---------|

1.  Define  `main()`

2.  Initialise variables

   - Declare several variables of different types, including 
   - Initialize some of the variables with specific values.

3.   Parse input arguments

4.   Identify pixel row and column offsets

5.   Select energy model

6.   Read elevation data

7.   Use horizon data

8.   Set number of hours for iterations

9.   Read {term}`SIS` and {term}`SID` data, compute global irradiance

10.  Read spectral correction values, temperature & wind speed time series

11.  Calculate solar geometry variables

12.  Optimise slope if requested

13.  Optimise slope and aspect if requested

14.  Set slope and aspect depending on tracking type

15.  Calculate total radiation

16.  Calculate system performance

17.  Return `0` and close `main()`

## `rsun_standalone_hourly_opt.cpp`

Functions 

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


## rsun_base.c

| Function                                                           | Start line | End | Notes
|--------------------------------------------------------------------|------------|-----|---------------------------------------------------------------------------------------------------------------------|
| - [ ] brad.c                                                       |            |     | Not used                                                                                                            |
| - [x] brad_angle_irradiance.c                                      |            |     | Defines s0, uses sh  s0 == sh. sh stands for 'solar height/declination' != altitude ?                              |
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
