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

from diagrams import Diagram, Edge, Cluster
from diagrams.custom import Custom
from diagrams.programming.language import Python
from diagrams.programming.framework import FastAPI

path_to_icons = '../icons'
path_to_logos = '../logos'

user_icon = "{path_to_icons}/noun-user-6616649.svg"
pydantic_icon = "{path_to_logos}/pydantic.svg"
xarray_icon = "{path_to_logos}/Xarray_RGB.png"
pandas_icon = "{path_to_logos}/pandas.svg"
data_array_icon = "{path_to_logos}/data_array.svg"
numpy_icon = "{path_to_logos}/numpy.svg"
scipy_icon = "{path_to_logos}/scipy.svg"
dask_icon = "{path_to_logos}/dask.svg"
cupy_icon = "{path_to_logos}/CuPy_300x300.png"
loguru_icon = "{path_to_logos}/loguru.png"
typer_icon = "{path_to_logos}/typer.svg"
rich_icon = "{path_to_logos}/rich.png"
pvlib_logo = "{path_to_logos}/pvlib.png"
skyfield_logo = "{path_to_logos}/skyfield.png"
solar_position_icon = "{path_to_icons}/sun-angle-outline.svg"
solar_irradiance_icon = "{path_to_icons}/sun-wireless-outline.svg"
global_horizontal_irradiance_icon = "{path_to_icons}/noun_global_horizontal_irradiance.svg"
direct_horizontal_irradiance_icon = "{path_to_icons}/noun_direct_horizontal_irradiance.svg"
temperature_icon = "{path_to_icons}/thermometer.svg"
wind_speed_icon = "{path_to_icons}/noun-windsock-4502486.svg"
meteorological_variables_icon = "{path_to_icons}/weather-partly-cloudy.svg"
photovoltaic_power_icon = f"{path_to_icons}/noun-solar-panel-6862742.svg"


try:
    with suppress(FileNotFoundError):
        with Diagram("pvgis-prototype", direction="TB", show=False) as diagram:
            diagram.render = lambda: None

            User = Custom("User", user_icon)
            Xarray = Custom("Input / Output", xarray_icon)

            with Cluster("Libraries"):
                python = Python("Python") # != Python
                Pandas = Custom("Pandas", pandas_icon)
                SciPy = Custom("SciPy", scipy_icon)
                with Cluster("Array Backend"):
                    NumPy = Custom("NumPy", numpy_icon)
                    with Cluster("Other Backends"):
                        Dask = Custom("Dask", dask_icon)
                        CuPy = Custom("CuPy", cupy_icon)

            with Cluster("Algorithms"):
                Solar_Position = Custom("Solar Position", solar_position_icon)
                Solar_Irradiance = Custom("Solar Irradiance", solar_irradiance_icon)
                Meteorological_Variables = Custom("Meteorological\nVariables", meteorological_variables_icon)
                Photovoltaic_Performance = Custom("Photovoltaic\nPerformance\nPVGIS 6", photovoltaic_power_icon)

            with Cluster("Optional External Libraries"):
                pvlib = Custom("pvlib", pvlib_logo)
                Skyfield = Custom("Skyfield", skyfield_logo)
                Other = Custom("Other", '')

            with Cluster("Validation"):
                Pydantic = Custom("Pydantic", pydantic_icon)

            #with Cluster("Debugging"):
            #    Loguru = Custom("Loguru", loguru_icon)

            with Cluster(""):
                API = Python("API")

            #with Cluster("Command Line Interface"):
            #    CLI = Python("CLI")
            #    Typer = Custom("Typer", typer_icon)
            #    Rich = Custom("Rich", rich_icon)

            WebAPI = FastAPI("WebAPI")

            Timestamping = Custom("Timestamping", '')
            Pandas - Edge(style="dashed") >> Timestamping

            Array_Computing = Custom("Array Computing", data_array_icon)
            [NumPy, Dask, CuPy] - Edge(style="dashed") >> Array_Computing

            Optimisation_Algorithms = Custom("Optimisation Algorithms", '')
            SciPy - Edge(style="dashed") >> Optimisation_Algorithms

            #NumPy \
            #<< Solar_Position \
            #<< Solar_Irradiance \
            #<< Photovoltaic_Performance
            
            #Photovoltaic_Performance \
            #<< [
            #    Solar_Irradiance,
            #    Solar_Position,
            #    ]
            
            #pvlib \
            #>> Solar_Position

            #Xarray >> API
            #Pydantic >> [API, CLI, WebAPI]
            #Loguru >> [API, CLI]

            #Solar_Position, Solar_Irradiance, Photovoltaic_Performance >> API
            #CLI - [Typer, Rich]
            #API >> [CLI, WebAPI]

            [Solar_Position, Photovoltaic_Performance] \
            - Edge(color="lightgrey", style="dashed") \
            - NumPy, SciPy

            Solar_Position \
            << Edge(color="grey", style="dashed") \
            << [pvlib, Skyfield, Other]

            with Cluster("SARAH 2/3 climate records - NetCDF files"):
                Global_Horizontal_Irradiance = Custom("Global\nHorizontal\nIrradiance\n(GHI)", global_horizontal_irradiance_icon)
                
                Direct_Horizontal_Irradiance = Custom("Direct\nHorizontal\nIrradiance\n(DHI)", direct_horizontal_irradiance_icon)

            Solar_Irradiance \
            << Edge(color="magenta") \
            << Xarray \
            << Edge(style="dashed", color="magenta") \
            << Global_Horizontal_Irradiance, Direct_Horizontal_Irradiance

            with Cluster("Meteorological Time Series - NetCDF files"):
                Temperature = Custom("Temperature", temperature_icon)
                Wind_Speed = Custom("Wind Speed", wind_speed_icon)

            Meteorological_Variables \
            << Edge(color="magenta") \
            << Xarray \
            << Edge(style="dashed", color="magenta") \
            << Temperature, Wind_Speed

            User \
            - Edge(style="dashed", color="blue") \
            >> WebAPI \
            >> Edge(style="dashed", color="blue") \
            >> API \
            >> Edge(style="dashed", color="blue") \
            >> Solar_Position \
            >> Edge(style="dashed", color="blue") \
            >> Solar_Irradiance \
            >> Edge(style="dashed", color="blue") \
            >> Meteorological_Variables \
            >> Edge(style="dashed", color="blue") \
            >> Photovoltaic_Performance \
            >> Edge(style="dashed", color="firebrick") \
            >> WebAPI \
            >> Edge(style="dashed", color="firebrick") \
            >> User

            WebAPI - Pydantic

            png = b64encode(diagram.dot.pipe(format="png")).decode()

    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")
```
