---
icon: material/compare-horizontal
tags:
  - Reference
  - Comparison
  - Features
  - Functionality
  - Capabilities
  - Archived notes
---


## Comprehensive Software Comparison

This comparison aims to provide a detailed examination of the differences and enhancements from PVGIS 5 to PV(G)IS 6 across various aspects of functionality and technology.


## PVGIS v6 vs. PVGIS v5.x

??? info "Capabilities & Functionality comparison"

    | Functionality                                   | PVGIS 5                                                                 | PV(G)IS 6                                                        |
    |-------------------------------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------|
    | Speed                                           | Instant                                                                 | Work-in-Progres                                                  |
    | Reliability                                     | Results assessed via studies, Some hard-to-fix bugs                     | Work-in-Progress; test each + every function                     |
    | Accuracy                                        | Untested accuracy of functions                            | Work-in-Progress; test each + every function                     |
    | Code Quality                                    | Untested                                                                | Automatic code styling, linting, etc.                            |
    | Automated tests                                 | No                                                                      | Automated tests via Pytest; Work-in-Progress                     |
    | Modularity                                      | No; Mixture of : C/C++ code, partly object-oriented, functional design  | Yes                                                              |
    | Flexibility                                     | No; Extensive code duplication, Hardcoding practices                    | Yes; Independent API modules & CLI tools for each functionality  |
    | Web API                                         | Yes; Based on Flask                                                     | Yes; Based on FastAPI                                            |
    | Core API                                        | No                                                                      | Yes; Python, Pydantic and more                                   |
    | CLI                                             | Yes; Cryptic arguments/parameters/flags names                           | Yes; Based on Typer; Rich text in the command line               |
    | Plotting results                                | No; Possible through the Web GUI                                        | Yes; Based on `matplotlib` and in the command line via `uniplot` |
    | Read input arguments and parameters             | Yes                                                                     | Yes; Based on Typer                                              |
    | Location-specific calculations                  | Identifies pixel row and column offsets                                 | Any Xarray-supported data format                                 |
    | Area-specific calculations                      | No                                                                      | Planned; Support custom raster and vector boundary maps          |
    | Select energy model                             |                                                                         |                                                                  |
    | Read / use elevation data                       |                                                                         | Any Xarray-supported data format                                 |
    | Read / use horizon data                         |                                                                         | Under development                                                |
    | Time series support                             | Set number of hours for iterations                                      | Timestamps via Pandas' DatetimeIndex                             |
    | Read external time series                       | SIS,SID time series; Restricted to custom time series format            | Any Xarray-supported data format (including NetCDF, Zarr, etc.)  |
    | Compute global irradiance                       |                                                                         | Any Xarray-supported data format (including NetCDF, Zarr, etc.)  |
    | Read spectral correction values                 |                                                                         |                                                                  |
    | Read temperature time series                    |                                                                         |                                                                  |
    | Read wind speed time series                     |                                                                         |                                                                  |
    | Calculate solar geometry variables              | Yes; Internal                                                           |                                                                  |
    | Optimise slope if requested                     | Yes                                                                     | Under development                                                |
    | Optimise slope and aspect if requested          | Yes                                                                     | Under development                                                |
    | Set slope and aspect depending on tracking type | Yes                                                                     | Planned                                                          |
    | Bi-facial solar module support                  | No                                                                      | Planned                                                          |
    | Calculate total radiation                       | Yes; Internal; Needs irradiance time series in custom format            | `irradiance` command                                             |
    | Calculate system performance                    | Yes; Huld 2011 (Modified King model)                                    | `power` command; Huld 2011 (Modified King model)                 |
    | Spectral Mismatch effect                        | Yes; Internal; Bases on 2013 spectrally resolved irradiance time series | Planned; Testing                                                 |
 


 ## Software Comparison

| Feature Category       | Old Software          | New Software          |
|------------------------|-----------------------|-----------------------|
| **Models**             |                       |                       |
| Solar Position         | Description Old       | Description New       |
| Solar Irradiance       | Description Old       | Description New       |
| Photovoltaic Performance | Description Old       | Description New       |
| **Implementation**     |                       |                       |
| Architecture           | Description Old       | Description New       |
| Core Software          | Description Old       | Description New       |
| CLI                    | Description Old       | Description New       |
| API                    | Description Old       | Description New       |
| Web API                | Description Old       | Description New       |
| **Backend**            |                       |                       |
| Implementation Language | Description Old       | Description New       |
| Coding Style           | Description Old       | Description New       |
| Testing                | Description Old       | Description New       |
| **Data I/O**           |                       |                       |
| File Formats Supported | Description Old       | Description New       |
| **Performance**        | Description Old       | Description New       |
| **Usability**          | Description Old       | Description New       |
| **Security Features**  | Description Old       | Description New       |
| **Integration**        | Description Old       | Description New       |
| **Support and Documentation** | Description Old | Description New       |


## Correspondence to C/C++ PVGIS v.5.2

!!! warning "Historic notes"

    An early effort to link the features of PVGIS v5.2
    to a modern version
    is presented below for the sace of archival reasons!

??? note "Functionality correspondence to old PVGIS C/C++ source code"

    | Functionality                                   | PVGIS 5 | PV(G)IS 6                                                       |
    |-------------------------------------------------|---------|-----------------------------------------------------------------|
    | Parse input arguments                           |         | Read input                                                      |
    | Identify pixel row and column offsets           |         | Any Xarray-supported data format                                |
    | Select energy model                             |         |                                                                 |
    | Read elevation data                             |         | Any Xarray-supported data format                                |
    | Use horizon data                                |         | ❓                                                              |
    | Set number of hours for iterations              |         | Timestamps via Pandas' DatetimeIndex                            |
    | Read external SIS and SID time series           |         | Any Xarray-supported data format (including NetCDF, Zarr, etc.) |
    | Compute global irradiance                       |         | Any Xarray-supported data format (including NetCDF, Zarr, etc.) |
    | Read spectral correction values                 |         |                                                                 |
    | Read temperature & wind speed time series       |         |                                                                 |
    | Calculate solar geometry variables              |         |                                                                 |
    | Optimise slope if requested                     |         | Planned                                                         |
    | Optimise slope and aspect if requested          |         | Planned                                                         |
    | Set slope and aspect depending on tracking type |         | Planned                                                         |
    | Calculate total radiation                       |         | `irradiance` command                                            |
    | Calculate system performance                    |         | `power` command                                                 |
