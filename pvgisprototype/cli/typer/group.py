#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
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
