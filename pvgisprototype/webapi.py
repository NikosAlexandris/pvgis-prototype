from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from git import Repo

from pvgisprototype.api.citation import generate_citation_text
from pvgisprototype.api.conventions import generate_pvgis_conventions
from pvgisprototype.log import initialize_web_api_logger
from pvgisprototype.web_api.config import Environment, get_environment, get_settings
from pvgisprototype.web_api.config.base import CommonSettings
from pvgisprototype.web_api.config.options import Profiler
from pvgisprototype.web_api.middlewares import (
    ClearCacheMiddleware,
    LogRequestIDMiddleware,
    profile_request_functiontrace,
    profile_request_pyinstrument,
    profile_request_scalene,
    profile_request_yappi,
    response_time_request,
)
from pvgisprototype.web_api.openapi import customise_openapi, tags_metadata
from pvgisprototype.web_api.performance.broadband import (
    get_photovoltaic_performance_analysis,
)
from pvgisprototype.web_api.performance.spectral_effect import (
    get_spectral_factor_series,
)
from pvgisprototype.web_api.position.overview import (
    get_calculate_solar_position_overview,
)
from pvgisprototype.web_api.power.broadband import (
    get_photovoltaic_power_output_series_multi,
    get_photovoltaic_power_series,
    get_photovoltaic_power_series_advanced,
)
from pvgisprototype.web_api.surface.optimise import get_optimised_surface_position
from pvgisprototype.web_api.tmy import get_typical_meteorological_variable

current_file = Path(__file__).resolve()
assets_directory = current_file.parent / "web_api/assets"
static_directory = current_file.parent / "web_api/static"
data_directory = current_file.parent / "web_api/data"

summary = """
PVGIS
offers open-access insights
on :

- solar radiation ☀ ;

- and location-specific estimates of

    - photovoltaic performance 📈,

    - for various technologies 🔌🔋

    - over Europe & Africa 🌍, largely Asia 🌏 and the Americas 🌎.
"""

description = """
<span style="color:red"> <ins>**This Application Is a Feasibility Study**</ins></span>
**limited to** longitudes ranging in [`7.5`, `10`] and latitudes in [`45`, `47.5`].

The **PVGIS Web API**
is a public service
supported by the
[Joint Research Centre (JRC)](https://joint-research-centre.ec.europa.eu/index_en)
European Commission. 🇪🇺
For detailed information and structured content,
please refer to the
[PVGIS Documentation](https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/).
"""

pvgis6_features = """
# Overview of Features

PVGIS 6
is a public service in the domain of photovoltaic performance analysis.
It introduces a series of advanced features and improvement over its predecessor.
Built with modern technologies and a user-centric design,
PVGIS 6 enhances user experience and broadens the scope of functionality,
making solar data more accessible.
This version is tailored to meet the needs of
researchers, developers, and prosumers,
offering comprehensive tools for detailed solar analysis.

# Algorithms & Models

- Optional solar positioning and incidence angle algorithms -- Default is NOAA's solar geometry set of equations (**under review**)
- Capability to disable atmospheric refraction for solar positioning.
- Surface position optimization supported by SciPy
- The same solar radiation model as in PVGIS 5.x (Hofierka, 2002), however based on tested calculations.
- From simple to fully analytical output of photovoltaic performance (power/energy) figures
- Reflectivity effect as a function of the solar incidence angle by Martin and Ruiz, 2005
- Spectal mismatch effect by Huld, 2011 based on the reference year 2013
- Photovoltaic efficiency coefficients by ESTI, C2, JRC, European Commission
- Overall system efficiency pre-set to 0.86, in other words 14% of loss for material degradation, aging, etc.
- Improved TMY engine, default is the ISO 15927-4 method as in PVGIS 5 and optionally the NREL and Sandia methods along with enhanced plots.

# Components

- Algorithmic repository based on Python and NumPy
- Core Application Programming Interface (API) for advance programmatic work
- Command Line Interface (CLI) through an expanded set of commands to support scripting, automation and exploratory research
- Web API: Offers a robust Web API compliant with modern standards for integration with other applications and automated retrieval of relevant time series

# Architecture & Development

- Custom Data Classes
- Duck Typing for interoperability between array computing backends (Work In-Progress)
- Comprehensive logging framework for troubleshooting and development support.
- Development Roadmap and Contribution Guidelines: Transparent development process with clear guidelines for contributors.

# Documentation

- A symbol system for quick reference of terms, quantities, units, data types and more items used throughout the application -- see [Symbols](https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/cli/symbols/)
- API, CLI, and Web API Documentation: Detailed documentation supports all functionalities, ensuring ease of use and accessibility.
- Rich metadata support for each calculation to support detailed documentation.

# Technical features

In :

- Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html) 
- Valid time zone identifiers from [the IANA Time Zone Database](https://www.iana.org/time-zones)
- Precision control of numerical outputs, would you ever need it!

Process :

- Optional algorithms for solar timing, positioning and the estimation of the solar incidence angle
- Disable atmospheric refraction for solar positioning
- Surface position optimisation supported by [SciPy](https://docs.scipy.org/doc/scipy/reference/optimize.html) (**pending integration**)
- Simpler power-rating model as well as module temperature model (**under review**)

Output Management

- Verbose output control for quick summaries and analytical output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)
- Built-in capability to generate visual plots directly in the command-line or to export as image file.
- **Fingerprint** each output for verification and tracing, enhancing data integrity and reproducibility.
- **QR Code** generation for easy sharing of results as an image or a Base64 string

## **Important Notes**

- The default time, if not given, regardless of the `frequency` is
  `00:00:00`. It is then expected to get `0` incoming solar irradiance and
  subsequently photovoltaic power/energy output.

- Of the four parameters `start_time`, `end_time`, `periods`, and
  `frequency`, exactly three must be specified. If `frequency` is omitted,
  the resulting timestamps (a Pandas `DatetimeIndex` object)
  will have `periods` linearly spaced elements between `start_time` and
  `end_time` (closed on both sides). Learn more about frequency strings at
  [Offset aliases](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).

# Input data

The application can read any Xarray-supported data format.
Notwithstanding, the default input data sources are :

- time series data limited to the period **2005** - **2023**.
- solar irradiance from the [SARAH3 climate records](https://wui.cmsaf.eu/safira/action/viewDoiDetails?acronym=SARAH_V003)
- temperature and wind speed estimations from [ERA5 Reanalysis](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) collection
- spectral effect factor time series (Huld, 2011) _for the reference year 2013_
"""


