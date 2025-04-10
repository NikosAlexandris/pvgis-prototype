from rich import print
from numpy import isnan, nansum, nanmean, ndarray, full
from rich.console import Console, RenderableType
from rich.text import Text
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.cli.print.irradiance.keys import (
        KEYS_TO_EXCLUDE,
        KEYS_TO_SUM,
        KEYS_TO_AVERAGE,
        )

def add_key_table_columns(
    table,
    dictionary,
    timestamps,
    rounding_places,
    keys_to_sum=KEYS_TO_SUM,
    keys_to_average=KEYS_TO_AVERAGE,
    keys_to_exclude=KEYS_TO_EXCLUDE,
) -> RenderableType:
    """
    Notes
    -----
    Important : the input `dictionary` is expected to be a flat one.

    """
    from devtools import debug
    debug(locals())
    # ------------------------------------------------- Nested dictionary ? ---
    # for section, section_content in dictionary.items():
    #     print(f"{section_content=}")
        # for key, value in section_content.items():
    # -- Nested dictionary ? --------------------------------------------------

    for key, value in dictionary.items():
        print(f"{key=}")
        if key in keys_to_exclude:
            print(f"[red]Excluding[/red] {key=}")
            print()
        if key not in keys_to_exclude:

            # sum of array values

            if isinstance(value, (float, int)):
                dictionary[key] = full(len(timestamps), value)

            if isinstance(value, str):
                dictionary[key] = full(len(timestamps), str(value))

            # add sum of value/s to the column footer

            if key in keys_to_sum:
                print(f"{key=} to [code magenta]sum[/code magenta]")
                if (
                    isinstance(value, ndarray)
                    # and not isnan(value).all()
                    and value.dtype.kind in "if"
                ):
                    print(f"{value=}")
                    sum_of_key_value = Text(
                        str(round_float_values(nansum(value), rounding_places)),
                        style="code purple",
                    )
                    table.add_column(
                        header=key,
                        footer=sum_of_key_value,
                        footer_style="white",
                        no_wrap=False,
                    )

            elif key in keys_to_average:
                print(f"{key=} to [code blue]average[/code blue]")
                if (
                    isinstance(value, ndarray) and value.dtype.kind in "if"
                ) | isinstance(value, float):
                    table.add_column(
                        header=key,
                        footer=Text(str(nanmean(value))),  # Mean of Key Value
                        footer_style="italic blue",
                        no_wrap=False,
                    )
            else:
                print(f"[code][green]Adding[/green][/code] {key=}")
                table.add_column(key, no_wrap=False)

    Console().print(table)
    return table


# def process_nested_dictionary(
#     table: Table,
#     dictionary: dict,
#     timestamps,
#     rounding_places: int,
#     keys_to_sum: set,
#     keys_to_average: set,
#     keys_to_exclude: set,
#     parent_key: str = "",
# ):
#     """
#     Recursively processes a nested dictionary to add columns to the table.
#     """
#     for key, value in dictionary.items():
#         # Construct full key path for nested keys
#         full_key = f"{parent_key}.{key}" if parent_key else key

#         if key in keys_to_exclude:
#             continue  # Skip excluded keys

#         if isinstance(value, dict):
#             # Recursively process nested dictionaries
#             process_nested_dictionary(
#                 table=table,
#                 dictionary=value,
#                 timestamps=timestamps,
#                 rounding_places=rounding_places,
#                 keys_to_sum=keys_to_sum,
#                 keys_to_average=keys_to_average,
#                 keys_to_exclude=keys_to_exclude,
#                 parent_key=full_key,
#             )
#         else:
#             # Process leaf nodes (arrays, scalars, or strings)
#             process_value(
#                 table=table,
#                 key=full_key,
#                 value=value,
#                 timestamps=timestamps,
#                 rounding_places=rounding_places,
#                 keys_to_sum=keys_to_sum,
#                 keys_to_average=keys_to_average,
#             )


# def process_value(
#     table: Table,
#     key: str,
#     value,
#     timestamps,
#     rounding_places: int,
#     keys_to_sum: set,
#     keys_to_average: set,
# ):
#     """
#     Processes a single key-value pair and adds it as a column to the table.
#     """
#     # Convert scalars or strings to arrays for consistency
#     if isinstance(value, (float, int)):
#         value = full(len(timestamps), value)
#     elif isinstance(value, str):
#         value = full(len(timestamps), str(value))

#     footer = None
#     footer_style = None

#     # Determine footer based on whether the key is in keys_to_sum or keys_to_average
#     if key in keys_to_sum:
#         if isinstance(value, ndarray) and value.dtype.kind in "if":
#             footer = Text(
#                 str(round_float_values(nansum(value), rounding_places)),
#                 style="bold purple",
#             )
#             footer_style = "white"
#     elif key in keys_to_average:
#         if isinstance(value, ndarray) and value.dtype.kind in "if":
#             footer = Text(
#                 str(round_float_values(nanmean(value), rounding_places)),
#                 style="italic blue",
#             )
#             footer_style = "blue"

#     # Add the column to the table
#     table.add_column(header=key, footer=footer, footer_style=footer_style, no_wrap=False)


# def add_key_table_columns(
#     table: Table,
#     dictionary: dict,
#     timestamps,
#     rounding_places: int,
#     keys_to_sum: set = KEYS_TO_SUM,
#     keys_to_average: set = KEYS_TO_AVERAGE,
#     keys_to_exclude: set = KEYS_TO_EXCLUDE,
# ) -> RenderableType:
#     """
#     Adds columns to a Rich table based on the keys and values in a nested dictionary.
    
#     This function supports recursive processing of nested dictionaries.
    
#     Args:
#         table (Table): The Rich Table object to which columns will be added.
#         dictionary (dict): The input dictionary containing data.
#         timestamps (DatetimeIndex): The timestamps corresponding to the data.
#         rounding_places (int): Number of decimal places to round numerical values.
#         keys_to_sum (set): Keys for which column footers should show sums.
#         keys_to_average (set): Keys for which column footers should show averages.
#         keys_to_exclude (set): Keys to exclude from processing.

#     Returns:
#         RenderableType: The modified Rich Table object.
#     """
#     from devtools import debug
#     debug(locals())

#     process_nested_dictionary(
#         table=table,
#         dictionary=dictionary,
#         timestamps=timestamps,
#         rounding_places=rounding_places,
#         keys_to_sum=keys_to_sum,
#         keys_to_average=keys_to_average,
#         keys_to_exclude=keys_to_exclude,
#         parent_key="",  # Start with no parent key
#     )

#     Console().print(table)
#     return table
