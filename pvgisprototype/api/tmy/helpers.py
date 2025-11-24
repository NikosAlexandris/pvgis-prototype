#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import matplotlib.pyplot as plt
from pvgisprototype.log import logger
import warnings
from typing import Any
from xarray import Dataset


def retrieve_nested_value(
    dictionary: dict, 
    key: str,
    default: Any = None,
) -> Any:
    """
    Recursively search for a key in a nested dictionary structure.
    
    This function performs a depth-first search through nested dictionaries,
    OrderedDicts, and similar mappings to find the first occurrence of the
    specified key.
    
    Parameters
    ----------
    dictionary : dict
        The nested dictionary structure to search
    key : str
        The key to search for
    default : Any, optional
        Default value to return if key not found (default: None)
        
    Returns
    -------
    Any
        The value associated with the key, or default if not found
        
    Examples
    --------
    >>> data = {'a': {'b': {'c': 42}}}
    >>> retrieve_nested_value(data, 'c')
    42
    
    >>> retrieve_nested_value(data, 'missing', default='Not found')
    'Not found'
    
    >>> # Works with OrderedDict from build_output()
    >>> tmy_value = retrieve_nested_value(output, 'TMY')

    """
    if isinstance(dictionary, dict):
        # Direct key match
        if key in dictionary:
            logger.debug(f"Found key '{key}' at current level")
            return dictionary[key]

        # Recursively search each value
        for _, value in dictionary.items():
            result = retrieve_nested_value(value, key, default=None)
            if result is not None:
                logger.debug(f"Found key '{key}' in nested structure")
                return result

    logger.debug(f"Key '{key}' not found in structure")

    return default


def set_matplotlib_backend(verbose: bool = False):
    """Configure matplotlib fonts to support Unicode characters."""
    # logger.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
    # if verbose:
    #     warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")


def get_data_variable_from_dataset(dataset: Dataset) -> str | None:
    """Auto-select if exactly one variable exists."""
    data_vars = list(dataset.data_vars)

    if not data_vars:
        raise ValueError(f"No data variables found in dataset !")

    if len(data_vars) == 1:
        logger.info(
            f"Auto-detected single data variable: {data_vars[0]}",
            alt=f"[yellow]Auto-detected single data variable :[/yellow] {data_vars[0]}"
        )
        return data_vars[0]

    # Multiple variables - warn and require explicit choice
    logger.warning(
        f"⚠️  AMBIGUOUS: Dataset has {len(data_vars)} variables: {data_vars}\n"
        + f"Please specify: --variable '<variable_name>'"
    )

    return None  # Force user to choose
