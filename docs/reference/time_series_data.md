---
icon: fontawesome/solid/diagram-project
title: Time Series Data
tags:
  - Data
  - Time Series
  - Solar Irradiance
  - Global Horizontal Irradiance
  - Direct Horizontal Irradiance
  - Spectral Factor
  - Temperature
  - Wind Speed
---

PVGIS works both as clear-sky simulation engine as well as analysing the
performance of a photovoltaic system based on external time series data for
solar irradiance and important meteorological variables alike.

The default set of input time series that power the calculations of the public Web
application, and the Web API as well, is :

- Solar irradiance time series from the SARAH2/3 climate data records
- Temperature at 2m height from ERA5
- Wind speed at 10m heiht from ERA5
- Spectral factor series for 2013, equally used for every other year, produced
  by Thomas Huld and ... in collaboration with ...


## Reading time series

How does PVGIS 6 read external time series ?

```python exec="true" html="true"
from base64 import b64encode
from contextlib import suppress

from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom

transmission_control_protocol_icon = "docs/icons/noun-transmission-control-protocol-6111114.svg"
data_analysis_icon = "docs/icons/noun-data-analysis.svg"
irradiance_icon = "docs/icons/wiggly_vertical_line.svg"
global_irradiance_icon = "docs/icons/noun-sun-525998.svg"
direc_irradiance_icon = "docs/icons/noun-sun-525998.svg"
spectral_effect_icon = "docs/icons/noun-sun-525998.svg"
temperature_icon = "docs/icons/thermometer.svg"
photovoltaic_power_icon = "docs/icons/noun-solar-energy-853048.svg"
wind_speed_icon = "docs/icons/noun-windsock-4502486.svg"  #Windsock by Dani Pomal from <a href="https://thenounproject.com/browse/icons/term/windsock/" target="_blank" title="Windsock Icons">Noun Project</a> (CC BY 3.0) 
cupy_icon = "docs/logos/CuPy_300x300.png"
xarray_icon = "docs/logos/Xarray_RGB.svg"
netcdf_icon = "docs/logos/netcdf-400x400.png"
data_array_icon = "docs/logos/data_array.svg"
numpy_icon = "docs/logos/numpy.svg"
dask_icon = "docs/logos/dask.svg"
pydantic_icon = "docs/logos/pydantic.png"
zarr_icon = "docs/logos/zarr.png"  # zarr_logo_x.png
kerchunk_icon = "docs/logos/kerchunk.png"
binary_data_icon = "docs/logos/pastebin.svg"
files_icon = "docs/icons/files.svg"
pandas_icon = "docs/logos/pandas.svg"
python = "docs/logos/python.svg"
c_icon = "docs/logos/c.svg"
cplusplus_icon = "docs/logos/cplusplus.svg"


try:
    with suppress(FileNotFoundError):
        with Diagram("Analysis of Photovoltaic Performance", direction="TB", show=False) as diagram:
            diagram.render = lambda: None



            # "Raw" Data Acquisition & Production

            Satellite_to_Data = Custom("Data Acquisition", transmission_control_protocol_icon)
            ERA5_Data = Custom("ERA5 Reanalysis Data", data_array_icon)
            Analysis = Custom("Analysis & Production", data_analysis_icon)


            # Data

            Data = Custom("Data / Observations", files_icon)
            Files = Custom("Data", files_icon)
            NetCDF = Custom("", netcdf_icon)

            with Cluster("Time Series"):

                with Cluster("SARAH 2/3 climate records"):
                    Global_Irradiance = Custom("Global Horizontal Irradiance\n(GHI)", irradiance_icon)
                    Direct_Irradiance = Custom("Direct Horizontal Irradiance\n(DHI)", irradiance_icon)
            
                with Cluster("ERA5 Reanalysis Data"):
                    Temperature = Custom("Temperature", temperature_icon)
                    Wind_Speed = Custom("Wind Speed", wind_speed_icon)

                Spectral_Effect = Custom("\nSpectral Factor", spectral_effect_icon)


            # Tools

            # 
            Kerchunk = Custom("Kerchunk", kerchunk_icon)
            #In_Memory = Custom("First Call Read In Memory", '')


            # Pre-Processed Data

            with Cluster('*First Call Read In-Memory'):
                Index = Custom("Index", binary_data_icon)

            with Cluster('*On Disk'):
                Zarr = Custom("Zarr store", zarr_icon)


            # Input Data to PVGIS
            
            with Cluster("Time Series for Photovoltaic Analysis"):

                Virtual_Zarr = Custom("Virtual Zarr store", zarr_icon)
                PVGIS_Time_Series = Custom("PVGIS-Native\nTime Series Format", binary_data_icon)


            # Analysis of Photovoltaic Performance

            with Cluster("Photovoltaic Performance Analysis"):

                # PVGIS software version 5/6
                PVGIS_5 = Custom("PVGIS 5", '')
                PVGIS_6 = Custom("PVGIS 6", '')


            with Cluster("Photovoltaic Power / Energy"):
                Photovoltaic_Power = Custom("Photovoltaic Energy\nPVGIS 6", photovoltaic_power_icon)
                Photovoltaic_Power_PVGIS_5 = Custom("Photovoltaic Energy\nPVGIS 5", photovoltaic_power_icon)

            # Workflow

            # Format of Time Series Data

            Satellite_to_Data >> Global_Irradiance >> NetCDF
            Satellite_to_Data >> Direct_Irradiance >> NetCDF

            Satellite_to_Data \
            - Edge(label="+", style="dashed") \
            - Analysis \
            >> ERA5_Data

            ERA5_Data >> Temperature >> NetCDF
            ERA5_Data >> Wind_Speed >> NetCDF
            Analysis >> Spectral_Effect >> NetCDF


            # PVGIS 6

            NetCDF \
            - Edge(label="Read NetCDF files", color="firebrick", style="dashed") \
            - Kerchunk \
            - Edge(
                   label="Generate Index /\nVirtual Zarr",
                   color="firebrick",
                   style="dashed"
                  ) \
            - Index \
            - Virtual_Zarr \
            - Edge(label="Read from virtual Zarr store", color="firebrick", style="dashed") \
            - PVGIS_6 \
            >> Photovoltaic_Power


            # PVGIS 5.x

            Satellite_to_Data \
            >> NetCDF

            NetCDF \
            - Edge(label="Observations or modelled data", color="blue", style="dashed") \
            - Edge(label="Daily Data\nProducer's chunking", color="blue", style="dashed") \
            - Edge(
                    label="Rechunking to yearly time series\nMassive Transfer to Zarr Store\nData Duplication",
                    color="blue", style="dashed"
                  ) \
            - Zarr \
            - Edge(label="from (Massive!) Zarr store", color="blue", style="dashed") \
            - PVGIS_Time_Series \
            - Edge(label="PVGIS-Native time series format", color="blue", style="dashed") \
            >> PVGIS_5 \
            >> Photovoltaic_Power_PVGIS_5


            # Encode diagram as a PNG and print it in HTML Image format

            png = b64encode(diagram.dot.pipe(format="png")).decode()

    # Finally, print the "flow"

    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")
```

## Icons

- sun by Jolan Soens from <a href="https://thenounproject.com/browse/icons/term/sun/" target="_blank" title="sun Icons">Noun Project</a> (CC BY 3.0)

- transmission control protocol by bsd studio from <a href="https://thenounproject.com/browse/icons/term/transmission-control-protocol/" target="_blank" title="transmission control protocol Icons">Noun Project</a> (CC BY 3.0)

- time series by Christina Barysheva from <a href="https://thenounproject.com/browse/icons/term/time-series/" target="_blank" title="time series Icons">Noun Project</a> (CC BY 3.0)
