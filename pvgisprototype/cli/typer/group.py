from typer.core import TyperGroup
from click import Context


class OrderCommands(TyperGroup):
  def list_commands(self, ctx: Context):
    """Return list of commands in the order appear.
    See: https://github.com/tiangolo/typer/issues/428#issuecomment-1238866548
    """
    return list(self.commands)
