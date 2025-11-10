---
icon: material/chat-processing
title: Verbosity
subtitle: Show what's going on
description: Multiple levels of verbosity for each command line tool
tags:
  - How-To
  - CLI
  - Verbosity
---

**Verbosity** is a fundamental functional element in PVGIS.
It enables to retrieve detailed parts of the calculation chain
right from the solar positioning
and through the solar irradiance components
up to the photovoltaic performance figures.
The following examples
demonstrate how it works and what type of output we can get.

<div class="grid cards" markdown>

- :simple-levelsdotfyi: __Multiple verbosity levels__

    Use the `-v` flag to keep it minimal or up to `-vvvvvvvvv`,
    to get all of the calculation details!

- __Index__

    Use `--index` or simply `-i` to index the output.

- :shushing_face: __Quiet__

    Use `--quiet` to silence longer time series
    that take some time to print in the terminal.

- :material-bug: __Debugging__

    If things don't work out, use `-vvvvvvvvvv`
    <!-- ```python exec="true" -->
    <!-- from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL -->
    <!-- print(f"-{DEBUG_AFTER_THIS_VERBOSITY_LEVEL * 'v'}") -->
    <!-- ``` -->
    to get debugging details!

</div>


## :simple-shortcut: Shortcut `-v`

`-v` is a shortcut for `--verbose`.
And `-vv` is the same as asking twice for `--verbose`,
i.e. `--verbose --verbose`.

=== "--verbose"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35 '2010-01-27 12:00:00' --verbose
    ```

=== "-v"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35 '2010-01-27 12:00:00' -v
    ```

=== "--verbose --verbose"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35 '2010-01-27 12:00:00' --verbose --verbose
    ```

=== "--vv"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35 '2010-01-27 12:00:00' -vv
    ```

## :simple-levelsdotfyi: Multiple levels

=== "No verbosity"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35
    ```

=== "-v"


    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35 -v
    ```

=== "-vv"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35 -vv
    ```

=== "-vvv"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35 -vvv
    ```

=== "-vvvv"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35 -vvvv
    ```

=== "-vvvvv"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35 -vvvvv
    ```

=== "-vvvvvv"

    ``` bash exec="true" result="ansi" source="above"
    pvgis-prototype power broadband 8.628 45.812 214 180 35 -vvvvvv
    ```

## Index

Indexing can make it easier to spot a line of interest in the output table.
We can ask for it via `--index` or simply `-i` 

``` bash exec="true" result="ansi" source="above" hl_lines="6"
pvgis-prototype power broadband \
    8.628 45.812 214 180 35 \
    --start-time '2010-01-27' \
    --end-time '2010-01-28' \
    -vv \
    --index
```

## :shushing_face: Quiet

Need to silence (a) long time series output ?
Printing very long time series in the terminal is rather impractical,
aside that it takes quite some time for the print-out.
To work-around this inconvenience,
there is a `--quiet` flag which will **ommit the print out altogether**.

``` bash exec="true" result="ansi" source="above" hl_lines="5"
pvgis-prototype power broadband \
    8 45 214 167 \
    --start-time '2000-01-01' \
    --end-time '2020-12-31' \
    --quiet
```

_How is this useful ?_
This option may be useful for timing the duration of processes
or printing a plot of the output or metadata of the command itself.

### :material-timer: Duration of command execution

We can _time_ the duration of a command that processes a long time series
using the terminal's built-in function `time` :

``` bash exec="true" result="ansi" source="material-block" hl_lines="1"
time \
pvgis-prototype power broadband \
    8 45 214 167 \
    --start-time '2000-01-01' \
    --end-time '2020-12-31' \
    --quiet
```

## :material-bug: Debugging

There is an important constant in the core API 
named `DEBUG_AFTER_THIS_VERBOSITY_LEVEL`.

!!! info "Default array backend and data type"

    ```bash exec="true" session="debug-after-this-verbosity-level"
    python << 'EOF'
    from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
    print(f'{DEBUG_AFTER_THIS_VERBOSITY_LEVEL=}')
    EOF
    ```

Using more `-v`s than the constant `DEBUG_AFTER_THIS_VERBOSITY_LEVEL`
in (almost!) every command,
will print the _complete_ set of local variables
relevant to the (API) function
called from the invoked command line tool.

??? example "Example support for debugging (very long output)"

    ``` bash exec="true" result="ansi" source="above" hl_lines="6"
    pvgis-prototype power broadband \
        8 45 214 167 \
        --start-time '2000-01-01' \
        --end-time '2020-12-31' \
        --quiet \
        -vvvvvvvvvvv
    ```
