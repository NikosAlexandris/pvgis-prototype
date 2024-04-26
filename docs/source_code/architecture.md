---
icon: fontawesome/solid/diagram-project
title: Architecture
tags:
  - pvgisprototype
  - Python
  - Dependencies
  - Dependency Tree
---


```python exec="true" html="true"
from base64 import b64encode
from contextlib import suppress

from diagrams import Diagram, Cluster
from diagrams.custom import Custom
from urllib.request import urlretrieve
from diagrams.programming.language import Python
from diagrams.programming.framework import FastAPI


numpy_icon = "docs/logos/numpylogo.png"
xarray_icon = "docs/logos/Xarray_Logo_RGB_Final.png"
pydantic_icon = "docs/logos/pydantic_logo.png"
loguru_icon = "docs/logos/loguru_logo.png"
typer_icon = "docs/logos/typer_logo-margin.png"
rich_icon = "docs/logos/rich_logo.png"


try:
    with suppress(FileNotFoundError):
        with Diagram("pvgis-prototype", direction="TB", show=False) as diagram:
            diagram.render = lambda: None
            # pvis = Python("pv(g)is")
            NumPy = Custom("", numpy_icon)
            Xarray = Custom("Input/Output", xarray_icon)

            with Cluster("Algorithms"):
                # Algorithms = Python("Algorithms")
                Solar_Geometry = Python("Solar Geometry")
                Solar_Irradiance = Python("Solar Irradiance")
                Photovoltaic_Performance = Python("Photovoltaic_Performance")
                External_Libraries = Python("External Libraries ?")

            with Cluster("Validation & Debugging"):
                Pydantic = Custom("Pydantic", pydantic_icon)
                Loguru = Custom("Loguru", loguru_icon)

            with Cluster(""):
                API = Python("API")

            with Cluster("Command Line Interface"):
                CLI = Python("CLI")
                Typer = Custom("Typer", typer_icon)
                Rich = Custom("Rich", rich_icon)

            WebAPI = FastAPI("WebAPI")

            NumPy >> Solar_Geometry, Solar_Irradiance, Photovoltaic_Performance
            Photovoltaic_Performance << Solar_Irradiance << Solar_Geometry
            External_Libraries >> Solar_Geometry

            Xarray >> API
            Pydantic >> API, CLI, WebAPI
            Loguru >> API, CLI

            Solar_Geometry, Solar_Irradiance, Photovoltaic_Performance >> API
            CLI << Typer, Rich
            API >> CLI, WebAPI

            png = b64encode(diagram.dot.pipe(format="png")).decode()
    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")
```
