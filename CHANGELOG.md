# Changelog

All notable changes to PVGIS 6 (pvgis-prototype) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

_No unreleased changes yet._

---

## [6.0.0-alpha] - 2025-12-01

**First tagged pre-release of PVGIS 6 Prototype.**

This Alpha tag
marks the first tagged version of the complete Python rewrite of PVGIS.
It represents development work from May 2023 through December 2025,
with over 3,600 commits.
This (non-)"release" is intended for
**demonstration, developer onboarding, early testing, and community feedback**.

### Highlights

- **Complete end-to-end system**: CLI, Web API, core algorithms, data models, I/O pipeline, and documentation
- **Solar position & geometry**: Several algorithms (NOAA, Jenčo) with refraction corrections, sunrise/sunset, hour angle
- **Irradiance modeling**: Global/direct/diffuse components, Hofierka (2002), Muneer (1990), Martin & Ruiz (2005), spectral effects, bifacial support
- **PV performance**: Huld et al. (2011) model, Faiman (2008) thermal, multi-technology support (cSi, CdTe, CIS), loss factors
- **Horizon shading**: Profile interpolation, sun-horizon analysis, shading state determination
- **Modern Python stack**: FastAPI, Pydantic, Xarray, Pandas, asyncio, NumPy/Numba optimization, type hints, pytest, CI/CD
- **Rich outputs**: CSV/JSON export, terminal tables (Rich), plots (Uniplot), QR codes, fingerprinting
- **Extensible architecture**: YAML-based data models, automatic validation, metadata handling

### Added

- Sample CSV output files for photovoltaic performance analysis
- Documentation page for CSV output format
- All core CLI commands: `position`, `irradiance`, `power`, `performance`, `tmy` (prototype)
- All major Web API endpoints: `/api/v1/position/overview`, `/api/v1/irradiance/*`, `/api/v1/performance/*`, `/api/v1/tmy`
- Comprehensive test suite (algorithms, API, CLI)
- MkDocs-based documentation system
- Dev container, pre-commit hooks, GitLab CI/CD pipeline

### Changed

- Updated dependencies: numpy 2.0.2, numba 0.60.0, llvmlite 0.43.0
- Refined pyproject.toml and uv.lock for stable dependency resolution

### Fixed

- Position overview Web API endpoint functionality
- NotoSansMath font availability and installation
- CI pipeline configuration (Python image, virtual environment setup)
- CSV output timestamp handling in irradiance functions
- Sky-reflected irradiance YAML data model definitions
- Refracted solar altitude in global inclined irradiance output
- DatetimeIndex frequency inference

### Known Issues & Limitations

**This is an Alpha release. Not production-ready.**

- Many API endpoints and CLI commands are incomplete, experimental, or require further refactoring
- Numerous TODO/FIXME markers throughout codebase; some features are placeholders
- Full cross-consistency and validation between CLI and API not guaranteed
- Core data pipelines and algorithm modules are functional but not finalized
- Documentation incomplete in many areas; expect breaking changes in future releases
- Feedback and community testing welcome; please report issues on GitLab

### What's Next

