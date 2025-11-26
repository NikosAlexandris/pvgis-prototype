---
icon: material/file-document-arrow-right-outline
title: TMY
tags:
  - PVGIS
  - Conventions
  - Concepts
  - Solar Azimuth Origin
  - Units
  - Conversions
  - UTC
  - Local Time
  - Date
  - Time
  - Datetime
  - Assumptions
  - Solar Incidence Definition
  - Solar Positioning
  - Photovoltaic Efficiency
  - Spectral Data
---

PVGIS follows standardized conventions
to ensure consistency and accuracy
across all solar energy calculations.
The following sections overview fundamental conventions.

??? seealso "Conventions in the command line ?"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype conventions
    ```

## Azimuth Origin

PVGIS uses the **North-Up convention** where **North = 0°**.

```
        N (0°)
         ▲
    W ◄──┼──► E (90°)
         ▼
       S (180°)
```

**Conversions from other systems**


| Input System | Conversion to North-Up |
|--------------|------------------------|
| South-based (S=0°) | `North-Up = Input - 180°` |
| East-based (E=0°)  | `North-Up = Input - 90°`  |


## Angular Units

- All calculations use **radians** for precision  [*Default*]
- Atmospheric refraction uses **degrees**  [*Exception*]

The `calculate_refracted_solar_altitude_series()` function
requires degree inputs and returns degree outputs.

## Time Zones

**All calculations are performed in UTC** by default.

Local time support converts :

1. Local time → UTC (input)
2. Perform calculations in UTC
3. UTC → Local time (output)

## Timestamps

PVGIS handles timestamps flexibly :

- **With external time series data:** Respects existing timestamps and filters by `start_time`/`end_time`
- **Without external time series data:** Generates timestamps using at least 2 of:

  - `start_time`
  - `end_time`
  - `frequency` (default: hourly)
  - `periods`

## Solar Incidence Angle

PVGIS defines the incidence angle
using the **sun-vector to surface-normal convention**
following the Iqbal model.

## Solar Positioning

**Algorithm:** NOAA solar geometry equations

**Validation:**
  - Hundreds of thousands of automated tests
  - Cross-validated against US Naval Observatory (USNO) data

## Spectral Response

PV efficiency coefficients are derived from **ESTI Lab research** (JRC Unit C2, European Commission).

**Key concepts:**

- **Spectral Factor:** Ratio of actual spectrum to reference spectrum (AM1.5)
- **Efficiency Curves:** Module-type-specific performance adjustments

## Input Data Requirements

Solar irradiance data must have:

- Consistent temporal resolution
- Complete temporal coverage for the period of interest
- Uniform time steps
