from click import Context
from typer.core import TyperGroup


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order they appear.
        See: https://github.com/tiangolo/typer/issues/428#issuecomment-1238866548
        """
        order = [
            "introduction",
            "global",
            "direct",
            "diffuse",
            "reflected",
            "extraterrestrial",
        ]
        ordered_commands = [command for command in order if command in self.commands]
        additional_commands = [
            command for command in self.commands if command not in ordered_commands
        ]

        return ordered_commands + additional_commands
