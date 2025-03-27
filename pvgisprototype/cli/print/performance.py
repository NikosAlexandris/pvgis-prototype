from numpy import ndarray
import numpy
from numpy.typing import NDArray
from rich.box import SIMPLE_HEAD, MINIMAL
from rich.columns import Columns
from rich.console import Console, JustifyMethod
from rich.panel import Panel
from rich.table import Table
from pandas import DatetimeIndex
from zoneinfo import ZoneInfo

from rich.text import Text
from pvgisprototype.api.performance.report import report_photovoltaic_performance
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.cli.print.time import build_time_table, build_time_panel
from pvgisprototype.cli.print.helpers import determine_frequency, infer_frequency_from_timestamps
from pvgisprototype.constants import (
    ANGLE_UNIT_NAME,
    AZIMUTH_ORIGIN_COLUMN_NAME,
    AZIMUTH_ORIGIN_NAME,
    ELEVATION_NAME,
    ENERGY_NAME_WITH_SYMBOL,
    FINGERPRINT_COLUMN_NAME,
    HORIZON_HEIGHT_COLUMN_NAME,
    HORIZON_HEIGHT_NAME,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_NAME,
    INCIDENCE_DEFINITION,
    LATITUDE_NAME,
    LONGITUDE_NAME,
    NET_EFFECT,
    ORIENTATION_NAME,
    PEAK_POWER_COLUMN_NAME,
    PEAK_POWER_UNIT_NAME,
    POSITIONING_ALGORITHM_COLUMN_NAME,
    POSITIONING_ALGORITHM_NAME,
    REFLECTIVITY,
    SHADING_ALGORITHM_COLUMN_NAME,
    SHADING_ALGORITHM_NAME,
    SPECTRAL_EFFECT_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_NAME,
    SYSTEM_LOSS,
    TECHNOLOGY_NAME,
    TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME,
    TILT_NAME,
    TIMING_ALGORITHM_COLUMN_NAME,
    TIMING_ALGORITHM_NAME,
)
from pvgisprototype.cli.print.sparklines import convert_series_to_sparkline


def build_performance_table(
    frequency_label: str,
    quantity_style: str,
    value_style: str,
    unit_style: str,
    mean_value_unit_style: str,
    percentage_style: str,
    # reference_quantity_style,
) -> Table:
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


def build_algorithmic_metadata_table() -> Table:
    """ """
    algorithmic_metadata_table = Table(
        box=None,
        show_header=True,
        header_style="bold dim",
        show_edge=False,
        pad_edge=False,
    )
    algorithmic_metadata_table.add_column(
        f"{TIMING_ALGORITHM_NAME}", justify="center", style="bold", no_wrap=True
    )
    algorithmic_metadata_table.add_column(
        f"{POSITIONING_ALGORITHM_NAME}", justify="center", style="bold", no_wrap=True
    )
    # algorithmic_metadata_table.add_column(
    #     # f"{INCIDENCE_ALGORITHM_NAME}", justify="center", style="bold", no_wrap=True
    #     f"{INCIDENCE_NAME}", justify="center", style="bold", no_wrap=True
    # )
    algorithmic_metadata_table.add_column(
        f"{AZIMUTH_ORIGIN_NAME}", justify="center", style="bold", no_wrap=True
    )
    algorithmic_metadata_table.add_column(
        f"{INCIDENCE_DEFINITION}", justify="center", style="bold", no_wrap=True
    )
    algorithmic_metadata_table.add_column(
        f"{SHADING_ALGORITHM_NAME}", justify="center", style="bold", no_wrap=True
    )
    # algorithmic_metadata_table.add_column(
    #     f"{HORIZON_HEIGHT_NAME}", justify="center", style="bold", no_wrap=True
    # )

    return algorithmic_metadata_table


def build_horizon_profile_table() -> Table:
    """ """
    horizon_profile_table = Table(
        box=None,
        show_header=True,
        header_style="bold dim",
        show_edge=False,
        pad_edge=False,
    )
    horizon_profile_table.add_column(
        f"{HORIZON_HEIGHT_NAME}",
        # justify="right",
        style="bold", no_wrap=True
    )

    return horizon_profile_table



def build_position_panel(position_table, width) -> Panel:
    """ """
    return Panel(
        position_table,
        # title="Positioning",  # Add title to provide context without being too bold
        # title_align="left",  # Align the title to the left
        subtitle="Solar Surface",
        subtitle_align="right",
        # box=None,
        safe_box=True,
        style="",
        border_style="dim",  # Soften the panel with a dim border style
        # expand=False,
        # expand=True,
        padding=(0, 2),
        # width=width,
    )


