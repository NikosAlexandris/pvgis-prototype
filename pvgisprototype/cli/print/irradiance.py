from pvgisprototype.log import logger
from numpy import nansum, nanmean, ndarray, full
from rich.box import SIMPLE_HEAD
from xarray import DataArray
from pandas import DatetimeIndex, Timestamp, to_datetime
from zoneinfo import ZoneInfo
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.cli.print.legend import build_legend_table
from pvgisprototype.constants import (
    EFFICIENCY_COLUMN_NAME,
    PEAK_POWER_UNIT_NAME,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    REAR_SIDE_EFFICIENCY_COLUMN_NAME,
    REAR_SIDE_SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME,
    REAR_SIDE_SPECTRAL_FACTOR_COLUMN_NAME,
    REFLECTIVITY_FACTOR_COLUMN_NAME,
    SPECTRAL_EFFECT_COLUMN_NAME,
    SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME,
    SPECTRAL_FACTOR_COLUMN_NAME,
    SUN_HORIZON_POSITIONS_NAME,
    SYMBOL_LOSS,
    ANGLE_UNITS_COLUMN_NAME,
    AZIMUTH_ORIGIN_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    EFFECTIVE_GLOBAL_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME,
    GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_DEFINITION,
    IRRADIANCE_SOURCE_COLUMN_NAME,
    LATITUDE_COLUMN_NAME,
    LOCAL_TIME_COLUMN_NAME,
    LONGITUDE_COLUMN_NAME,
    NOT_AVAILABLE,
    PEAK_POWER_COLUMN_NAME,
    PERIGEE_OFFSET_COLUMN_NAME,
    PHOTOVOLTAIC_MODULE_TYPE_NAME,
    POSITIONING_ALGORITHM_COLUMN_NAME,
    POWER_MODEL_COLUMN_NAME,
    RADIATION_MODEL_COLUMN_NAME,
    ROUNDING_PLACES_DEFAULT,
    SHADING_ALGORITHM_COLUMN_NAME,
    SHADING_STATES_COLUMN_NAME,
    SOLAR_CONSTANT_COLUMN_NAME,
    SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_TILT_COLUMN_NAME,
    SYMBOL_LOSS,
    SYMBOL_LOSS_NAME,
    SYMBOL_MEAN,
    SYMBOL_MEAN_NAME,
    SYMBOL_POWER_NAME,
    SYMBOL_SUMMATION,
    SYMBOL_SUMMATION_NAME,
    SYSTEM_EFFICIENCY_COLUMN_NAME,
    TECHNOLOGY_NAME,
    TEMPERATURE_COLUMN_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    TIME_COLUMN_NAME,
    UNIT_NAME,
    UNITLESS,
    WIND_SPEED_COLUMN_NAME,
)
from pvgisprototype.constants import (
    REAR_SIDE_SURFACE_ORIENTATION_COLUMN_NAME,
    REAR_SIDE_SURFACE_TILT_COLUMN_NAME,
    REAR_SIDE_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    REAR_SIDE_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    REAR_SIDE_EFFECTIVE_GLOBAL_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_SPECTRAL_EFFECT_COLUMN_NAME,
    REAR_SIDE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_DIRECT_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_DIFFUSE_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
)
KEYS_TO_EXCLUDE = {
    UNIT_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    REAR_SIDE_SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_TILT_COLUMN_NAME,
    REAR_SIDE_SURFACE_TILT_COLUMN_NAME,
    ANGLE_UNITS_COLUMN_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    POSITIONING_ALGORITHM_COLUMN_NAME,
    SOLAR_CONSTANT_COLUMN_NAME,
    PERIGEE_OFFSET_COLUMN_NAME,
    PHOTOVOLTAIC_MODULE_TYPE_NAME,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    AZIMUTH_ORIGIN_COLUMN_NAME,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_DEFINITION,
    SUN_HORIZON_POSITIONS_NAME,
    SHADING_ALGORITHM_COLUMN_NAME,
    SHADING_STATES_COLUMN_NAME,
    IRRADIANCE_SOURCE_COLUMN_NAME,
    RADIATION_MODEL_COLUMN_NAME,
    TECHNOLOGY_NAME,
    PEAK_POWER_COLUMN_NAME,
    PEAK_POWER_UNIT_NAME,
    POWER_MODEL_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
}
KEYS_TO_SUM = {
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    EFFECTIVE_GLOBAL_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME,
    SPECTRAL_EFFECT_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
}
REAR_SIDE_KEYS_TO_SUM = {
    REAR_SIDE_PHOTOVOLTAIC_POWER_COLUMN_NAME,
    REAR_SIDE_PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    REAR_SIDE_EFFECTIVE_GLOBAL_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_SPECTRAL_EFFECT_COLUMN_NAME,
    REAR_SIDE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_DIRECT_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_DIFFUSE_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    REAR_SIDE_GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REAR_SIDE_REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
}
KEYS_TO_AVERAGE = {
    EFFICIENCY_COLUMN_NAME,
    REAR_SIDE_EFFICIENCY_COLUMN_NAME,
    SYSTEM_EFFICIENCY_COLUMN_NAME,
    SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME,
    REAR_SIDE_SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME,
    SPECTRAL_FACTOR_COLUMN_NAME,
    REAR_SIDE_SPECTRAL_FACTOR_COLUMN_NAME,
    REFLECTIVITY_FACTOR_COLUMN_NAME,
    REAR_SIDE_REFLECTIVITY_COLUMN_NAME,
    TEMPERATURE_COLUMN_NAME,
    WIND_SPEED_COLUMN_NAME,
}


