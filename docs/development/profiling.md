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

# Web API Profiling

This page details how to profile the Web API to identify performance bottlenecks and optimize your application's efficiency. It covers installing additional performance-boosting packages (`uvloop`, `httptools`) and setting up various profilers (`scalene`, `pyinstrument`, `yappi`).

## Performance Optimizations

!!! Tip
    By installing `uvloop`, you can get a 10% performance increase over `asyncio`.
    
    To install `uvloop`, run:
    ```bash
    pip install uvloop
    ```
    FastAPI will automatically use it from your environment.  
    _(Source: M. Trylesinski, Performance tips by the FastAPI Expert, Europython Conference, 2023, Prague)_

!!! Tip
    By installing `httptools`, you can get a 10% performance increase over `h11`.
    
    To install `httptools`, run:
    ```bash
    pip install httptools
    ```
    FastAPI will automatically use it from your environment.  
    _(Source: M. Trylesinski, Performance tips by the FastAPI Expert, Europython Conference, 2023, Prague)_

## Profiling Tools Overview

The application supports several profilers for analyzing performance, including:
- `scalene`
- `pyinstrument`
- `yappi`

## Configuring the .env file or an enviromental variable

!!! Note
    Variable `PVGISPROTOTYPE_WEB_API_ENVIRONMENT` can get values: `PRODUCTION`, `DEVELOPMENT`

The `.env` file is used to configure the environment variable (`PVGISPROTOTYPE_WEB_API_ENVIRONMENT`) for profiling. Below is an example `.env` file:

```env
PVGISPROTOTYPE_WEB_API_ENVIRONMENT=DEVELOPMENT
```

The .env file **should be located in the main directory** of the repository.

Alternatively, the environment variable PVGISPROTOTYPE_ENV can be set directly using the following command:

```bash
export PVGISPROTOTYPE_WEB_API_ENVIRONMENT=DEVELOPMENT
```

## Profiling settings

All the settings regarding the Web API can be found in `pvgisprototype.web_api.config.settings.py`. The file is like bellow:

```python
from pvgisprototype.web_api.config.options import (
    Profiler,
    ProfileOutput,
)
from pvgisprototype.web_api.config.options import (
    LogLevel,
    LogFormat,
)

# Common default settings
LOG_LEVEL_DEFAULT = LogLevel.info
PROFILING_ENABLED_PRODUCTION_DEFAULT = False
LOG_FORMAT_DEFAULT = LogFormat.uvicorn

# Development default settings
LOG_LEVEL_DEVELOPMENT_DEFAULT = LogLevel.info
PROFILING_ENABLED_DEVELOPMENT_DEFAULT = True
PROFILER_DEVELOPMENT_DEFAULT = Profiler.pyinstrument
PROFILE_OUTPUT_DEVELOPMENT_DEFAULT = ProfileOutput.json
MEASURE_REQUEST_TIME_DEVELOPMENT_DEFAULT = True

# Production default settings
MEASURE_REQUEST_TIME_PRODUCTION_DEFAULT = False
```

The available options for each variable are the following:

| Variable                              | Options                              |
|---------------------------------------|--------------------------------------|      
|PROFILER_DEVELOPMENT_DEFAULT           |`SCALENE`, `PYINSTRUMENT`, `YAPPI`    |                           
|PROFILE_OUTPUT_DEVELOPMENT_DEFAULT*    |`JSON`, `PSTAT`, `CALLGRIND`, `HTML`  |

!!! Note 
    If the selected profiler does not support the specified output format, it defaults to:
    
    - `JSON` for `SCALENE` and `PYINSTRUMENT`

    - `PSTAT` for `YAPPI`


## Profiling with pyinstrument

### Installing pyinstrument

To install `pyinstrument`, run:

```bash
pip install pyinstrument
```

### Profile using pyinstrument as a middleware

Profiling with package `pyinstrument` is supported as middleware in the application. When `PROFILER_DEVELOPMENT_DEFAULT=PYINSTRUMENT` is selected, you can run the Web API with the following command:

`uvicorn pvgisprototype.webapi:app --port 8001`

After performing a request to the Web API, a profiling file will be generated in the main directory. The file will be named `profile_pyinstrument*`, with the appropriate extension based on the chosen output format (JSON, etc.).

## Profiling with yappi

### Installing yappi

To install `yappi`, run:

```bash
pip install yappi
```

### Profile using yappi as a middleware

Profiling with package `yappi` is also supported as middleware in the application. When PROFILER_DEVELOPMENT_DEFAULT=YAPPI is selected, you can start the Web API with the following command:

`uvicorn pvgisprototype.webapi:app --port 8001`

Once a request to the Web API is completed, a profiling file will be generated in the main directory. The file will be named `profile_yappi*`, along with the chosen output extension.

## Profiling with scalene

### Installing scalene

To install `scalene`, run:

```bash
pip install scalene
```

and verify installation by typing:

``` bash exec="true" result="ansi" source="above"
scalene --help
```

### Running scalene from the command line and profile the Web API instance

In order to run `scalene` along with the a local instance of PVGIS Web API run:

```bash
scalene --json --outfile where/to/store/profile.json --no-browser pvgisprototype/webapi.py
```

Then, open the application using the [Swagger UI](https://swagger.io/tools/swagger-ui/), run a specific request, and after the request completes, terminate the local instance using `Ctrl + C`. The output profiling file will be saved to the specified path.

### Profile using scalene as a middleware

The application supports using scalene as a middleware. Option `PROFILER` must be `SCALENE`.

!!! Important
    **The local instance must be invoked using `scalene` i.e:**
    
    **`scalene --json --outfile ./profile_scalene.json --no-browser pvgisprototype/webapi.py`**

When the instance is incoked with `scalene` then perform a request to the service and when finished close the instance. The output file will be named `profile_scalene.json`.