def build_algorithmic_metadata_panel(algorithmic_metadata_table) -> Panel:
    """ """
    return Panel(
        algorithmic_metadata_table,
        subtitle="Algorithmic metadata",
        subtitle_align="right",
        # box=None,
        safe_box=True,
        style="",
        expand=False,
        padding=(0, 3),
    )


def build_horizon_profile_panel(horizon_profile_table) -> Panel:
    """ """
    return Panel(
        horizon_profile_table,
        # subtitle="Horizon height profile",
        # subtitle_align="right",
        box=MINIMAL,
        # safe_box=True,
        # border_style=None,
        # style="",
        expand=False,
        padding=0,
        width=60,
    )


def build_photovoltaic_module_table() -> Table:
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


def build_photovoltaic_module_panel(photovoltaic_module_table) -> Panel:
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
    prefix_text: str = "PVGIS v6",
    justify_text: JustifyMethod = "center",
    style_text: str = "white dim",
    border_style: str = "dim",
    padding: tuple = (0, 2),
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


def build_fingerprint_panel(fingerprint) -> Panel:
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
def build_version_and_fingerprint_panels(
    version:bool = False,
    fingerprint: bool = False,
) -> list[Panel]:
    """Dynamically build panels based on available data."""
    # Always yield version panel
    panels = []
    if version:
        panels.append(build_pvgis_version_panel())
    # Yield fingerprint panel only if fingerprint is provided
    if fingerprint:
        panels.append(build_fingerprint_panel(fingerprint))

    return panels


def build_version_and_fingerprint_columns(
    version:bool = False,
    fingerprint: bool = False,
) -> Columns:
    """Combine software version and fingerprint panels into a single Columns
    object."""
    version_and_fingeprint_panels = build_version_and_fingerprint_panels(
        version=version,
        fingerprint=fingerprint,
    )

    return Columns(version_and_fingeprint_panels, expand=False, padding=2)


