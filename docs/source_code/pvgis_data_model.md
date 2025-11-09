---
icon: material/language-python
title: Data Model
tags:
  - pvgisprototype
  - Python
  - Dependencies
  - Dependency Tree
---

## 🏗️ Data-Model Engineering

In PVGIS 6 **scientific data structures are defined in YAML, not Python**.
A transformation engine generates Python-native data models.
This separation enables domain scientists to shape models and data structures
while developers maintain a transformation engine.

- Core entities are **described once in YAML**.  
- Recursive loaders convert YAML into rich Python dictionaries and Pydantic models.  
- Complex relationships may be **visualised as graphs** to uncover redundant structures, reveal hidden coupling, and guide refactors.

#### 📐 A layered architecture

##### 1 YAML definitions

Atomic YAML files declare data structures—field names, types, units, dependencies—in a clean, programming-language-agnostic format. A scientist defines `GlobalInclinedIrradiance` by listing its physical components (direct beam, diffuse sky, ground reflection) without writing Python.

<!-- !!! note "See the YAML definitions directory" -->

<!--     ``` title="definitions.yaml" -->
<!--     --8<-- "pvgisprototype/core/data_model/definitions.yaml" -->
<!--     ``` -->

The contents of the `definitions.yaml` directory

```python exec="true" result="tree"
from pathlib import Path

def print_tree(directory, level=1):
    directory = Path(directory)
    if not directory.is_dir():
        return  # ensure it's a directory

    # list first level files and directories
    tree = str()
    for path in sorted(directory.iterdir()):
        if path.name.startswith('_'):
            continue  # skip files or directories starting with '_'
        if path.is_dir():
            tree += f"    {path.name}/"  # add slash to indicate it's a directory
        else:
            tree += f"    {path.name}"
        tree += '\n'

    return tree

tree = print_tree('pvgisprototype/core/data_model/definitions.yaml')
print(tree)
```

The `require:` directive enables **compositional inheritance**: a model pulls attributes from multiple parent templates, reusing common patterns (timestamps, location metadata) while adding domain-specific fields (Linke turbidity, albedo, temperature coefficients).

##### 2 Definition factory

The `generate.py` script orchestrates a **graph-based resolution algorithm**:

```bash
python generate.py --log-level DEBUG --log-file definitions.log
```

A safe and reusable command to run and generate the `definitions.py` is :

```bash
yes "yes" | rm definitions.py && echo "PVGIS_DATA_MODEL_DEFINITIONS = {}" > definitions.py && python generate.py --log-level DEBUG --log-file definitions.log
```



This function

- Loads YAML files and parses `require:` directives (inheritance declarations)
- Traverses dependency trees using **recursive descent**, detecting circular references
- Merges parent attributes into child models via deep-merge logic
- Generates a consolidated `definitions.py` containing fully expanded model specifications

This approach collapses complex inheritance chains (e.g., `SolarAltitude` → `DataModelTemplate` → `BaseTemplate`) into a single, self-contained definition.

A future task for the project would be to run this _generation_ automatically at installation time !

##### 3 Runtime factories

**DataModelFactory** dynamically generates Pydantic models:

```python
from pvgisprototype import SolarAzimuth  # Factory lookup → instantiation
```

The factory maps YAML type strings to Python types, injects NumPy array handling, and enables validation that catches errors like **missing required fields, incorrect data types, incompatible array shapes, or out-of-range values** before calculations proceed.

Functions of the context factory transform model instances into structured outputs :

```python
result.build_output(verbose=2)  # Nested dict ready for API/CLI/Web API
```

The above reads output structure definitions from YAML,
evaluates conditional sections (e.g., verbosity levels),
and constructs nested dictionaries representing calculation results.
This ensures API responses, CLI output, and documentation remain synchronized.

#### 🔄 Command and data object lifecycle

Data models exist **transiently**—instantiated on-demand, used during calculation, garbage-collected immediately after:

**1. Import**

```python
from pvgisprototype import GlobalInclinedIrradiance
```

Models are imported from the consolidated `definitions.py` module.

**2. Factory generation**

At runtime, **DataModelFactory** retrieves the model's definition and dynamically generates a Pydantic class.

**3. Calculation**

Models are typically returned by calculation functions:

```python
def calculate_solar_position(latitude, longitude, timestamp):
    # ... calculations ...
    return SolarAzimuth(
        value=azimuth_array,
        solaraltitude=altitude_array,
        timestamp=timestamp,
        location=(latitude, longitude)
    )
```

