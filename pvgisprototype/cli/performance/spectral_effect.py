# From PVGIS 5.x -------------------------------------------------------------
# from pvgisprototype.algorithms.pvis.spectral_factor import (
#     # calculate_minimum_spectral_mismatch,
#     calculate_spectral_factor,
# )
#
# def spectral_mismatch(  # series ?
#     response_wavelengths,
#     spectral_response,
#     number_of_junctions: int,
#     spectral_power_density,  # =spectral_power_density_up_to_1050,
# ):
#     """ """
#     (
#         minimum_spectral_mismatch,
#         minimum_junction,
#     ) = calculate_minimum_spectral_mismatch(
#         response_wavelengths=response_wavelengths,
#         spectral_response=spectral_response,
#         number_of_junctions=number_of_junctions,
#         spectral_power_density=spectral_power_density,
#     )

# def spectral_factor(
#     minimum_spectral_mismatch,
#     global_total_power,
#     standard_conditions_response,
# ):  # series ?
#     """ """
#     spectral_factor = calculate_spectral_factor(
#         minimum_spectral_mismatch=minimum_spectral_mismatch,
#         global_total_power=global_total_power,
#         standard_conditions_response=standard_conditions_response,
#     )
#
#     return spectral_factor
#

"""
Calculate the spectral factor
"""

from rich.progress import Progress, SpinnerColumn, TextColumn
from pvgisprototype.api.series.hardcodings import check_mark, exclamation_mark, x_mark
from pvgisprototype.api.spectrum.constants import MAX_WAVELENGTH, MIN_WAVELENGTH
import typer
from pvgisprototype.api.spectrum.models import (
    PhotovoltaicModuleSpectralResponsivityModel,
    SpectralMismatchModel,
)
from pvgisprototype.api.spectrum.spectral_effect import calculate_spectral_factor
from pvgisprototype.cli.typer.log import typer_option_log
from datetime import datetime
from pandas import DataFrame, DatetimeIndex
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pathlib import Path
from typing import Annotated, List
from pvgisprototype.cli.typer.plot import (
    typer_option_uniplot,
    typer_option_uniplot_terminal_width,
)
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
)
from pvgisprototype.cli.typer.time_series import (
    typer_option_in_memory,
    typer_option_mask_and_scale,
    typer_option_nearest_neighbor_lookup,
    typer_option_tolerance,
)
from pvgisprototype.constants import (
    WAVELENGTHS_CSV_COLUMN_NAME_DEFAULT,
    SPECTRAL_RESPONSIVITY_CSV_COLUMN_NAME_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
    ANALYSIS_FLAG_DEFAULT,
    CSV_PATH_DEFAULT,
    FINGERPRINT_FLAG_DEFAULT,
    SPECTRAL_FACTOR_COLUMN_NAME,
    QUIET_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    METADATA_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    TOLERANCE_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
)
from pvgisprototype.cli.typer.irradiance import (
    typer_option_minimum_spectral_irradiance_wavelength,
    typer_option_maximum_spectral_irradiance_wavelength,
    typer_argument_spectrally_resolved_irradiance,
)
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
    typer_option_multi_thread,
)
from pvgisprototype.cli.typer.spectral_responsivity import (
    # typer_argument_spectral_responsivity,
    typer_option_photovoltaic_module_type,
    typer_option_spectral_responsivity_pandas,
    typer_option_integrate_spectral_responsivity,
    typer_option_responsivity_column_name,
    typer_option_wavelength_column_name,
)
from pvgisprototype.cli.typer.spectral_factor import typer_option_spectral_factor_model
from pvgisprototype.cli.typer.spectrum import (
    typer_option_reference_spectrum,
    typer_option_integrate_reference_spectrum,
)
from pvgisprototype import SpectralResponsivity, SolarIrradianceSpectrum
from pvgisprototype.cli.typer.output import (
    typer_option_csv,
)
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.data.spectral_responsivity import (
    SPECTRAL_RESPONSIVITY_DATA,
)
from pvgisprototype.cli.typer.output import (
    typer_option_command_metadata,
    typer_option_csv,
    typer_option_fingerprint,
    typer_option_index,
    typer_option_rounding_places,
)
from pvgisprototype.cli.typer.statistics import (
    typer_option_analysis,
    typer_option_statistics,
)
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_timestamps,
    typer_option_end_time,
    typer_option_frequency,
    typer_option_periods,
    typer_option_random_timestamps,
    typer_option_start_time,
    typer_option_timezone,
)
from pvgisprototype.cli.typer.location import (
    typer_argument_elevation,
    typer_argument_latitude_in_degrees,
    typer_argument_longitude_in_degrees,
)
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.cli.typer.time_series import (
    typer_option_data_variable,
)


