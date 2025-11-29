---
icon: simple/fastapi
title: Web API
tags:
  - How-To
  - Web API
  - FastAPI
---

PVGIS provides a FastAPI-based web service
for programmatic access to solar calculations and photovoltaic performance analysis.
If you wish to run and test the Web API server,
you can follow the following instructions

## Quick Start

``` bash
pip install .[web]
uvicorn pvgisprototype.webapi:app --reload
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) for the interactive API documentation.


## What You Can Do

The Web API exposes almost the same calculations available
through the [CLI](/cli/index.md) and the core [Python API](/api/index.md):

- **Performance Analysis** - System efficiency and energy yield
- **PV Power** - Photovoltaic system output calculations
- **Optimal Solar Surface Positioning** - Sun angles at any location and time

## Architecture

```
HTTP Request → FastAPI Endpoints → Core API → Algorithms → JSON Response
```


The Web API is a thin REST layer over PVGIS' core calculation engine,
ensuring consistency across all interfaces.

## Documentation Sections

- [Install](install.md) - Set up FastAPI and uvicorn
- [Run](run.md) - Launch and configure the server
- [Examples](examples.md) - Sample requests and responses

## Interactive Documentation

When running, FastAPI automatically generates interactive docs:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

These interfaces let you test endpoints directly in your browser.

## For Developers

See [Web API Source Code](/source_code/web_api.md) for implementation details.
