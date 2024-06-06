from typing import Annotated
from typing import Optional

from pvgisprototype import Latitude

from pvgisprototype.algorithms.noaa.event_hour_angle import calculate_event_hour_angle_series_noaa
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.position import typer_argument_solar_declination
from pvgisprototype.cli.typer.position import typer_argument_surface_tilt
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose

from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT

from pvgisprototype.api.position.hour_angle import calculate_event_hour_angle_series
from pvgisprototype import SurfaceTilt
from pvgisprototype import SolarDeclination
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import DATA_TYPE_DEFAULT, ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import QUIET_FLAG_DEFAULT
from pandas import DatetimeIndex
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.constants import STATISTICS_FLAG_DEFAULT
from pvgisprototype.constants import CSV_PATH_DEFAULT
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype.cli.typer.data_processing import typer_option_dtype
from pvgisprototype.cli.typer.data_processing import typer_option_array_backend
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.constants import UNIPLOT_FLAG_DEFAULT
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.cli.typer.output import typer_option_panels_output
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.cli.typer.output import typer_option_index
from pathlib import Path


def sunrise(
    latitude: Annotated[float, typer_argument_latitude],
    solar_declination: Annotated[Optional[float], typer_argument_solar_declination] = 45,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    panels: Annotated[bool, typer_option_panels_output] = False,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
):
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * π / 180'

    The hour angle (ω) is the angle at any instant through which the earth has
    to turn to bring the meridian of the observer directly in line with the
    sun's rays measured in radian. In other words, it is a measure of time,
    expressed in angular measurement, usually degrees, from solar noon. It
    increases by 15° per hour, negative before solar noon and positive after
    solar noon.
    """
    latitude = Latitude(value=latitude, unit=RADIANS)
    event_hour_angle_series = calculate_event_hour_angle_series(
        latitude=latitude,
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    surface_tilt = SurfaceTilt(value=surface_tilt, unit=RADIANS)
    solar_declination = SolarDeclination(value=solar_declination, unit=RADIANS)

    from pvgisprototype.cli.print import print_hour_angle_table
    print_hour_angle_table(
            latitude=latitude,
            rounding_places=rounding_places,
            surface_tilt=surface_tilt,
            declination=solar_declination,
            hour_angle=hour_angle,
            units=angle_output_units,
    )
