from typing import Annotated
from typing import Optional
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
from datetime import datetime
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pathlib import Path
from pvgisprototype.cli.typer_parameters import typer_option_global_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_argument_solar_constant
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.constants import RADIANS
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.api.series.models import MethodsForInexactMatches
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_uniplot
from pvgisprototype.cli.typer_parameters import typer_option_uniplot_terminal_width
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_log
from pvgisprototype.cli.typer_parameters import typer_option_index
from pvgisprototype.cli.typer_parameters import typer_option_fingerprint
from pvgisprototype.cli.typer_parameters import typer_option_quiet
from pvgisprototype.api.irradiance.diffuse import calculate_diffuse_inclined_irradiance_time_series
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.cli.typer.timestamps import typer_option_periods


@log_function_call
def get_diffuse_inclined_irradiance_time_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    periods: Annotated[Optional[int], typer_option_periods] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = False,
    global_horizontal_irradiance: Annotated[Optional[Path], typer_option_global_horizontal_irradiance] = None,
    direct_horizontal_irradiance: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    surface_orientation: Annotated[Optional[float], typer_option_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[float, typer_option_surface_tilt] = SURFACE_TILT_DEFAULT,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT, # REVIEW-ME + Typer Parser
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModel, typer_option_solar_position_model] = SolarPositionModel.noaa,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.noaa,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_argument_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
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
) -> None:
    diffuse_inclined_irradiance_time_series = calculate_diffuse_inclined_irradiance_time_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        global_horizontal_component=global_horizontal_irradiance,
        direct_horizontal_component=direct_horizontal_irradiance,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_angular_loss_factor=apply_angular_loss_factor,
        solar_position_model=solar_position_model,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        multi_thread=multi_thread,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print import print_irradiance_table_2
            print_irradiance_table_2(
                longitude=convert_float_to_degrees_if_requested(
                    longitude, angle_output_units
                ),
                latitude=convert_float_to_degrees_if_requested(
                    latitude, angle_output_units
                ),
                timestamps=timestamps,
                dictionary=diffuse_inclined_irradiance_time_series.components,
                title = (
                    DIFFUSE_INCLINED_IRRADIANCE
                    + f" in-plane irradiance series {IRRADIANCE_UNITS}"
                ),
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = diffuse_inclined_irradiance_time_series.value.flatten().astype(str)
            csv_str = ','.join(flat_list)
            print(csv_str)

    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv
        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=diffuse_inclined_irradiance_time_series.components,
            filename=csv,
        )
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics
        print_series_statistics(
            data_array=diffuse_inclined_irradiance_time_series.value,
            timestamps=timestamps,
            title="Diffuse inclined irradiance",
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_time_series
        uniplot_data_array_time_series(
            data_array=diffuse_inclined_irradiance_time_series.value,
            data_array_2=None,
            lines=True,
            supertitle = 'Diffuse Inclined Irradiance Series',
            title = 'Diffuse Inclined Irradiance Series',
            label = 'Diffuse Inclined Irradiance',
            label_2 = None,
            unit = IRRADIANCE_UNITS,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=diffuse_inclined_irradiance_time_series.components)
