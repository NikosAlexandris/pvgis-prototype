from pvgisprototype.log import logger
from numpy import nansum, nanmean, ndarray, full
from rich.box import SIMPLE_HEAD
from xarray import DataArray
from pandas import DatetimeIndex, Timestamp, to_datetime
from zoneinfo import ZoneInfo
from rich.console import Console
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


def print_irradiance_table(
    title: str | None = "Power & Irradiance",
    values: ndarray | None = None,
    longitude=None,
    latitude=None,
    elevation=None,
    timestamps: Timestamp | DatetimeIndex = Timestamp.now(),
    timezone: ZoneInfo | None = None,
    data_model_components: dict = dict(),
    rear_side_dictionary: dict = dict(),
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    user_requested_timestamps=None,
    user_requested_timezone=None,
    verbose=1,
    index: bool = False,
    surface_orientation=True,
    surface_tilt=True,
) -> None:
    """ """
    print(f'{title=}')
    print(f'{data_model_components=}')

    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    elevation = round_float_values(elevation, 0)  # rounding_places)

    caption = str()
    if longitude or latitude or elevation:
        caption = "[underline]Location[/underline]  "
    if longitude and latitude:
        caption += f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold]"
    if elevation:
        caption += f", Elevation: [bold]{elevation} m[/bold]"


    # print(f"{dictionary=}")
    # print()
    metadata = data_model_components.pop('Metadata', {})
    # print(f'{metadata=}')
    # print()
    print(f"{data_model_components=}")

    surface_orientation = round_float_values(
        (
            data_model_components.get(SURFACE_ORIENTATION_COLUMN_NAME, None)
            if surface_orientation
            else None
        ),
        rounding_places,
    )
    surface_tilt = round_float_values(
        data_model_components.get(SURFACE_TILT_COLUMN_NAME, None) if surface_tilt else None,
        rounding_places,
    )

    # # Rear-side ?
    # if rear_side_dictionary:
    #     rear_side_surface_orientation = round_float_values(
    #         rear_side_dictionary.get(REAR_SIDE_SURFACE_ORIENTATION_COLUMN_NAME, None), 
    #         rounding_places
    #     )
    #     rear_side_surface_tilt = round_float_values(
    #         rear_side_dictionary.get(REAR_SIDE_SURFACE_TILT_COLUMN_NAME, None), 
    #         rounding_places
    #     )
    # if any(
    #     val is not None 
    #     # for val in [surface_orientation, surface_tilt, rear_side_surface_orientation, rear_side_surface_tilt]
    #     for val in [surface_orientation, surface_tilt]
    # ):
    #     caption += "\n[underline]Position[/underline]  "

    if surface_orientation is not None:
        caption += (
            f"{SURFACE_ORIENTATION_COLUMN_NAME}: [bold]{surface_orientation}[/bold], "
        )

    if surface_tilt is not None:
        caption += f"{SURFACE_TILT_COLUMN_NAME}: [bold]{surface_tilt}[/bold] "

    # # Rear side ?
    # if rear_side_dictionary:
    #     if rear_side_surface_orientation is not None:
    #         caption += (
    #             f", {REAR_SIDE_SURFACE_ORIENTATION_COLUMN_NAME}: [bold]{rear_side_surface_orientation}[/bold], "
    #         )

    #     if rear_side_surface_tilt is not None:
    #         caption += f"{REAR_SIDE_SURFACE_TILT_COLUMN_NAME}: [bold]{rear_side_surface_tilt}[/bold] "

    # Units for both front-side and rear-side too !  Should _be_ the same !
    units = data_model_components.get(ANGLE_UNITS_COLUMN_NAME, UNITLESS)
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
    photovoltaic_module_type = data_model_components.get(PHOTOVOLTAIC_MODULE_TYPE_NAME, None)
    technology_name_and_type = data_model_components.get(TECHNOLOGY_NAME, None)
    photovoltaic_module, mount_type = (
        technology_name_and_type.split(":")
        if technology_name_and_type
        else (None, None)
    )
    peak_power = str(data_model_components.get(PEAK_POWER_COLUMN_NAME, None))
    peak_power += f' [dim]{data_model_components.get(PEAK_POWER_UNIT_NAME, None)}[/dim]'

    algorithms = data_model_components.get(POWER_MODEL_COLUMN_NAME, None)
    irradiance_data_source = data_model_components.get(IRRADIANCE_SOURCE_COLUMN_NAME, None)
    radiation_model = data_model_components.get(RADIATION_MODEL_COLUMN_NAME, None)
    timing_algorithm = data_model_components.get(TIME_ALGORITHM_COLUMN_NAME, None)
    position_algorithm = data_model_components.get(POSITIONING_ALGORITHM_COLUMN_NAME, None)
    azimuth_origin = data_model_components.get(AZIMUTH_ORIGIN_COLUMN_NAME, None)
    if data_model_components.get(SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME) is not None:
        solar_positions_to_horizon = [position.value for position in data_model_components.get(SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME, None)]
    else:
        solar_positions_to_horizon = None
    incidence_algorithm = data_model_components.get(INCIDENCE_ALGORITHM_COLUMN_NAME, None)
    shading_algorithm = data_model_components.get(SHADING_ALGORITHM_COLUMN_NAME, None)
    if data_model_components.get(SHADING_STATES_COLUMN_NAME) is not None:
        shading_states = [state.value for state in data_model_components.get(SHADING_STATES_COLUMN_NAME, None)]
    else:
        shading_states = None

    # Review Me : What does and what does NOT make sense to have separately ?
    if rear_side_dictionary:
        rear_side_peak_power = str(data_model_components.get(PEAK_POWER_COLUMN_NAME, None))
        rear_side_peak_power += f' [dim]{data_model_components.get(PEAK_POWER_UNIT_NAME, None)}[/dim]'
        rear_side_algorithms = data_model_components.get(POWER_MODEL_COLUMN_NAME, None)
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

    solar_incidence_definition = data_model_components.get(INCIDENCE_DEFINITION, None)
    if solar_incidence_definition is not None:
        caption += f"{INCIDENCE_DEFINITION}: [bold yellow]{solar_incidence_definition}[/bold yellow]"

    solar_constant = data_model_components.get(SOLAR_CONSTANT_COLUMN_NAME, None)
    perigee_offset = data_model_components.get(PERIGEE_OFFSET_COLUMN_NAME, None)
    eccentricity_correction_factor = data_model_components.get(
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

    # solar_incidence_algorithm = data_model_components.get(INCIDENCE_ALGORITHM_COLUMN_NAME, None)
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

    caption = caption.rstrip(", ")  # Remove trailing comma + space

    # a Legend for symbols 

    # then : Create a Legend table for the symbols in question
    legend = build_legend_table(
        dictionary=data_model_components,
        caption=caption,
        show_sum=True,
        show_mean=True,
        show_header=False,
        box=None,
    )

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
    rear_side_table = None  # in order to avoid the "unbound error"
    # totals_table = None
    if rear_side_dictionary:
        rear_side_table = Table(
            title=f'Rear-side {title}',
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

    if index:
        table.add_column("Index")
        if rear_side_table:
            rear_side_table.add_column("Index")
            # totals_table.add_column("")

    # base columns

    # Define the time column name based on the timezone or user requests
    time_column_name = TIME_COLUMN_NAME if user_requested_timestamps is None else LOCAL_TIME_COLUMN_NAME
    # table.add_column("Time", footer=SYMBOL_SUMMATION)  # footer = 'Something'
    table.add_column(
        time_column_name,
        no_wrap=True,
        footer=f"{SYMBOL_SUMMATION} / [blue]{SYMBOL_MEAN}[/blue]",
        footer_style="purple",
    )
    if rear_side_table:
        rear_side_table.add_column(
            time_column_name,
            no_wrap=True,
            footer=f"{SYMBOL_SUMMATION} / [blue]{SYMBOL_MEAN}[/blue]",
            footer_style="purple",
        )
        # totals_table.add_column("")

    # remove the 'Title' entry! ---------------------------------------------
    data_model_components.pop("Title", NOT_AVAILABLE)
    if rear_side_dictionary:
        rear_side_dictionary.pop("Title", NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    # add and process additional columns

    for key, value in data_model_components.items():
        if key not in KEYS_TO_EXCLUDE:
            # sum of array values

            if isinstance(value, (float, int)):
                dictionary[key] = full(len(timestamps), value)

            if isinstance(value, str):
                dictionary[key] = full(len(timestamps), str(value))

            # add sum of value/s to the column footer
            if key in KEYS_TO_SUM:
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

            elif key in KEYS_TO_AVERAGE:
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

    # add and process additional columns to rear-side table
    if rear_side_table:
        for key, value in rear_side_dictionary.items():
            if key not in KEYS_TO_EXCLUDE:
                # sum of array values

                if isinstance(value, (float, int)):
                    rear_side_dictionary[key] = full(len(timestamps), value)

                if isinstance(value, str):
                    rear_side_dictionary[key] = full(len(timestamps), str(value))

                # add sum of value/s to the column footer
                if key in REAR_SIDE_KEYS_TO_SUM:
                    if isinstance(value, ndarray) and value.dtype.kind in "if":
                        sum_of_key_value = Text(
                            str(round_float_values(nansum(value), rounding_places)),
                            style="bold purple",
                        )
                        rear_side_table.add_column(
                            header=key,
                            footer=sum_of_key_value,
                            footer_style='white',
                            no_wrap=False,
                        )

                elif key in KEYS_TO_AVERAGE:
                    if (
                            (
                                isinstance(value, ndarray)
                                and value.dtype.kind in "if"
                                )
                            | isinstance(value, float)
                    ):
                        rear_side_table.add_column(
                            header=key,
                            footer=Text(str(nanmean(value))),  # Mean of Key Value
                            footer_style='italic blue',
                            no_wrap=False,
                        )
                else:
                    rear_side_table.add_column(key, no_wrap=False)

    # Zip series and timestamps
    filtered_dictionary = {
        key: value for key, value in data_model_components.items() if key not in KEYS_TO_EXCLUDE
    }
    zipped_series = zip(*filtered_dictionary.values())
    zipped_data = zip(timestamps, zipped_series)

    # Populate table
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

    if rear_side_table:
        # Zip series and timestamps
        filtered_rear_side_dictionary = {
            key: value
            for key, value in rear_side_dictionary.items()
            if key not in KEYS_TO_EXCLUDE
        }
        rear_side_zipped_series = zip(*filtered_rear_side_dictionary.values())
        rear_side_zipped_data = zip(timestamps, rear_side_zipped_series)

        # Populate table
        index_counter = 1
        for timestamp, values in rear_side_zipped_data:
            row = []

            if index:
                row.append(str(index_counter))
                index_counter += 1

            row.append(to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S"))

            for idx, (column_name, value) in enumerate(
                zip(filtered_rear_side_dictionary.keys(), values)
            ):
                # First row of the table is the header
                if idx == 0:  # assuming after 'Time' is the value of main interest
                    # Make first row item bold
                    bold_value = Text(
                        str(round_float_values(value, rounding_places)), style="bold dark_orange",
                    )
                    row.append(bold_value)

                else:
                    if not isinstance(value, None| str) or isinstance(value, float):
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

            rear_side_table.add_row(*row)

    if verbose:
        Console().print(table)
        if rear_side_table:
            Console().print(rear_side_table)

        # Create Panels for both caption and legend
        caption_panel = Panel(
            caption,
            subtitle="[gray]Reference[/gray]",
            subtitle_align="right",
            border_style="dim",
            expand=False
        )
        legend_panel = Panel(
            legend,
            subtitle="[dim]Legend[/dim]",
            subtitle_align="right",
            border_style="dim",
            expand=False,
            padding=(0,1),
            # style="dim",
        )

        # Use Columns to place them side-by-side
        from rich.columns import Columns
        Console().print(Columns([caption_panel, legend_panel]))