def build_caption_for_irradiance_data(
    longitude=None,
    latitude=None,
    elevation=None,
    timezone: ZoneInfo | None = None,
    dictionary: dict = dict(),
    rear_side_dictionary: dict = dict(),
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    surface_orientation=True,
    surface_tilt=True,
):
    """
    """
    caption = str()
    if longitude or latitude or elevation:
        caption = "[underline]Location[/underline]  "
    if longitude and latitude:
        caption += f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold]"
    if elevation:
        caption += f", Elevation: [bold]{elevation} m[/bold]"

    surface_orientation = round_float_values(
        (
            dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME, None)
            if surface_orientation
            else None
        ),
        rounding_places,
    )
    surface_tilt = round_float_values(
        dictionary.get(SURFACE_TILT_COLUMN_NAME, None) if surface_tilt else None,
        rounding_places,
    )

    if any(
        val is not None 
        # for val in [surface_orientation, surface_tilt, rear_side_surface_orientation, rear_side_surface_tilt]
        for val in [surface_orientation, surface_tilt]
    ):
        caption += "\n[underline]Position[/underline]  "

    if surface_orientation is not None:
        caption += (
            f"{SURFACE_ORIENTATION_COLUMN_NAME}: [bold]{surface_orientation}[/bold], "
        )

    if surface_tilt is not None:
        caption += f"{SURFACE_TILT_COLUMN_NAME}: [bold]{surface_tilt}[/bold] "

    # Rear-side ?
    if rear_side_dictionary:

        rear_side_surface_orientation = round_float_values(
            rear_side_dictionary.get(REAR_SIDE_SURFACE_ORIENTATION_COLUMN_NAME, None), 
            rounding_places
        )
        if rear_side_surface_orientation is not None:
            caption += (
                f", {REAR_SIDE_SURFACE_ORIENTATION_COLUMN_NAME}: [bold]{rear_side_surface_orientation}[/bold], "
            )
        
        rear_side_surface_tilt = round_float_values(
            rear_side_dictionary.get(REAR_SIDE_SURFACE_TILT_COLUMN_NAME, None), 
            rounding_places
        )
        if rear_side_surface_tilt is not None:
            caption += f"{REAR_SIDE_SURFACE_TILT_COLUMN_NAME}: [bold]{rear_side_surface_tilt}[/bold] "

    # Units for both front-side and rear-side too !  Should _be_ the same !
    units = dictionary.get(ANGLE_UNITS_COLUMN_NAME, UNITLESS)
    if (
        longitude
        or latitude
        or elevation
        or surface_orientation
        # or rear_side_surface_orientation
        or surface_tilt
        # or rear_side_surface_tilt
        and units is not None
    ):
        caption = f"[underline]Angular units[/underline] [dim]{units}[/dim]\n" + caption

    # Mainly about : Mono- or Bi-Facial ?
    # Maybe do the following :
    # If NOT rear_side_dictionary.get(PHOTOVOLTAIC_MODULE_TYPE_NAME)
    #     Then use the one from the dictionary which should be Monofacial
    # Else :
    #    Use the rear_side_dictionary which should be defined as Bifacial !
    photovoltaic_module_type = dictionary.get(PHOTOVOLTAIC_MODULE_TYPE_NAME, None)
    technology_name_and_type = dictionary.get(TECHNOLOGY_NAME, None)
    photovoltaic_module, mount_type = (
        technology_name_and_type.split(":")
        if technology_name_and_type
        else (None, None)
    )
    peak_power = str(dictionary.get(PEAK_POWER_COLUMN_NAME, None))
    peak_power += f' [dim]{dictionary.get(PEAK_POWER_UNIT_NAME, None)}[/dim]'

    algorithms = dictionary.get(POWER_MODEL_COLUMN_NAME, None)
    irradiance_data_source = dictionary.get(IRRADIANCE_SOURCE_COLUMN_NAME, None)
    radiation_model = dictionary.get(RADIATION_MODEL_COLUMN_NAME, None)
    timing_algorithm = dictionary.get(TIME_ALGORITHM_COLUMN_NAME, None)
    position_algorithm = dictionary.get(POSITIONING_ALGORITHM_COLUMN_NAME, None)
    azimuth_origin = dictionary.get(AZIMUTH_ORIGIN_COLUMN_NAME, None)
    if dictionary.get(SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME) is not None:
        solar_positions_to_horizon = [position.value for position in dictionary.get(SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME, None)]
    else:
        solar_positions_to_horizon = None
    incidence_algorithm = dictionary.get(INCIDENCE_ALGORITHM_COLUMN_NAME, None)
    shading_algorithm = dictionary.get(SHADING_ALGORITHM_COLUMN_NAME, None)

    if dictionary.get(SHADING_STATES_COLUMN_NAME) is not None:
        shading_states = [state.value for state in dictionary.get(SHADING_STATES_COLUMN_NAME, None)]
    else:
        shading_states = None

    # Review Me : What does and what does NOT make sense to have separately ?
    if rear_side_dictionary:
        rear_side_peak_power = str(dictionary.get(PEAK_POWER_COLUMN_NAME, None))
        rear_side_peak_power += f' [dim]{dictionary.get(PEAK_POWER_UNIT_NAME, None)}[/dim]'
        rear_side_algorithms = dictionary.get(POWER_MODEL_COLUMN_NAME, None)
    # ------------------------------------------------------------------------
    
    # Photovoltaic Module

    if photovoltaic_module:
        caption += "\n[underline]Module[/underline]  "
        caption += f"Type: [bold]{photovoltaic_module_type.name}[/bold], "
        caption += f"{TECHNOLOGY_NAME}: [bold]{photovoltaic_module}[/bold], "
        caption += f"Mount: [bold]{mount_type}[/bold], "
        caption += f"{PEAK_POWER_COLUMN_NAME}: [bold]{peak_power}[/bold]"

    # Fundamental Definitions

    if surface_orientation or surface_tilt:
        caption += "\n[underline]Definitions[/underline]  "

    if azimuth_origin:
        caption += f"Azimuth origin : [bold blue]{azimuth_origin}[/bold blue], "

    if timezone == ZoneInfo('UTC'):
        caption += f"[bold]{timezone}[/bold], "
    else:
        caption += f"Local Zone : [bold]{timezone}[/bold], "

    solar_incidence_definition = dictionary.get(INCIDENCE_DEFINITION, None)
    if solar_incidence_definition is not None:
        caption += f"{INCIDENCE_DEFINITION}: [bold yellow]{solar_incidence_definition}[/bold yellow]"

    solar_constant = dictionary.get(SOLAR_CONSTANT_COLUMN_NAME, None)
    perigee_offset = dictionary.get(PERIGEE_OFFSET_COLUMN_NAME, None)
    eccentricity_correction_factor = dictionary.get(
        ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME, None
    )

    if solar_positions_to_horizon:
        caption += f"Positions to horizon : [bold]{solar_positions_to_horizon}[/bold], "

    # Algorithms

    if algorithms or radiation_model or timing_algorithm or position_algorithm:
        caption += "\n[underline]Algorithms[/underline]  "

    if algorithms:
        caption += f"{POWER_MODEL_COLUMN_NAME}: [bold]{algorithms}[/bold], "

    if radiation_model:
        caption += f"{RADIATION_MODEL_COLUMN_NAME}: [bold]{radiation_model}[/bold], "

    if timing_algorithm:
        caption += f"Timing : [bold]{timing_algorithm}[/bold], "

    if position_algorithm:
        caption += f"Positioning : [bold]{position_algorithm}[/bold], "

    if incidence_algorithm:
        caption += f"Incidence : [bold yellow]{incidence_algorithm}[/bold yellow], "

    if shading_algorithm:
        caption += f"Shading : [bold]{shading_algorithm}[/bold], "
    # if rear_side_shading_algorithm:
    #     caption += f"Rear-side Shading : [bold]{rear_side_shading_algorithm}[/bold]"


    # if shading_states:
    #     caption += f"Shading states : [bold]{shading_states}[/bold]"
    # if rear_side_shading_states:
    #     caption += f"Rear-side Shading states : [bold]{rear_side_shading_states}[/bold]"

    # solar_incidence_algorithm = dictionary.get(INCIDENCE_ALGORITHM_COLUMN_NAME, None)
    # if solar_incidence_algorithm is not None:
    #     caption += f"{INCIDENCE_ALGORITHM_COLUMN_NAME}: [bold yellow]{solar_incidence_algorithm}[/bold yellow], "

    if solar_constant and perigee_offset and eccentricity_correction_factor:
        caption += "\n[underline]Constants[/underline] "
        caption += f"{SOLAR_CONSTANT_COLUMN_NAME} : {solar_constant}, "
        caption += f"{PERIGEE_OFFSET_COLUMN_NAME} : {perigee_offset}, "
        caption += f"{ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME} : {eccentricity_correction_factor}, "

    # Sources ?

    if irradiance_data_source:
        caption += f"\n{IRRADIANCE_SOURCE_COLUMN_NAME}: [bold]{irradiance_data_source}[/bold], "

    return caption.rstrip(", ")  # Remove trailing comma + space


