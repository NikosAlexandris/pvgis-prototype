from numpy import isnan, ndarray
from pandas import DatetimeIndex, Timestamp
from zoneinfo import ZoneInfo
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.cli.print.irradiance.caption import build_caption_for_irradiance_data
from pvgisprototype.cli.print.irradiance.table import build_irradiance_table, populate_irradiance_table, print_table_and_legend
from pvgisprototype.cli.print.legend import build_legend_table
from pvgisprototype.constants import (
    LOCAL_TIME_COLUMN_NAME,
    ROUNDING_PLACES_DEFAULT,
    SYMBOL_MEAN,
    SYMBOL_SUMMATION,
    TIME_COLUMN_NAME,
)
from pvgisprototype.cli.print.irradiance.keys import (
        KEYS_TO_EXCLUDE,
        KEYS_TO_SUM,
        REAR_SIDE_KEYS_TO_SUM,
        KEYS_TO_AVERAGE,
        )


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
                    elif issubclass(value.dtype.type, (float, int)) and isnan(value).all():
                        continue 

                    else:
                        flat_dictionary[key] = value
                else:
                    flat_dictionary[key] = value

    flatten(dictionary)
    return flat_dictionary


def print_irradiance_table_2(
    title: str | None = "Power & Irradiance",
    irradiance_data: dict = dict(),
    rear_side_irradiance_data: dict = dict(),
    longitude=None,
    latitude=None,
    elevation=None,
    surface_orientation=True,
    surface_tilt=True,
    timestamps: Timestamp | DatetimeIndex = Timestamp.now(),
    user_requested_timestamps=None,
    timezone: ZoneInfo | None = None,
    user_requested_timezone=None,
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    index: bool = False,
    verbose=1,
) -> None:
    """ """
    irradiance_data = flatten_dictionary(irradiance_data)
    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    elevation = round_float_values(elevation, 0)  # rounding_places)

    # Caption

    caption = build_caption_for_irradiance_data(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timezone=timezone,
        dictionary=irradiance_data,
        rear_side_irradiance_data=rear_side_irradiance_data,
        rounding_places=rounding_places,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
    )

    # then : create a Legend table for the symbols in question
    
    legend = build_legend_table(
        dictionary=irradiance_data,
        caption=caption,
        show_sum=True,
        show_mean=True,
        show_header=False,
        box=None,
    )

    # Define the time column name based on the timezone or user requests

    time_column_name = TIME_COLUMN_NAME if user_requested_timestamps is None else LOCAL_TIME_COLUMN_NAME

    # Build the irradiance table/s

    table = build_irradiance_table(
        title=title,
        index=index,
        dictionary=irradiance_data,
        timestamps=timestamps,
        rounding_places=rounding_places,
        time_column_name=time_column_name,
        time_column_footer=f"{SYMBOL_SUMMATION} / [blue]{SYMBOL_MEAN}[/blue]",  # Abusing this "cell" as a "Row Name" 
        time_column_footer_style = "purple",  # to make it somehow distinct from the Column !
        keys_to_sum = KEYS_TO_SUM,
        keys_to_average = KEYS_TO_AVERAGE,
        keys_to_exclude = KEYS_TO_EXCLUDE,
    )

    if rear_side_irradiance_data:
        rear_side_table = build_irradiance_table(
            title=f'Rear-side {title}',
            index=index,
            dictionary=irradiance_data,
            timestamps=timestamps,
            rounding_places=rounding_places,
            time_column_name=time_column_name,
            time_column_footer=f"{SYMBOL_SUMMATION} / [blue]{SYMBOL_MEAN}[/blue]",
            time_column_footer_style = "purple",
            keys_to_sum = REAR_SIDE_KEYS_TO_SUM,
            keys_to_average = KEYS_TO_AVERAGE,
            keys_to_exclude = KEYS_TO_EXCLUDE,
        )
        # totals_table = Table(
        #     title=f'Total {title}',
        #     # caption=caption.rstrip(', '),  # Remove trailing comma + space
        #     caption_justify="left",
        #     expand=False,
        #     padding=(0, 1),
        #     box=SIMPLE_HEAD,
        #     header_style="bold gray50",
        #     show_footer=True,
        #     footer_style='white',
        #     row_styles=["none", "dim"],
        #     highlight=True,
        # )
        # if index:
            # totals_table.add_column("")
        # totals_table.add_column("")
    else:
        rear_side_table = None  # in order to avoid the "unbound error"
        # totals_table = None

    # Populate table/s

    table = populate_irradiance_table(
                        table=table,
                        dictionary=irradiance_data,
                        timestamps=timestamps,
                        index=index,
                        rounding_places=rounding_places,
                    )

    if rear_side_table:
        rear_side_table = populate_irradiance_table(
                            table=rear_side_table,
                            dictionary=rear_side_irradiance_data,
                            timestamps=timestamps,
                            index=index,
                            rounding_places=rounding_places,
                        )

    # Print if requested via at least 1x `-v`

    if verbose:
        print_table_and_legend(
            caption=caption,
            table=table,
            rear_side_table=rear_side_table,
            legend=legend,
        )
