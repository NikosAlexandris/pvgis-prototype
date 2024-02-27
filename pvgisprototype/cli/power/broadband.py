from typing import Annotated
from typing import List
from typing import Optional
from datetime import datetime
from pathlib import Path
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.cli.print import print_irradiance_table_2
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.cli.write import write_irradiance_csv
from pvgisprototype.api.geometry.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.api.geometry.models import SolarIncidenceModel
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithm
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.irradiance.power import calculate_photovoltaic_power_output_series
from pvgisprototype.algorithms.pvis.constants import MINIMUM_SPECTRAL_MISMATCH
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_horizon_heights
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype import TemperatureSeries
from pvgisprototype.cli.typer_parameters import typer_argument_temperature_series
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype import WindSpeedSeries
from pvgisprototype.cli.typer_parameters import typer_argument_wind_speed_series
from pvgisprototype.cli.typer_parameters import typer_option_albedo
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_efficiency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_periods
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_groupby
from pvgisprototype.cli.typer_parameters import typer_option_global_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_pv_power_algorithm
from pvgisprototype.cli.typer_parameters import typer_option_module_temperature_algorithm
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_option_system_efficiency
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.cli.typer_parameters import typer_option_uniplot
from pvgisprototype.cli.typer_parameters import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.cli.typer_parameters import typer_option_profiling
from pvgisprototype.cli.typer_parameters import typer_option_index
from pvgisprototype.constants import ALBEDO_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import EFFICIENCY_DEFAULT
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from pvgisprototype.constants import POWER_UNIT
from pvgisprototype.constants import ENERGY_UNIT
from pvgisprototype.constants import LINKE_TURBIDITY_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SYSTEM_EFFICIENCY_DEFAULT
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype import LinkeTurbidityFactor
from rich import print

from pandas import DatetimeIndex


def photovoltaic_power_output_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[Optional[DatetimeIndex], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    periods: Annotated[Optional[int], typer_option_periods] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_time_series: bool = False,
    global_horizontal_irradiance: Annotated[Optional[Path], typer_option_global_horizontal_irradiance] = None,
    direct_horizontal_irradiance: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    temperature_series: Annotated[TemperatureSeries, typer_argument_temperature_series] = TEMPERATURE_DEFAULT,
    wind_speed_series: Annotated[WindSpeedSeries, typer_argument_wind_speed_series] = WIND_SPEED_DEFAULT,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    dtype = 'float64',
    array_backend = 'NUMPY',
    surface_tilt: Annotated[Optional[float], typer_option_surface_tilt] = SURFACE_TILT_DEFAULT,
    surface_orientation: Annotated[Optional[float], typer_option_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[Optional[float], typer_option_albedo] = ALBEDO_DEFAULT,
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModel, typer_option_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[SolarIncidenceModel, typer_option_solar_incidence_model] = SolarIncidenceModel.jenco,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    # horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
    system_efficiency: Annotated[Optional[float], typer_option_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[PVModuleEfficiencyAlgorithm, typer_option_pv_power_algorithm] = PVModuleEfficiencyAlgorithm.king,
    temperature_model: Annotated[ModuleTemperatureAlgorithm, typer_option_module_temperature_algorithm] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[Optional[float], typer_option_efficiency] = None,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    statistics: Annotated[bool, typer_option_statistics] = False,
    groupby: Annotated[Optional[str], typer_option_groupby] = None,
    csv: Annotated[Path, typer_option_csv] = None,
    uniplot: Annotated[bool, typer_option_uniplot] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = False,
    profile: Annotated[bool, typer_option_profiling] = False,
):
    """
    Estimate the photovoltaic power over a time series or an arbitrarily
    aggregated energy production of a PV system connected to the electricity
    grid (without battery storage) based on broadband solar irradiance, ambient
    temperature and wind speed.
    """
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        periods=periods,
        frequency=frequency,
        timezone=timezone,
        random_time_series=random_time_series,
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        dtype=dtype,
        array_backend=array_backend,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
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
        # horizon_heights=horizon_heights,
        system_efficiency=system_efficiency,
        power_model=power_model,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
        profile=profile,
    )

    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if verbose > 0:
        print_irradiance_table_2(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=photovoltaic_power_output_series,
            title=photovoltaic_power_output_series['Title'] + f" series {POWER_UNIT}",
            rounding_places=rounding_places,
            index=index,
            verbose=verbose,
        )
        if csv:
            write_irradiance_csv(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                dictionary=photovoltaic_power_output_series,
                filename=csv,
            )
    else:
        flat_list = photovoltaic_power_output_series.flatten().astype(str)
        csv_str = ','.join(flat_list)
        print(csv_str)

    if statistics:
        print_series_statistics(
            data_array=photovoltaic_power_output_series,
            timestamps=timestamps,
            groupby=groupby,
            title="Photovoltaic power output",
        )
    if uniplot:
        import os 
        terminal_columns, _ = os.get_terminal_size() # we don't need lines!
        terminal_length = int(terminal_columns * terminal_width_fraction)
        from functools import partial
        from uniplot import plot as default_plot
        plot = partial(default_plot, width=terminal_length)
        from pvgisprototype.api.series.hardcodings import exclamation_mark
        title="Photovoltaic power output"
        lines = True
        if isinstance(photovoltaic_power_output_series, float):
            print(f"{exclamation_mark} [red]Aborting[/red] as I [red]cannot[/red] plot the single float value {float}!")
            return
        import numpy as np
        if verbose > 0:
            photovoltaic_power_output_series = list(photovoltaic_power_output_series.values())[0]
        if isinstance(photovoltaic_power_output_series, np.ndarray):
            # supertitle = getattr(photovoltaic_power_output_series, 'long_name', 'Untitled')
            supertitle = 'Photovoltaic Power Output Series'
            # label = getattr(photovoltaic_power_output_series, 'name', None)
            label = 'Photovoltaic Power'
            # label_2 = getattr(photovoltaic_power_output_series_2, 'name', None) if photovoltaic_power_output_series_2 is not None else None
            # unit = getattr(photovoltaic_power_output_series, 'units', None)
            unit = POWER_UNIT
            plot(
                # xs=timestamps,
                # xs=photovoltaic_power_output_series,
                # ys=[photovoltaic_power_output_series, photovoltaic_power_output_series_2] if photovoltaic_power_output_series_2 is not None else photovoltaic_power_output_series,
                ys=photovoltaic_power_output_series,
                legend_labels=label,
                lines=lines,
                title=title if title else supertitle,
                y_unit=' ' + str(unit),
            )
