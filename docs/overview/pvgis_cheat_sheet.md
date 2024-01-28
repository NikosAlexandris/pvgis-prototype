## Introduction

   Overview of the software.
   Purpose and main features.

## Installation and Setup

PVGIS can be installed relatively simply using `pip`.
However,
it is rather a good idea to [create a virtual environment][] first
and install PVGIS there-in.

### Install Python

Ensure Python is installed on your system.
You can download it from [python.org](https://python.org).

### Virtual environment

#### Create a virtual environment manually

1- Access your terminal (Linux/Mac) or command prompt (Windows).

2- Create a Virtual Environment

    - Navigate to the directory where you want to create your project.

    - Run the following command to create a virtual environment named

      `pvgis-virtual-environment` (although you can name it anything you like):
       
       On Windows: ```python On Windows: python -m venv env ```

       On Linux/Mac: ``` python python3 -m venv env ```

3- Activate the Virtual Environment

    - Before installing packages, activate the virtual environment : 

      On Windows:
      ``` sh
      .\env\Scripts\activate
      ```
      
      On Linux/Mac : 
      ``` bash
      source env/bin/activate
      ```

    - Your command prompt should now show the name of the virtual environment,
    indicating it is active.

    - Now you can install regular Python packages by using `pip`.

4- Deactivating the Virtual Environment

    - To leave from working with PVGIS,
      don't forget to deactivate the virtual environment
      by typing `deactivate` in the terminal or command prompt.

#### Creating a virtual environment automatically using `direnv`

##### Install `direnv`

...

### Install PVGIS

- Install PVGIS using pip

    PVGIS is not yet available in PyPi.
    However,
    `pip` can install Python packages directly from a Git repository.

    - While inside the virtual environment,
    install `pvgis` using pip:

    ``` bash
    pip install git+https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype
    ```

- Verify Installation

    - After installation, 
    you can verify that the package is installed correctly
    by checking its version

    ``` bash
    pvgis-prototype --version
    ```

    or running a basic command, if available.

    ``` bash
    pvgis-prototype --help
    ```

## Basic Commands and Syntax

- Common or essential commands
- Basic syntax rules for commands and parameters

## Data Input and Sources

- Information on how to input data into the software
- Details about supported data formats and sources

## Core Functionalities

- Key features :
- calculation of solar radiation components
  - PV module temperature effect
  - Consideration of system losses

- Common tasks

## Advanced Features

- Using external time series

## Examples

- Step-by-step examples
- Cover typical and advanced use cases

## Troubleshooting

..

## Updates and Versioning

- Information on how to update the software.
- Notes on version history or significant changes in the latest version.
