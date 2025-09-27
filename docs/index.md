---
icon: material/eye
title: PVGIS
subtitle: Photovoltaic Geographic Information System
tags:
  - PVGIS
  - Overview
---

[![pipeline status](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/badges/mkdocs/pipeline.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commits/mkdocs) 
[![coverage report](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/badges/mkdocs/coverage.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commits/mkdocs) 
[![Latest Release](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/badges/release.svg)](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/releases) 
---

# PVGIS

:material-human-greeting-variant: Welcome to the documentation of
the Photovoltaic Geographical Information System (PVGIS).

[PVGIS][PVGIS]
is an open [web application][PVGIS Web Application]
of the :flag_eu: European Commission.
It is developed and maintained
in the [Joint Research Centre (JRC)][JRC]
for over two decades
by the Energy Efficiency and Renewables Unit (Ispra) of the Energy,
Transport and Climate directorate.

[JRC]: https://joint-research-centre.ec.europa.eu/index_en

The content is designed to help you navigate through
the features, capabilities, and detailed references
for the PVGIS command line interface (CLI),
its Web application programming interface (Web API),
and its core API. (1)
{ .annotate }

1. The _Web_ API is not the same as the _core_ API.
   The former _consumes_ the latter
   to produce a FastAPI-based Web API interface.

## Features & Capabilities

PVGIS
offers cost-free public service insights
on solar radiation and photovoltaic performance,
providing location-specific estimates of power output
for systems using various PV technologies.

<div class="grid cards" markdown>

- :material-solar-power-variant:{ .lg .middle } __Photovoltaic Potential__

    ---

    - :material-solar-power: Photovoltaic Performance Analysis
    - :material-power-plug: Grid-connected & :material-battery-high: Stand-alone
    - :material-fingerprint: [Fingerprint](cli/fingerprint.md)ed reproducible calculations
    - :material-qrcode-scan: [QR-Code](cli/qrcode.md) shareable results

- :octicons-graph-24:{ .lg .middle } __Time Series__

    ---

    - :material-sun-wireless-outline: Solar Radiation
    - :material-thermometer: Temperature
    - :wind_blowing_face: Wind Speed 
    - :material-weather-partly-cloudy: Typical Meteorological Year for 9 climate variables
    
- :material-map:{ .lg .middle } __Coverage & Maps__ (1)
{ .annotate }

    1. !!! warning "Printing ?"
           [:thinking: https://thinkbeforeprinting.org/](https://thinkbeforeprinting.org/)

    ---

    - Europe & Africa :earth_africa:
    - Largely Asia :earth_asia:
    - America :earth_americas:
    - Country/regional maps of solar resource & PV potential

- :fontawesome-solid-people-group:{ .lg .middle } __Public Service__

    ---

    - Supported by the 🇪🇺 European Commission
    - :material-currency-eur-off: Cost free
    - :material-lock-off: Open access
    - :material-search-web: [> 50K Web API requests / week](reference/web_traffic.md)

- :octicons-feed-public-16:{ .lg .middle } __Open by design__

    ---

    ![](images/Logo_EUPL.svg.png){align=right height=100px width=100px}

    - :material-language-python: Python [API](#) based on :simple-numpy: NumPy
    - :material-web: [Web API](#) based on :simple-fastapi: FastAPI
    - :material-console: [CLI](#) based on Typer
    - :material-open-source-initiative: Open Source [License](#) EUPL-1.2


- :material-translate:{ .lg .middle } __Languages__

    ---

    ![](images/languages-in-pvgis.svg){align=right height=100px width=100px}

    - English
    - French  |  German
    - Spanish  |  Italian

</div>

For a full list of features, see the [Features](overview/features.md) page.

## Components

<div class="grid cards" markdown>

- :material-web: __[Web API](#)__

    ---

    **New to PVGIS' Web API ?**

    Start with our entry level [Web API](web_api/index.md) guide
    to get up and running quickly.

- :material-console: __[CLI](#)__

    ---

    **Interested to work interactively ?**

    Check out the [collection of command line tools](cli/index.md)

- :material-language-python: __Python [API](#)__

    ---

    **For advanced users and programmers**

    Need to work programmatically with the [PVGIS API](api/index.md) ?
    Peek over relevant [API examples]() and the [source code](source_code/index.md) documentation.

- Development

    ---

    **Interested in contributing ?**

    Head over to the [Development](development/index.md) section
    and check out :

    - [Contribution Guidelines](development/contribution_guidelines.md) & [Conventions](development/conventions.md)
    - [Adding New Features](development/adding_new_features.md)
    - [Testing](development/pytest.md)

</div>

# Support & Community

If you have questions or need support,
check out the [FAQ](support/faq.md) section.

Thank you for choosing PVGIS for your solar irradiance calculation needs!
:fontawesome-solid-hands-praying:

### Contact points

<div class="grid cards" markdown>

- :material-at: __Support Mailbox__

    ---

    Questions and comments can be sent to our mailbox:

    [JRC-PVGIS@ec.europa.eu](mailto:JRC-PVGIS@ec.europa.eu)

- :fontawesome-solid-map-location-dot: __Postal Address__

    ---

    European Commission, Joint Research Centre
    Energy Efficiency and Renewables Unit
    via E. Fermi 2749, TP 450
    I-21027 Ispra (VA)
    Italy

</div>

[PVGIS]: https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis_en

[PVGIS Web Application]: https://re.jrc.ec.europa.eu/pvg_tools/en/