class ExtendedFastAPI(FastAPI):
    def __init__(
        self, settings: CommonSettings, environment: Environment, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.environment = environment


@asynccontextmanager
async def application_logger_initializer(
    app: ExtendedFastAPI,
):
    """Initialize Loguru for FastAPI & Uvicorn."""
    initialize_web_api_logger(  # Initialize Loguru for FastAPI & Uvicorn
        log_level=app.settings.LOG_LEVEL,
        rich_handler=app.settings.USE_RICH,
        server=app.settings.WEB_SERVER,
        access_log_path=app.settings.ACCESS_LOG_PATH,
        error_log_path=app.settings.ERROR_LOG_PATH,
        rotation=app.settings.ROTATION,
        retention=app.settings.RETENTION,
        compression=app.settings.COMPRESSION,
        log_console=app.settings.LOG_CONSOLE,
    )

    yield  # Application starts here


app = ExtendedFastAPI(
    title="PVGIS Web API Proof-of-Concept",
    description=description,
    summary=summary,
    version="6",
    openapi_tags=tags_metadata,
    terms_of_service="https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-background-information/data-protection_en",
    contact={
        "name": "PVGIS, Joint Research Centre, European Commission",
        "url": "https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-background-information/pvgis-contact-points_en",
        "email": "JRC-PVGIS@ec.europa.eu",
    },
    license_info={
        "name": "EUPL-1.2",
        "url": "https://spdx.org/licenses/EUPL-1.2.html",
    },
    swagger_ui_parameters={
        # "syntaxHighlight.theme": "obsidian",
        "syntaxHighlight": False,
        # "defaultModelsExpandDepth": -1,  # Hide models section
        "docExpansion": "none",  # expand only tags
        "filter": True,  # filter tags
        "displayRequestDuration": True,  # Display request duration
        "showExtensions": True,  # Show vendor extensions
    },
    default_response_class=ORJSONResponse,
    settings=get_settings(),
    environment=get_environment(),
    lifespan=application_logger_initializer,
)


app.mount("/assets", StaticFiles(directory=str(assets_directory)), name="assets")
app.mount("/static", StaticFiles(directory=str(static_directory)), name="static")
app.mount(
    "/data_catalog", StaticFiles(directory=str(data_directory)), name="data_catalog"
)
templates = Jinja2Templates(directory="pvgisprototype/web_api/templates")


def get_git_information():
    repository_path = Path(__file__).resolve().parent
    repository = Repo(repository_path, search_parent_directories=True)
    commit = repository.head.commit
    commit_hash = commit.hexsha[:7]
    commit_date = commit.committed_datetime.strftime("%B %Y")
    return commit_hash, commit_date


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    commit_hash, commit_date = get_git_information()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "commit_hash": commit_hash, "commit_date": commit_date},
    )


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_css_url="/static/custom.css",
        swagger_js_url="/static/custom.js",
    )


@app.get("/features", tags=["Features"])
async def get_features():
    return pvgis6_features


@app.get("/references/conventions-in-pvgis", tags=["Reference"])
async def print_conventions_text():
    return generate_pvgis_conventions()


@app.get("/references/license", tags=["Reference"])
async def print_license_text():
    return generate_citation_text()


