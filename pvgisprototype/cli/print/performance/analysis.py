import numpy
from numpy.typing import NDArray
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from pandas import DatetimeIndex
from zoneinfo import ZoneInfo
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype import PhotovoltaicPower
from pvgisprototype.cli.print.irradiance.data import flatten_dictionary
from pvgisprototype.api.performance.report import report_photovoltaic_performance
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.cli.print.performance.horizon import build_horizon_profile_panel, generate_horizon_profile_polar_plot
from pvgisprototype.cli.print.performance.metadata import build_algorithmic_metadata_panel, build_algorithmic_metadata_table, populate_algorithmic_metadata_table
from pvgisprototype.cli.print.performance.photovoltaic_module import build_photovoltaic_module_panel, build_photovoltaic_module_table, populate_photovoltaic_module_table
from pvgisprototype.cli.print.performance.position import build_position_panel, build_position_table, populate_position_table
from pvgisprototype.cli.print.performance.table import add_table_row, build_performance_table
from pvgisprototype.cli.print.time import build_time_table, build_time_panel, populate_time_table
from pvgisprototype.cli.print.helpers import determine_frequency, infer_frequency_from_timestamps
from pvgisprototype.cli.print.version_and_fingerprint import build_version_and_fingerprint_columns
from pvgisprototype.constants import (
    ENERGY_NAME_WITH_SYMBOL,
    RADIANS,
    REFLECTIVITY,
    SPECTRAL_EFFECT_NAME,
    SYSTEM_LOSS,
    TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME,
)


def print_change_percentages_panel(
    # dictionary: dict = dict(),
    photovoltaic_power: PhotovoltaicPower,
    title: str = "Analysis of Performance",
    longitude=None,
    latitude=None,
    elevation=None,
    surface_orientation: float | bool = True,
    surface_tilt: float | bool = True,
    horizon_profile: NDArray | None = None,
    timestamps: DatetimeIndex | None = None,
    timezone: ZoneInfo | None = None,
    angle_output_units: str = RADIANS,
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
    # dictionary = flatten_dictionary(photovoltaic_power.presentation)
    results = report_photovoltaic_performance(
        # dictionary=dictionary,
        dictionary=photovoltaic_power,
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
    position_table = populate_position_table(
        table=position_table,
        data_model=photovoltaic_power,
        latitude=latitude,
        longitude=longitude,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        rounding_places=positioning_rounding_places,
    )
    position_panel = build_position_panel(position_table, width=performance_table.width)


    # Algorithmic metadata panel

    algorithmic_metadata_table = populate_algorithmic_metadata_table(
        data_model=photovoltaic_power
    )
    algorithmic_metadata_panel = build_algorithmic_metadata_panel(
        algorithmic_metadata_table
    )
    
    # Horizon profile

    if horizon_profile is not None:
        horizon_profile_polar_plot = generate_horizon_profile_polar_plot(horizon_profile)
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

    # Timing

    time_table = build_time_table()
    time_table = populate_time_table(
        table=time_table, timestamps=timestamps, timezone=timezone
    )
    time_panel = build_time_panel(time_table)


    # Photovoltaic Module

    photovoltaic_module_table = build_photovoltaic_module_table()
    photovoltaic_module_table = populate_photovoltaic_module_table(
        table=photovoltaic_module_table,
        photovoltaic_power=photovoltaic_power,
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

    fingerprint = photovoltaic_power.presentation['Fingerprint']['Fingerprint 🆔']
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
