from xarray.core.utils import K
from pvgisprototype.log import logger
from numpy import nansum, ndarray, full
from rich.box import SIMPLE_HEAD
from xarray import DataArray
from pandas import DatetimeIndex, Timestamp, to_datetime
from zoneinfo import ZoneInfo
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import (
SHADING_STATE_COLUMN_NAME,
SYMBOL_LOSS,
    ANGLE_UNITS_COLUMN_NAME,
    AZIMUTH_ORIGIN_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
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
SYMBOL_SUMMATION,
    TECHNOLOGY_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    TIME_COLUMN_NAME,
    UNITLESS,
)


def print_irradiance_table_2(
    longitude=None,
    latitude=None,
    elevation=None,
    timestamps: Timestamp | DatetimeIndex = Timestamp.now(),
    timezone: ZoneInfo | None = None,
    dictionary: dict = dict(),
    title: str | None = "Irradiance data",
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    user_requested_timestamps=None,
    user_requested_timezone=None,
    verbose=1,
    index: bool = False,
    surface_orientation=True,
    surface_tilt=True,
) -> None:
    """ """
    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    elevation = round_float_values(elevation, 0)  # rounding_places)

    caption = str()
    if longitude or latitude or elevation:
        caption = "[underline]Location[/underline]  "
    if longitude and latitude:
        caption += f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold], "
    if elevation:
        caption += f"Elevation: [bold]{elevation} m[/bold]"

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
    if surface_orientation or surface_tilt:
        caption += "\n[underline]Position[/underline]  "

    if surface_orientation is not None:
        caption += (
            f"{SURFACE_ORIENTATION_COLUMN_NAME}: [bold]{surface_orientation}[/bold], "
        )

    if surface_tilt is not None:
        caption += f"{SURFACE_TILT_COLUMN_NAME}: [bold]{surface_tilt}[/bold] "

    units = dictionary.get(ANGLE_UNITS_COLUMN_NAME, UNITLESS)
    if (
        longitude
        or latitude
        or elevation
        or surface_orientation
        or surface_tilt
        and units is not None
    ):
        caption += f" [[dim]{units}[/dim]]"

    technology_name_and_type = dictionary.get(TECHNOLOGY_NAME, None)
    photovoltaic_module, mount_type = (
        technology_name_and_type.split(":")
        if technology_name_and_type
        else (None, None)
    )
    peak_power = dictionary.get(PEAK_POWER_COLUMN_NAME, None)
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
    
    if photovoltaic_module:
        caption += "\n[underline]Module[/underline]  "
        caption += f"{TECHNOLOGY_NAME}: {photovoltaic_module}, "
        caption += f"Mount type: {mount_type}, "
        caption += f"{PEAK_POWER_COLUMN_NAME}: {peak_power}"

    if algorithms or radiation_model or timing_algorithm or position_algorithm:
        caption += "\n[underline]Algorithms[/underline]  "

    if algorithms:
        caption += f"{POWER_MODEL_COLUMN_NAME}: [bold]{algorithms}[/bold], "

    if irradiance_data_source:
        caption += f"\n{IRRADIANCE_SOURCE_COLUMN_NAME}: [bold]{irradiance_data_source}[/bold], "

    if radiation_model:
        caption += f"{RADIATION_MODEL_COLUMN_NAME}: [bold]{radiation_model}[/bold], "

    if timing_algorithm:
        caption += f"Timing : [bold]{timing_algorithm}[/bold], "

    if timezone == ZoneInfo('UTC'):
        caption += f"[bold]{timezone}[/bold], "
    else:
        caption += f"Local Zone : [bold]{timezone}[/bold], "

    if position_algorithm:
        caption += f"Positioning : [bold]{position_algorithm}[/bold], "

    if azimuth_origin:
        caption += f"Azimuth origin : [bold indigo]{azimuth_origin}[/bold indigo], "

    if solar_positions_to_horizon:
        caption += f"Positions to horizon : [bold]{solar_positions_to_horizon}[/bold], "

    if incidence_algorithm:
        caption += f"Incidence : [bold yellow]{incidence_algorithm}[/bold yellow], "

    if shading_algorithm:
        caption += f"Shading : [bold]{shading_algorithm}[/bold]"

    if shading_states:
        caption += f"Shading states : [bold]{shading_states}[/bold]"

    # solar_incidence_algorithm = dictionary.get(INCIDENCE_ALGORITHM_COLUMN_NAME, None)
    # if solar_incidence_algorithm is not None:
    #     caption += f"{INCIDENCE_ALGORITHM_COLUMN_NAME}: [bold yellow]{solar_incidence_algorithm}[/bold yellow], "

    solar_incidence_definition = dictionary.get(INCIDENCE_DEFINITION, None)
    if solar_incidence_definition is not None:
        caption += f"{INCIDENCE_DEFINITION}: [bold yellow]{solar_incidence_definition}[/bold yellow]"

    solar_constant = dictionary.get(SOLAR_CONSTANT_COLUMN_NAME, None)
    perigee_offset = dictionary.get(PERIGEE_OFFSET_COLUMN_NAME, None)
    eccentricity_correction_factor = dictionary.get(
        ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME, None
    )

    if solar_constant and perigee_offset and eccentricity_correction_factor:
        caption += "\n[underline]Constants[/underline] "
        caption += f"{SOLAR_CONSTANT_COLUMN_NAME} : {solar_constant}, "
        caption += f"{PERIGEE_OFFSET_COLUMN_NAME} : {perigee_offset}, "
        caption += f"{ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME} : {eccentricity_correction_factor}, "

    from pvgisprototype.constants import SYMBOL_DESCRIPTIONS

    # add a caption for symbols found in the input dictionary
    caption += "\n[underline]Legend[/underline] "
    for symbol, description in SYMBOL_DESCRIPTIONS.items():
        if any(symbol in key for key in dictionary.keys()):
            caption += f"[yellow]{symbol}[/yellow] is {description}, "
    caption = caption.rstrip(", ")  # Remove trailing comma + space
    table = Table(
        title=title,
        # caption=caption.rstrip(', '),  # Remove trailing comma + space
        caption_justify="left",
        expand=False,
        padding=(0, 1),
        box=SIMPLE_HEAD,
        show_footer=True,
    )

    if index:
        table.add_column("Index")

    # base columns

    # Define the time column name based on the timezone or user requests
    time_column_name = TIME_COLUMN_NAME if user_requested_timestamps is None else LOCAL_TIME_COLUMN_NAME
    # table.add_column("Time", footer=SYMBOL_SUMMATION)  # footer = 'Something'
    table.add_column(time_column_name)

    # remove the 'Title' entry! ---------------------------------------------
    dictionary.pop("Title", NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    keys_to_exclude = {
        SURFACE_ORIENTATION_COLUMN_NAME,
        SURFACE_TILT_COLUMN_NAME,
        ANGLE_UNITS_COLUMN_NAME,
        TIME_ALGORITHM_COLUMN_NAME,
        POSITIONING_ALGORITHM_COLUMN_NAME,
        SOLAR_POSITIONS_TO_HORIZON_COLUMN_NAME,
        SOLAR_CONSTANT_COLUMN_NAME,
        PERIGEE_OFFSET_COLUMN_NAME,
        ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
        INCIDENCE_ALGORITHM_COLUMN_NAME,
        INCIDENCE_DEFINITION,
        SHADING_ALGORITHM_COLUMN_NAME,
        SHADING_STATES_COLUMN_NAME,
        IRRADIANCE_SOURCE_COLUMN_NAME,
        RADIATION_MODEL_COLUMN_NAME,
        TECHNOLOGY_NAME,
        PEAK_POWER_COLUMN_NAME,
        POWER_MODEL_COLUMN_NAME,
        FINGERPRINT_COLUMN_NAME,
    }

    # add and process additional columns
    for key, value in dictionary.items():
        if key not in keys_to_exclude:
            # sum of array values
            if isinstance(value, ndarray) and value.dtype.kind in "if":
                sum_of_key_value = str(nansum(value))

            if isinstance(value, (float, int)):
                dictionary[key] = full(len(timestamps), value)

            if isinstance(value, str):
                dictionary[key] = full(len(timestamps), str(value))

            # # add sum of values as a new column to the footer
            # if sum_of_key_value:
            #     table.add_column(key, footer=sum_of_key_value)
            # else:
            #     table.add_column(key)
            table.add_column(key)


    # Zip series and timestamps
    filtered_dictionary = {
        key: value for key, value in dictionary.items() if key not in keys_to_exclude
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
                # Make first row items bold
                bold_value = Text(
                    str(round_float_values(value, rounding_places)), style="bold"
                )
                row.append(bold_value)

            else:
                # print(f'Idx : {idx}  |  Column name : {column_name}  | Value = {value}')
                if not isinstance(value, str) or isinstance(value, float):
                    # If values of this column are negative / represent loss
                    if SYMBOL_LOSS in column_name or value < 0:
                        # Make them bold red
                        red_value = Text(
                            str(round_float_values(value, rounding_places)),
                            style="bold red",
                        )
                        row.append(red_value)

                    else:
                        row.append(str(round_float_values(value, rounding_places)))

                else:
                    if value is not None:
                        row.append(value)

        table.add_row(*row)

    if verbose:
        Console().print(table)
        Console().print(Panel(caption, expand=False))


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