def add_key_table_columns(
    table,
    dictionary,
    timestamps,
    rounding_places,
    keys_to_sum = KEYS_TO_SUM,
    keys_to_average = KEYS_TO_AVERAGE,
    keys_to_exclude = KEYS_TO_EXCLUDE,
) -> RenderableType:
    """
    """
    for key, value in dictionary.items():
        if key not in keys_to_exclude:
            # sum of array values

            if isinstance(value, (float, int)):
                dictionary[key] = full(len(timestamps), value)

            if isinstance(value, str):
                dictionary[key] = full(len(timestamps), str(value))

            # add sum of value/s to the column footer
            if key in keys_to_sum:
                if isinstance(value, ndarray) and value.dtype.kind in "if":
                    sum_of_key_value = Text(
                        str(round_float_values(nansum(value), rounding_places)),
                        style="bold purple",
                    )
                    table.add_column(
                        header=key,
                        footer=sum_of_key_value,
                        footer_style='white',
                        no_wrap=False,
                    )

            elif key in keys_to_average:
                if (
                        (
                            isinstance(value, ndarray)
                            and value.dtype.kind in "if"
                            )
                        | isinstance(value, float)
                ):
                    table.add_column(
                        header=key,
                        footer=Text(str(nanmean(value))),  # Mean of Key Value
                        footer_style='italic blue',
                        no_wrap=False,
                    )
            else:
                table.add_column(key, no_wrap=False)

    return table


