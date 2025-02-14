"""
Output options
"""

import typer

from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_output,
    rich_help_panel_output_metadata,
)
from pvgisprototype.constants import (
    DEGREES,
    INDEX_IN_TABLE_OUTPUT_FLAG_TYPER_HELP,
    RADIANS,
)

# Version

typer_option_version = typer.Option(
    help="Report the software version",
    rich_help_panel=rich_help_panel_output,
)
# Command metadata

typer_option_command_metadata = typer.Option(
    help="Print command metadata",
    rich_help_panel=rich_help_panel_output_metadata,
)

# Index

typer_option_index = typer.Option(
    "--index",
    "--idx",
    "-i",
    help=INDEX_IN_TABLE_OUTPUT_FLAG_TYPER_HELP,
    show_default=True,
    show_choices=True,
    rich_help_panel=rich_help_panel_output,
)

# Decimals

typer_option_rounding_places = typer.Option(
    "--rounding-places",
    "-r",
    help="Number of digits to round results to",
    show_default=True,
    rich_help_panel=rich_help_panel_output,
)

# Units

typer_option_time_output_units = typer.Option(
    "--time-output-units",
    "-tou",
    help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]",
    show_default=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_output,
)
typer_option_angle_units = typer.Option(
    "--angle-input-units",
    "-aiu",
    help="Angular units for internal solar geometry calculations. :warning: [bold red]Keep fingers away![/bold red]",
    show_default=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_output,
)


def callback_angle_output_units(
    ctx: typer.Context,
    angle_output_units: str,
):
    """Callback function : set verbose to >=7 if analysis is requested !"""
    analysis = ctx.params.get("analysis")
    quick_response_code = ctx.params.get("quick_response_code")
    if analysis or quick_response_code:
        angle_output_units = DEGREES
    return angle_output_units


typer_option_angle_output_units = typer.Option(
    "--angle-output-units",
    "-aou",
    help=f"Angular units for solar geometry calculations ({DEGREES} or {RADIANS}). :warning: [bold red]Under development[/red bold]",
    show_default=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_output,
    callback=callback_angle_output_units,
)

# Quick Response Code

typer_option_quick_response = typer.Option(
    "--qr",
    "--qr-code",
    "--quick-response",
    "--quick-response-code",
    help="󰐳 Quick Response Code",
    show_default=True,
    rich_help_panel=rich_help_panel_output_metadata,
)

# Fingerprint


def callback_fingerprint(
    ctx: typer.Context,
    fingerprint: bool,
):
    """Callback function : set verbose to >=7 if analysis is requested !"""
    quick_response_code = ctx.params.get("quick_response_code")
    if quick_response_code:
        fingerprint = True
    return fingerprint


typer_option_fingerprint = typer.Option(
    "--fingerprint",
    "--fp",
    help="Fingerprint the output time series",
    is_flag=True,
    show_default=True,
    rich_help_panel=rich_help_panel_output_metadata,
    callback=callback_fingerprint,
)

# Layout

typer_option_panels_output = typer.Option(
    "--panels",
    help="Print output in panels",
    show_default=True,
    rich_help_panel=rich_help_panel_output,
)

# File naming and names

typer_option_output_filename = typer.Option(
    help="Output filename for the generated figure",
    rich_help_panel=rich_help_panel_output,
)
typer_option_variable_name_as_suffix = typer.Option(
    help="Suffix the output filename with the variable name",
    rich_help_panel=rich_help_panel_output,
)
typer_option_csv = typer.Option(
    help="CSV output filename",
    rich_help_panel=rich_help_panel_output,
)
