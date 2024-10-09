from typing import List
import numpy as np
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.table import Table
from rich.text import Text

from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import (
    NOT_AVAILABLE,
    ROUNDING_PLACES_DEFAULT,
    SYMBOL_LOSS,
    TITLE_KEY_NAME,
)


def style_value(value, style_if_negative="dim"):
    if value is not None:
        if value < 0:
            return f"[{style_if_negative}]{value}[/]"
        else:
            return str(value)
    return None


def safe_get_value(dictionary, key, index, default=NOT_AVAILABLE):
    """
    Parameters
    ----------
    dictionary: dict
        Input dictionary
    key: str
        key to retrieve from the dictionary
    index: int
        index ... ?

    Returns
    -------
    The value corresponding to the given `key` in the `dictionary` or the
    default value if the key does not exist.

    """
    value = dictionary.get(key, default)
    # if isinstance(value, np.ndarray) and value.size > 1:
    if isinstance(value, (list, np.ndarray)) and len(value) > index:
        return value[index]
    return value


def print_table(headers: List[str], data: List[List[str]]) -> None:
    """Create and print a table with provided headers and data."""
    table = Table(show_header=True, header_style="bold magenta", box=SIMPLE_HEAD)
    for header in headers:
        table.add_column(header)

    for row_data in data:
        table.add_row(*row_data)

    Console().print(table)