def build_irradiance_table(
    title: str | None,
    index: bool,
    dictionary,
    timestamps,
    rounding_places,
    time_column_name: RenderableType = "Time",
    time_column_footer: RenderableType = SYMBOL_SUMMATION,
    time_column_footer_style: str = "purple",
    keys_to_sum = KEYS_TO_SUM,
    keys_to_average = KEYS_TO_AVERAGE,
    keys_to_exclude = KEYS_TO_EXCLUDE,
) -> RenderableType:
    """
    """
    table = Table(
        title=title,
        # caption=caption.rstrip(', '),  # Remove trailing comma + space
        caption_justify="left",
        expand=False,
        padding=(0, 1),
        box=SIMPLE_HEAD,
        header_style="bold gray50",
        show_footer=True,
        footer_style='white',
        row_styles=["none", "dim"],
        highlight=True,
    )

    # base columns

    if index:
        table.add_column("Index")

    table.add_column(
        time_column_name,
        no_wrap=True,
        footer=time_column_footer,
        footer_style=time_column_footer_style,
    )

    # remove the 'Title' entry! ---------------------------------------------
    dictionary.pop("Title", NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    # add and process additional columns

    table = add_key_table_columns(
                        table=table,
                        dictionary=dictionary,
                        timestamps=timestamps,
                        rounding_places=rounding_places,
                        keys_to_sum=keys_to_sum,
                        keys_to_average=keys_to_average,
                        keys_to_exclude=keys_to_exclude,
                    )

    return table


def populate_irradiance_table(
    table,
    dictionary,
    timestamps,
    index,
    rounding_places,
) -> RenderableType:
    """
    """
    # Zip series and timestamps
    filtered_dictionary = {
        key: value for key, value in dictionary.items() if key not in KEYS_TO_EXCLUDE
    }
    zipped_series = zip(*filtered_dictionary.values())
    zipped_data = zip(timestamps, zipped_series)

    index_counter = 1
    for timestamp, values in zipped_data:
        row = []

        if index:
            row.append(str(index_counter))
            index_counter += 1

        row.append(to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S"))

        for idx, (column_name, value) in enumerate(
            zip(filtered_dictionary.keys(), values)
        ):
            # First row of the table is the header
            if idx == 0:  # assuming after 'Time' is the value of main interest
                # Make first row item bold
                bold_value = Text(
                    str(round_float_values(value, rounding_places)), style="bold dark_orange",
                )
                row.append(bold_value)

            else:
                if not isinstance(value, str) or isinstance(value, float):
                    # If values of this column are negative / represent loss
                    if f" {SYMBOL_LOSS}" in column_name or value < 0:  # Avoid matching any `-`
                        # Make them bold red
                        red_value = Text(
                            str(round_float_values(value, rounding_places)),
                            style="bold red",
                        )
                        row.append(red_value)

                    else:
                        row.append(str(round_float_values(value, rounding_places)))

                else:
                    from pvgisprototype.api.position.models import SunHorizonPositionModel
                    if value == SunHorizonPositionModel.above.value:
                        yellow_value = Text(
                            str(round_float_values(value, rounding_places)),
                            style="bold yellow",
                        )
                        row.append(yellow_value)
                    elif value == SunHorizonPositionModel.low_angle.value:
                        orange_value = Text(
                            str(round_float_values(value, rounding_places)),
                            style="dark_orange",
                        )
                        row.append(orange_value)
                    elif value == SunHorizonPositionModel.below.value:
                        red_value = Text(
                            str(round_float_values(value, rounding_places)),
                            style="red",
                        )
                        row.append(red_value)
                    else:  # value is not None:
                        row.append(value)

        table.add_row(*row)

    return table


def print_table_and_legend(
    caption: RenderableType,
    table: RenderableType,
    rear_side_table: RenderableType | None,
    legend: RenderableType,
    caption_subtitle: str = 'Reference',
    legend_subtitle: str = 'Legend',
) -> None:
    """
    """
    Console().print(table)
    if rear_side_table:
        Console().print(rear_side_table)

    # Create Panels for both caption and legend
    caption_panel = Panel(
        caption,
        subtitle=f"[gray]{caption_subtitle}[/gray]",
        subtitle_align="right",
        border_style="dim",
        expand=False
    )
    legend_panel = Panel(
        legend,
        subtitle=f"[dim]{legend_subtitle}[/dim]",
        subtitle_align="right",
        border_style="dim",
        expand=False,
        padding=(0,1),
        # style="dim",
    )

    # Use Columns to place them side-by-side
    from rich.columns import Columns
    Console().print(Columns([caption_panel, legend_panel]))


def print_irradiance_table_2(
    longitude=None,
    latitude=None,
    elevation=None,
    timestamps: Timestamp | DatetimeIndex = Timestamp.now(),
    timezone: ZoneInfo | None = None,
    dictionary: dict = dict(),
    rear_side_dictionary: dict = dict(),
    title: str | None = "Power & Irradiance",
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    user_requested_timestamps=None,
    user_requested_timezone=None,
    verbose=1,
    index: bool = False,
    surface_orientation=True,
    surface_tilt=True,
) -> None:
    """ """
    from devtools import debug
    debug(locals())

    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    elevation = round_float_values(elevation, 0)  # rounding_places)

    # Caption

    caption = build_caption_for_irradiance_data(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timezone=timezone,
        dictionary=dictionary,
        rear_side_dictionary=rear_side_dictionary,
        rounding_places=rounding_places,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
    )

    # then : create a Legend table for the symbols in question
    
    legend = build_legend_table(
        dictionary=dictionary,
        caption=caption,
        show_sum=True,
        show_mean=True,
        show_header=False,
        box=None,
    )

    # Define the time column name based on the timezone or user requests

    time_column_name = TIME_COLUMN_NAME if user_requested_timestamps is None else LOCAL_TIME_COLUMN_NAME

    table = build_irradiance_table(
        title=title,
        index=index,
        dictionary=dictionary,
        timestamps=timestamps,
        rounding_places=rounding_places,
        time_column_name=time_column_name,
        time_column_footer=f"{SYMBOL_SUMMATION} / [blue]{SYMBOL_MEAN}[/blue]",
        time_column_footer_style = "purple",
        keys_to_sum = KEYS_TO_SUM,
        keys_to_average = KEYS_TO_AVERAGE,
        keys_to_exclude = KEYS_TO_EXCLUDE,
    )

    if rear_side_dictionary:
        rear_side_table = build_irradiance_table(
            title=f'Rear-side {title}',
            index=index,
            dictionary=dictionary,
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

    # Populate table

    table = populate_irradiance_table(
                        table=table,
                        dictionary=dictionary,
                        timestamps=timestamps,
                        index=index,
                        rounding_places=rounding_places,
                    )

    if rear_side_table:
        rear_side_table = populate_irradiance_table(
                            table=rear_side_table,
                            dictionary=rear_side_dictionary,
                            timestamps=timestamps,
                            index=index,
                            rounding_places=rounding_places,
                        )

    if verbose:
        print_table_and_legend(
            caption=caption,
            table=table,
            rear_side_table=rear_side_table,
            legend=legend,
        )


def print_irradiance_xarray(
    location_time_series: DataArray,
    longitude=None,
    latitude=None,
    elevation=None,
    coordinate: str = None,
    title: str | None = "Irradiance data",
    rounding_places: int = 3,
    verbose: int = 1,
    index: bool = False,
) -> None:
    """
    Print the irradiance time series in a formatted table with each center wavelength as a column.

    Parameters
    ----------
    location_time_series : xr.DataArray
        The time series data with dimensions (time, center_wavelength).
    longitude : float, optional
        The longitude of the location.
    latitude : float, optional
        The latitude of the location.
    elevation : float, optional
        The elevation of the location.
    title : str, optional
        The title of the table.
    rounding_places : int, optional
        The number of decimal places to round to.
    verbose : int, optional
        Verbosity level.
    index : bool, optional
        Whether to show an index column.
    """
    console = Console()
    # Extract relevant data from the location_time_series

    # Prepare the table
    table = Table(
        title=title,
        caption_justify="left",
        expand=False,
        padding=(0, 1),
        box=SIMPLE_HEAD,
        show_footer=True,
    )

    if index:
        table.add_column("Index")

    if 'time' in location_time_series.dims:
        table.add_column("Time", footer=f"{SYMBOL_SUMMATION}")

    # Add columns for each center wavelength (irradiance wavelength)
    if 'center_wavelength' in location_time_series.coords:
        center_wavelengths = location_time_series.coords['center_wavelength'].values
        if center_wavelengths.size > 0:
            for wavelength in center_wavelengths:
                table.add_column(f"{wavelength:.0f} nm", justify="right")
        else:
            logger.warning("No center_wavelengths found in the dataset.")
    else:
        logger.warning("No 'center_wavelength' coordinate found in the dataset.")

    # Populate the table with the irradiance data

    # case of scalar data
    if 'time' not in location_time_series.dims:
        row = []
        if index:
            row.append("1")  # Single row for scalar data

        # Handle the presence of a coordinate (like center_wavelength)
        # if coordinate ... ?
        if 'center_wavelength' in location_time_series.coords:
            for irradiance_value in location_time_series.values:
                row.append(f"{round(irradiance_value, rounding_places):.{rounding_places}f}")
        else:
            row.append(f"{round(location_time_series.item(), rounding_places):.{rounding_places}f}")

        table.add_row(*row)


    else:
        irradiance_values = location_time_series.values
        for idx, timestamp in enumerate(location_time_series.time.values):
            row = []

            if index:
                row.append(str(idx + 1))

            # Convert timestamp to string format
            try:
                row.append(to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                logger.error(f"Invalid timestamp at index {idx}: {e}")
                row.append("Invalid timestamp")

            if 'center_wavelength' in location_time_series.coords:
                # add data variable values for each "coordinate" value at this timestamp
                # i.e. : irradiance values for each "center_wavelength" at this timestamp
                for irradiance_value in irradiance_values[idx]:
                    row.append(f"{round(irradiance_value, rounding_places):.{rounding_places}f}")
            else:
                #  a scalar, i.e. no Xarray "coordinate"
                row.append(f"{round(irradiance_values[idx], rounding_places):.{rounding_places}f}")

            table.add_row(*row)

    # Prepare a caption with the location information
    caption = str()
    if longitude is not None and latitude is not None:
        caption += f"Location  Longitude ϑ, Latitude ϕ = {longitude}, {latitude}"

    if elevation is not None:
        caption += f", Elevation: {elevation} m"

    caption += "\nLegend: Center Wavelengths (nm)"

    if verbose:
        console.print(table)
        console.print(Panel(caption, expand=False))
