---
icon: material/language-python
title: Core Source Code
subtitle: Python engineering for PVGIS
tags:
  - Core
  - Source Code
  - Python
  - Hashing
  - Caching
  - Engineering
---

# Core Engineering Components

The `core` module contains the foundational engineering infrastructure that
powers PVGIS. While [algorithms](algorithms.md) implement solar science and the
core [API](api.md) and [CLI][cli.md] provide user-facing interfaces, the core
module handles essential cross-cutting concerns like data model generation,
caching, hashing, and context management.

## What's in Core?

The core module includes:

- **Data Model Factory**: Dynamic generation of Pydantic models from YAML definitions
- **Context Builder**: Structured output generation and verbosity management
- **Caching System**: Performance optimization through memoization
- **Hashing Utilities**: Data fingerprinting for reproducibility and cache keys
- **Type Definitions**: Shared type hints and validation schemas

These components operate behind the scenes, ensuring type safety, performance,
and maintainability across the entire PVGIS codebase.

## Design Philosophy

Core components follow these principles:

- **Separation of concerns**: Scientific domain logic (algorithms) stays
  independent from the infrastructure (core) and interfaces (API, CLI, Web API)
- **Type safety**: Pydantic validation catches errors before calculations run
- **Performance**: Caching and efficient data structures minimize redundant computation
- **Extensibility**: Factory patterns enable adding new models without code duplication

## Key Components

### Data Model Factory

Transforms YAML definitions into runtime Pydantic classes, enabling:

- Centralized model definitions maintained by domain experts
- Automatic validation of calculation inputs and outputs
- Consistent structure across API, CLI, and Web API interfaces

See [Data Model](pvgis_data_model.md) for detailed documentation.

### Context Builder

Manages output generation based on verbosity levels and user requirements:

- Reads output structure definitions from YAML
- Evaluates conditional sections (e.g., metadata only at high verbosity)
- Constructs nested dictionaries ready for JSON/CSV/terminal output

### Caching and Hashing

Optimizes repeated calculations through:

- **Content-based caching**: Hash inputs to detect identical calculations
- **Memory management**: Configurable cache sizes and eviction policies
- **Reproducibility**: Fingerprints enable tracking data provenance

## Usage Pattern

Core components are typically not imported directly by users. Instead, they're
used internally by API functions:

User calls API function

``` python
from pvgisprototype.api import calculate_solar_position
```

``` python
result = calculate_solar_position(lat=45.0, lon=8.0, timestamp="2025-01-01")
```

Behind the scenes:

1. DataModelFactory creates SolarPosition model
2. Calculation runs and validates output
3. ContextBuilder generates structured result
4. Caching stores result for future identical requests

## Source Code Reference

::: pvgisprototype.core

    options:
        show_submodules: True
