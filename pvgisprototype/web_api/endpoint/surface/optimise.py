from pvgisprototype.web_api.cache.redis import USE_REDIS_CACHE
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.web_api.cache.caching import custom_cached
from pvgisprototype.log import logger
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel

from typing import Annotated
from urllib.parse import quote

from fastapi import Depends
from fastapi.responses import ORJSONResponse, Response
from pandas import DatetimeIndex

from pvgisprototype.api.quick_response_code import (
    QuickResponseCode,
    generate_quick_response_code_optimal_surface_position,
)
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerModeWithoutNone,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.web_api.dependency.dependable import (
    fastapi_dependable_angle_output_units,
    fastapi_dependable_common_datasets,
    fastapi_dependable_convert_timestamps,
    fastapi_dependable_fingerprint,
    fastapi_dependable_latitude,
    fastapi_dependable_longitude,
    process_optimise_surface_position,
)
from pvgisprototype.web_api.dependency.surface import process_surface_position_optimisation_method
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_csv,
    fastapi_query_elevation,
    fastapi_query_quick_response_code,
    fastapi_query_surface_position_optimisation_mode,
)
from pvgisprototype.web_api.schemas import AngleOutputUnit
from pvgisprototype.api.surface.positioning import optimise_surface_position
from typing import Annotated
from fastapi import Depends, HTTPException
from pvgisprototype import (
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.api.position.models import (
    ShadingModel,
)
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.surface.positioning import optimise_surface_position
from pvgisprototype.constants import (
    FINGERPRINT_FLAG_DEFAULT,
    NUMBER_OF_ITERATIONS_DEFAULT,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_albedo,
    fastapi_query_apply_reflectivity_factor,
    fastapi_query_csv,
    fastapi_query_eccentricity_correction_factor,
    fastapi_query_eccentricity_phase_offset,
    fastapi_query_efficiency,
    fastapi_query_elevation,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_end_time,
    fastapi_query_in_memory,
    fastapi_query_iterations,
    fastapi_query_mask_and_scale,
    fastapi_query_neighbor_lookup,
    fastapi_query_number_of_samping_points,
    fastapi_query_peak_power,
    fastapi_query_periods,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_power_model,
    fastapi_query_quick_response_code,
    fastapi_query_radiation_cutoff_threshold,
    fastapi_query_shgo_sampling_method,
    fastapi_query_solar_constant,
    fastapi_query_solar_time_model,
    fastapi_query_start_time,
    fastapi_query_statistics,
    fastapi_query_surface_position_optimisation_method,
    fastapi_query_surface_position_optimisation_mode,
    fastapi_query_system_efficiency,
    fastapi_query_temperature_model,
    fastapi_query_tolerance,
    fastapi_query_zero_negative_solar_incidence_angle,
)
from pvgisprototype.web_api.schemas import (
    Frequency,
    Timezone,
)
from pvgisprototype.web_api.dependency.common_datasets import (
    process_timestamps,
    _read_datasets,
    convert_timestamps_to_specified_timezone,
)
from pvgisprototype.web_api.dependency.location import (
    process_longitude,
    process_latitude,
)
from pvgisprototype.web_api.dependency.position import (
    process_surface_orientation,
    process_surface_tilt,
)
from pvgisprototype.web_api.dependency.time import (
    process_frequency,
    process_timezone,
    process_timezone_to_be_converted,
)
from pvgisprototype.web_api.dependency.shading import (
    process_shading_model,
)
from pvgisprototype.web_api.dependency.meteorology import (
    process_linke_turbidity_factor_series,
)
from pvgisprototype.web_api.dependency.fingerprint import (
    process_fingerprint,
)
from pvgisprototype.algorithms.huld.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)

