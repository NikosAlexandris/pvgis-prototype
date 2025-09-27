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

??? info "Scope & Target audience"

    | Category    | 5                                                                | 6   |
    |-------------|------------------------------------------------------------------|-----|
    | Citizens    | Yes                                                              | Yes |
    | Prosumers   | Yes                                                              | Yes |
    | Researchers | Indirectly & partly available through [r.sun][r.sun] (GRASS GIS) | Yes |
    | Developers  | -                                                                | Yes |
    | Industry    | -                                                                | -   |

    [r.sun]: https://grass.osgeo.org/grass83/manuals/r.sun.html

??? "Licensing"

    | License           | 5                                  | 6                                  |
    |-------------------|------------------------------------|------------------------------------|
    | Use license       | -                                  | EUPL-1.2, CCSA (Documentation)     |
    | User Feedback     | Positive/Negative feedback summary | Positive/Negative feedback summary |
    | Usage             | Examples of usage in ...  | Examples of usage in ...  |
    | Community Support | Active/Inactive, Size of community | Active/Inactive, Size of community |
    | Update Frequency  | Regular/Infrequent updates         | Regular/Infrequent updates         |

## Functionality

??? info "Capabilities & Functionality Comparison"

    | Functionality            | 5                                                                                    | 6                                                                 |
    |--------------------------|--------------------------------------------------------------------------------------|-------------------------------------------------------------------|
    | Solar Position           | Internal, Only the solar altitude part of final analysis, Hofierka 2002 (Jenco 1992) | Selectable, Jenco (1992), NOAA, NREL SPA[^SPA], Skyfield, pysolar |
    | Solar Incidence          | Internal, Hofierka 2002 (Jenco 1992)                                                 | Selectable, Jenco (1992), Iqbal 1992                              |
    | Solar Irradiance         | Part of final analysis, Hofierka 2002                                                | Independent for each radiation component, Hofierka 2002           |
    | Photovoltaic Performance | Huld 2011, Gracia 2016                                                               | Huld 2011, Gracia 2016                                            |

## Architecture

??? note "Implementation Details"

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
--8<-- "docs/reference/time_series_data_workflow_comparison_pvgis_v6_vs_v52.py"
```

## Performance

??? note "Efficienct & Reliability"

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

??? info "Customisation & Reliability"

    | Question                  | 5                                                       | 6                                                                        |
    |---------------------------|---------------------------------------------------------|--------------------------------------------------------------------------|
    | Customization Ease        | Very Difficult                                          | Very Easy                                                                |
    | Real-world Usage Examples | Data fetched through Public Web API                     |                                                                          |
    | Codebase Quality          | Poor                                                    | Estimated : Good, to be reviewed                                         |
    | Performance & Reliability | High performance, Poor reliability due to lack of tests | High performance, High reliability, Automated testing : Work-in-progress |

## Capabilities

??? info "Scientific Functionality"

    | Photovoltaic system | Software A | Software B |
    |---------------------|------------|------------|
    | Grid-connected      | Yes        | Yes        |
    | Off-Grid            | Yes        | Planned    |
    | Tracking            | Yes        | Planned    |

??? note "Other capabilities"

    | Capabilities                 | 5   | 6                |
    |------------------------------|-----|------------------|
    | Solar irradiance time series | Yes | Yes              |
    | Meteorological time series   | Yes | Yes              |
    | TMY                          | Yes | Work-in-progress |
    | Fingerprinted results        | -   | Yes              |
    | QR-Code shareable output     | -   | Yes              |
