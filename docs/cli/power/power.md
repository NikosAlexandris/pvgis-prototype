---
icon: material/solar-power 
title: Photovoltaic performance
subtitle: Estimate photovoltaic performance over a time series
tags:
  - How-To
  - CLI
---

!!! abstract "Estimate photovoltaic performance"

    | Command                                               | Subcommand                                                    | Description                                                                                                                                      |
    |-------------------------------------------------------|---------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
    | :octicons-command-palette-24: [**`power`**](power.md) |                                                               | 🔌 Estimate the performance of a photovoltaic system over a time series                                                                          |
    |                                                       | :octicons-command-palette-24: [**`broadband`**](broadband.md) | :simple-spectrum: Estimate the photovoltaic performance based on broadband irradiance, ambient temperature and wind speed                        |
    |                                                       | :octicons-command-palette-24: [**`spectral`**](spectral.md)                                 | :material-heat-wave: Estimate the photovoltaic performance based on spectrally resolved irradiance, ambient temperature and wind speed Prototype |

We can see the available `power` commands in the command line :

``` bash exec="true" result="ansi" source="above"
pvgis-prototype power
```
