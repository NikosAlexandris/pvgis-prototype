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
import typer

from pvgisprototype.cli.irradiance.diffuse.altitude import (
    get_diffuse_solar_altitude_coefficients_series,
    get_diffuse_solar_altitude_function_series,
)
from pvgisprototype.cli.irradiance.diffuse.horizontal import (
    get_diffuse_horizontal_irradiance_series,
)
from pvgisprototype.cli.irradiance.diffuse.inclined import (
    get_diffuse_inclined_irradiance_series,
)
from pvgisprototype.cli.irradiance.diffuse.sky_irradiance import (
    get_diffuse_sky_irradiance_series,
)
from pvgisprototype.cli.irradiance.diffuse.kb_ratio import get_kb_ratio_series
from pvgisprototype.cli.irradiance.diffuse.term_n import get_term_n_series
from pvgisprototype.cli.irradiance.diffuse.transmission_function import (
    get_diffuse_transmission_function_series,
)
from pvgisprototype.cli.irradiance.diffuse.ground_reflected import (
    get_ground_reflected_inclined_irradiance_series,
)
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_irradiance_series,
    rich_help_panel_toolbox,
)
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.constants import (
    GROUND_REFLECTED_IRRADIANCE_TYPER_HELP,
    GROUND_REFLECTED_IRRADIANCE_TYPER_HELP_SHORT,
)


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=":sun_with_face:🗤 Estimate the diffuse sky- or ground-reflected irradiance incident on a surface",
)
app.command(
    name="inclined",
    no_args_is_help=True,
    help="🗤∡ Calculate the diffuse sky-reflected inclined irradiance incident on a surface over a period of time",
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_diffuse_inclined_irradiance_series)
app.command(
    name="horizontal",
    no_args_is_help=True,
    help="🗤⭳ Estimate the diffuse sky-reflected horizontal irradiance over a period of time",
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_diffuse_horizontal_irradiance_series)
app.command(
    name="ground-reflected",
    help=f"🗤{GROUND_REFLECTED_IRRADIANCE_TYPER_HELP}",
    short_help=f"🗤{GROUND_REFLECTED_IRRADIANCE_TYPER_HELP_SHORT}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_ground_reflected_inclined_irradiance_series)
app.command(
    name="kb-ratio",
    no_args_is_help=True,
    help="Kb : Calculate the ratio of the direct to the extraterrestrial horizontal irradiance over a period of time",
    rich_help_panel=rich_help_panel_toolbox,
)(get_kb_ratio_series)
app.command(
    name="n-terms",
    no_args_is_help=True,
    help="N∝ Calculate the N term for the diffuse sky irradiance function over a period of time",
    rich_help_panel=rich_help_panel_toolbox,
)(get_term_n_series)
app.command(
    name="sky-irradiances",
    no_args_is_help=True,
    help="🗤☉ Calculate the diffuse sky irradiance over a period of time",
    rich_help_panel=rich_help_panel_toolbox,
)(get_diffuse_sky_irradiance_series)
app.command(
    name="transmission-function",
    no_args_is_help=True,
    help="ƒ⇝ Calculate the diffuse transmission function over a series of linke turbidity factors",
    rich_help_panel=rich_help_panel_toolbox,
)(get_diffuse_transmission_function_series)
app.command(
    name="diffuse-altitude-coefficients",
    no_args_is_help=True,
    help="🗤⦩× Calculate the diffuse solar altitude coefficients",
    rich_help_panel=rich_help_panel_toolbox,
)(get_diffuse_solar_altitude_coefficients_series)
app.command(
    name="diffuse-altitude",
    no_args_is_help=True,
    help="🗤⦩ Calculate the diffuse solar altitude angle over a period of time",
    rich_help_panel=rich_help_panel_toolbox,
)(get_diffuse_solar_altitude_function_series)
