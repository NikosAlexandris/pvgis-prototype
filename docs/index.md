# PVGIS Reference

Welcome to the documentation of PVGIS 

Please head over to [Summary of Documentation](SUMMARY.md) for a summary of all modules, classes, and functions.

## Installation

### Requirements

- Python

1. Clone the source code repository
2. Step in
3. Install the Python package


### Install !

<div class="termy">

```console
$ git clone https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype
$ cd pvis-be-prototype
$ pip install ."[all]"
---> 100%
Successfully installed pvis
```

</div>

**Note**: that will include
<a href="https://rich.readthedocs.io/" class="external-link" target="_blank">Rich</a>.
Rich is library to *display* visually pleasing information on the terminal.
Is it deeply integrated into **PVIS**.


Then, welcome yourself in the command line interface

<div class="termy">

```console
❯ pvgis-prototype

 Usage: pvgis-prototype [OPTIONS] COMMAND [ARGS]...

 PVGIS Command Line Interface prototype

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────╮
│ --version                Show the version of the application and exit                             │
│ --log      -l      PATH  Specify a log file to write logs to, or omit for stderr. [default: None] │
│ --help                   Show this message and exit.                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Input / Output ───────────────────────────────────────────────────────────────╮
│ --verbose  -v      INTEGER  Show details while executing commands [default: 0] │
╰────────────────────────────────────────────────────────────────────────────────╯
╭─ Performance ──────────────────────────────────────────────────────────────────╮
│ power  🔌 Estimate the performance of a photovoltaic system over a time series │
╰────────────────────────────────────────────────────────────────────────────────╯
╭─ Time series ────────────────────────────────────────────────────────────╮
│ series      💹 Work with time series                                     │
│ irradiance  🌞 Estimate the solar irradiance incident on a solar surface │
╰──────────────────────────────────────────────────────────────────────────╯
╭─ Solar geometry ───────────────────────────────────────────────────────────────────────────╮
│ time      ⌛ Calculate the solar time for a location and moment                            │
│ position  📐 Calculate solar geometry parameters for a location and moment in time         │
│ surface   󰶛  Calculate solar surface geometry parameters for a location and moment in time │
╰────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Toolbox ───────────────────────────╮
│ utilities  🧰  Diagnostic functions │
╰─────────────────────────────────────╯
╭─ Reference ─────────────────────────────────────╮
│ manual  📖 Manual for solar radiation variables │
╰─────────────────────────────────────────────────╯
```

</div>


Auto-completion in the command line can be installed optionally.
This is offered via a hidden command ! 

<div class="termy">

``` console
❯ pvgis-prototype completion show --help

 Usage: pvgis-prototype completion show [OPTIONS]
                                        SHELL:{bash|zsh|fish|powershell|pwsh}

 Show completion for the specified shell, to copy or customize it.

╭─ Arguments ───────────────────────────────────────────────────────────────────────────╮
│ *    shell      SHELL:{bash|zsh|fish|powershell|p  [default: None] [required]         │
│                 wsh}                                                                  │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                           │
╰───────────────────────────────────────────────────────────────────────────────────────╯
```

</div>

# Welcome to the PVGIS Reference

Welcome to the official documentation of PVGIS API. This comprehensive guide is designed to help you navigate through the features, capabilities, and detailed API references of PVGIS.

## About PVGIS

[Provide a brief overview of what PVGIS API is, its purpose, and what problems it solves. Mention any key features or unique selling points of your API.]

## Getting Started

If you're new to PVGIS API, start with our [Basic Usage](basic_usage.md) guide to get up and running quickly. Learn how to configure and integrate the API into your projects with ease.

## Key Features

- **Feature 1**: [Short description of feature]
- **Feature 2**: [Short description of feature]
- **Feature 3**: [Short description of feature]
- [And so on...]

For a full list of features, see the [Features](features.md) page.

## API Reference

Dive into the detailed API documentation to understand the full capabilities of PVGIS API:

- [Module Index](SUMMARY.md): Explore the comprehensive list of all modules, classes, and functions provided by PVGIS API.
- [Class References](reference/classes.md): Detailed documentation of all classes within the API.
- [Function Index](reference/functions.md): List and descriptions of all functions available in the API.

## CLI Reference

`pvis` is the CLI component of PVGIS.
..

## Advanced Topics

For advanced users, we offer in-depth guides and discussions on more complex aspects of PVGIS API:

- [Advanced Use](advanced_use.md)
- [Adding New Features](adding_new_features.md)

## Under Development

- [Performance Optimization](performance_optimisation.md)

## Contributing

PVGIS API is an open-source project, and we welcome contributions of all forms. If you're interested in contributing, please read our [Contribution Guidelines](contribution_guidelines.md).

## Support and Community

If you have questions or need support, join our [Community Forum](community_forum.md) or check out the [FAQ](faq.md) section.

Thank you for choosing PVGIS API for your solar irradiance calculation needs!

---

**Note**: This documentation is auto-generated and regularly updated to reflect the latest changes in the API.
