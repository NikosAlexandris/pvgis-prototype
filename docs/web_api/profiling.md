---
icon: material/application-cog
description: Profiling of the application
title: Profiling
subtitle: Profiling of PVGIS
tags:
  - How-To
  - Web API
  - Examples
---

This page is an detailed guide on how the application is being profiled.

# Web API profiling

!!! Tip
    By installing `uvloop` you can get a 10% increase of performance (instead of `asyncio`).
    Try installing `uvloop` to your environment by running `pip install uvloop` and FastAPI will automatically use it from your enviroment. (Source: M. Trylesinski, Performance tips by the FastAPI Expert, Europython Conference, 2023, Prague)

!!! Tip
    By installing `httptools` you can get a 10% increase of performance (instead of `h11`).
    Try installing `httptools` to your environment by running `pip install httptools` and FastAPI will automatically use it from your enviroment. (Source: M. Trylesinski, Performance tips by the FastAPI Expert, Europython Conference, 2023, Prague)

## Profiling with scalene

First `scalene` must be installed in the environment. To install `scalene` run:

`pip install scalene`

to verify installation try typing:

``` bash exec="true" result="ansi" source="above"
scalene --help

```

In order to run `scalene` along with the a local instance of PVGIS Web API run:

`scalene --json --outfile where/to/store/profile.json --no-browser pvgisprototype/webapi.py`

Then open using the application using the SWAGGER UI and run a specific request that you want to profile. When the request is finished terminate the local web API instance using `Ctrl + c`.
The output profiling file then will be filled in the selected path.