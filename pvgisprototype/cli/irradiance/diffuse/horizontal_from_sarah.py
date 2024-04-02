from typing import Annotated
from typing import Optional
from pathlib import Path
from datetime import datetime
from pvgisprototype.api.series.models import MethodsForInexactMatches
from pvgisprototype.cli.typer.irradiance import typer_argument_global_horizontal_irradiance
from pvgisprototype.cli.typer.irradiance import typer_argument_direct_horizontal_irradiance
from pvgisprototype.cli.typer.location import typer_argument_longitude_in_degrees
from pvgisprototype.cli.typer.location import typer_argument_latitude_in_degrees
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.time_series import typer_option_mask_and_scale
from pvgisprototype.cli.typer.time_series import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer.time_series import typer_option_tolerance
from pvgisprototype.cli.typer.time_series import typer_option_in_memory
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.output import typer_option_statistics
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.output import typer_option_index
from pvgisprototype.cli.typer.output import typer_option_fingerprint
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.api.irradiance.diffuse import read_horizontal_irradiance_components_from_sarah
from pvgisprototype.api.irradiance.diffuse import calculate_diffuse_horizontal_component_from_sarah
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call


@log_function_call
def get_diffuse_horizontal_component_from_sarah(
    shortwave: Annotated[Path, typer_argument_global_horizontal_irradiance],
    direct: Annotated[Path, typer_argument_direct_horizontal_irradiance],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamps: Annotated[Optional[datetime], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = True,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    uniplot: Annotated[bool, typer_option_uniplot] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = 0,
    index: Annotated[bool, typer_option_index] = False,
    fingerprint: Annotated[bool, typer_option_fingerprint] = False,
    quiet: Annotated[bool, typer_option_quiet] = False,
):
    """Calculate the diffuse horizontal irradiance from SARAH time series.

    Parameters
    ----------
    shortwave: Path
        Filename of surface short-wave (solar) radiation downwards time series
        (short name : `ssrd`) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth. This parameter
        comprises both direct and diffuse solar radiation.

    direct: Path
        Filename of surface .. time series
        (short name : ``) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth. 

    Returns
    -------
    diffuse_horizontal_irradiance: float
        The diffuse radiant flux incident on a horizontal surface per unit area in W/m².
    """
    if shortwave and direct:
        horizontal_irradiance_components = (
            read_horizontal_irradiance_components_from_sarah(
                shortwave=shortwave,
                direct=direct,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                mask_and_scale=mask_and_scale,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                in_memory=in_memory,
                multi_thread=multi_thread,
                verbose=verbose,
                log=log,
            )
        )
        global_horizontal_irradiance_series = horizontal_irradiance_components[
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
        direct_horizontal_irradiance_series = horizontal_irradiance_components[
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
        diffuse_horizontal_irradiance_series = calculate_diffuse_horizontal_component_from_sarah(
            global_horizontal_irradiance_series=global_horizontal_irradiance_series,
            direct_horizontal_irradiance_series=direct_horizontal_irradiance_series,
            # longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
            # latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
            # timestamps=timestamps,
            # neighbor_lookup=neighbor_lookup,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )

    if not quiet:
        if verbose > 0:
            from pvgisprototype.constants import TITLE_KEY_NAME
            from pvgisprototype.cli.print import print_irradiance_table_2
            print_irradiance_table_2(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                dictionary=diffuse_horizontal_irradiance_series.components,
                title=diffuse_horizontal_irradiance_series.components[TITLE_KEY_NAME] + f' in-plane irradiance series {IRRADIANCE_UNITS}',
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = diffuse_horizontal_irradiance_series.value.flatten().astype(str)
            csv_str = ','.join(flat_list)
            print(csv_str)
    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv
        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=diffuse_horizontal_irradiance_series.components,
            filename=csv,
        )
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics
        print_series_statistics(
            data_array=diffuse_horizontal_irradiance_series.value,
            timestamps=timestamps,
            title="Diffuse horizontal irradiance",
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_time_series
        uniplot_data_array_time_series(
            data_array=diffuse_horizontal_irradiance_series.value,
            data_array_2=None,
            lines=True,
            supertitle = 'Diffuse Horizontal Irradiance Series',
            title = 'Diffuse Horizontal Irradiance Series',
            label = 'Diffuse Horizontal Irradiance',
            label_2 = None,
            unit = IRRADIANCE_UNITS,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=diffuse_horizontal_irradiance_series.components)