Check out the [issues](https://code.europa.eu/pvgis/pvgis/-/issues)
at the official repository

---

## Development Milestones (Pre-Alpha)

> **Note**: The following versions (0.3.0–0.9.0)
represent **logical development milestones**
reconstructed from Git history for internal documentation.
They were never tagged or released publicly.
The `6.0.0-alpha` tag above is the **first official tagged version**.

### [0.9.0] - 2024-10-27 - Horizon Shading Integration

#### Added
- Complete horizon shading implementation
- Shading state determination (sunlit, potentially-sunlit, in-shade)
- Horizon profile interpolation based on solar azimuth
- Integration with irradiance and power calculations
- CLI and API support for shading analysis
- Polars integration for fast data operations

#### Changed
- Massively refactored printing functions to support shading
- Updated constants and typer components for shading
- Overhauled API `position/shading.py` module
- Moved shading algorithm under PVIS module

### [0.8.0] - 2024-09-28 - Timezone & TMY Improvements

#### Added
- Major timezone handling refactor
- Improved CLI UX with azimuth convention helpers
- Prototype TMY (Typical Meteorological Year) functionality
- Time series filtering based on Xarray coordinates
- Generate timestamps with improved flexibility

#### Changed
- Major refactor of timezone-related functions
- Updated CLI components for better timestamp handling
- Improved DatetimeIndex operations
- Enhanced caching to support numpy ndarrays

#### Fixed
- Error handling for start and end time on API
- TMY calculations after extended development pause

### [0.7.0] - 2024-06-30 - Web API & Optimization

#### Added
- Surface position optimization endpoint
- Intake data catalog endpoint (experimental)
- Custom caching implementation
- Comparison documentation (v6 vs v5.2)
- Architecture and time series diagrams

#### Changed
- Split performance-relevant bits in API
- Simplified caching mechanism
- Safeguarded empty DatetimeIndex cases
- Major Web API updates and refactoring

#### Fixed
- QR generator for multiple surfaces API calls
- Web API endpoint for broadband multi-surface analysis

### [0.6.0] - 2024-04-01 - Data Model & CLI Enhancements

#### Added
- Major restructure of API power modules
- Diffuse horizontal irradiance calculations
- Solar incidence calculations (Jenčo algorithm)
- Irradiance custom data class
- Panel output option for CLI
- Print functions for solar position in columns

#### Changed
- Updated type mapping in data class factory
- Restructured CLI diffuse output with uniplot option
- Enhanced API direct and reflected irradiance modules

#### Fixed
- Missing log parameter in `model_solar_azimuth()`
- CSV output excluding fingerprint column
- Dependencies in pyproject.toml

### [0.5.0] - 2023-12-22 - Vectorization & FastAPI Foundation

#### Added
- Major vectorization of NOAA solar geometry functions
- FastAPI Web API foundation
- Metadata for FastAPI app
- Spectral factor and mismatch calculation commands
- MkDocs documentation system
- GitLab CI/CD for documentation

#### Changed
- Major update to timestamp generation mechanism
- Adopted Pandas timing engine
- Massively renamed classes to `..Model` from `..Models`
- Restructured power-related modules

#### Fixed
- Timezone attachment for DatetimeIndex
- Return statements in power calculation functions

### [0.4.0] - 2023-09-01 - Core Algorithm Implementation

#### Added
- NOAA solar position algorithms
- PVGIS solar geometry models
- Jenčo solar incidence calculations
- YAML-based parameter definitions
- Data class generation system
- Comprehensive test suite for algorithms

#### Changed
- Split NOAA models into parameter and function models
- Consolidated API constants
- Updated parameter models structure

#### Fixed
- Refracted solar altitude calculations
- Solar declination computations
- Angle output unit handling

### [0.3.0] - 2023-08-01 - Project Foundation

#### Added
- Initial project structure
- Basic CLI with Typer
- Core API modules
- Test framework with pytest
- Configuration files (pyproject.toml, setup.cfg)
- Git repository setup
- Package structure (`pvgisprototype`)
- Development environment configuration
- Testing infrastructure
- Documentation skeleton

---

## Project History & Context

**PVGIS 6** is a complete Python rewrite of the PVGIS (Photovoltaic Geographical Information System) originally developed at the European Commission's Joint Research Centre (JRC). Development began in **May 2023**.

### Development Statistics

- **2023**: 1,695 commits — Foundation and core algorithms
- **2024**: 1,511 commits — Feature development and Web API
- **2025**: 136+ commits — Refinement and Alpha release preparation

**Total**: Over **3,600 commits** across multiple development phases.

### Development Phases

**Phase 1: Assessment & Planning (Nov 2021 – Apr 2023)**
- Comprehensive assessment of PVGIS ≤5.2 legacy system
- "State & Future of PVGIS" internal presentation (Sep 2022)
- Feasibility study planning (Apr 2023)

**Phase 2: Proof-of-Concept Launch (May – Dec 2023)**
- Proof-of-Concept production launch (May 2023)
- Git repository creation at JRC GitLab (Jun 2023)
- Solar positioning prototype using NOAA's equations with NumPy (~120s runtime, Nov 2023)
- Meeting with CM-SAF Team (DWD) on chunking for large time series (Nov 2023)
- "Proof-of-Concept Modern PVGIS" internal presentation (Nov 2023)
- Breakthrough: Vectorization of solar positioning functions, PV power modeling acceleration (~2.5s runtime, Dec 2023)
- External presentation at DWD, Germany (Dec 2023)

**Phase 3: Performance Optimization & Testing (Jan – Jun 2024)**
- Enhanced PV power modeling: ~3.5s for 15 years of hourly data (Mar 2024)
- Testing framework introduction (Apr 2024)
- 335,336 automated tests for solar positioning (May 2024)
- Web API feature integration: QR codes, fingerprinting (Jun 2024)
- "PVGIS 6: A bit more than a Proof-of-Concept" internal presentation (Jun 2024)

**Phase 4: Scaling & Stakeholder Engagement (Jul – Nov 2024)**
- Web API optimization: <1 sec response time (Aug 2024)
- "PVGIS 6: Nearing an Alpha Version" internal presentation (Oct 2024)
- Issue tracking milestone: ~200 issues in GitLab (Oct 2024)
- 141,246 automated tests for optimal surface positioning (Nov 2024)
- "PVGIS 6" presentation at Digital Stakeholder Forum, DIGIT, EC (Nov 2024)

**Phase 5: Compliance, Security & Public Release (Dec 2024 – Dec 2025)**
- "SARAH data in PVGIS: Past, present & future", CM-SAF Workshop, DWD (Jan 2025)
- Static analysis & vulnerability assessment, Security Assurance, DIGIT, EC (Jun 2025)
- Intellectual property clearance: Source code approved for EUPL 1.2 license, IPR, EC (Jul 2025)
- "PVGIS Version 6" final internal PoC presentation (Jul 2025)
- **Alpha release preparation and public tagging (Dec 2025)**

### Legacy PVGIS Versions

**Previous versions** (PVGIS 5.x and earlier) were implemented in **C/C++**
and are still maintained separately.
PVGIS 6 is designed with the goal to replace the legacy implementation
powering the public web service at:

- **Web service**: https://re.jrc.ec.europa.eu/pvg_tools/en/
- **Homepage**: https://pvgis.jrc.it
- **JRC page**: https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis_en

---

## Version Links

[Unreleased]: https://gitlab.com/NikosAlexandris/pvgis-prototype/compare/v6.0.0-alpha...HEAD
[6.0.0-alpha]: https://gitlab.com/NikosAlexandris/pvgis-prototype/releases/tag/v6.0.0-alpha