def print_quantity_table(
    dictionary: dict = dict(),
    title: str = "Series",
    main_key: str = None,
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    verbose=1,
    index: bool = False,
) -> None:
    table = Table(title=title, box=SIMPLE_HEAD)

    if index:
        table.add_column("Index")

    # remove the 'Title' entry! ---------------------------------------------
    dictionary.pop(TITLE_KEY_NAME, NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    # # base columns
    # if verbose > 0:

    # additional columns based dictionary keys
    for key in dictionary.keys():
        if dictionary[key] is not None:
            table.add_column(key)

    if not main_key:  # consider the 1st key of having the "valid" number of values
        main_key = list(dictionary.keys())[0]

    # Convert single float or int values to arrays of the same length as the "main' key
    for key, value in dictionary.items():
        if isinstance(value, (float, int)):
            dictionary[key] = np.full(len(dictionary[main_key]), value)

        if isinstance(value, str):
            dictionary[key] = np.full(len(dictionary[main_key]), str(value))

    # Zip series
    zipped_series = zip(*dictionary.values())

    # Populate table
    index_counter = 1
    for values in zipped_series:
        row = []

        if index:
            row.append(str(index_counter))
            index_counter += 1

        for idx, (column_name, value) in enumerate(zip(dictionary.keys(), values)):
            if idx == 0:  # assuming after 'Time' is the value of main interest
                bold_value = Text(
                    str(round_float_values(value, rounding_places)), style="bold"
                )
                row.append(bold_value)
            else:
                if not isinstance(value, str):
                    if SYMBOL_LOSS in column_name:
                        red_value = Text(
                            str(round_float_values(value, rounding_places)),
                            style="bold red",
                        )
                        row.append(red_value)
                    else:
                        row.append(str(round_float_values(value, rounding_places)))
                else:
                    row.append(value)
        table.add_row(*row)

    if verbose:
        Console().print(table)


def print_irradiance_table_2(
    longitude=None,
    latitude=None,
    elevation=None,
    timestamps: Timestamp | DatetimeIndex = Timestamp.now(),
    timezone: ZoneInfo | None = None,
    dictionary: dict = dict(),
    title: str = "Irradiance series",
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
    incidence_algorithm = dictionary.get(INCIDENCE_ALGORITHM_COLUMN_NAME, None)

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

    if incidence_algorithm:
        caption += f"Incidence : [bold yellow]{incidence_algorithm}[/bold yellow], "

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
        SOLAR_CONSTANT_COLUMN_NAME,
        PERIGEE_OFFSET_COLUMN_NAME,
        ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
        INCIDENCE_ALGORITHM_COLUMN_NAME,
        INCIDENCE_DEFINITION,
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
            if isinstance(value, np.ndarray) and value.dtype.kind in "if":
                sum_of_key_value = str(np.nansum(value))

            if isinstance(value, (float, int)):
                dictionary[key] = np.full(len(timestamps), value)

            if isinstance(value, str):
                dictionary[key] = np.full(len(timestamps), str(value))

            # add sum of values as a new column to the footer
            if sum_of_key_value:
                table.add_column(key, footer=sum_of_key_value)
            else:
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
                if not isinstance(value, str):
                    # If values of this column are negative / represent loss
                    if SYMBOL_LOSS in column_name:
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
    title: str = "Irradiance series",
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

    # Extract relevant data from the location_time_series
    timestamps = location_time_series.time.values
    center_wavelengths = location_time_series.center_wavelength.values
    irradiance_values = location_time_series.values

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

    table.add_column("Time", footer="Total")  # Timestamp column

    # Add columns for each center wavelength (irradiance wavelength)
    for wavelength in center_wavelengths:
        table.add_column(f"{wavelength:.0f} nm", justify="right")

    # Populate the table with the irradiance data
    for idx, timestamp in enumerate(timestamps):
        row = []

        if index:
            row.append(str(idx + 1))

        # Convert timestamp to string format
        row.append(datetime.utcfromtimestamp(timestamp.tolist() / 1e9).strftime("%Y-%m-%d %H:%M:%S"))

        # Add irradiance values for each center wavelength at this timestamp
        for irradiance in irradiance_values[idx]:
            row.append(f"{round(irradiance, rounding_places):.{rounding_places}f}")

        table.add_row(*row)

    # Prepare a caption with the location information
    caption = str()
    if longitude is not None and latitude is not None:
        caption += f"Location  Longitude ϑ, Latitude ϕ = {longitude}, {latitude}"

    if elevation is not None:
        caption += f", Elevation: {elevation} m"

    caption += "\nLegend: Center Wavelengths (nm)"

    if verbose:
        console = Console()
        console.print(table)
        console.print(Panel(caption, expand=False))


def add_table_row(
    table,
    quantity,
    value,
    unit,
    mean_value,
    mean_value_unit,
    standard_deviation=None,
    percentage=None,
    reference_quantity=None,
    series=np.array([]),
    timestamps: DatetimeIndex = None,
    frequency: str = "YE",
    source: str = None,
    quantity_style=None,
    value_style="cyan",
    unit_style="cyan",
    mean_value_style="cyan",
    mean_value_unit_style="cyan",
    percentage_style="dim",
    reference_quantity_style="white",
    rounding_places=1,
):
    """
    Adds a row to a table with automatic unit handling and optional percentage.

    Parameters
    ----------
    table :
                The table object to which the row will be added.
    quantity :
                The name of the quantity being added.
    value :
                The numerical value associated with the quantity.
    base_unit :
                The base unit of measurement for the value.
    percentage :
                Optional; the percentage change or related metric.
    reference_quantity :
                Optional; the reference quantity for the percentage.
    rounding_places :
                Optional; the number of decimal places to round the value.

    Notes
    -----
    - Round value if rounding_places specified.
    - Convert units from base_unit to a larger unit if value exceeds 1000.
    - Add row to specified table.

    """
    effects = {
        REFLECTIVITY,
        SPECTRAL_EFFECT_NAME,
        TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME,
        SYSTEM_LOSS,
        NET_EFFECT,
    }

    if value is None or np.isnan(value):
        signed_value = "-"  # this _is_ the variable added in a row !
    else:
        if isinstance(value, (float, np.float32, np.float64, int, np.int32, np.int64)):
            styled_value = (
                f"[{value_style}]{value:.{rounding_places}f}"
                if value_style
                else f"{value:.{rounding_places}f}"
            )
            signed_value = (
                f"[{quantity_style}]+{styled_value}"
                if quantity in effects and value > 0
                else styled_value
            )
        else:
            raise TypeError(f"Unexpected type for value: {type(value)}")

    # Need first the unstyled quantity for the `signed_value` :-)
    quantity = f"[{quantity_style}]{quantity}" if quantity_style else quantity

    # Mean value and unit
    mean_value = (
        f"[{mean_value_style}]{mean_value:.{rounding_places}f}"
        if mean_value_style
        else f"{mean_value:.{rounding_places}f}"
    )
    if standard_deviation:
        standard_deviation = (
            f"[{mean_value_style}]{standard_deviation:.{rounding_places}f}"
            if mean_value_style
            else f"{standard_deviation:.{rounding_places}f }"
        )
    else:
        standard_deviation = ""

    # Style the unit
    unit = f"[{unit_style}]{unit}" if unit_style else unit

    # Get the reference quantity
    reference_quantity = (
        f"[{reference_quantity_style}]{reference_quantity}"
        if reference_quantity_style
        else reference_quantity
    )

    # Build the sparkline
    sparkline = (
        convert_series_to_sparkline(series, timestamps, frequency)
        if series.size > 0
        else ""
    )

    # Prepare the basic row data structure
    row = [quantity, signed_value, unit]

    # Add percentage and reference quantity if applicable
    if percentage is not None:
        # percentage = f"[red]{percentage:.{rounding_places}f}" if percentage < 0 else f"[{percentage_style}]{percentage:.{rounding_places}f}"
        percentage = (
            f"[red bold]{percentage:.{rounding_places}f}"
            if percentage < 0
            else f"[green bold]+{percentage:.{rounding_places}f}"
        )
        row.extend([f"{percentage}"])
        if reference_quantity:
            row.extend([reference_quantity])
        else:
            row.extend([""])
    else:
        row.extend(["", ""])
    if sparkline:
        row.extend([sparkline])
    if mean_value:
        if not sparkline:
            row.extend([""])
        row.extend([mean_value, mean_value_unit, (standard_deviation)])
    else:
        row.extend([""])
    if source:
        row.extend([source])

    # table.add_row(
    #     quantity,
    #     value,
    #     unit,
    #     percentage,
    #     reference_quantity,
    #     style=quantity_style
    # )
    table.add_row(*row)


def determine_frequency(timestamps):
    """ """
    # First, get the "frequency" from the timestamps
    time_groupings = {
        "YE": "Yearly",
        "S": "Seasonal",
        "ME": "Monthly",
        "W": "Weekly",
        "D": "Daily",
        "3h": "3-Hourly",
        "h": "Hourly",
        "min": "Minutely",
        "8min": "8-Minutely",
    }
    if timestamps.year.unique().size > 1:
        frequency = "YE"
    elif timestamps.month.unique().size > 1:
        frequency = "ME"
    elif timestamps.to_period().week.unique().size > 1:
        frequency = "W"
    elif timestamps.day.unique().size > 1:
        frequency = "D"
    elif timestamps.hour.unique().size > 1:
        if timestamps.hour.unique().size < 17:  # Explain Me !
            frequency = "h"
        else:
            frequency = "3h"
    elif timestamps.minute.unique().size < 17:  # Explain Me !
        frequency = "min"
    else:
        frequency = "8min"  # by 8 characters for a sparkline if timestamps > 64 min
    frequency_label = time_groupings[frequency]

    return frequency, frequency_label


def build_performance_table(
    frequency_label,
    quantity_style,
    value_style,
    unit_style,
    mean_value_unit_style,
    percentage_style,
    reference_quantity_style,
):
    """
    Setup the main performance table with appropriate columns.
    """
    table = Table(
        # title="Photovoltaic Performance",
        # caption="Detailed view of changes in photovoltaic performance.",
        show_header=True,
        header_style="bold magenta",
        # show_footer=True,
        # row_styles=["none", "dim"],
        box=SIMPLE_HEAD,
        highlight=True,
    )
    table.add_column(
        "Quantity",
        justify="left",
        style=quantity_style,  # style="magenta",
        no_wrap=True,
    )
    table.add_column(
        "Total",  # f"{SYMBOL_SUMMATION}",
        justify="right",
        style=value_style,  # style="cyan",
    )
    table.add_column(
        "Unit",
        justify="left",
        style=unit_style,  # style="magenta",
    )
    table.add_column(
        "%",
        justify="right",
        style=percentage_style,  # style="dim",
    )
    table.add_column(
        "of",
        justify="left",
        style="dim",  # style=reference_quantity_style)
    )
    table.add_column(f"{frequency_label} Sums", style="dim", justify="center")
    # table.add_column(f"{frequency_label} Mean", justify="right", style="white dim")#style=value_style)
    table.add_column("Mean", justify="right", style="white dim")  # style=value_style)
    table.add_column(
        "Unit",  # for Mean values
        justify="left",
        style=mean_value_unit_style,
    )

    table.add_column(
        "Variability", justify="right", style="dim"
    )  # New column for standard deviation
    table.add_column("Source", style="dim", justify="left")

    return table


def build_position_table() -> Table:
    """ """
    position_table = Table(
        box=None,
        show_header=True,
        header_style="bold dim",
        show_edge=False,
        pad_edge=False,
    )
    position_table.add_column(
        f"{LATITUDE_NAME}", justify="center", style="bold", no_wrap=True
    )
    position_table.add_column(
        f"{LONGITUDE_NAME}", justify="center", style="bold", no_wrap=True
    )
    position_table.add_column(
        f"{ELEVATION_NAME}", justify="center", style="bold", no_wrap=True
    )
    position_table.add_column(
        f"{ORIENTATION_NAME}", justify="center", style="bold", no_wrap=True
    )
    position_table.add_column(
        f"{TILT_NAME}", justify="center", style="bold", no_wrap=True
    )

    return position_table


def build_position_panel(position_table) -> Panel:
    """ """
    return Panel(
        position_table,
        subtitle="Solar Surface",
        subtitle_align="right",
        # box=None,
        safe_box=True,
        style="",
        expand=False,
        padding=(0, 3),
    )


def build_time_table():
    """ """
    time_table = Table(
        box=None,
        show_header=True,
        header_style=None,
        show_edge=False,
        pad_edge=False,
    )
    time_table.add_column("Start", justify="left", style="bold")
    time_table.add_column("Every", justify="left", style="dim bold")
    time_table.add_column("End", justify="left", style="dim bold")

    return time_table


def build_photovoltaic_module_table():
    """ """
    photovoltaic_module_table = Table(
        box=None,
        show_header=True,
        header_style=None,
        show_edge=False,
        pad_edge=False,
    )
    photovoltaic_module_table.add_column("Tech", justify="right", style="bold")
    photovoltaic_module_table.add_column("Peak-Power", justify="center", style="bold")
    photovoltaic_module_table.add_column("Mount Type", justify="left", style="bold")

    return photovoltaic_module_table


def build_photovoltaic_module_panel(photovoltaic_module_table):
    """ """
    photovoltaic_module_panel = Panel(
        photovoltaic_module_table,
        subtitle="PV Module",
        subtitle_align="right",
        safe_box=True,
        expand=True,
        padding=(0, 2),
    )

    return photovoltaic_module_panel


def build_pvgis_version_panel(
    prefix_text="PVGIS v6",
    justify_text="center",
    style_text="white dim",
    border_style="dim",
    padding=(0, 2),
) -> Panel:
    """ """
    from pvgisprototype._version import __version__

    pvgis_version = Text(
        f"{prefix_text} ({__version__})",
        justify=justify_text,
        style=style_text,
    )
    return Panel(
        pvgis_version,
        # subtitle="[reverse]Fingerprint[/reverse]",
        # subtitle_align="right",
        border_style=border_style,
        # style="dim",
        expand=False,
        padding=padding,
    )


def build_fingerprint_panel(fingerprint):
    """ """
    fingerprint = Text(
        f"{fingerprint}",
        justify="center",
        style="yellow bold",
    )
    return Panel(
        fingerprint,
        subtitle="[reverse]Fingerprint[/reverse]",
        subtitle_align="right",
        border_style="dim",
        style="dim",
        expand=False,
        padding=(0, 2),
    )


# from rich.console import group
# @group()
def build_version_and_fingerprint_panels(fingerprint=None):
    """Dynamically build panels based on available data."""
    # Always yield version panel
    panels = [build_pvgis_version_panel()]
    # Yield fingerprint panel only if fingerprint is provided
    if fingerprint:
        panels.append(build_fingerprint_panel(fingerprint))

    return panels


def build_version_and_fingerprint_columns(fingerprint) -> Columns:
    """Combine software version and fingerprint panels into a single Columns
    object."""
    version_and_fingeprint_panels = build_version_and_fingerprint_panels(
        fingerprint=fingerprint
    )
    return Columns(version_and_fingeprint_panels, expand=False, padding=2)


def print_change_percentages_panel(
    longitude=None,
    latitude=None,
    elevation=None,
    surface_orientation: bool = True,
    surface_tilt: bool = True,
    timestamps: DatetimeIndex | datetime = [datetime.now()],
    dictionary: dict = dict(),
    title: str = "Analysis of Performance",
    rounding_places: int = 1,  # ROUNDING_PLACES_DEFAULT,
    verbose=1,
    index: bool = False,
    fingerprint: bool = False,
    quantity_style="magenta",
    value_style="cyan",
    unit_style="cyan",
    percentage_style="dim",
    reference_quantity_style="white",
):
    """Print a formatted table of photovoltaic performance metrics using the
    Rich library.

    Analyse the photovoltaic performance in terms of :

    - In-plane (or inclined) irradiance without reflectivity loss
    - Reflectivity effect as a function of the solar incidence angle
    - Irradiance after reflectivity effect
    - Spectral effect due to variation in the natural sunlight spectrum and its
      difference to standardised artificial laborary light spectrum
    - Effective irradiance = Inclined irradiance + Reflectivity effect + Spectral effect
    - Loss as a function of the PV module temperature and low irradiance effects
    - Conversion of the effective irradiance to photovoltaic power
    - Total net effect = Reflectivity, Spectral effect, Temperature & Low
      irradiance

    Finally, report the photovoltaic power output after system loss and
    degradation with age

    """
    frequency, frequency_label = determine_frequency(timestamps=timestamps)
    add_empty_row_before = {
        # IN_PLANE_IRRADIANCE,
        REFLECTIVITY,
        # IRRADIANCE_AFTER_REFLECTIVITY,
        SPECTRAL_EFFECT_NAME,
        # EFFECTIVE_IRRADIANCE_NAME,
        TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME,
        # PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
        SYSTEM_LOSS,
        # PHOTOVOLTAIC_POWER_LONG_NAME,
        # f"[white dim]{POWER_NAME}",
        f"[green bold]{ENERGY_NAME_WITH_SYMBOL}",
        # f"[white dim]{NET_EFFECT}",
    }
    performance_table = build_performance_table(
        frequency_label=frequency_label,
        quantity_style=quantity_style,
        value_style=value_style,
        unit_style=unit_style,
        mean_value_unit_style="white dim",
        percentage_style=percentage_style,
        reference_quantity_style=reference_quantity_style,
    )
    results = report_photovoltaic_performance(
        dictionary=dictionary,
        timestamps=timestamps,
        frequency=frequency,
        verbose=verbose,
    )

    # Add rows based on the dictionary keys and corresponding values
    for label, (
        (value, value_style),
        (unit, unit_style),
        (mean_value, mean_value_style),
        (mean_value_unit, mean_value_unit_style),
        standard_deviation,
        percentage,
        style,
        reference_quantity,
        input_series,
        source,
    ) in results.items():
        if label in add_empty_row_before:
            performance_table.add_row()
        add_table_row(
            table=performance_table,
            quantity=label,
            value=value,
            unit=unit,
            mean_value=mean_value,
            mean_value_unit=mean_value_unit,
            standard_deviation=standard_deviation,
            percentage=percentage,
            reference_quantity=reference_quantity,
            series=input_series,
            timestamps=timestamps,
            frequency=frequency,
            source=source,
            quantity_style=quantity_style,
            value_style=value_style,
            unit_style=unit_style,
            mean_value_style=mean_value_style,
            mean_value_unit_style=mean_value_unit_style,
            percentage_style=percentage_style,
            reference_quantity_style=reference_quantity_style,
            rounding_places=rounding_places,
        )

    # Positioning
    position_table = build_position_table()
    positioning_rounding_places = 3
    latitude = round_float_values(
        latitude, positioning_rounding_places
    )  # rounding_places)
    # position_table.add_row(f"{LATITUDE_NAME}", f"[bold]{latitude}[/bold]")
    longitude = round_float_values(
        longitude, positioning_rounding_places
    )  # rounding_places)
    surface_orientation = (
        dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME, None)
        if surface_orientation
        else None
    )
    surface_orientation = round_float_values(
        surface_orientation, positioning_rounding_places
    )
    surface_tilt = (
        dictionary.get(SURFACE_TILT_COLUMN_NAME, None) if surface_tilt else None
    )
    surface_tilt = round_float_values(surface_tilt, positioning_rounding_places)
    position_table.add_row(
        f"{latitude}",
        f"{longitude}",
        f"{elevation}",
        f"{surface_orientation}",
        f"{surface_tilt}",
    )
    # position_table.add_row("Time :", f"{timestamp[0]}")
    # position_table.add_row("Time zone :", f"{timezone}")

    longest_label_length = max(len(key) for key in dictionary.keys())
    surface_position_keys = {
        SURFACE_ORIENTATION_NAME,
        SURFACE_TILT_NAME,
        ANGLE_UNIT_NAME,
        # INCIDENCE_DEFINITION,
        # UNIT_NAME,
    }
    for key, value in dictionary.items():
        if key in surface_position_keys:
            padded_key = f"{key} :".ljust(longest_label_length + 3, " ")
            if key == INCIDENCE_DEFINITION:
                value = f"[yellow]{value}[/yellow]"
            position_table.add_row(padded_key, str(value))

    position_panel = build_position_panel(position_table)

    time_table = build_time_table()
    time_table.add_row(
        str(timestamps.strftime("%Y-%m-%d %H:%M").values[0]),
        str(timestamps.freqstr),
        str(timestamps.strftime("%Y-%m-%d %H:%M").values[-1]),
    )
    time_panel = Panel(
        time_table,
        # title="Time",
        # subtitle="Time",
        # subtitle_align="right",
        safe_box=True,
        expand=False,
        padding=(0, 2),
    )
    photovoltaic_module, mount_type = dictionary.get(TECHNOLOGY_NAME, None).split(":")
    peak_power = dictionary.get(PEAK_POWER_COLUMN_NAME, None)
    photovoltaic_module_table = build_photovoltaic_module_table()
    photovoltaic_module_table.add_row(
        photovoltaic_module,
        f"[green]{peak_power}[/green]",
        mount_type,
    )

    photovoltaic_module_panel = build_photovoltaic_module_panel(
        photovoltaic_module_table
    )
    # panels = [position_panel, time_panel, photovoltaic_module_panel]

    # columns = Columns(
    #         panels,
    #         # expand=True,
    #         # equal=True,
    #         padding=2,
    #         )

    performance_panel = Panel(
        performance_table,
        title=title,
        expand=False,
        # style="on black",
    )
    photovoltaic_module_columns = Columns(
        [position_panel, time_panel, photovoltaic_module_panel],
        # expand=True,
        # equal=True,
        padding=3,
    )

    fingerprint = dictionary.get(FINGERPRINT_COLUMN_NAME, None)
    columns = build_version_and_fingerprint_columns(fingerprint)

    from rich.console import Group

    group = Group(
        performance_panel,
        photovoltaic_module_columns,
        columns,
    )
    # panel_group = Group(
    #         Panel(
    #             performance_table,
    #             title='Analysis of Performance',
    #             expand=False,
    #             # style="on black",
    #             ),
    #         columns,
    #     # Panel(table),
    #     # Panel(position_panel),
    # #     Panel("World", style="on red"),
    #         fit=False
    # )

    # Console().print(panel_group)
    # Console().print(Panel(performance_table))
    Console().print(group)


def print_finger_hash(dictionary: dict):
    """ """
    fingerprint = dictionary.get(FINGERPRINT_COLUMN_NAME, None)
    if fingerprint is not None:
        fingerprint_panel = Panel.fit(
            Text(f"{fingerprint}", justify="center", style="bold yellow"),
            subtitle="[reverse]Fingerprint[/reverse]",
            subtitle_align="right",
            border_style="dim",
            style="dim",
        )
        Console().print(fingerprint_panel)


def print_solar_position_series_in_columns(
    longitude,
    latitude,
    timestamps,
    timezone,
    table,
    rounding_places=ROUNDING_PLACES_DEFAULT,
    index: bool = False,
):
    panels = []

    # Iterating through each timestamp
    for i, timestamp in enumerate(timestamps):
        table_panel = Table(title=f"Time: {timestamp}", box=ROUNDED)
        table_panel.add_column("Parameter", justify="right")
        table_panel.add_column("Value", justify="left")

        # Optionally add an index column
        if index:
            table_panel.add_column("Index", style="dim")
            table_panel.add_row("Index", str(i))

        # Add longitude, latitude, and other non-time-varying parameters
        table_panel.add_row("Longitude", str(longitude))
        table_panel.add_row("Latitude", str(latitude))

        # For each parameter of interest, aggregate across models for this timestamp
        parameters = [
            "Declination",
            "Hour Angle",
            "Zenith",
            "Altitude",
            "Azimuth",
            "Incidence",
        ]
        for param in parameters:
            # Assume `table` is a dictionary of models, each containing a list of values for each parameter
            values = [
                round_float_values(model_result[param][i], rounding_places)
                for model_name, model_result in table.items()
                if param in model_result
            ]
            value_str = ", ".join(map(str, values))  # Combine values from all models
            table_panel.add_row(param, value_str)

        panel = Panel(table_panel, expand=True)
        panels.append(panel)

    Console().print(Columns(panels))


from typing import Dict

def print_spectral_factor(
    timestamps,
    spectral_factor_container: Dict,
    spectral_factor_model: List,
    photovoltaic_module_type: List,
    rounding_places: int = 3,
    include_statistics: bool = False,
    title: str = "Spectral Factor",
    verbose: int = 1,
    index: bool = False,
    show_footer: bool = True,
) -> None:
    """Print the spectral factor series in a formatted table.

    Parameters
    ----------
    - timestamps :
        The time series timestamps.
    - spectral_factor :
        Dictionary containing spectral factor data for different models and module types.
    - spectral_factor_model :
        List of spectral factor models.
    - photovoltaic_module_type :
        List of photovoltaic module types.
    - rounding_places :
        Number of decimal places for rounding.
    - include_statistics :
        Whether to include mean, median, etc., in the output.
    - verbose : int
        Verbosity level.
    - index : bool
        Whether to show an index column.
    """
    # Initialize the table with title and formatting options
    table = Table(
        title=title,
        caption_justify="left",
        expand=False,
        padding=(0, 1),
        box=SIMPLE_HEAD,
        show_footer=show_footer,
    )
    if index:
        table.add_column("Index")

    table.add_column("Time", footer="μ" if show_footer else None)
        # Initialize dictionary to store the means for each module type
    means = {}

    # Calculate mean values for the footer
    if show_footer:
        for module_type in photovoltaic_module_type:
            model = spectral_factor_model[0]  # Assuming only one model for simplicity
            spectral_factor_series = spectral_factor_container.get(model).get(module_type).get(SPECTRAL_FACTOR_COLUMN_NAME)
            mean_value = np.nanmean(spectral_factor_series)
            means[module_type.value] = f"{mean_value:.{rounding_places}f}"

    # Add columns for each photovoltaic module type with optional footer
    for module_type in photovoltaic_module_type:
        footer_text = means.get(module_type.value, "") if show_footer else None
        table.add_column(f"{module_type.value}", justify="right", footer=footer_text)

    # Aggregate data for each timestamp
    for _index, timestamp in enumerate(timestamps):
        row = []

        if index:
            row.append(str(_index + 1))  # count from 1

        row.append(str(timestamp))

        for module_type in photovoltaic_module_type:
            model = spectral_factor_model[0]  # Assuming only one model for simplicity
            sm_value = spectral_factor_container.get(model).get(module_type).get(SPECTRAL_FACTOR_COLUMN_NAME)[_index]
            row.append(f"{round(sm_value, rounding_places):.{rounding_places}f}")
        table.add_row(*row)

    print()

    # Print the table if verbose is enabled
    if verbose:
        console = Console()
        console.print(table)

        # Optionally, display additional information in a panel
        if verbose > 1:
            extra_info = "Spectral Mismatch calculated for different photovoltaic module types using specified models."
            console.print(Panel(extra_info, expand=False))
>>>>>>> 49-gitlab-update-tmy-4-Merge-Request
