from typing import Annotated, Optional
from datetime import datetime
from pathlib import Path
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.api.irradiance.shortwave import calculate_global_horizontal_irradiance_time_series
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.location import typer_argument_elevation
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.irradiance import typer_option_global_horizontal_irradiance
from pvgisprototype.cli.typer.irradiance import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer.time_series import typer_option_mask_and_scale
from pvgisprototype.cli.typer.time_series import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer.time_series import typer_option_tolerance
from pvgisprototype.cli.typer.time_series import typer_option_in_memory
from pvgisprototype.cli.typer.linke_turbidity import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.refraction import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer.albedo import typer_option_albedo
from pvgisprototype.cli.typer.irradiance import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.position import typer_option_solar_incidence_model
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.timing import typer_option_global_time_offset
from pvgisprototype.cli.typer.timing import typer_option_hour_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_solar_constant
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.output import typer_option_time_output_units
from pvgisprototype.cli.typer.output import typer_option_angle_units
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
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
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import ALBEDO_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call


@log_function_call
def get_global_horizontal_irradiance_time_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[Optional[datetime], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = False,
    global_horizontal_irradiance: Annotated[Optional[Path], typer_option_global_horizontal_irradiance] = None,
    direct_horizontal_irradiance: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = [LINKE_TURBIDITY_TIME_SERIES_DEFAULT], # REVIEW-ME + Typer Parser
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: Annotated[Optional[float], typer_option_albedo] = ALBEDO_DEFAULT,
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModel, typer_option_solar_position_model] = SolarPositionModel.noaa,
    solar_incidence_model: Annotated[SolarIncidenceModel, typer_option_solar_incidence_model] = SolarIncidenceModel.jenco,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.noaa,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    # horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    uniplot: Annotated[bool, typer_option_uniplot] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = False,
    log: Annotated[int, typer_option_log] = 0,
    index: Annotated[bool, typer_option_index] = False,
    fingerprint: Annotated[bool, typer_option_fingerprint] = False,
    quiet: Annotated[bool, typer_option_quiet] = False,
):
    """Calculate the global horizontal irradiance (GHI)

    The global horizontal irradiance represents the total amount of shortwave
    radiation received from above by a surface horizontal to the ground. It
    includes both the direct and the diffuse solar radiation.
    """
    global_horizontal_irradiance_series = calculate_global_horizontal_irradiance_time_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        start_time=start_time,
        frequency=frequency,
        end_time=end_time,
        timezone=timezone,
        random_timestamps=random_timestamps,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
        apply_angular_loss_factor=apply_angular_loss_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
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
                dictionary=global_horizontal_irradiance_series.components,
                title = (
                    global_horizontal_irradiance_series.components[TITLE_KEY_NAME]
                    + f" in-plane irradiance series {IRRADIANCE_UNITS}"
                ),
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = global_horizontal_irradiance_series.value.flatten().astype(str)
            csv_str = ','.join(flat_list)
            print(csv_str)

    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv
        write_irradiance_csv(
            longitude=None,
            latitude=None,
            timestamps=timestamps,
            dictionary=global_horizontal_irradiance_series.components,
            filename=csv,
        )
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics
        print_series_statistics(
            data_array=global_horizontal_irradiance_series.value,
            timestamps=timestamps,
            title="Global irradiance",
            rounding_places=rounding_places,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_time_series
        uniplot_data_array_time_series(
            data_array=global_horizontal_irradiance_series.value,
            data_array_2=None,
            lines=True,
            supertitle = 'Global Horizontal Irradiance Series',
            title = 'Global Horizontal Irradiance Series',
            label = 'Global Horizontal Irradiance',
            label_2 = None,
            unit = IRRADIANCE_UNITS,
            # terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=global_horizontal_irradiance_series.components)