from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    ECCENTRICITY_PHASE_OFFSET,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    NUMBER_OF_ITERATIONS_DEFAULT,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    PEAK_POWER_DEFAULT,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_OUTPUT_FILENAME,
    QUIET_FLAG_DEFAULT,
    RADIATION_CUTOFF_THRESHHOLD,
    ROUNDING_PLACES_DEFAULT,
    SOLAR_CONSTANT,
    STATISTICS_FLAG_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.web_api.dependency.dependable import (
    fastapi_dependable_angle_output_units,
    fastapi_dependable_common_datasets,
    fastapi_dependable_convert_timestamps,
    fastapi_dependable_convert_timezone,
    fastapi_dependable_fingerprint,
    fastapi_dependable_frequency,
    fastapi_dependable_groupby,
    fastapi_dependable_latitude,
    fastapi_dependable_linke_turbidity_factor_series,
    fastapi_dependable_longitude,
    fastapi_dependable_optimise_surface_position,
    fastapi_dependable_quiet,
    fastapi_dependable_read_datasets,
    fastapi_dependable_shading_model,
    fastapi_dependable_solar_incidence_models,
    fastapi_dependable_solar_position_model,
    fastapi_dependable_surface_orientation,
    fastapi_dependable_surface_tilt,
    fastapi_dependable_timestamps,
    fastapi_dependable_timezone,
    fastapi_dependable_verbose,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_albedo,
    fastapi_query_apply_reflectivity_factor,
    fastapi_query_csv,
    fastapi_query_eccentricity_correction_factor,
    fastapi_query_efficiency,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_in_memory,
    fastapi_query_mask_and_scale,
    fastapi_query_neighbor_lookup,
    fastapi_query_peak_power,
    fastapi_query_eccentricity_phase_offset,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_power_model,
    fastapi_query_quick_response_code,
    fastapi_query_radiation_cutoff_threshold,
    fastapi_query_solar_constant,
    fastapi_query_solar_time_model,
    fastapi_query_start_time,
    fastapi_query_statistics,
    fastapi_query_system_efficiency,
    fastapi_query_temperature_model,
    fastapi_query_tolerance,
    fastapi_query_zero_negative_solar_incidence_angle,
)
from pvgisprototype.web_api.schemas import (
    # AnalysisLevel,
    AngleOutputUnit,
    Frequency,
    GroupBy,
    Timezone,
)

