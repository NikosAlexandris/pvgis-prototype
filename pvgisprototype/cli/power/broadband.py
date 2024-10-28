"""
CLI module to calculate the photovoltaic power output over a
location for a period in time.
"""

from datetime import datetime
from pathlib import Path
from typing import Annotated
from zoneinfo import ZoneInfo

import typer
from pandas import DatetimeIndex, Timestamp
from rich import print
from xarray import DataArray

from pvgisprototype import (
    LinkeTurbidityFactor,
    SpectralFactorSeries,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.api.power.broadband_multiple_surfaces import (
    calculate_photovoltaic_power_output_series_from_multiple_surfaces,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.series.spectral_factor import get_spectral_factor_series
from pvgisprototype.api.series.temperature import get_temperature_series
from pvgisprototype.api.series.time_series import get_time_series
from pvgisprototype.api.series.wind_speed import get_wind_speed_series
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
    round_float_values,
)
from pvgisprototype.cli.print.qr import QuickResponseCode
from pvgisprototype.cli.typer.albedo import typer_option_albedo
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
    typer_option_multi_thread,
)
from pvgisprototype.cli.typer.earth_orbit import (
    typer_option_eccentricity_correction_factor,
    typer_option_perigee_offset,
    typer_option_solar_constant,
)
from pvgisprototype.cli.typer.efficiency import (
    typer_option_efficiency,
    typer_option_module_temperature_algorithm,
    typer_option_pv_power_algorithm,
    typer_option_system_efficiency,
)
from pvgisprototype.cli.typer.irradiance import (
    typer_option_apply_reflectivity_factor,
    typer_option_direct_horizontal_irradiance,
    typer_option_global_horizontal_irradiance,
)
from pvgisprototype.cli.typer.linke_turbidity import (
    typer_option_linke_turbidity_factor_series,
)
from pvgisprototype.cli.typer.location import (
    typer_argument_elevation,
    typer_argument_latitude,
    typer_argument_longitude,
)
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.output import (
    typer_option_angle_output_units,
    typer_option_command_metadata,
    typer_option_csv,
    typer_option_fingerprint,
    typer_option_index,
    typer_option_quick_response,
    typer_option_rounding_places,
)
from pvgisprototype.cli.typer.photovoltaic import (
    typer_option_photovoltaic_module_model,
    typer_option_photovoltaic_module_peak_power,
)
from pvgisprototype.cli.typer.plot import (
    typer_option_uniplot,
    typer_option_uniplot_terminal_width,
)
from pvgisprototype.cli.typer.position import (
    typer_argument_surface_orientation,
    typer_argument_surface_tilt,
    typer_option_solar_incidence_model,
    typer_option_solar_position_model,
    typer_option_surface_orientation_multi,
    typer_option_surface_tilt_multi,
    typer_option_zero_negative_solar_incidence_angle,
)
from pvgisprototype.cli.typer.shading import(
    typer_option_horizon_profile,
    typer_option_shading_model,
)
from pvgisprototype.cli.typer.profiling import typer_option_profiling
from pvgisprototype.cli.typer.refraction import (
    typer_option_apply_atmospheric_refraction,
    typer_option_refracted_solar_zenith,
)
from pvgisprototype.cli.typer.spectral_factor import (
    typer_argument_spectral_factor_series,
)
from pvgisprototype.cli.typer.statistics import (
    typer_option_groupby,
    typer_option_nomenclature,
    typer_option_statistics,
)
from pvgisprototype.cli.typer.temperature import typer_argument_temperature_series
from pvgisprototype.cli.typer.time_series import (
    typer_option_in_memory,
    typer_option_mask_and_scale,
    typer_option_nearest_neighbor_lookup,
    typer_option_tolerance,
)

# from pvgisprototype.cli.typer.location import typer_argument_horizon_heights
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_timestamps,
    typer_option_end_time,
    typer_option_frequency,
    typer_option_periods,
    typer_option_random_timestamps,
    typer_option_start_time,
    typer_option_timezone,
)
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.cli.typer.wind_speed import typer_argument_wind_speed_series
from pvgisprototype.cli.typer.validate_output import typer_option_validate_output
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ANALYSIS_FLAG_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_FLAG_DEFAULT,
    GROUPBY_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    METADATA_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    NOMENCLATURE_FLAG_DEFAULT,
    PERIGEE_OFFSET,
    PHOTOVOLTAIC_MODULE_DEFAULT,
    POWER_UNIT,
    QUIET_FLAG_DEFAULT,
    RADIANS,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    SOLAR_CONSTANT,
    SPECTRAL_FACTOR_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    TEMPERATURE_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TOLERANCE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    cPROFILE_FLAG_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger


@log_function_call
def photovoltaic_power_output_series(
    ctx: typer.Context,
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    surface_orientation: Annotated[
        float | None, typer_argument_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float | None, typer_argument_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[DatetimeIndex | None, typer_argument_timestamps] = str(Timestamp.now()),
    timezone: Annotated[ZoneInfo | None, typer_option_timezone] = None,
    start_time: Annotated[
        datetime | None, typer_option_start_time
    ] = None,  # Used by a callback function
    periods: Annotated[
        int | None, typer_option_periods
    ] = None,  # Used by a callback function
    frequency: Annotated[
        str | None, typer_option_frequency
    ] = None,  # Used by a callback function
    end_time: Annotated[
        datetime | None, typer_option_end_time
    ] = None,  # Used by a callback function
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    global_horizontal_irradiance: Annotated[
        Path | None, typer_option_global_horizontal_irradiance
    ] = None,
    direct_horizontal_irradiance: Annotated[
        Path | None, typer_option_direct_horizontal_irradiance
    ] = None,
    spectral_factor_series: Annotated[
        SpectralFactorSeries, typer_argument_spectral_factor_series
    ] = SPECTRAL_FACTOR_DEFAULT,  # Accept also list of float values ?
    temperature_series: Annotated[
        TemperatureSeries, typer_argument_temperature_series
    ] = TEMPERATURE_DEFAULT,
    wind_speed_series: Annotated[
        WindSpeedSeries, typer_argument_wind_speed_series
    ] = WIND_SPEED_DEFAULT,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Annotated[
        bool, typer_option_apply_atmospheric_refraction
    ] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[
        float | None, typer_option_refracted_solar_zenith
    ] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[float | None, typer_option_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, typer_option_apply_reflectivity_factor
    ] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, typer_option_solar_position_model
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, typer_option_solar_incidence_model
    ] = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: Annotated[
        bool, typer_option_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[
        SolarTimeModel, typer_option_solar_time_model
    ] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[
        float, typer_option_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    horizon_profile: Annotated[DataArray | None, typer_option_horizon_profile] = None,
    shading_model: Annotated[
        ShadingModel, typer_option_shading_model] = ShadingModel.pvis,  # for performance analysis : should be one !
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, typer_option_photovoltaic_module_model
    ] = PHOTOVOLTAIC_MODULE_DEFAULT,  # PhotovoltaicModuleModel.CSI_FREE_STANDING,
    peak_power: Annotated[float, typer_option_photovoltaic_module_peak_power] = 1,
    system_efficiency: Annotated[
        float | None, typer_option_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, typer_option_pv_power_algorithm
    ] = PhotovoltaicModulePerformanceModel.king,
    temperature_model: Annotated[
        ModuleTemperatureAlgorithm, typer_option_module_temperature_algorithm
    ] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[
        float | None, typer_option_efficiency
    ] = EFFICIENCY_FACTOR_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    multi_thread: Annotated[
        bool, typer_option_multi_thread
    ] = MULTI_THREAD_FLAG_DEFAULT,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    rounding_places: Annotated[
        int, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[str | None, typer_option_groupby] = GROUPBY_DEFAULT,
    nomenclature: Annotated[
        bool, typer_option_nomenclature
    ] = NOMENCLATURE_FLAG_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, typer_option_quick_response
    ] = QuickResponseCode.NoneValue,
    profile: Annotated[bool, typer_option_profiling] = cPROFILE_FLAG_DEFAULT,
    validate_output: Annotated[bool, typer_option_validate_output] = VALIDATE_OUTPUT_DEFAULT,
):
    """Estimate the photovoltaic power output for a location and a moment or period
    in time.

    Estimate the photovoltaic power over a time series or an arbitrarily
    aggregated energy production of a PV system connected to the electricity
    grid (without battery storage) based on broadband solar irradiance, ambient
    temperature and wind speed.

    Notes
    -----
    The optional input parameters `global_horizontal_irradiance` and
    `direct_horizontal_irradiance` accept any Xarray-support data file format
    and mean the global and direct irradiance on the horizontal plane.

    Inside the API, however, and for legibility, the same parameters in the
    functions that calculate the diffuse and direct components, are defined as
    `global_horizontal_component` and `direct_horizontal_component`. This is to
    avoid confusion at the function level. For example, the function
    `calculate_diffuse_inclined_irradiance_series()` can read the direct
    horizontal component (thus the name of it `direct_horizontal_component` as
    well as simulate it.  The point is to make it clear that if the
    `direct_horizontal_component` parameter is True (which means the user has
    provided an external dataset), then read it using the
    `select_time_series()` function.

    """
    # print(f"Invoked subcommand: {ctx.invoked_subcommand}")
    # print(f'Context: {ctx}')
    # print(f'Context: {ctx.params}')

    # user_requested_timestamps = timestamps
    # user_requested_timezone = timezone  # Set to UTC by the callback functon !

    # # ------------------------------------------------------------------------
    # timezone = utc_zoneinfo = ZoneInfo('UTC')
    # logger.info(
    #         f"Input time zone : {timezone}",
    #         alt=f"Input time zone : [code]{timezone}[/code]"
    #         )

    # if timestamps.tz is None:
    #     timestamps = timestamps.tz_localize(utc_zoneinfo)
    #     logger.info(
    #         f"Naive input timestamps\n({user_requested_timestamps})\nlocalized to UTC aware for all internal calculations :\n{timestamps}"
    #     )

    # elif timestamps.tz != utc_zoneinfo:
    #     timestamps = timestamps.tz_convert(utc_zoneinfo)
    #     logger.info(
    #         f"Input zone\n{user_requested_timezone}\n& timestamps :\n{user_requested_timestamps}\n\nconverted for all internal calculations to :\n{timestamps}",
    #         alt=f"Input zone : [code]{user_requested_timezone}[/code]\n& timestamps :\n{user_requested_timestamps}\n\nconverted for all internal calculations to :\n{timestamps}"
    #     )
    # # ------------------------------------------------------------------------
    temperature_series, wind_speed_series, spectral_factor_series = get_time_series(
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        spectral_factor_series=spectral_factor_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        dtype=dtype,
        array_backend=array_backend,
        multi_thread=multi_thread,
        verbose=verbose,
        log=log,
    )
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        timestamps=timestamps,
        timezone=timezone,
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        spectral_factor_series=spectral_factor_series,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
        apply_reflectivity_factor=apply_reflectivity_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        horizon_height=horizon_profile,  # Review naming please ?
        shading_model=shading_model,
        angle_output_units=angle_output_units,
        photovoltaic_module=photovoltaic_module,
        peak_power=peak_power,
        system_efficiency=system_efficiency,
        power_model=power_model,
        temperature_model=temperature_model,
        efficiency=efficiency,
        dtype=dtype,
        array_backend=array_backend,
        multi_thread=multi_thread,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
        profile=profile,
        validate_output=validate_output,
    )  # Re-Design Me ! ------------------------------------------------

    # +++

    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if quick_response_code.value != QuickResponseCode.NoneValue:
        from pvgisprototype.cli.print.qr import print_quick_response_code

        print_quick_response_code(
            dictionary=photovoltaic_power_output_series.components,
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=True,
            surface_tilt=True,
            timestamps=timestamps,
            rounding_places=rounding_places,
            output_type=quick_response_code,
        )
        return
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print.irradiance import print_irradiance_table_2

            print_irradiance_table_2(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                dictionary=photovoltaic_power_output_series.components,
                # title=photovoltaic_power_output_series['Title'] + f" series {POWER_UNIT}",
                rounding_places=rounding_places,
                index=index,
                surface_orientation=True,
                surface_tilt=True,
                verbose=verbose,
            )
        else:
            # ------------------------- Better handling of rounding vs dtype ?
            print(
                ",".join(
                    # round_float_values(
                    #     photovoltaic_power_output_series.value.flatten(),
                    #     rounding_places,
                    # ).astype(str)
                    photovoltaic_power_output_series.value.flatten().astype(str)
                )
            )
    if statistics:
        from pvgisprototype.cli.print.series import print_series_statistics

        print_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=timestamps,
            groupby=groupby,
            title="Photovoltaic power output",
            rounding_places=rounding_places,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_series

        uniplot_data_array_series(
            data_array=photovoltaic_power_output_series.value,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle="Photovoltaic Power Output Series",
            title="Photovoltaic power output",
            label="Photovoltaic Power",
            extra_legend_labels=None,
            unit=POWER_UNIT,
            terminal_width_fraction=terminal_width_fraction,
        )
    if metadata:
        import click

        from pvgisprototype.cli.print.metadata import print_command_metadata

        print_command_metadata(context=click.get_current_context())
    if fingerprint:
        from pvgisprototype.cli.print.fingerprint import print_finger_hash

        print_finger_hash(dictionary=photovoltaic_power_output_series.components)
    # Call write_irradiance_csv() last : it modifies the input dictionary !
    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv

        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=photovoltaic_power_output_series.components,
            filename=csv,
            index=index,
        )


