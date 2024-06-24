---
icon: material/compare-horizontal
title: PVGIS 6 vs 5.2
tags:
  - Reference
  - Comparison
  - Features
  - Functionality
  - Capabilities
  - Archived notes
---

This section compares in detail PVGIS v6 with its predecessor v5.
The shift to a new generation of PVGIS
brings in a complete overhaul at the software level,
including the design, architecture and functionality
while aiming to cover all capabilities of the previous generation.

## Target audience & License

???+ info "Scope & Target audience"

    | Category    | 5                                                                | 6   |
    |-------------|------------------------------------------------------------------|-----|
    | Citizens    | Yes                                                              | Yes |
    | Prosumers   | Yes                                                              | Yes |
    | Researchers | Indirectly & partly available through [r.sun][r.sun] (GRASS GIS) | Yes |
    | Developers  | -                                                                | Yes |
    | Industry    | -                                                                | -   |

    [r.sun]: https://grass.osgeo.org/grass83/manuals/r.sun.html

???+ "Licensing"

    | License           | 5                                  | 6                                  |
    |-------------------|------------------------------------|------------------------------------|
    | Use license       | -                                  | EUPL-1.2, CCSA (Documentation)     |
    | User Feedback     | Positive/Negative feedback summary | Positive/Negative feedback summary |
    | Usage             | Examples of usage in ...  | Examples of usage in ...  |
    | Community Support | Active/Inactive, Size of community | Active/Inactive, Size of community |
    | Update Frequency  | Regular/Infrequent updates         | Regular/Infrequent updates         |

## Functionality

???+ info "Capabilities & Functionality Comparison"

    | Functionality            | 5                                                                                    | 6                                                                 |
    |--------------------------|--------------------------------------------------------------------------------------|-------------------------------------------------------------------|
    | Solar Position           | Internal, Only the solar altitude part of final analysis, Hofierka 2002 (Jenco 1992) | Selectable, Jenco (1992), NOAA, NREL SPA[^SPA], Skyfield, pysolar |
    | Solar Incidence          | Internal, Hofierka 2002 (Jenco 1992)                                                 | Selectable, Jenco (1992), Iqbal 1992                              |
    | Solar Irradiance         | Part of final analysis, Hofierka 2002                                                | Independent for each radiation component, Hofierka 2002           |
    | Photovoltaic Performance | Huld 2011, Gracia 2016                                                               | Huld 2011, Gracia 2016                                            |

## Architecture

???+ note "Implementation Details"

    | Component     | 5                                    | 6                                                                    |
    |---------------|--------------------------------------|----------------------------------------------------------------------|
    | Language      | C/C++                                | Python                                                               |
    | Core Software | Monolithic design                    | Modular, clear API / CLI / Web API boundaries, scalable architecture |
    | CLI           | Few independent stand-alone programs | Unified CLI with rich options                                        |
    | API           | -                                    | Comprehensive API suite                                              |
    | Web API       | Flask-based                          | FastAPI, asynchronous support                                        |
    | CORS          | -                                    | Yes / Work-in-progress                                               |

    | Aspect       | 5                   | 6                                     |
    |--------------|---------------------|---------------------------------------|
    | Coding Style | Mixed, inconsistent | PEP-8 compliant, Formmatted via Black |  
    | Testing      | Manual tests only   | Automated with continuous integration |

## Data I/O Capabilities

??? success "Data Input/Output"

    | File Formats Supported | 5                              | 6                                             |
    |------------------------|--------------------------------|-----------------------------------------------|
    | Input formats          | Limited to proprietary formats | Extensive support including CSV, JSON, NetCDF |
    | Input formats  | PVGIS native time series format, Text | Extensive support including any Xarray-supported format*[^Xarray data IO] like NetCDF & Zarr, CSV, JSON |
    | Output formats | Text, mixed/partly separated fields   | Rich output formats including CSV, JSON, XML, NetCDF, PNG                                               |
    | Database       | -[^*]                                     | -[^*]                                                                                                       |

[^*]: In strict technical terms, PVGIS was and remains a database-less application.

[^Xarray data IO]: https://docs.xarray.dev/en/stable/user-guide/io.html

### Time Series Data Workflow