@custom_cached
async def get_optimised_surface_position(
    common_datasets: Annotated[dict, fastapi_dependable_common_datasets],
    _read_datasets: Annotated[dict, Depends(_read_datasets)],
    # optimal_surface_position: Annotated[
    #     dict,
    #     Depends(
    #         process_optimise_surface_position
    #     ),  # NOTE This dependency is used to get the optimal position
    # ],
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        float, Depends(process_surface_orientation)
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float, Depends(process_surface_tilt)
    ] = SURFACE_TILT_DEFAULT,
    start_time: Annotated[str | None, fastapi_query_start_time] = "2013-01-01",
    periods: Annotated[int | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = "2013-12-31",
    timestamps: Annotated[str | None, Depends(process_timestamps)] = None,
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
    timezone_for_calculations: Annotated[
        Timezone, fastapi_dependable_convert_timezone
    ] = Timezone.UTC,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    neighbor_lookup: Annotated[
        MethodForInexactMatches, fastapi_query_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float, fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, fastapi_query_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[
        float | LinkeTurbidityFactor, Depends(process_linke_turbidity_factor_series)
    ] = LinkeTurbidityFactor(),
    albedo: Annotated[float, fastapi_query_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, fastapi_query_apply_reflectivity_factor
    ] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, fastapi_dependable_solar_position_model
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, fastapi_dependable_solar_incidence_models
    ] = SolarIncidenceModel.iqbal,
    shading_model: Annotated[
        ShadingModel, Depends(process_shading_model)
    ] = ShadingModel.pvgis,
    zero_negative_solar_incidence_angle: Annotated[
        bool, fastapi_query_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[
        SolarTimeModel, fastapi_query_solar_time_model
    ] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[
            float, fastapi_query_solar_constant
    ] = SOLAR_CONSTANT,
    eccentricity_phase_offset: Annotated[
            float, fastapi_query_eccentricity_phase_offset
    ] = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: Annotated[
        float, fastapi_query_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    peak_power: Annotated[float, fastapi_query_peak_power] = PEAK_POWER_DEFAULT,
    system_efficiency: Annotated[
        float, fastapi_query_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, fastapi_query_power_model
    ] = PhotovoltaicModulePerformanceModel.king,
    radiation_cutoff_threshold: Annotated[
        float, fastapi_query_radiation_cutoff_threshold
    ] = RADIATION_CUTOFF_THRESHHOLD,
    temperature_model: Annotated[
        ModuleTemperatureAlgorithm,
        fastapi_query_temperature_model,
    ] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[
        float | None, fastapi_query_efficiency
    ] = EFFICIENCY_FACTOR_DEFAULT,
    surface_position_optimisation_mode: Annotated[
        SurfacePositionOptimizerMode, fastapi_query_surface_position_optimisation_mode
    ] = SurfacePositionOptimizerMode.Tilt,
    surface_position_optimisation_method: Annotated[
        SurfacePositionOptimizerMethod,
        Depends(process_surface_position_optimisation_method),
    ] = SurfacePositionOptimizerMethod.l_bfgs_b,
    shgo_sampling_method: Annotated[
        SurfacePositionOptimizerMethodSHGOSamplingMethod,
        fastapi_query_shgo_sampling_method,
    ] = SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
    number_of_sampling_points: Annotated[
        int, fastapi_query_number_of_samping_points
    ] = NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    iterations: Annotated[int, fastapi_query_iterations] = NUMBER_OF_ITERATIONS_DEFAULT,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    # log: Annotated[int, fastapi_query_log] = LOG_LEVEL_DEFAULT,
    # profile: Annotated[bool, fastapi_query_profiling] = cPROFILE_FLAG_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.NoneValue,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    quiet: Annotated[bool, fastapi_dependable_quiet] = QUIET_FLAG_DEFAULT,
    # fingerprint: Annotated[
    #     bool, Depends(process_fingerprint)
    # ] = FINGERPRINT_FLAG_DEFAULT,
    fingerprint: Annotated[
        bool, fastapi_dependable_fingerprint
    ] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    optimise_surface_position: Annotated[
        SurfacePositionOptimizerMode, fastapi_dependable_optimise_surface_position
    ] = SurfacePositionOptimizerMode.NoneValue,
    # user_requested_timestamps: Annotated[
    #     None, Depends(convert_timestamps_to_specified_timezone)
    # ] = None,
    user_requested_timestamps: Annotated[
        DatetimeIndex | None, fastapi_dependable_convert_timestamps
    ] = None,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
):
    """Estimate the optimal positioning of a solar surface (Orientation, Tilt or Orientation & Tilt), optionally for various technologies, at a specific location and a period in time.

    # Features

    - A symbol nomenclature for easy identification of quantities, units, and more -- see [Symbols](https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/cli/symbols/)
    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html)
    - Valid time zone identifiers from [the IANA Time Zone Database](https://www.iana.org/time-zones)
    - Surface position optimisation supported by [SciPy](https://docs.scipy.org/doc/scipy/reference/optimize.html)
    - Get from simple to detailed output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)

    ## **Important Notes**

    - The default time, if not given, regardless of the `frequency` is
      `00:00:00`. It is then expected to get `0` incoming solar irradiance and
      subsequently photovoltaic power/energy output.

    - Of the four parameters `start_time`, `end_time`, `periods`, and
      `frequency`, exactly three must be specified. If `frequency` is omitted,
      the resulting timestamps (a Pandas `DatetimeIndex` object)
      will have `periods` linearly spaced elements between `start_time` and
      `end_time` (closed on both sides). Learn more about frequency strings at
      [Offset aliases](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).

    # Algorithms & Models

    - Solar radiation model by Hofierka, 2002
    - Photovoltaic efficiency coefficients by ESTI, C2, JRC, European Commission
    - Solar positioning based on NOAA's solar geometry equations
    - Reflectivity effect as a function of the solar incidence angle by Martin and Ruiz, 2005
    - Spectal mismatch effect by Huld, 2011
    - Overall system efficiency pre-set to 0.86, in other words 14% of loss for material degradation, aging, etc.

    # Input data

    This function consumes internally :

    - time series data limited to the period **2005** - **2023**.
    - solar irradiance from the [SARAH3 climate records](https://wui.cmsaf.eu/safira/action/viewDoiDetails?acronym=SARAH_V003)
    - temperature and wind speed estimations from [ERA5 Reanalysis](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) collection
    - spectral effect factor time series (Huld, 2011) _for the reference year 2013_
    """
    if surface_position_optimisation_mode == SurfacePositionOptimizerMode.NoneValue:
        return {}

    else:
        optimal_surface_position, _optimal_surface_position = optimise_surface_position(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            #
            surface_orientation=surface_orientation,
            min_surface_orientation=SurfaceOrientation().min_radians,
            max_surface_orientation=SurfaceOrientation().max_radians,
            # min_surface_orientation=min_surface_orientation,
            # max_surface_orientation=max_surface_orientation,
            surface_tilt=surface_tilt,
            min_surface_tilt=SurfaceTilt().min_radians,
            max_surface_tilt=SurfaceTilt().max_radians,
            # min_surface_tilt=min_surface_tilt,
            # max_surface_tilt=max_surface_tilt,
            #
            timestamps=timestamps,
            # timezone=timezone,
            timezone=timezone_for_calculations,  # type: ignore
            #
            global_horizontal_irradiance=_read_datasets[
                "global_horizontal_irradiance_series"
            ],
            direct_horizontal_irradiance=_read_datasets[
                "direct_horizontal_irradiance_series"
            ],
            temperature_series=_read_datasets["temperature_series"],
            wind_speed_series=_read_datasets["wind_speed_series"],
            spectral_factor_series=_read_datasets["spectral_factor_series"],
            #
            photovoltaic_module=photovoltaic_module,
            #
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            # adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            # refracted_solar_zenith=refracted_solar_zenith,
            albedo=albedo,
            apply_reflectivity_factor=apply_reflectivity_factor,
            #
            solar_position_model=solar_position_model,
            # sun_horizon_position=sun_horizon_position,
            solar_incidence_model=solar_incidence_model,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            solar_time_model=solar_time_model,
            #
            solar_constant=solar_constant,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            #
            horizon_profile=_read_datasets["horizon_profile"],
            shading_model=shading_model,
            # shading_states=shading_states,
            #
            peak_power=peak_power,
            system_efficiency=system_efficiency,
            power_model=power_model,
            temperature_model=temperature_model,
            efficiency=efficiency,
            #
            mode=surface_position_optimisation_mode,
            method=surface_position_optimisation_method,
            number_of_sampling_points=number_of_sampling_points,
            iterations=iterations,
            # precision_goal=precision_goal,
            shgo_sampling_method=shgo_sampling_method,
            #
            # workers=workers,
            angle_output_units=angle_output_units,
            # dtype=dtype,
            # array_backend=array_backend,
            verbose=verbose,
            # log=log,
            fingerprint=fingerprint,
            # profile=profile,
        )

        if (optimal_surface_position["Surface Tilt"] is None) or (  # type: ignore
            optimal_surface_position["Surface Orientation"] is None  # type: ignore
        ):
            raise HTTPException(
                status_code=400,
                detail="Using combination of input could not find optimal surface position",
            )

        from devtools import debug
        logger.debug(_optimal_surface_position)
        print(_optimal_surface_position)

        # return optimal_surface_position  # type: ignore

    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------

    if csv:
        from fastapi.responses import StreamingResponse

        print(optimal_surface_position)

        csv_content = ",".join(["Surface Orientation", "Surface Tilt"]) + "\n"
        csv_content += f"{convert_float_to_degrees_if_requested(optimal_surface_position['Surface Orientation'].value, angle_output_units)},{convert_float_to_degrees_if_requested(optimal_surface_position['Surface Tilt'].value, angle_output_units)}"
        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={quote(csv)}"},
        )

        return response_csv

    response: dict = {}
    headers = {
        "Content-Disposition": 'attachment; filename="pvgis_optimal_solar_surface_position.json"'
    }

    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = optimal_surface_position[  # type: ignore
            FINGERPRINT_COLUMN_NAME
        ]

    if quick_response_code.value != QuickResponseCode.NoneValue:
        quick_response = generate_quick_response_code_optimal_surface_position(
            dictionary=optimal_surface_position,
            longitude=longitude,  # type: ignore
            latitude=latitude,  # type: ignore
            elevation=elevation,  # type: ignore
            surface_orientation=True,
            surface_tilt=True,
            timestamps=user_requested_timestamps,
            rounding_places=ROUNDING_PLACES_DEFAULT,
            output_type=quick_response_code,
        )

        if quick_response_code.value == QuickResponseCode.Base64:
            response["QR"] = f"data:image/png;base64,{quick_response}"  # type: ignore
        elif quick_response_code.value == QuickResponseCode.Image:
            from io import BytesIO

            buffer = BytesIO()
            image = quick_response.make_image()  # type: ignore
            image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            return Response(content=image_bytes, media_type="image/png")

    response["Optimal Surface Position"] = {
        "Surface orientation": convert_float_to_degrees_if_requested(
            optimal_surface_position["Surface Orientation"].value, angle_output_units
        ),
        "Surface tilt": convert_float_to_degrees_if_requested(
            optimal_surface_position["Surface Tilt"].value, angle_output_units
        ),
    }

    return ORJSONResponse(response, headers=headers, media_type="application/json")