@log_function_call
def spectral_factor(
    irradiance: Annotated[
        Path,
        typer_argument_spectrally_resolved_irradiance,
    ],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(
        now_utc_datetimezone()
    ),
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
    timezone: Annotated[str | None, typer_option_timezone] = None,
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    responsivity: Annotated[
        SpectralResponsivity,
        typer_option_spectral_responsivity_pandas,
    ] = SPECTRAL_RESPONSIVITY_DATA,  # Accept also list of float values ?
    integrate_responsivity: Annotated[
        bool,
        typer_option_integrate_spectral_responsivity,
    ] = False,
    responsivity_column: Annotated[
        str,
        typer_option_responsivity_column_name,
    ] = SPECTRAL_RESPONSIVITY_CSV_COLUMN_NAME_DEFAULT,
    wavelength_column: Annotated[
        str,
        typer_option_wavelength_column_name,
    ] = WAVELENGTHS_CSV_COLUMN_NAME_DEFAULT,
    photovoltaic_module_type: Annotated[
        List[PhotovoltaicModuleSpectralResponsivityModel],
        typer_option_photovoltaic_module_type,
    ] = [PhotovoltaicModuleSpectralResponsivityModel.cSi],
    spectrally_resolved_irradiance: Annotated[str, typer_option_data_variable] = "",
    average_irradiance_density: Annotated[str, typer_option_data_variable] = "",
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    limit_spectral_range: Annotated[
        bool,
        typer.Option(
            help="Limit the spectral range of the irradiance input data. Default for `spectral_factor_model = Pelland`"
        ),
    ] = False,
    min_wavelength: Annotated[
        float, typer_option_minimum_spectral_irradiance_wavelength
    ] = MIN_WAVELENGTH,
    max_wavelength: Annotated[
        float, typer_option_maximum_spectral_irradiance_wavelength
    ] = MAX_WAVELENGTH,
    reference_spectrum: Annotated[
        None | DataFrame,
        typer_option_reference_spectrum,
    ] = None,  # AM15G_IEC60904_3_ED4,
    integrate_reference_spectrum: Annotated[
        bool,
        typer_option_integrate_reference_spectrum,
    ] = False,
    spectral_factor_model: Annotated[
        List[SpectralMismatchModel], typer_option_spectral_factor_model
    ] = [SpectralMismatchModel.pvlib],
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    multi_thread: Annotated[
        bool, typer_option_multi_thread
    ] = MULTI_THREAD_FLAG_DEFAULT,
    rounding_places: Annotated[
        int, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    analysis: Annotated[bool, typer_option_analysis] = ANALYSIS_FLAG_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    show_footer: Annotated[bool, typer.Option(help="Show output table footer")] = True,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
):
    """ """
    # Ugly Hacks ! -----------------------------------------------------------
    from pvgisprototype.api.position.models import select_models

    photovoltaic_module_type = select_models(
        PhotovoltaicModuleSpectralResponsivityModel, photovoltaic_module_type
    )  # Using a callback fails!

    # ------------------------------------------------------------------------
    def is_netcdf(file_path: Path) -> bool:
        return file_path.suffix in {".nc", ".netcdf"}

    if is_netcdf(irradiance):
        # irradiance = (
        #     select_time_series(
        #         time_series=irradiance,
        #         longitude=longitude,
        #         latitude=latitude,
        #         timestamps=timestamps,
        #         neighbor_lookup=neighbor_lookup,
        #         tolerance=tolerance,
        #         mask_and_scale=mask_and_scale,
        #         in_memory=in_memory,
        #         verbose=verbose,
        #         log=log,
        #     )
        #     .to_numpy()
        #     .astype(dtype=dtype)
        # )
        spectrally_resolved_irradiance = select_time_series(
            time_series=irradiance,
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            variable=spectrally_resolved_irradiance,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            mask_and_scale=mask_and_scale,
            in_memory=in_memory,
            verbose=verbose,
            log=log,
        )
        if (
            SpectralMismatchModel.mihaylov in spectral_factor_model
            or SpectralMismatchModel.pvlib in spectral_factor_model
        ):
            logger.debug(
                f"Average irradiance density :\n{average_irradiance_density}",
                alt=f"[bold]Average irradiance density[/bold] :\n{average_irradiance_density}",
            )
            if average_irradiance_density:
                average_irradiance_density = select_time_series(
                    time_series=irradiance,
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    variable=average_irradiance_density,
                    neighbor_lookup=neighbor_lookup,
                    tolerance=tolerance,
                    mask_and_scale=mask_and_scale,
                    in_memory=in_memory,
                    verbose=verbose,
                    log=log,
                )

            # # Ugly Hack! --------------------------------------------------- #
            # if not isinstance(average_irradiance_density, DataArray) and isinstance(spectrally_resolved_irradiance, DataArray):
            #     spectrally_resolved_irradiance = spectrally_resolved_irradiance.rename(
            #         {wavelength_column: "wavelength"}
            #     )
            # # Ugly Hack! --------------------------------------------------- #

    if limit_spectral_range:
        import numpy

        if numpy.any(
            numpy.logical_or(
                irradiance[wavelength_column] < min_wavelength,
                irradiance[wavelength_column] > max_wavelength,
            )
        ):
            logger.debug(
                f"{check_mark} The input irradiance wavelengths are within the reference range [{min_wavelength}, {max_wavelength}]."
            )
        else:
            logger.warning(
                f"{x_mark} The input irradiance wavelengths exceed the reference range [{min_wavelength}, {max_wavelength}]. Filtering..."
            )
            irradiance = irradiance.sel(
                center_wavelength=numpy.logical_and(
                    irradiance[wavelength_column] > min_wavelength,
                    irradiance[wavelength_column] < max_wavelength,
                )
            )
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Calculating spectral factor...", total=None)
        spectral_factor_series = calculate_spectral_factor(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            timestamps=timestamps,
            timezone=timezone,
            irradiance=spectrally_resolved_irradiance,
            average_irradiance_density=average_irradiance_density,
            responsivity=responsivity,
            photovoltaic_module_type=photovoltaic_module_type,
            reference_spectrum=reference_spectrum,
            integrate_reference_spectrum=integrate_reference_spectrum,
            spectral_factor_models=spectral_factor_model,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )
    # longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    # latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print.spectral_factor import print_spectral_factor

            print_spectral_factor(
                timestamps=timestamps,
                spectral_factor_container=spectral_factor_series.components,
                spectral_factor_model=spectral_factor_model,
                photovoltaic_module_type=photovoltaic_module_type,
                # include_statistics=statistics,
                title="Spectral Factor",
                verbose=verbose,
                index=index,
                show_footer=show_footer,
            )
        else:
            spectral_factor_dictionary = {}
            for model in spectral_factor_model:
                for module_type in photovoltaic_module_type:
                    mismatch_data = (
                        spectral_factor_series.components.get(model)
                        .get(module_type)
                        .get(SPECTRAL_FACTOR_COLUMN_NAME)
                    )
                    if isinstance(mismatch_data, memoryview):
                        import numpy

                        mismatch_data = (numpy.array(mismatch_data).values.flatten(),)
                    # # ------------------------- Better handling of rounding vs dtype ?
                    #     from pvgisprototype.api.utilities.conversions import round_float_values
                    #     mismatch_data = round_float_values(
                    #                 mismatch_data,
                    #             rounding_places,
                    #         ).astype(str)
                    # # ------------------------- Better handling of rounding vs dtype ?
                    spectral_factor_dictionary[module_type.name] = mismatch_data

                header = ", ".join(spectral_factor_dictionary.keys())
                print(header)

                # mismatch_values = ", ".join(mismatch_data.astype(str))
                # print(f'{module_type.name}, {mismatch_values}')

                # maximum length of mismatch data to properly format rows
                max_length = max([len(v) for v in spectral_factor_dictionary.values()])

                # Print each row of mismatch values, transposing the values
                for i in range(max_length):
                    row = []
                    for module_type in spectral_factor_dictionary:
                        if i < len(spectral_factor_dictionary[module_type]):
                            row.append(
                                f"{spectral_factor_dictionary[module_type][i]:.6f}"
                            )
                        else:
                            row.append("")  # Handle cases where lengths are uneven
                    print(", ".join(row))

    if csv:
        from pvgisprototype.cli.write import write_spectral_factor_csv

        write_spectral_factor_csv(
            longitude=None,
            latitude=None,
            timestamps=timestamps,
            spectral_factor_dictionary=spectral_factor_series.components,
            filename=csv,
            index=index,
        )
    if statistics:
        from pvgisprototype.api.series.statistics import (
            print_spectral_factor_statistics,
        )

        print_spectral_factor_statistics(
            spectral_factor=spectral_factor_series.components,
            spectral_factor_model=spectral_factor_model,
            photovoltaic_module_type=photovoltaic_module_type,
            timestamps=timestamps,
            # groupby=groupby,
            title="Spectral Factor Statistics",
            rounding_places=rounding_places,
            verbose=verbose,
            show_footer=show_footer,
        )
    # if analysis:
    #     from pvgisprototype.cli.print import print_change_percentages_panel

    #     print_change_percentages_panel(
    #         longitude=longitude,
    #         latitude=latitude,
    #         elevation=elevation,
    #         timestamps=timestamps,
    #         dictionary=photovoltaic_power_output_series.components,
    #         # title=photovoltaic_power_output_series['Title'] + f" series {POWER_UNIT}",
    #         rounding_places=1,  # minimalism
    #         index=index,
    #         surface_orientation=True,
    #         surface_tilt=True,
    #         fingerprint=fingerprint,
    #         verbose=verbose,
    #     )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_spectral_factor_series

        uniplot_spectral_factor_series(
            spectral_factor_dictionary=spectral_factor_series.value,
            spectral_factor_model=spectral_factor_model,
            photovoltaic_module_type=photovoltaic_module_type,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            # lines=True,
            # supertitle="Spectral Mismatch Factor",
            supertitle=spectral_factor_series.supertitle,
            # title="Spectral Factor",
            title=spectral_factor_series.title,
            # label=photovoltaic_module_types,
            # label=spectral_factor_series.label,
            # extra_legend_labels=None,
            # unit='',
            terminal_width_fraction=terminal_width_fraction,
        )
    if metadata:
        import click

        from pvgisprototype.cli.print import print_command_metadata

        print_command_metadata(context=click.get_current_context())
    if fingerprint and not analysis:
        from pvgisprototype.cli.print.fingerprint import print_finger_hash

        print_finger_hash(dictionary=spectral_factor_series.presentation)