def add_table_row(
    table,
    quantity,
    value,
    unit,
    mean_value,
    mean_value_unit,
    standard_deviation = None,
    percentage = None,
    reference_quantity = None,
    series: ndarray = numpy.array([]),
    timestamps: DatetimeIndex | None = None,
    frequency: str = "YE",
    source: str | None = None,
    quantity_style = None,
    value_style: str = "cyan",
    unit_style: str = "cyan",
    mean_value_style: str = "cyan",
    mean_value_unit_style: str = "cyan",
    percentage_style: str = "dim",
    reference_quantity_style: str = "white",
    rounding_places: int = 1,
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

    if value is None or numpy.isnan(value):
        signed_value = "-"  # this _is_ the variable added in a row !
    else:
        if isinstance(value, (float, numpy.float32, numpy.float64, int, numpy.int32, numpy.int64)):
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


def print_change_percentages_panel(
    longitude=None,
    latitude=None,
    elevation=None,
    surface_orientation: float | bool = True,
    surface_tilt: float | bool = True,
    horizon_profile: NDArray | None = None,
    timestamps: DatetimeIndex | None = None,
    timezone: ZoneInfo | None = None,
    dictionary: dict = dict(),
    title: str = "Analysis of Performance",
    rounding_places: int = 1,  # ROUNDING_PLACES_DEFAULT,
    verbose=1,
    index: bool = False,
    version: bool = False,
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
        # reference_quantity_style=reference_quantity_style,
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
    # surface_orientation: float | None = (
    #     dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME, None)
    #     if surface_orientation
    #     else None
    # )
    # surface_orientation: float = round_float_values(
    #     surface_orientation, positioning_rounding_places
    # )
    surface_orientation: float | None = dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME)
    if surface_orientation is not None:
        surface_orientation = round_float_values(
            surface_orientation, positioning_rounding_places
        )

    # Get and round surface_tilt if it's not None
    # surface_tilt: float | None = (
    #     dictionary.get(SURFACE_TILT_COLUMN_NAME, None) if surface_tilt else None
    # )
    # surface_tilt: float = round_float_values(surface_tilt, positioning_rounding_places)
    surface_tilt: float | None = dictionary.get(SURFACE_TILT_COLUMN_NAME)
    if surface_tilt is not None:
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

    position_panel = build_position_panel(position_table, width=performance_table.width)

    # Algorithmic metadata panel
    algorithmic_metadata_panel = None
    timing_algorithm: str | None = dictionary.get(TIMING_ALGORITHM_COLUMN_NAME)
    position_algorithm: str | None = dictionary.get(POSITIONING_ALGORITHM_COLUMN_NAME)
    incidence_algorithm: str | None = dictionary.get(INCIDENCE_ALGORITHM_COLUMN_NAME)
    azimuth_origin: str | None = dictionary.get(AZIMUTH_ORIGIN_COLUMN_NAME)
    incidence_angle_definition: str | None = dictionary.get(INCIDENCE_DEFINITION)
    shading_algorithm: str | None = dictionary.get(SHADING_ALGORITHM_COLUMN_NAME)
    if all(
        [
            timing_algorithm,
            position_algorithm,
            incidence_algorithm,
            azimuth_origin,
            incidence_angle_definition,
        ]
    ):
        algorithmic_metadata_table = build_algorithmic_metadata_table()
        algorithmic_metadata_table.add_row(
            f"{timing_algorithm}",
            f"{position_algorithm}",
            # f"{incidence_algorithm}",
            f"{azimuth_origin}",
            f"{incidence_angle_definition}, {incidence_algorithm}",
            f"{shading_algorithm}",
        )
        algorithmic_metadata_panel = build_algorithmic_metadata_panel(
            algorithmic_metadata_table
        )
    
    if horizon_profile is not None:
        azimuthal_directions_radians = numpy.linspace(0, 2 * numpy.pi, horizon_profile.size)
        from pvgisprototype.cli.plot.uniplot import Plot
        horizon_profile_polar_plot = Plot(
            xs=numpy.degrees(azimuthal_directions_radians),
            ys=horizon_profile,
            lines=True,
            width=45,
            height=3,
            x_gridlines=[],
            y_gridlines=[],
            character_set="braille",
            # color=[colors[1]],
            # legend_labels=[labels[1]],
            color=["blue"],  # Add color
            legend_labels=["Horizon Profile"],  # Add legend
            interactive=False,
        )
        # horizon_profile_table = build_horizon_profile_table()
        # horizon_profile_table.add_row(
            # # f"{horizon_profile_polar_plot}",
            # horizon_profile_polar_plot
        # )
        horizon_profile_panel = build_horizon_profile_panel(
            # horizon_profile_table
            horizon_profile_polar_plot
        )
    else:
        horizon_profile_panel = None

    if algorithmic_metadata_panel and horizon_profile_panel is not None:
        metadata_columns = Columns([
            algorithmic_metadata_panel,
            horizon_profile_panel,
            ])
    else:
        metadata_columns = None

    time_table = build_time_table()
    frequency, frequency_label = infer_frequency_from_timestamps(timestamps)
    time_table.add_row(
        str(timestamps.strftime("%Y-%m-%d %H:%M").values[0]),
        str(frequency) if frequency and frequency != 'Single' else '-',
        str(timestamps.strftime("%Y-%m-%d %H:%M").values[-1]),
        str(timezone),
    )
    time_panel = build_time_panel(time_table)

    photovoltaic_module, mount_type = dictionary.get(TECHNOLOGY_NAME, None).split(":")
    peak_power = dictionary.get(PEAK_POWER_COLUMN_NAME, None)
    peak_power_unit = dictionary.get(PEAK_POWER_UNIT_NAME, None)
    photovoltaic_module_table = build_photovoltaic_module_table()
    photovoltaic_module_table.add_row(
        photovoltaic_module,
        f"[green]{peak_power}[/green] {peak_power_unit}",
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
        [
            panel
            for panel in [
                position_panel,
                time_panel,
                photovoltaic_module_panel,
            ]
            if panel
        ],
        # expand=True,
        # equal=True,
        padding=3,
    )

    fingerprint = dictionary.get(FINGERPRINT_COLUMN_NAME, None)
    version_and_fingerprint_columns = build_version_and_fingerprint_columns(
        version=version,
        fingerprint=fingerprint,
    )

    from rich.console import Group

    group_panels = [
        panel
        for panel in [
            photovoltaic_module_columns,
            performance_panel,
            # algorithmic_metadata_panel,
            metadata_columns,
            # horizon_profile_panel,
            version_and_fingerprint_columns,
        ]
        if panel is not None
    ]
    group = Group(*group_panels)

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
