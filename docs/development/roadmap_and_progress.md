---
icon: material/list-status
tags:
  - Development
  - Roadmap
  - Progress
---

<style>
.twemoji.checked svg {
    color: #00e676;
}
.twemoji.blank svg {
    color: rgba(0, 0, 0, 0.07);
}
</style>

??? note "Stages, Status and Icons"

    !!! info inline "Stages"

        `Planning`

        : Items that have not yet been started
         
        `Design`

        : Scoping & user experience design
         
        `Develop`

        : Actively building
        
        `Test`

        : Testing and iterating
         
        `Beta`
         
        : Release for optional use, may have rough edges or additional features in development

        `Release`
         
        : Stable release
         
        `Public Beta`

        : Release for optional use, may have rough edges or additional features in development

        `Full Release`
         
        : Stable public release

    !!! note inline "Status"

        - [x] Completed

        :material-progress-question: Work In Progress

        - [ ] In Queue  

    !!! info inline "Icons"

        :material-clock-start: start timestamp

        :material-clock-end: end timestamp

        :material-table-arrow-left: input optional parameters

        ∡ Tilt angle

        ↻ Orientation angle

        ∡ Inclined irradiance components

        ⭸ Horizontal irradiance component

        ⦜ Normal (right) angle

        ⭍ Effective irradiance

        % Fraction (i.e. for sky-view fraction)

        ⌁ Power
        
        ㎾ Power unit

        ㎾h Energy unit

        ⌇ Irradiance

        ⌇% Relative irradiance

        W/m² Irradiance unit
---

## :material-pencil: Input

!!! abstract "Read input arguments, parameters and data"

    | Read functions                                                          | Plan | Design | Develop | Test | Beta | Optimise | Release |
    |-------------------------------------------------------------------------|------|--------|---------|------|------|----------|---------|
    | ^^Read input required arguments^^                                       |      |        |         |      |      |          |         |
    | Read :material-clock-start: start timestamp for time series                                    | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read :material-clock-end: end timestamp for time series                                      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read :material-table-arrow-left: input optional parameters                                          | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read ∡ Tilt angle                                                       | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read ↻ Orientation angle                                                | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | ^^Identify geographic location^^                                        |      |        |         |      |      |          |         |
    | Read geographic location :fontawesome-solid-location-crosshairs: Longitude                                      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read geographic location :fontawesome-solid-location-crosshairs: Latitude                                       | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read input (data, arguments)                                            | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read input data [solar irradiance, meteorological variables, elevation] | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read input data :material-sun-wireless-outline: solar irradiance                                        | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read external data :material-chart-multiple: time series (ex.: SIS, SID)                                   | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | ^^Read input data :material-weather-partly-cloudy: meteorological variables^^                            |      |        |         |      |      |          |         |
    | Read input :material-thermometer: temperature                                                  | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read input :wind_blowing_face: wind speed                                                   | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   |      |          |         |
    | Read input :material-elevation-rise: elevation data                                               | :material-checkbox-marked-circle:{.checked}   |        |         |      |      |          |         |
    | Read input horizon data (or calculate on-the-fly?)                      | :material-checkbox-marked-circle:{.checked}   |        |         |      |      |          |         |

## :material-calculator-variant-outline: Calculations

!!! abstract "Calculate solar geometry variables, solar irradiance components, photovoltaic performance"

    | Calculation functions                                                      | Plan                                        | Design                                      | Develop                                     | Test                                        | Beta                                        | Optimise | Release |
    |----------------------------------------------------------------------------|---------------------------------------------|---------------------------------------------|---------------------------------------------|---------------------------------------------|---------------------------------------------|----------|---------|
    | ^^Generate time series^^ based on user input `start` and `end` timestamps  | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} |          |         |
    | Set default ∡ Tilt angle                                                   | :material-checkbox-marked-circle:{.checked} |                                             |                                             |                                             |                                             |          |         |
    | Set default ↻ Orientation angle                                            | :material-checkbox-marked-circle:{.checked} |                                             |                                             |                                             |                                             |          |         |
    | Calculate horizon data on-the-fly (alternative to Read input horizon data) | :material-checkbox-marked-circle:{.checked} |                                             |                                             |                                             |                                             |          |         |
    | Calculate/Identify shading [Shade]                                         | :material-checkbox-marked-circle:{.checked} |                                             |                                             |                                             |                                             |          |         |
    | Select energy model                                                        | :material-checkbox-marked-circle:{.checked} |                                             |                                             |                                             |                                             |          |         |
    | Calculate global irradiance                                                | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} |                                             | :material-checkbox-marked-circle:{.checked} |          |         |
    | Read spectral correction values                                            | :material-checkbox-marked-circle:{.checked} |                                             |                                             |                                             |                                             |          |         |
    | Calculate solar geometry variables [^0]                                         | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} |          |         |
    | Identify solar position [Above horizon, Low angle, Below horizon]          | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} |                                             | :material-checkbox-marked-circle:{.checked} |          |         |
    | Optimise tilt[^slope] if requested                                                | :material-checkbox-marked-circle:{.checked} |                                             |                                             |                                             |                                             |          |         |
    | Optimise tilt[^slope] and orientation[^aspect] if requested                                     | :material-checkbox-marked-circle:{.checked} |                                             |                                             |                                             |                                             |          |         |
    | Set tilt and orientation depending on tracking type ?                          | :material-progress-question:                |                                             |                                             |                                             |                                             |          |         |
    | Calculate total radiation                                                  | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} |                                             | :material-checkbox-marked-circle:{.checked} |          |         |
    | Calculate system performance                                               | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} | :material-checkbox-marked-circle:{.checked} |                                             | :material-checkbox-marked-circle:{.checked} |          |         |