@app.get("/references/citation", tags=["Reference"])
async def print_citation_text():
    return generate_citation_text()


@app.get("/references/download-citation", tags=["Reference"])
async def download_citation():
    citation = generate_citation_text()
    import json
    import tempfile

    from fastapi.responses import FileResponse

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as tmp:
        json.dump(citation, tmp, indent=4)
        tmp_path = tmp.name

    return FileResponse(
        tmp_path, media_type="application/json", filename="citation.json"
    )


@app.get("/references/publications", tags=["Reference"], response_class=FileResponse)
async def print_references():
    bibtex_file_path = assets_directory / "references.bib"
    return FileResponse(
        bibtex_file_path, media_type="application/x-bibtex", filename="references.bib"
    )


@app.get("/get-data-catalog", response_class=ORJSONResponse, tags=["Data-Catalog"])
async def get_catalog():
    file_path = data_directory / "pvgis_intake_data_catalog.yml"
    print(f"{file_path=}")
    try:
        with open(file_path, "r") as file:
            catalog_data = yaml.safe_load(file)
            return catalog_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Catalog file not found")
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=500, detail=f"Error parsing YAML file: {str(e)}"
        )


@app.get("/download-data-catalog", response_class=FileResponse, tags=["Data-Catalog"])
async def download_catalog():
    print(f"{data_directory=}")
    file_path = (
        data_directory / "pvgis_intake_data_catalog.yml"
    )  # Update this path to where the file is stored on your server
    print(f"{file_path=}")
    try:
        return FileResponse(
            file_path, media_type="application/x-yaml", filename="pvgis6_catalog.yaml"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Catalog file not found")


app.get(
    "/performance/broadband",
    tags=["Performance"],
    response_class=ORJSONResponse,
    summary="Analysis of photovoltaic performance",
    operation_id="performance-broadband",
    response_description="Analysis of Photovoltaic Performance (JSON)",
    status_code=status.HTTP_201_CREATED,
)(get_photovoltaic_performance_analysis)

app.get(
    "/performance/spectral-effect",
    tags=["Performance"],
    response_class=ORJSONResponse,
    summary="Estimate the spectal factor for one or more photovoltaic module types",
    operation_id="performance-spectral-effect",
    response_description="Estimate the spectal factor, a ratio of photovoltaic power generated by a solar module under actual conditions compared to standard reference conditions.",
    status_code=status.HTTP_201_CREATED,
)(get_spectral_factor_series)

app.get(
    "/power/broadband-demo",
    tags=["Power"],
    summary="A demonstration endpoint for calculating photovoltaic power",
    operation_id="power-broadband-demo",
)(get_photovoltaic_power_series)

app.get(
    "/power/broadband",
    tags=["Power"],
    summary="Calculate the photovoltaic power",
    operation_id="power-broadband",
)(get_photovoltaic_power_series_advanced)

app.get(
    "/power/broadband-multiple-surfaces",
    tags=["Power"],
    summary="Calculate the photovoltaic power generated for multiple surfaces",
    operation_id="power-broadband-multiple-surfaces",
)(get_photovoltaic_power_output_series_multi)

app.get(
    "/power/surface-position-optimisation",
    tags=["Power"],
    summary="Calculate the optimal surface position for a photovoltaic module",
    operation_id="surface-position-optimisation",
)(get_optimised_surface_position)

app.get(
    "/typical-meteorological-variable",
    tags=["TMY"],
    summary="Calculate the typical meteorological variable",
    operation_id="typical-meteorological-variable",
)(get_typical_meteorological_variable)

app.get(
    "/solar-position/overview",
    tags=["Solar-Position"],
    summary="Calculate the solar position time series",
    operation_id="overview",
)(get_calculate_solar_position_overview)

if app.settings.MEASURE_REQUEST_TIME:  # type: ignore
    app.middleware("http")(response_time_request)

if app.settings.PROFILING_ENABLED:
    if app.settings.PROFILER == Profiler.scalene:  # type: ignore
        app.middleware("http")(profile_request_scalene)
    elif app.settings.PROFILER == Profiler.pyinstrument:  # type: ignore
        app.middleware("http")(
            lambda request, call_next: profile_request_pyinstrument(request, call_next, profile_output=app.settings.PROFILE_OUTPUT)  # type: ignore
        )
    elif app.settings.PROFILER == Profiler.yappi:  # type: ignore
        app.middleware("http")(
            lambda request, call_next: profile_request_yappi(request, call_next, profile_output=app.settings.PROFILE_OUTPUT)  # type: ignore
        )
    elif app.settings.PROFILER == Profiler.functiontrace:  # type: ignore
        app.middleware("http")(profile_request_functiontrace)

app.add_middleware(LogRequestIDMiddleware)
app.add_middleware(ClearCacheMiddleware)

app.openapi = customise_openapi(app)  # type: ignore


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8001)
