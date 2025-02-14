from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from typer import Context


def print_command_metadata(context: Context):
    """ """
    command_parameters = {}
    command_parameters["command"] = context.command_path
    command_parameters = command_parameters | context.params
    command_parameters_panel = Panel.fit(
        Pretty(command_parameters, no_wrap=True),
        subtitle="[reverse]Command Metadata[/reverse]",
        subtitle_align="right",
        border_style="dim",
        style="dim",
    )
    Console().print(command_parameters_panel)

    # write to file ?
    import json

    from pvgisprototype.validation.serialisation import CustomEncoder

    with open("command_parameters.json", "w") as json_file:
        json.dump(command_parameters, json_file, cls=CustomEncoder, indent=4)
