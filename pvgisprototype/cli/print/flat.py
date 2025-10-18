from numpy import isnan, ndarray


def flatten_dictionary(dictionary):
    """
    Flatten a nested dictionary

    Parameters
    ----------
    dictionary: dict
        The nested dictionary to flatten

    Returns
    -------
    A flattened dictionary excluding the specified keys

    """
    flat_dictionary = {}

    def flatten(input_dictionary):
        for key, value in input_dictionary.items():

            if isinstance(value, dict):
                flatten(value)

            else:
                # Discard empty arrays
                if isinstance(value, ndarray):
                    if value.size == 0:
                        continue

                    # Discard arrays that are all NaN
                    elif (
                        issubclass(value.dtype.type, (float, int))
                        and isnan(value).all()
                    ):
                        continue

                    else:
                        flat_dictionary[key] = value
                else:
                    flat_dictionary[key] = value

    flatten(dictionary)
    return flat_dictionary
