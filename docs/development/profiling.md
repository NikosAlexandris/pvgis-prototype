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


Profiling the PVGIS Web API

This page explains how to profile the PVGIS Web API
using profilers (Scalene, Pyinstrument, Yappi, FunctionTrace).
in order to identify performance bottlenecks
and optimize application efficiency.
It also covers installing the performance-boosting packages `uvloop`,
`httptools`.

# Web API Profiling

It covers installing additional performance-boosting packages (`uvloop`, `httptools`) and setting up various profilers (`scalene`, `pyinstrument`, `yappi`).

## Performance Optimization

!!! tip Install `uvloop`

    `uvloop` reportedly brings a 10% performance increase over
    [`asyncio`](https://docs.python.org/3/library/asyncio.html).
    
    To install `uvloop`, run:

    ```bash
    pip install uvloop
    ```
    
    FastAPI will automatically use it from your environment.  

    _(Source: M. Trylesinski, Performance tips by the FastAPI Expert, Europython Conference, 2023, Prague)_

!!! tip Install `httptools`

    `httptools` reportedly brings a 10% performance increase over
    [`h11`](https://h11.readthedocs.io/en/latest/).
    
    To install `httptools`, run:

    ```bash
    pip install httptools
    ```

    FastAPI will automatically use it from your environment.  

    _(Source: M. Trylesinski, Performance tips by the FastAPI Expert, Europython Conference, 2023, Prague)_

## Profiling Tools

Supported profilers for performance analysis include :

- `scalene`
- `pyinstrument`
- `yappi`
- `functiontrace`

## Environment configuration

Set the environment variable `PVGISPROTOTYPE_WEB_API_ENVIRONMENT`
to switch between the `Production` and `Development` environments.

This can be done either :

- in a file named `.env` and **placed in the main directory** of the source code

  ``` env
  PVGISPROTOTYPE_WEB_API_ENVIRONMENT="Development"
  ```

- alternatively, setting the variable in question directly via :

  ```bash
  export PVGISPROTOTYPE_WEB_API_ENVIRONMENT="Development"
  ```

## Profiling settings

Configuration is defined in `pvgisprototype.web_api.config.settings.py`.

Example settings :

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
PROFILER_DEVELOPMENT_DEFAULT = Profiler.Pyinstrument
PROFILE_OUTPUT_DEVELOPMENT_DEFAULT = ProfileOutput.json
MEASURE_REQUEST_TIME_DEVELOPMENT_DEFAULT = True

# Production default settings
MEASURE_REQUEST_TIME_PRODUCTION_DEFAULT = False
```

Available options :

| Variable                              | Options                              |
|---------------------------------------|--------------------------------------|      
|PROFILER_DEVELOPMENT_DEFAULT           |`Scalene`, `Pyinstrument`, `Yappi`, `FunctionTrace`    |                           
|PROFILE_OUTPUT_DEVELOPMENT_DEFAULT*    |`JSON`, `PSTAT`, `CALLGRIND`, `HTML`  |

!!! Note 

    If a profiler doesn't support the specified output format,
    defaults are :
    
    - `JSON` for `Scalene`, `Pyinstrument` and `FunctionTrace`

    - `PSTAT` for `Yappi`


## Pyinstrument

### Installation

To install `pyinstrument`, run:

```bash
pip install pyinstrument
```

### Usage

To profile with `pyinstrument`,
set `PROFILER_DEVELOPMENT_DEFAULT="Pyinstrument"`
and run the Web API :

`uvicorn pvgisprototype.webapi:app --port 8001`

After performing a request to the Web API,
a profiling file will be generated in the main directory
named `profile_pyinstrument.<extension>`
where `extension` bases upon chosen output format, for example `JSON`.

## Yappi

### Installation

To install `yappi`, run:

```bash
pip install yappi
```

### Usage

To profile with `yappi`,
set `PROFILER_DEVELOPMENT_DEFAULT="Yappi"`
and start the Web API via :

`uvicorn pvgisprototype.webapi:app --port 8001`

Once a request to the Web API is completed,
a profiling file named `profile_yappi.<extension>`
where `extension` depends on the chosen output format,
will be generated in the main directory

## Scalene

### Installation

To install `scalene`, run:

```bash
pip install scalene
```

and verify installation by typing:

``` bash exec="true" result="ansi" source="above"
scalene --help
```

### Running scalene from the command line

In order to use `scalene` along with a local instance of the PVGIS Web API,
run:

```bash
scalene --json --outfile where/to/store/profile.json --no-browser pvgisprototype/webapi.py
```

Then,
open the application using the [Swagger UI](https://swagger.io/tools/swagger-ui/),
run a specific request
and after the request completes
terminate the local instance using `Ctrl + C`.
The profiling file will be saved to the specified path.

### Middleware Usage

To profile with `scalene` as a middleware
set the `PROFILER` option to `Scalene`
and run the server via

``` bash
scalene --json --outfile ./profile_scalene.json --no-browser pvgisprototype/webapi.py
```

Once the Web API server is invoked using `scalene`
we can perform a request and stop it right after.
The output file will be named `profile_scalene.json`.

## FunctionTrace

### Installation

[FunctionTrace](https://functiontrace.com/) comes in two necessary pieces :
a server, and a language-specific client.

!!! Note

    It's currently necessary to have `cargo` installed in order to install
    FunctionTrace, as functiontrace-server is not packaged for all supported
    operating systems. You can install cargo via rustup.

    ``` bash
    # Install the server
    cargo install functiontrace-server
    ```

    ``` bash
    # Install the Python client
    pip install functiontrace
    ```

### FunctionTrace as a middleware

To trace the PVGIS Web API `webapi.py`,  load it via functiontrace :

``` bash
functiontrace --trace-memory pvgisprototype/webapi.py
```

### Viewing Traces

> From https://functiontrace.com/

To view a recorded trace file,
go to the Firefox Profiler and choose Load a profile from file,
then select the desired trace file.
This step will perform some processing,
but is entirely local - your trace file never leaves your own machine!

> Note: If this is your first time using the Firefox Profiler, you may want to skim the [UI guide](https://profiler.firefox.com/docs/#/./guide-ui-tour) for it.
