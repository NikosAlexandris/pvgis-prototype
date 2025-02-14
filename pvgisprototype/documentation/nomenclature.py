from datetime import datetime

from pandas import DatetimeIndex
from rich.box import SIMPLE

from pvgisprototype.constants import (
    EFFECTIVE_GLOBAL_IRRADIANCE_DESCRIPTION,
    EFFECTIVE_IRRADIANCE_NAME,
    GLOBAL_EFFECTIVE_IRRADIANCE,
    GLOBAL_IN_PLANE_IRRADIANCE,
    GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY,
    GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY,
    GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY,
    GLOBAL_IRRADIANCE_NAME,
    IN_PLANE_IRRADIANCE,
    IRRADIANCE_AFTER_REFLECTIVITY,
    IRRADIANCE_AFTER_REFLECTIVITY_DESCRIPTION,
    IRRADIANCE_UNIT,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_LONG_NAME,
    PHOTOVOLTAIC_POWER_UNIT,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_DESCRIPTION,
    REFLECTIVITY,
    REFLECTIVITY_DESCRIPTION,
    SPECTRAL_EFFECT_COLUMN_NAME,
    SPECTRAL_EFFECT_DESCRIPTION,
    SYSTEM_LOSS,
    SYSTEM_LOSS_DESCRIPTION,
    TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME,
    TEMPERATURE_AND_LOW_IRRADIANCE_DESCRIPTION,
    TOTAL_NET_EFFECT,
    TOTAL_NET_EFFECT_DESCRIPTION,
)