[^0]: See also detailed Implementation for [Solar Position](solar_position.md)

[^slope]: In PVGIS <= 5.x and older, `tilt` is referred as `slope` angle

[^aspect]: In PVGIS <= 5.x and older, `orientation` is referred as `aspect` angle
                                                                                                                                   
## :octicons-graph-24: Output

!!! abstract "Output"                                                                                                             
                                                                                                                                 
    | Output quantities and attributes                                     | Plan | Design | Develop | Test | Beta | Optimise | Release |
    |----------------------------------------------------------------------|------|--------|---------|------|------|----------|---------|
    | ϑ Longitude                                                          | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ϕ Latitude                                                           | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Elevation                                                            | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ∡ Tilt                                                               | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ↻ Orientation                                                        | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Timestamps                                                           | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Time zone (if user requested a local time)                           | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ⌁ Power                                                              | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Energy (aggregated time series of PV power series)                   | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Efficiency %                                                         | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Loss                                                                 | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ^^Global irradiance^^                                                | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Global broadband inclined ∡                                          | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Global broadband horizontal ==modelled== ⭸                                      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Global broadband horizontal read from external source ⭸              | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Globel spectrally resolved inclined irradiance                       | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   |      |          |         |
    | ^^Direct^^                                                           | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Direct irradiance **effective** ⭍                                    | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Direct inclined ∡                                                    | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Direct horizontal irradiance ==modelleld== ⭸                         | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Direct horizontal read from external source ⭸                        | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Direct normal irradiance ⦜                                           | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ^^Diffuse irradiance^^                                               | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Diffuse irradiance **effective** 🗤⭍                                  | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Diffuse inclined irradiance ∡                                        | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Diffuse horizontal irradiance ==modelled== ⭸                         | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Diffuse horizontal calculated from external source ⭸                 | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Diffuse clear sky irradiance ☀                                       | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ^^Reflected irradiance^^                                             | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Reflected irradiance **effective** ☈⭍                                | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Reflected ∡                                                          | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ^^Extraterrestrial irradiance^^                                      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Extra ⦜                                                              | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Extraterrestrial normal irradiance ⦜ ==modelled==                    | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ^^Solar geometry variables^^                                         | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Overview ⦩⦬ solar position parameters for a moment or 📈 time series | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ⭸ Solar incidence angle                                              | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | 🕛 🌐 Hour angle (ω)                                                 | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | 🌅 Hour angle (ω) at sun rise and set angle                          | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ⦬ Solar azimuth angle                                                | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Solar zenith angle                                                   | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ∢ Solar declination angle                                            | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ⦩ Solar altitude angle                                               | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ^^Other quantities^^                                                 | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Refracted altitude                                                   | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Albedo **constant** *modifiable*                                     | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Sky view fraction %                                                  | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Solar constant *modifiable*                                          | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Perigee constant *modifiable*                                        | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Eccentricity *modifiable*                                            | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Linke′ turbidity adjusted                                            | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Linke turbidity                                                      | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Rayleigh index                                                       | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Air mass index                                                       | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ^^Metadata^^                                                         | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Efficiency Algorithm                                                 | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Irradiance source                                                    | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | Incidence algorithm                                                  | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ⯐ Positioning algorithm                                              | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |
    | ⏲ Timing algorithm                                                   | :material-checkbox-marked-circle:{.checked}   | :material-checkbox-marked-circle:{.checked}     | :material-checkbox-marked-circle:{.checked}      | :material-progress-question:   | :material-checkbox-marked-circle:{.checked}   |          |         |

## Help :material-help:

!!! ract "Introduction in to .."

    | Command / Subject | Introduction subcommand | Description                                |
    |-------------------|-------------------------|--------------------------------------------|
    | `power`           | `intro`                 | A short primer on photovoltaic performance |
    | `irradiance`      | `intro`                 | A short primer on solar irradiance         |
    | `position`        | `intro`                 | A short primer on solar geometry           |
