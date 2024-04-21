---
icon: material/console-line
description: A collection of How-To recipes on the use of PVGIS
title: How to work with PVGIS
subtitle: Learn how to work with PVGIS interactively
tags:
  - How-To
  - CLI
---

## Toolbox Overview

PVGIS is _also_ a collection of command line tools.

<div class="grid cards" markdown>

- :material-solar-power-variant:{ .lg .middle } __Photovoltaic performance__

    ---

    :octicons-command-palette-24: [**`power`**](power/power.md) 🔌 Estimate the performance of a photovoltaic system over a time series

    | Subcommand                                                                                    | Description                                                                                                                                      |
    |-----------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
    | :octicons-command-palette-24: [**`broadband`**](power/power.md##Broadband irradiance)         | :simple-spectrum: Estimate the photovoltaic performance based on broadband irradiance, ambient temperature and wind speed                        |
    | :octicons-command-palette-24: [**`spectral`**](power/power.md##Spectrally resoled irradiance) | :material-heat-wave: Estimate the photovoltaic performance based on spectrally resolved irradiance, ambient temperature and wind speed Prototype |

- :octicons-graph-24:{ .lg .middle } __Time Series__

    ---

    :octicons-command-palette-24: [**`series`**]() 💹 Work with time series
    
    :octicons-command-palette-24: [**`irradiance`**]() :material-sun-wireless: Estimate the solar irradiance incident on a solar surface

    |                                               |                                                             |
    |-----------------------------------------------|-------------------------------------------------------------|
    | :octicons-command-palette-24: [**`intro`**]() | :fontawesome-solid-info: A short primer on solar irradiance |
    
- :octicons-sun-24: :triangular_ruler:{ .lg .middle } __Solar Position__

    ---

    :octicons-command-palette-24: [**`time`**]() :material-sun-clock: Calculate the solar time for a location and moment

    :octicons-command-palette-24: [**`position`**]() :material-sun-angle: Calculate solar geometry parameters for a location and moment in time
    
    | Subcommand                                                            | Description                                                                      |
    |-----------------------------------------------------------------------|----------------------------------------------------------------------------------|
    | :octicons-command-palette-24: [**`intro`**](position/introduction.md) | :fontawesome-solid-info: A short primer on solar geometry

    :octicons-command-palette-24: [**`surface`**]() 󰶛  Calculate solar surface geometry parameters for a location and moment in time

- :material-information-variant:{ .lg .middle } __Reference__

    ---

    |                                         |                                                |
    |-----------------------------------------|------------------------------------------------|
    | 📖 Manual for solar radiation variables | :octicons-command-palette-24: [**`manual`**]() |

- :material-translate:{ .lg .middle } __Diagnostics__

    ---

    |                          |                                                   |
    |--------------------------|---------------------------------------------------|
    | 🧰  Diagnostic functions | :octicons-command-palette-24: [**`utilities`**]() |

</div>


Welcome yourself in the PVGIS command line interface (CLI) 

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype
```