def print_nomenclature_panel(
    longitude=None,
    latitude=None,
    elevation=None,
    timestamps: DatetimeIndex | datetime = datetime.now(),
    dictionary: dict = dict(),
    title: str = "Changes",
    rounding_places: int = 1,  # ROUNDING_PLACES_DEFAULT,
    verbose=1,
    index: bool = False,
    surface_orientation=True,
    surface_tilt=True,
):
    """ """
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    # from pvgisprototype.api.power.metrics import irradiance_changes
    # print(irradiance_changes)

    description_table = Table(
        title="Nomenclature",
        caption="Description of quantities, units and percentage calculations",
        show_header=True,
        header_style="bold magenta",
        row_styles=["none", "dim"],
        box=SIMPLE,
        highlight=True,
    )
    description_table.add_column("Quantity", justify="left", style="cyan", no_wrap=True)
    # table.add_column(f"{SYMBOL_SUMMATION}", justify="right", style="cyan")
    description_table.add_column(
        "Description", justify="left", style="cyan", no_wrap=True
    )
    description_table.add_column("Unit", justify="right", style="magenta")
    description_table.add_column("% of", style="dim", justify="center")
    # description_table.add_column(f"{frequency_label} sums", style="dim", justify="center")
    description_table.add_column("Contributes to", style="dim", justify="center")

    # In-Plane irradiance (before changes)
    description_table.add_row(
        f"{IN_PLANE_IRRADIANCE}",  # Quantity
        f"{GLOBAL_IRRADIANCE_NAME}",  # Description
        f"{IRRADIANCE_UNIT}",  # Unit
        # f"100 {GLOBAL_IRRADIANCE_NAME}",  # % of (which) Quantity
        f"{GLOBAL_IN_PLANE_IRRADIANCE_AFTER_REFLECTIVITY}",  # Outputs to (which) Quantity
    )
    # Reflectivity
    description_table.add_row(
        f"{REFLECTIVITY}",
        f"{REFLECTIVITY_DESCRIPTION}",
        f"{IRRADIANCE_UNIT}",
        f"{GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY}",
        f"{GLOBAL_IN_PLANE_IRRADIANCE}",
    )
    # Irradiance after reflectivity change
    description_table.add_row(
        f"[white dim]{IRRADIANCE_AFTER_REFLECTIVITY}",
        f"[white dim]{IRRADIANCE_AFTER_REFLECTIVITY_DESCRIPTION}",
        f"[white dim]{IRRADIANCE_UNIT}",
        f"{GLOBAL_IN_PLANE_IRRADIANCE}",
    )

    # Change due to Spectral Effects
    # description_table.add_row("Spectral Effects [%]", f"{spectral_effects_gain:.2f}%")
    description_table.add_row(
        # f"{SPECTRAL_EFFECT_COLUMN_NAME} {SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME}",
        # f"{SPECTRAL_EFFECT} {SPECTRAL_EFFECT_PERCENTAGE}",
        f"{SPECTRAL_EFFECT_COLUMN_NAME}",
        f"{SPECTRAL_EFFECT_DESCRIPTION}",
        f"{IRRADIANCE_UNIT}",
        f"{GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY}",
        f"{GLOBAL_EFFECTIVE_IRRADIANCE}",
    )
    # Effective irradiance after spectral effect
    description_table.add_row(
        f"[white dim]{EFFECTIVE_IRRADIANCE_NAME}",
        f"[white dim]{EFFECTIVE_GLOBAL_IRRADIANCE_DESCRIPTION}",
        f"[white dim]{IRRADIANCE_UNIT}",
        f"{GLOBAL_IN_PLANE_IRRADIANCE_BEFORE_REFLECTIVITY}",
        f"{PHOTOVOLTAIC_POWER_LONG_NAME}",
    )

    # Temperature & Low Irradiance effect
    description_table.add_row(
        f"{TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME}",
        f"{TEMPERATURE_AND_LOW_IRRADIANCE_DESCRIPTION}",
        f"{IRRADIANCE_UNIT}",
        f"{GLOBAL_EFFECTIVE_IRRADIANCE}",
        f"{PHOTOVOLTAIC_POWER_LONG_NAME}",
    )

    # Effective Power after temperature and low irradiance
    description_table.add_row(
        f"[white dim]{PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS}",
        f"[white dim]{PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_DESCRIPTION}",
        f"[white dim]{PHOTOVOLTAIC_POWER_UNIT}",
        f"{GLOBAL_EFFECTIVE_IRRADIANCE}",
        f"{PHOTOVOLTAIC_POWER_LONG_NAME}",
    )

    # # System Efficiency
    # description_table.add_row(
    #         f"{SYSTEM_EFFICIENCY}",
    #         f"{SYSTEM_EFFICIENCY_DESCRIPTION}",
    #         f"{PHOTOVOLTAIC_POWER_UNIT}",
    #         f"{PHOTOVOLTAIC_POWER_LONG_NAME}",
    #         f"{PHOTOVOLTAIC_POWER_LONG_NAME}",
    #         )

    # System Loss
    description_table.add_row(
        f"{SYSTEM_LOSS}",
        f"{SYSTEM_LOSS_DESCRIPTION}",
        f"{PHOTOVOLTAIC_POWER_UNIT}",
        f"{PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME}",
        f"{PHOTOVOLTAIC_POWER_LONG_NAME}",
    )

    # Total change
    description_table.add_row(
        f"{TOTAL_NET_EFFECT}",
        f"{TOTAL_NET_EFFECT_DESCRIPTION}",
        f"{IRRADIANCE_UNIT}",
        f"{GLOBAL_IN_PLANE_IRRADIANCE}",
        f"{PHOTOVOLTAIC_POWER_LONG_NAME}",
    )
    # Photovoltaic Power
    description_table.add_row(
        f"{PHOTOVOLTAIC_POWER_COLUMN_NAME}",
        f"{PHOTOVOLTAIC_POWER_LONG_NAME}",
        f"{PHOTOVOLTAIC_POWER_UNIT}",
        f"{GLOBAL_EFFECTIVE_IRRADIANCE}",
    )

    panel = Panel(description_table, title="Nomenclature", expand=False)
    console = Console()
    console.print(panel)
