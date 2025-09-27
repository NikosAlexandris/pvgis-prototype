---
icon: material/tools
title: Irradiance
tags:
  - CLI
  - Tools
  - Solar Irradiance
hide:
  - toc
---

With PVGIS,
you can calculate individual solar irradiance components at will. Almost!
While effort has been put to set sane default values for optional parameters,
there are many parameters at your fingertips.

<div class="grid cards" markdown>

- :octicons-command-palette-24: [**`irradiance`**]() :material-sun-wireless: Estimate the solar irradiance incident on a solar surface

    ---

    | Subcommand                                               | Description                                                   |
    |----------------------------------------------------------|---------------------------------------------------------------|
    | :octicons-command-palette-24: [**`introduction`**]()     | :fontawesome-solid-info: A short primer on solar irradiance   |
    | :octicons-command-palette-24: [**`global`**]()           | ⸾ Calculate the global irradiance                             |
    | :octicons-command-palette-24: [**`direct`**]()           | ⇣ Calculate the direct irradiance                             |
    | :octicons-command-palette-24: [**`diffuse`**]()          | 🗤 Calculate the diffuse irradiance                            |
    | :octicons-command-palette-24: [**`reflected`**]()        | ☈ Calculate the clear-sky ground reflected irradiance         |
    | :octicons-command-palette-24: [**`extraterrestrial`**]() | ☀ Calculate the extraterrestrial normal irradiance            |
    | :octicons-command-palette-24: [**`loss`**]()             | ⦟ Calculate the reflectivity loss factor Yet not implemented! |
    | :octicons-command-palette-24: [**`limits`**]()           | [] Calculate physically possible irradiance limits            |

</div>

We can see the list of available subcommands for `irradiance` by running

``` bash exec="true" result="ansi" source="above"
pvgis-prototype irradiance
```
