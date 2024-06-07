---
title: PVGIS 5.2
tags:
  - Reference
  - PVGIS v5.2
  - Features
  - Functionality
  - Capabilities
  - Archived notes
---

## Photovoltaic performance

The Workflow in PVGIS v5.2 is :

```
[II] In-Plane Irradiance
     │
     │ (Reflectivity Calculation)
     ▼
[RE] Reflectivity Effect = II * Reflectivity
     │
     │ (Temperature & Low Irradiance Adjustment)
     ▼
[TE] Temp. & Low Irradiance Effect = II * RE * Temp. & Low Irradiance Coeff.
     │
     │ (Power Calculation)
     ▼
 [P] Power = II + II * RE * TE
     │
     │ (Spectral Calculation)
     ▼
[SE] Spectral Effect = P * Spectral Factor
     │
     │ (Sum of Effects)
     ▼
[EP] "Effective" Power = P + SE
     │
     │ (System Loss Calculation)
     ▼
[SL] System Loss = EP * System Loss Factor
     │
     │ (Final Power Output)
     ▼
[PP] Final Photovoltaic Power Output = EP + SL
```

## Functions 

|                                   | C function                              | start line | end  | in Python                                                  | Remarks                                                   |
|-----------------------------------|-----------------------------------------|------------|------|------------------------------------------------------------|-----------------------------------------------------------|
| :material-checkbox-blank-circle:  | systemEfficiency()                      | 75         | 78   |                                                            |                                                           |
| :material-checkbox-blank-circle:  | setSystemEfficiency()                   | 79         | 82   |                                                            |                                                           |
| :material-checkbox-blank-circle:  | useTimeOffset()                         | 85         | 88   |                                                            |                                                           |
| :material-checkbox-blank-circle:  | setUseTimeOffset()                      | 89         | 92   |                                                            |                                                           |
| :material-checkbox-marked-circle: | ~~joules2~~ Not used!                   | 98         | 189  |                                                            |                                                           |
| :material-checkbox-marked-circle: | joules_onetime()                        | 192        | 284  | to calculate_hourly_radiation.py                           |                                                           |
| :material-checkbox-blank-circle:  | EnergyContributionPerformanceModelMPP() | 286        | 396  | energy_contribution_performance_model_mpp.py               |                                                           |
| :material-checkbox-blank-circle:  | optimizeSlope()                         | 400        | 532  | optimise_slope.py                                          |                                                           |
| :material-checkbox-blank-circle:  | optimizeSlopeAspect()                   | 535        | 868  |                                                            |                                                           |
| :material-checkbox-blank-circle:  | main()                                  | 889        | 2013 |                                                            |                                                           |
| :material-checkbox-blank-circle:  | joules_with_unshadowed()                | 2025       | 2147 |                                                            |                                                           |
| :material-checkbox-marked-circle:                             | dateFromHour()                          | 2158       | 2205 | get_day_from_hour_of_year() in solar_geometry_variables.py |                                                           |
| :material-checkbox-blank-circle:  | updateGeometryYear()                    | 2208       | 2454 |                                                            |                                                           |
| :material-checkbox-marked-circle:                             | calculateGeometryYear()                 | 2456       | 2708 | solar_declination.py                                       | Among others, calculates solar declination based on Jenco |
| :material-checkbox-marked-circle: | calculateTotal()                        | 2711       | 2802 |                                                            |                                                           |
| :material-checkbox-marked-circle: | calculate()                             | 2805       | 3128 |                                                            |                                                           |

## rsun_base.c

| Function                                                                                      | Start line | End | Notes
|-----------------------------------------------------------------------------------------------|------------|-----|---------------------------------------------------------------------------------------------------------------------|
| :material-checkbox-blank-circle: brad.c                                                       |            |     | Not used                                                                                                            |
| :material-checkbox-marked-circle: brad_angle_irradiance.c                                     |            |     | Defines s0, uses sh  s0 == sh. sh stands for 'solar height/declination' != altitude ?                               |
| :material-checkbox-blank-circle: brad_angle_loss.c                                            |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: brad_angle_loss_with_cs.c                                    |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: drad.c                                                       |            |     |                                                                                                                     |
| :material-checkbox-marked-circle: drad.cpp                                                    |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: drad_angle_irradiance.c                                      |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: drad_angle_loss.c                                            |            |     |                                                                                                                     |
| :material-checkbox-marked-circle: drad_angle_loss.cpp                                         |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: drad_angle_loss_with_cs.c                                    |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: efficiency.c                                                 |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: efficiency_ww.c                                              |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: initEfficiencyCoeffs.c                                       |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: initEfficiencyCoeffsWind.c                                   |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: SplinesMonthlyTemperature.c                                  |            |     |                                                                                                                     |
| :material-checkbox-marked-circle: calculateAngleLoss.c                                        |            |     | Calculates loss to direct horizontal irradiance due to solar declination. Hardcodes incidence angle (AOIConstants)! |
| :material-checkbox-marked-circle: calculate_angle_loss.c                                      |            |     | Variable                                                                                                            |
| :material-checkbox-marked-circle: com_declin.c                                                |            |     | Inverts sign of calculated declination due to trigonometry mathematical error!                                      |
| :material-checkbox-marked-circle: com_par.c                                                   |            |     | Simpler approximations. How do they compare with others?                                                            |
| :material-checkbox-marked-circle: com_par_const.c                                             |            |     |                                                                                                                     |
| :material-checkbox-marked-circle: com_sol_const.c                                             |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: correctTemperatureElevation.c                                |            |     |                                                                                                                     |
| :material-checkbox-marked-circle: dateFromHour.c                                              |            |     | Complex, not needed                                                                                                 |
| :material-checkbox-blank-circle: dni_rad.c                                                    |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: imageTimeOffset.c                                            |            |     |                                                                                                                     |
| :material-checkbox-marked-circle: lumcline2.c                                                 |            |     | Calculates the solar declination based on Jenco                                                                     |
| :material-checkbox-blank-circle: rearrangeHorizon.c                                           |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: satgeo.c                                                     |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: satgeomsgnew.c                                               |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: slotHourOffset.c                                             |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: small_functions_from_start_and_before_calculate_angle_loss.c |            |     |                                                                                                                     |
| :material-checkbox-blank-circle: temperature.c                                                |            |     |                                                                                                                     |