Pydantic validation occurs immediately upon instantiation, ensuring downstream functions receive well-formed, type-safe data.

**4. Output Generation**

Each data model embeds an output structure definition describing how its attributes should be presented. The **ContextBuilder** reads this structure and calls the model's `.build_output()` method:

```python
result = calculate_solar_position(lat, lon, time)
output = result.build_output(verbose=2)
```

This populates the `output` attribute automatically—a structured dict ready for consumption by:

- **Web API endpoints** (JSON responses)
- **CLI tools** (formatted terminal output)
- **Core API functions** (programmatic access)

**5. Expiration**

Once output is returned, the model instance is garbage-collected. No persistent state remains between requests, ensuring thread safety and predictable memory usage in multi-user environments.

#### 🌐 Language-Agnostic Philosophy

YAML definitions are intentionally **programming-free**. This way they can be
reused in other contexts and programming languages.
Another experimental idea/feature embeds *dependency annotations*
(e.g., "GlobalInclinedIrradiance requires: direct beam, diffuse sky, tilt angle")
that may serve as **executable documentation**.
While the current prototype doesn't really/fully exploit such annotations,
they enable:

- **Cross-platform model reuse** (parsers in Julia, R, JavaScript could regenerate workflows)
- **Transparent calculation pipelines** (researchers see required inputs without reading code)
- **Automated dependency graphs** (visualize model relationships)

#### Graph visualisation & more 

PVGIS can visualise its own data model graphs.

**Examples**

The `data_model_template.yaml` is  

```yaml
name: DataModelTemplate
label: Data Model Template
description: A generic template for data models
symbol: ⎄
color: gray

require:
 
  # Identifier attributes
  - attribute/name
  - attribute/shortname
  - attribute/supertitle
  - attribute/title
  - attribute/label
  - attribute/description
  - attribute/symbol

  # Values
  - attribute/value
  - attribute/unit

  # Metadata attribute
  - attribute/algorithm
  - attribute/equation
  - metadata/data_source
```

and brings in various _attributes_ to build a template data model.

For example, the `symbol` attribute is described in a YAML file itself

```yaml
name: SymbolAttribute
label: Symbol
description: Attribute for a symbol of a data model
color: lightgray

sections:

  symbol:
    type: str
    title: Symbol
    description: Symbol for the data model
    initial:

```

We can visualise the _template_ via :

```bash
pvgis-prototype data-model --log-file data_model.log visualise gravis-d3 --yaml-file  definitions.yaml/data_model_template.yaml
```

will generate an dynamic and clickable HTML file (here an SVG export of it is shown)


  ![Data Model Template](docs/reference/data_model_template_graph.svg)


This is for example the generic template which many data model definitions use.

The mostly complex photovltaic power output data structure can be visualised
visualised

```bash
rm data_model_graph.html  # first -- or fix-the CLI to overwrite this !
pvgis-prototype data-model visualise gravis-d3 --yaml-file  definitions.yaml/power/photovoltaic.yaml
```

  ![Data Model Template](docs/reference/photovoltaic_power_data_model_graph.svg)


> Ditto, this image is unreadable.  Generate the HTML file, open and explore it
> in your browser !


#### ⚖️ The trade-off

**Why this complexity?**

PVGIS counts a large number of interconnected data models
that may evolve as solar research advances.
Changes to irradiance algorithms, metadata structures,
or output formats propagate through YAML edits—not scattered code modifications.
Domain experts can contribute directly to model definitions
while developers can focus in the transformation engine.

**Acknowledged limitations**  

- **Learning curve**: Understanding `require` chains requires conceptual investment
- **Debugging difficulty**: YAML merge errors can be opaque—yet the build process generates detailed logs
- **Build-time dependency**: Changes require regenerating `definitions.py`

**Future work**  

A refactoring pass will migrate hardcoded values from `constants.py`
into YAML definitions,
completing the separation of domain knowledge from implementation.

#### 🎯 This approach is...

- Managing **dozens of similar but distinct** data structures
- Enabling **cross-disciplinary collaboration** (scientists define models, engineers build infrastructure)
- Supporting **rapidly changing domain requirements** (new algorithms, extended outputs)
- Ensuring **long-term maintainability** over immediate simplicity

This architecture prioritizes **scientific transparency** and **future flexibility** over ease of onboarding—a deliberate trade-off recognizing that PVGIS models will outlive any single development team.

