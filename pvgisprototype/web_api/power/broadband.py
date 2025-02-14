import math
from typing import Annotated
from urllib.parse import quote

from fastapi.responses import ORJSONResponse, PlainTextResponse, Response
from fastapi import Depends
from pandas import DatetimeIndex

from pvgisprototype import LinkeTurbidityFactor, SpectralFactorSeries
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
    ShadingModel,
)
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.api.power.broadband_multiple_surfaces import (
    calculate_photovoltaic_power_output_series_from_multiple_surfaces,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.quick_response_code import (
    QuickResponseCode,
    generate_quick_response_code,
)
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    PEAK_POWER_DEFAULT,
    PERIGEE_OFFSET,
    PHOTOVOLTAIC_PERFORMANCE_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_OUTPUT_FILENAME,
    QUIET_FLAG_DEFAULT,
    RADIATION_CUTOFF_THRESHHOLD,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
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
from pvgisprototype.web_api.dependencies import (
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
    fastapi_dependable_refracted_solar_zenith,
    fastapi_dependable_solar_incidence_models,
    fastapi_dependable_solar_position_models,
    fastapi_dependable_spectral_factor_series,
    fastapi_dependable_surface_orientation,
    fastapi_dependable_surface_orientation_list,
    fastapi_dependable_surface_tilt,
    fastapi_dependable_surface_tilt_list,
    fastapi_dependable_timestamps,
    fastapi_dependable_timezone,
    fastapi_dependable_verbose,
    fastapi_dependable_shading_model,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_albedo,
    fastapi_query_apply_atmospheric_refraction,
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
    fastapi_query_perigee_offset,
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
    AnalysisLevel,
    AngleOutputUnit,
    Frequency,
    GroupBy,
    Timezone,
)


async def get_photovoltaic_power_series_advanced(
    common_datasets: Annotated[dict, fastapi_dependable_common_datasets],
    _read_datasets: Annotated[
        dict, fastapi_dependable_read_datasets
    ],  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        float, fastapi_dependable_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float, fastapi_dependable_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[str | None, fastapi_dependable_timestamps] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = "2013-01-01",
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] =  "2013-12-31",
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    # global_horizontal_irradiance: Annotated[Path | None, fastapi_query_global_horizontal_irradiance] = None,
    # direct_horizontal_irradiance: Annotated[Path | None, fastapi_query_direct_horizontal_irradiance] = None,
    # temperature_series: Annotated[float, fastapi_query_temperature_series] = TEMPERATURE_DEFAULT,
    # temperature_series: Optional[TemperatureSeries] = fastapi_dependable_temperature_series,
    # wind_speed_series: Annotated[float, fastapi_query_wind_speed_series] = WIND_SPEED_DEFAULT,
    # wind_speed_series: Optional[WindSpeedSeries] = fastapi_dependable_wind_speed_series,
    #spectral_factor_series: Annotated[
    #    SpectralFactorSeries, fastapi_dependable_spectral_factor_series
    #] = None,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, fastapi_query_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float, fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, fastapi_query_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[
        float | LinkeTurbidityFactor, fastapi_dependable_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Annotated[
        bool, fastapi_query_apply_atmospheric_refraction
    ] = True,
    refracted_solar_zenith: Annotated[
        float, fastapi_dependable_refracted_solar_zenith
    ] = math.degrees(REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT),
    albedo: Annotated[float, fastapi_query_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, fastapi_query_apply_reflectivity_factor
    ] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, fastapi_dependable_solar_position_models
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, fastapi_dependable_solar_incidence_models
    ] = SolarIncidenceModel.iqbal,
    shading_model: Annotated[ShadingModel, fastapi_dependable_shading_model] = ShadingModel.pvis,    
    zero_negative_solar_incidence_angle: Annotated[
        bool, fastapi_query_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[
        SolarTimeModel, fastapi_query_solar_time_model
    ] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, fastapi_query_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, fastapi_query_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[
        float, fastapi_query_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
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
    # dtype: str = DATA_TYPE_DEFAULT,
    # array_backend: str = ARRAY_BACKEND_DEFAULT,
    # multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    # uniplot: Annotated[bool, fastapi_query_uniplot] = UNIPLOT_FLAG_DEFAULT,
    # terminal_width_fraction: Annotated[float, fastapi_query_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    # log: Annotated[int, fastapi_query_log] = LOG_LEVEL_DEFAULT,
    # profile: Annotated[bool, fastapi_query_profiling] = cPROFILE_FLAG_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.NoneValue,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    quiet: Annotated[bool, fastapi_dependable_quiet] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[
        bool, fastapi_dependable_fingerprint
    ] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    optimise_surface_position: Annotated[
        SurfacePositionOptimizerMode, fastapi_dependable_optimise_surface_position
    ] = SurfacePositionOptimizerMode.NoneValue,
    timezone_for_calculations: Annotated[
        Timezone, fastapi_dependable_convert_timezone
    ] = Timezone.UTC,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    user_requested_timestamps: Annotated[
        DatetimeIndex | None, fastapi_dependable_convert_timestamps
    ] = None,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
):
    """Estimate the photovoltaic power output for a solar surface.

    Estimate the photovoltaic power for a solar surface over a time series or
    an arbitrarily aggregated energy production of a PV system connected to the
    electricity grid (without battery storage) based on broadband solar
    irradiance, ambient temperature and wind speed.

    <span style="color:red"> <ins>**This Application Is a Feasibility Study**</ins></span>
    **limited to** longitudes ranging in [`7.5`, `10`] and latitudes in [`45`, `47.5`].

    # Features

    - A symbol nomenclature for easy identification of quantities, units, and more -- see [Symbols](https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/cli/symbols/)
    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html)
    - Valid time zone identifiers from [the IANA Time Zone Database](https://www.iana.org/time-zones)
    - Surface position optimisation supported by [SciPy](https://docs.scipy.org/doc/scipy/reference/optimize.html)
    - Get from simple to detailed output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)
    - Share a **QR-Code** with a summary of the analysis
    - **Fingerprint** your analysis
    - Document your analysis including all **input metadata**

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

    if optimise_surface_position:
        surface_orientation = optimise_surface_position["surface_orientation"].value  # type: ignore
        surface_tilt = optimise_surface_position["surface_tilt"].value  # type: ignore

    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        timestamps=timestamps,
        timezone=timezone_for_calculations,
        global_horizontal_irradiance=_read_datasets[
            "global_horizontal_irradiance_series"
        ],
        direct_horizontal_irradiance=_read_datasets[
            "direct_horizontal_irradiance_series"
        ],
        temperature_series=_read_datasets["temperature_series"],
        wind_speed_series=_read_datasets["wind_speed_series"],
        # spectral_factor_series=_read_datasets["spectral_factor_series"],
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        linke_turbidity_factor_series=linke_turbidity_factor_series,  # LinkeTurbidityFactor = LinkeTurbidityFactor(value = LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
        apply_reflectivity_factor=apply_reflectivity_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        horizon_profile=_read_datasets["horizon_profile"],
        shading_model=shading_model,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        photovoltaic_module=photovoltaic_module,
        peak_power=peak_power,
        system_efficiency=system_efficiency,
        power_model=power_model,
        radiation_cutoff_threshold=radiation_cutoff_threshold,
        temperature_model=temperature_model,
        efficiency=efficiency,
        # dtype=dtype,
        # array_backend=array_backend,
        # multi_thread=multi_thread,
        verbose=verbose,
        # log=verbose,
        fingerprint=fingerprint,
        # profile=profile,
    )
    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------

    if csv:
        from pvgisprototype.web_api.utilities import generate_photovoltaic_output_csv

        in_memory_csv = generate_photovoltaic_output_csv(
            dictionary=photovoltaic_power_output_series.components,
            latitude=latitude,
            longitude=longitude,
            timestamps=user_requested_timestamps,
            timezone=timezone,
        )  # type: ignore

        # Based on https://github.com/fastapi/fastapi/discussions/9049 since file is already in memory is faster to return it as PlainTextResponse
        response = PlainTextResponse(
            content=in_memory_csv,
            headers={"Content-Disposition": f"attachment; filename={quote(csv)}"},
            media_type="text/csv",
        )

        return response

    response: dict = {}  # type: ignore
    headers = {
        "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
    }

    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = photovoltaic_power_output_series.components[  # type: ignore
            FINGERPRINT_COLUMN_NAME
        ]

    if quick_response_code.value != QuickResponseCode.NoneValue:
        quick_response = generate_quick_response_code(
            dictionary=photovoltaic_power_output_series.components,
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
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

    if statistics:
        from numpy import atleast_1d, ndarray

        from pvgisprototype.api.statistics.xarray import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=user_requested_timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        converted_series_statistics = {
            key: atleast_1d(value) if isinstance(value, ndarray) else value
            for key, value in series_statistics.items()
        }  # NOTE Important since calculate_series_statistics returns scalars and ORJSON cannot serielise them
        response["Statistics"] = converted_series_statistics  # type: ignore

    if not quiet:
        if verbose > 0:
            response = photovoltaic_power_output_series.components
        else:
            response = {
                PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series.value,  # type: ignore
            }

    return ORJSONResponse(response, headers=headers, media_type="application/json")


async def get_photovoltaic_power_series(
    _read_datasets: Annotated[
        dict, fastapi_dependable_read_datasets
    ],  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        float, fastapi_dependable_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float, fastapi_dependable_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[str | None, fastapi_dependable_timestamps] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = "2013-01-01",
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = "2013-12-31",
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    shading_model: Annotated[ShadingModel, fastapi_dependable_shading_model] = ShadingModel.pvis,        
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    system_efficiency: Annotated[
        float, fastapi_query_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, fastapi_query_power_model
    ] = PhotovoltaicModulePerformanceModel.king,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    peak_power: Annotated[float, fastapi_query_peak_power] = PEAK_POWER_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.NoneValue,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    quiet: Annotated[bool, fastapi_dependable_quiet] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[
        bool, fastapi_dependable_fingerprint
    ] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    timezone_for_calculations: Annotated[
        Timezone, fastapi_dependable_convert_timezone
    ] = Timezone.UTC,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    user_requested_timestamps: Annotated[
        DatetimeIndex | None, fastapi_dependable_convert_timestamps
    ] = None,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
):
    """
    **DEMO**: Estimate the photovoltaic power output for a solar surface.

    Estimate the photovoltaic power for a solar surface over a time series or an arbitrarily aggregated energy production of a PV system connected to the electricity
    grid (without battery storage) based on broadband solar irradiance, ambient temperature and wind speed.
    
    <span style="color:red"> <ins>**This Application Is a Feasibility Study**</ins></span>
    **limited to** longitudes ranging in [`7.5`, `10`] and latitudes in [`45`, `47.5`].

    # Features

    - A symbol nomenclature for easy identification of quantities, units, and more -- see [Symbols](https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/cli/symbols/)
    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html)
    - Valid time zone identifiers from [the IANA Time Zone Database](https://www.iana.org/time-zones)
    - Get from simple to detailed output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)
    - Share a **QR-Code** with a summary of the analysis
    - **Fingerprint** your analysis
    - Document your analysis including all **input metadata**

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

    ## Need more control ?

    In the `/power/broadband` endpoint you may find :

    - Optional algorithms for solar timing, positioning and the estimation of the solar incidence angle
    - Disable atmospheric refraction for solar positioning
    - Simpler power-rating model as well as module temperature model
    - and more

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
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone_for_calculations,
        global_horizontal_irradiance=_read_datasets[
            "global_horizontal_irradiance_series"
        ],
        direct_horizontal_irradiance=_read_datasets[
            "direct_horizontal_irradiance_series"
        ],
        temperature_series=_read_datasets["temperature_series"],
        wind_speed_series=_read_datasets["wind_speed_series"],
        # spectral_factor_series=common_datasets["spectral_factor_series"],
        horizon_profile=_read_datasets["horizon_profile"],
        shading_model=shading_model,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        angle_output_units=angle_output_units,
        power_model=power_model,
        peak_power=peak_power,
        verbose=verbose,
        fingerprint=fingerprint,
    )
    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------

    if csv:
        from pvgisprototype.web_api.utilities import generate_photovoltaic_output_csv

        in_memory_csv = generate_photovoltaic_output_csv(
            dictionary=photovoltaic_power_output_series.components,
            latitude=latitude,
            longitude=longitude,
            timestamps=user_requested_timestamps,
            timezone=timezone,
        )  # type: ignore

        # Based on https://github.com/fastapi/fastapi/discussions/9049 since file is already in memory is faster to return it as PlainTextResponse
        response = PlainTextResponse(
            content=in_memory_csv,
            headers={"Content-Disposition": f"attachment; filename={quote(csv)}"},
            media_type="text/csv",
        )

        return response

    response: dict = {}  # type: ignore
    headers = {
        "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
    }

    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = photovoltaic_power_output_series.components[  # type: ignore
            FINGERPRINT_COLUMN_NAME
        ]

    if quick_response_code.value != QuickResponseCode.NoneValue:
        quick_response = generate_quick_response_code(
            dictionary=photovoltaic_power_output_series.components,
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
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

    if statistics:
        from numpy import atleast_1d, ndarray

        from pvgisprototype.api.statistics.xarray import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=user_requested_timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        converted_series_statistics = {
            key: atleast_1d(value) if isinstance(value, ndarray) else value
            for key, value in series_statistics.items()
        }  # NOTE Important since calculate_series_statistics returns scalars and ORJSON cannot serielise them
        response["Statistics"] = converted_series_statistics  # type: ignore

    if not quiet:
        if verbose > 0:
            response = photovoltaic_power_output_series.components
        else:
            response = {
                PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series.value,  # type: ignore
            }

    return ORJSONResponse(response, headers=headers, media_type="application/json")


async def get_photovoltaic_power_output_series_multi(
    _read_datasets: Annotated[
        dict, fastapi_dependable_read_datasets
    ],  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        list[float], fastapi_dependable_surface_orientation_list
    ] = [float(SURFACE_ORIENTATION_DEFAULT)],
    surface_tilt: Annotated[list[float], fastapi_dependable_surface_tilt_list] = [
        float(SURFACE_TILT_DEFAULT)
    ],
    timestamps: Annotated[str | None, fastapi_dependable_timestamps] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = "2013-01-01",
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = "2013-12-31",
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    #spectral_factor_series: Annotated[
    #    SpectralFactorSeries, fastapi_dependable_spectral_factor_series
    #] = None,
    shading_model: Annotated[ShadingModel, fastapi_dependable_shading_model] = ShadingModel.pvis,    
    neighbor_lookup: Annotated[
        MethodForInexactMatches, fastapi_query_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float, fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, fastapi_query_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[
        float | LinkeTurbidityFactor, fastapi_dependable_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Annotated[
        bool, fastapi_query_apply_atmospheric_refraction
    ] = True,
    refracted_solar_zenith: Annotated[
        float, fastapi_dependable_refracted_solar_zenith
    ] = math.degrees(REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT),
    albedo: Annotated[float, fastapi_query_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, fastapi_query_apply_reflectivity_factor
    ] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, fastapi_dependable_solar_position_models
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, fastapi_dependable_solar_incidence_models
    ] = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: Annotated[
        bool, fastapi_query_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[
        SolarTimeModel, fastapi_query_solar_time_model
    ] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, fastapi_query_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, fastapi_query_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[
        float, fastapi_query_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
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
    # radiation_cutoff_threshold: Annotated[float, fastapi_query_radiation_cutoff_threshold] = RADIATION_CUTOFF_THRESHHOLD,
    temperature_model: Annotated[
        ModuleTemperatureAlgorithm, fastapi_query_temperature_model
    ] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[
        float | None, fastapi_query_efficiency
    ] = EFFICIENCY_FACTOR_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.NoneValue,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    quiet: Annotated[bool, fastapi_dependable_quiet] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[
        bool, fastapi_dependable_fingerprint
    ] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    timezone_for_calculations: Annotated[
        Timezone, fastapi_dependable_convert_timezone
    ] = Timezone.UTC,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    user_requested_timestamps: Annotated[
        DatetimeIndex | None, fastapi_dependable_convert_timestamps
    ] = None,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
):
    """Calculate the total photovoltaic power/energy generated for a series of
    surface orientation and tilt angle pairs, optionally for various
    technologies, free-standing or building-integrated, at a specific location
    and a given period.

    # Features

    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html)
    - Optional algorithms for solar timing, positioning and the estimation of the solar incidence angle
    - Optionally Disable the atmospheric refraction for solar positioning
    - Optional power-rating models on top of optional module temperature models (pending integration of alternatives)
    - Get from simple to detailed output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)
    - Share a **QR-Code** with a summary of the analysis
    - **Fingerprint** your analysis
    - Document your analysis including all **input metadata**

    ## **Important Notes**

    - The function expects pairs of surface orientation
      (`surface_orientation`) and tilt (`surface_tilt`) angles, that is the
      number of requested orientation angles should equal the number of
      requested tilt angles.

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
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series_from_multiple_surfaces(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        timestamps=timestamps,
        timezone=timezone_for_calculations,
        global_horizontal_irradiance=_read_datasets[
            "global_horizontal_irradiance_series"
        ],
        direct_horizontal_irradiance=_read_datasets[
            "direct_horizontal_irradiance_series"
        ],
        temperature_series=_read_datasets["temperature_series"],
        wind_speed_series=_read_datasets["wind_speed_series"],
        # spectral_factor_series=common_datasets["spectral_factor_series"],
        horizon_profile=_read_datasets["horizon_profile"],
        shading_model=shading_model,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        linke_turbidity_factor_series=linke_turbidity_factor_series,  # LinkeTurbidityFactor = LinkeTurbidityFactor(value = LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
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
        photovoltaic_module=photovoltaic_module,
        # peak_power=peak_power,
        system_efficiency=system_efficiency,
        power_model=power_model,
        # radiation_cutoff_threshold=radiation_cutoff_threshold,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
        # log=verbose,
        fingerprint=True,
    )

    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------

    if csv:
        from pvgisprototype.web_api.utilities import generate_photovoltaic_output_csv

        in_memory_csv = generate_photovoltaic_output_csv(
            dictionary=photovoltaic_power_output_series.components,
            latitude=latitude,
            longitude=longitude,
            timestamps=user_requested_timestamps,
            timezone=timezone,
        )  # type: ignore

        # Based on https://github.com/fastapi/fastapi/discussions/9049 since file is already in memory is faster to return it as PlainTextResponse
        response = PlainTextResponse(
            content=in_memory_csv,
            headers={"Content-Disposition": f"attachment; filename={quote(csv)}"},
            media_type="text/csv",
        )

        return response

    response: dict = {}  # type: ignore
    headers = {
        "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
    }

    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = photovoltaic_power_output_series.components[  # type: ignore
            FINGERPRINT_COLUMN_NAME
        ]

    if quick_response_code.value != QuickResponseCode.NoneValue:
        quick_response = generate_quick_response_code(
            dictionary=photovoltaic_power_output_series.components,
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
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

    if statistics:
        from numpy import atleast_1d, ndarray

        from pvgisprototype.api.statistics.xarray import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.series,
            timestamps=timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        converted_series_statistics = {
            key: atleast_1d(value) if isinstance(value, ndarray) else value
            for key, value in series_statistics.items()
        }  # NOTE Important since calculate_series_statistics returns scalars and ORJSON cannot serielise them
        response["Statistics"] = converted_series_statistics  # type: ignore

    if not quiet:
        if verbose > 0:
            response = photovoltaic_power_output_series.components
        else:
            response = {
                PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series.series,  # type: ignore
            }

    return ORJSONResponse(response, headers=headers, media_type="application/json")