```python exec="true" html="true"
from base64 import b64encode
from contextlib import suppress

from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.programming.language import C
from diagrams.programming.language import Cpp
from diagrams.programming.language import Python

irradiance_icon = "docs/icons/wiggly_vertical_line.svg"
spectral_effect_icon = "docs/icons/noun-sun-525998.svg"
temperature_icon = "docs/icons/thermometer.svg"
photovoltaic_power_icon = "docs/icons/noun-solar-energy-853048.svg"
wind_speed_icon = "docs/icons/noun-windsock-4502486.svg"  #Windsock by Dani Pomal from <a href="https://thenounproject.com/browse/icons/term/windsock/" target="_blank" title="Windsock Icons">Noun Project</a> (CC BY 3.0) 
cupy_icon = "docs/logos/CuPy_300x300.png"
xarray_icon = "docs/logos/Xarray_RGB.svg"
netcdf_icon = "docs/logos/netcdf-400x400.png"
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

            # PVGIS software version 5/6

            with Cluster("PVGIS <= 5.x"):
                PVGIS_5 = C("")
                PVGIS_5Cpp = Cpp("")

            with Cluster("PVGIS 6"):
                PVGIS_6 = Custom("PVGIS 6", pvgis6_icon)
                NumPy = Custom("NumPy", numpy_icon)
                Xarray = Custom("Input/Output", xarray_icon)


            # Raw Data

            Data = Custom("Data / Observations", files_icon)
            Files = Custom("Data", files_icon)
            NetCDF = Custom("NetCDF", netcdf_icon)
            #with Cluster('*On Disk'):
                #Zarr = Custom("Zarr store", zarr_icon)
                Zarr = Custom("Ordinary store", zarr_icon)

            with Cluster("Time Series"):

                with Cluster("SARAH 2/3 climate records"):
                    Global_Irradiance = Custom("Global\nHorizontal\nIrradiance\n(GHI)", irradiance_icon)
                    Direct_Irradiance = Custom("Direct\nHorizontal\nIrradiance\n(DHI)", irradiance_icon)
            
                with Cluster("ERA5 time series"):
                    Temperature = Custom("Temperature", temperature_icon)
                    Wind_Speed = Custom("Wind Speed", wind_speed_icon)

                Spectral_Effect = Custom("\nSpectral Factor", spectral_effect_icon)


            with Cluster("Data Pre-Processing PVGIS 6"):

                # Tools
                Kerchunk = Custom("Kerchunk", kerchunk_icon)

                with Cluster("Input Data Format"):
                    # Pre-Processed Data
                    Kerchunk_Reference_Set = Custom("Kerchunk Reference Set", binary_data_icon)

            with Cluster("Possible Input Data Formats"):
                HDF5 = Custom("HDF5", '')
                NetCDF
                Zarr
                CSV = Custom("CSV", '')
                GRIB = Custom("GRIB", '')
                # Virtual_Zarr = Custom("Virtual store", zarr_icon)

            with Cluster("Analysis of Photovoltaic Performance PVGIS 6"):
                Photovoltaic_Power = Custom("Photovoltaic Power", photovoltaic_power_icon)


            with Cluster("PVGIS <= 5.x"):

                with Cluster("Data Pre-Processing"):
                    Zarr

                with Cluster("Input Data Format"):
                    PVGIS_Time_Series = Custom("Only\nPVGIS-Native\nTime Series Format", binary_data_icon)

            with Cluster("Photovoltaic Performance Analysis PVGIS <=5.x"):
                #Photovoltaic_Power_PVGIS_5 = Custom("Photovoltaic Power PVGIS 5", photovoltaic_power_icon)
                Photovoltaic_Power_PVGIS_5 = Custom("Photovoltaic Energy\nPVGIS 5", photovoltaic_power_icon)

            # Workflow =======================================================

            # Format of Time Series Data

            Global_Irradiance >> NetCDF
            Direct_Irradiance >> NetCDF
            Temperature >> NetCDF
            Wind_Speed >> NetCDF
            Spectral_Effect >> NetCDF


            # PVGIS 6

            NetCDF \
            - Edge(label="Scan NetCDF files", color="red", style="dashed") \
            - Kerchunk \
            - Edge(label="Generate Reference Set", color="red", style="dashed") \
            - Kerchunk_Reference_Set \
            - Edge(label="Read with Zarr engine", color="red", style="dashed") \
            >> Xarray \
            >> PVGIS_6 \
            - NumPy \
            >> Photovoltaic_Power
            
            [NetCDF, HDF5, CSV, Zarr] \
            - Edge(label="Read NetCDF files", color="red", style="dashed") \
            >> Xarray


            # PVGIS 5.x

            Data \
            - Edge(label="Observations or modelled data", color="blue", style="dashed") \
            - NetCDF \
            - Edge(label="Provider's chunking", color="blue", style="dashed") \
            - Zarr \
            - Edge(label="from Massive Zarr store", color="blue", style="dashed") \
            - PVGIS_Time_Series \
            - Edge(label="Read with custom C code", color="blue", style="dashed") \
            >> PVGIS_5 \
            >> Photovoltaic_Power_PVGIS_5

            # Alternative 

            #Satellite_to_Data \
            #>> NetCDF

            #NetCDF \
            #- Edge(label="Observations or modelled data", color="blue", style="dashed") \
            #- Edge(label="Daily Data\nProducer's chunking", color="blue", style="dashed") \
            #- Edge(
            #        label="Rechunking to yearly time series\nMassive Transfer to Zarr Store\nData Duplication",
            #        color="blue", style="dashed"
            #      ) \
            #- Zarr \
            #- Edge(label="from (Massive!) Zarr store", color="blue", style="dashed") \
            #- PVGIS_Time_Series \
            #- Edge(label="PVGIS-Native time series format", color="blue", style="dashed") \
            #>> PVGIS_5 \
            #>> Photovoltaic_Power_PVGIS_5


            # Encode diagram as a PNG and print it in HTML Image format

            png = b64encode(diagram.dot.pipe(format="png")).decode()

    # Finally, print the "flow"

    print(f'<img src="data:image/png;base64, {png}"/>')

except Exception as e:
    print(f"An error occurred: {e}")
```