@log_function_call
def photovoltaic_power_output_series_from_multiple_surfaces(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    surface_orientation: Annotated[
        list | None, typer_option_surface_orientation_multi
    ] = [float(SURFACE_ORIENTATION_DEFAULT)],
    surface_tilt: Annotated[list | None, typer_option_surface_tilt_multi] = [
        float(SURFACE_TILT_DEFAULT)
    ],
    timestamps: Annotated[DatetimeIndex | None, typer_argument_timestamps] = str(Timestamp.now()),
    start_time: Annotated[datetime | None, typer_option_start_time] = None,
    periods: Annotated[int | None, typer_option_periods] = None,
    frequency: Annotated[str | None, typer_option_frequency] = None,
    end_time: Annotated[datetime | None, typer_option_end_time] = None,
    timezone: Annotated[str | None, typer_option_timezone] = None,
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    global_horizontal_irradiance: Annotated[
        Path | None, typer_option_global_horizontal_irradiance
    ] = None,
    direct_horizontal_irradiance: Annotated[
        Path | None, typer_option_direct_horizontal_irradiance
    ] = None,
    spectral_factor_series: Annotated[
        SpectralFactorSeries, typer_argument_spectral_factor_series
    ] = SPECTRAL_FACTOR_DEFAULT,  # Accept also list of float values ?
    temperature_series: Annotated[
        TemperatureSeries, typer_argument_temperature_series
    ] = TEMPERATURE_DEFAULT,
    wind_speed_series: Annotated[
        WindSpeedSeries, typer_argument_wind_speed_series
    ] = WIND_SPEED_DEFAULT,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Annotated[
        bool, typer_option_apply_atmospheric_refraction
    ] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[
        float | None, typer_option_refracted_solar_zenith
    ] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[float | None, typer_option_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, typer_option_apply_reflectivity_factor
    ] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, typer_option_solar_position_model
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, typer_option_solar_incidence_model
    ] = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: Annotated[
        bool, typer_option_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_profile: Annotated[DataArray | None, typer_option_horizon_profile] = None,
    shading_model: Annotated[
        ShadingModel, typer_option_shading_model] = ShadingModel.pvis,  # for performance analysis : should be one !
    solar_time_model: Annotated[
        SolarTimeModel, typer_option_solar_time_model
    ] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[
        float, typer_option_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, typer_option_photovoltaic_module_model
    ] = PHOTOVOLTAIC_MODULE_DEFAULT,  # PhotovoltaicModuleModel.CSI_FREE_STANDING,
    system_efficiency: Annotated[
        float | None, typer_option_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, typer_option_pv_power_algorithm
    ] = PhotovoltaicModulePerformanceModel.king,
    temperature_model: Annotated[
        ModuleTemperatureAlgorithm, typer_option_module_temperature_algorithm
    ] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[
        float | None, typer_option_efficiency
    ] = EFFICIENCY_FACTOR_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    multi_thread: Annotated[
        bool, typer_option_multi_thread
    ] = MULTI_THREAD_FLAG_DEFAULT,
    rounding_places: Annotated[
        int, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[str | None, typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, typer_option_quick_response
    ] = QuickResponseCode.NoneValue,
    metadata: Annotated[bool, typer_option_command_metadata] = False,
    profile: Annotated[bool, typer_option_profiling] = cPROFILE_FLAG_DEFAULT,
    validate_output: Annotated[bool, typer_option_validate_output] = VALIDATE_OUTPUT_DEFAULT,
):
    """Estimate the sum of photovoltaic output for multiple solar surface
    setups for a location and a moment or period in time.

    Estimate the sum of photovoltaic power over a time series or an arbitrarily
    aggregated energy production of multiple PV system setups, i.e. different
    tilts and orientations, connected to the electricity grid (without battery
    storage) based on broadband solar irradiance, ambient temperature and wind
    speed.

    Notes
    -----
    The optional input parameters `global_horizontal_irradiance` and
    `direct_horizontal_irradiance` accept any Xarray-support data file format
    and mean the global and direct irradiance on the horizontal plane.

    Inside the API, however, and for legibility, the same parameters in the
    functions that calculate the diffuse and direct components, are defined as
    `global_horizontal_component` and `direct_horizontal_component`. This is to
    avoid confusion at the function level. For example, the function
    `calculate_diffuse_inclined_irradiance_series()` can read the direct
    horizontal component (thus the name of it `direct_horizontal_component` as
    well as simulate it.  The point is to make it clear that if the
    `direct_horizontal_component` parameter is True (which means the user has
    provided an external dataset), then read it using the
    `select_time_series()` function.

    """
    if len(surface_tilt) != len(surface_orientation):
        from pvgisprototype.api.series.hardcodings import exclamation_mark

        logger.error(
            f"{exclamation_mark} Aborting as length of --surface_orientation and --surface_tilt is not the same!",
            alt=f"{exclamation_mark} [red]Aborting[/red] as [red]length[/red] [code]--surface-orientation[/code] and [code]--surface-tilt[/code] [red]is not the same[/red]!",
        )
        return

    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series_from_multiple_surfaces(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        timestamps=timestamps,
        timezone=timezone,
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        spectral_factor_series=spectral_factor_series,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        dtype=dtype,
        array_backend=array_backend,
        multi_thread=multi_thread,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
        apply_reflectivity_factor=apply_reflectivity_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        horizon_height=horizon_profile,
        shading_model=shading_model,
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        power_model=power_model,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
        profile=profile,
        validate_output=validate_output,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if quick_response_code.value != QuickResponseCode.NoneValue:
        from pvgisprototype.cli.print.qr import print_quick_response_code

        print_quick_response_code(
            dictionary=photovoltaic_power_output_series.components,
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=True,
            surface_tilt=True,
            timestamps=timestamps,
            rounding_places=rounding_places,
        )
        return
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print.irradiance import print_irradiance_table_2

            print_irradiance_table_2(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                dictionary=photovoltaic_power_output_series.components,
                # title=photovoltaic_power_output_series['Title'] + f" series {POWER_UNIT}",
                rounding_places=rounding_places,
                index=index,
                surface_orientation=True,
                surface_tilt=True,
                verbose=verbose,
            )
        else:
            flat_list = photovoltaic_power_output_series.series.flatten().astype(str)
            csv_str = ",".join(flat_list)
            print(csv_str)
    if statistics:
        from pvgisprototype.cli.print.series import print_series_statistics

        print_series_statistics(
            data_array=photovoltaic_power_output_series.series,
            timestamps=timestamps,
            groupby=groupby,
            title="Photovoltaic power output",
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_series

        individual_series = [
            series.value
            for series in photovoltaic_power_output_series.individual_series
        ]
        surface_orientation = [
            convert_float_to_degrees_if_requested(orientation, angle_output_units)
            for orientation in surface_orientation
        ]
        surface_tilt = [
            convert_float_to_degrees_if_requested(tilt, angle_output_units)
            for tilt in surface_tilt
        ]
        surface_orientation = round_float_values(surface_orientation, rounding_places)
        surface_tilt = round_float_values(surface_tilt, rounding_places)
        individual_labels = [
            f"Orientation, Tilt : {orientation}°, {tilt}°"
            for orientation, tilt in zip(surface_orientation, surface_tilt)
        ]
        uniplot_data_array_series(
            data_array=photovoltaic_power_output_series.series,
            list_extra_data_arrays=individual_series,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle="Photovoltaic Power Output Series",
            title="Photovoltaic power output from multiple surfaces",
            label="Sum of Photovoltaic Power",
            extra_legend_labels=individual_labels,
            unit=POWER_UNIT,
            terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print.fingerprint import print_finger_hash

        print_finger_hash(dictionary=photovoltaic_power_output_series.components)
    if metadata:
        import click

        from pvgisprototype.cli.print.metadata import print_command_metadata

        print_command_metadata(context=click.get_current_context())
    # Call write_irradiance_csv() last : it modifies the input dictionary !
    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv

        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=photovoltaic_power_output_series.components,
            filename=csv,
            index=index,
        )