## Performance

???+ note "Efficienct & Reliability"

    | Metric            | 5                                           | 6                                                |
    |-------------------|---------------------------------------------|--------------------------------------------------|
    | Speed             | Instant                                     | Feels instant, Optimizable via Numba, DaCe       |
    | Reliability       | Known issues, occasionally affecting output | Improved with robust testing                     |
    | Accuracy          | Satisfactory checked with research work     | High, with rigorous testing                      |
    | Automated Testing | None                                        | Comprehensive suite via Pytest                   |
    | Code Quality      | Not standardized                            | PEP-8 compliant, linted code                     |
    | Modularity        | Mixed code styles                           | Fully modular with clean separation of concerns  |
    | Flexibility       | Limited, extensive hardcoding               | Highly flexible and customizable                 |
    | Web API           | Flask-based                                 | Rebuilt with FastAPI for asynchronous operations |
    | Core API          | -                                           | Robust core API supporting various integrations  |
    | CLI               | Few command line tools, poor UX             | Advanced CLI with Typer, enhanced UX             |
    | Data Handling     | PVGIS-native time series format only        | Supports multiple formats via Xarray             |
    | Plotting Results  | Via Web GUI only                            | Integrated plotting in CLI and Web API           |

[^SPA]: https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.spa.html

???+ info "Customisation & Reliability"

    | Question                  | 5                                                       | 6                                                                        |
    |---------------------------|---------------------------------------------------------|--------------------------------------------------------------------------|
    | Customization Ease        | Very Difficult                                          | Very Easy                                                                |
    | Real-world Usage Examples | Data fetched through Public Web API                     |                                                                          |
    | Codebase Quality          | Poor                                                    | Estimated : Good, to be reviewed                                         |
    | Performance & Reliability | High performance, Poor reliability due to lack of tests | High performance, High reliability, Automated testing : Work-in-progress |

## Capabilities

???+ info "Scientific Functionality"

    | Photovoltaic system | Software A | Software B |
    |---------------------|------------|------------|
    | Grid-connected      | Yes        | Yes        |
    | Off-Grid            | Yes        | Planned    |
    | Tracking            | Yes        | Planned    |

???+ note "Other capabilities"

    | Capabilities                 | 5   | 6                |
    |------------------------------|-----|------------------|
    | Solar irradiance time series | Yes | Yes              |
    | Meteorological time series   | Yes | Yes              |
    | TMY                          | Yes | Work-in-progress |
    | Fingerprinted results        | -   | Yes              |
    | QR-Code shareable output     | -   | Yes              |
