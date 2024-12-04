from datetime import datetime
from pathlib import Path
from typing import List, Optional
from zoneinfo import ZoneInfo
from typing import Annotated
from fastapi import Depends, Query
from pandas import DatetimeIndex
from fastapi.responses import ORJSONResponse
from pvgisprototype.api.position.overview import calculate_solar_position_overview_series
from pvgisprototype.api.position.models import (
    SolarTimeModel,
    SolarPositionModel,
)
from pvgisprototype.api.position.overview import (
    model_solar_position_overview_series,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    ECCENTRICITY_CORRECTION_FACTOR,
    PERIGEE_OFFSET,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
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
)
from pvgisprototype.web_api.schemas import (
    AnalysisLevel,
    AngleOutputUnit,
    Frequency,
    GroupBy,
    Timezone,
)
from pvgisprototype.api.position.models import (
    ShadingModel,
)
from xarray import DataArray
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT, SURFACE_TILT_DEFAULT
import math
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
)
from pvgisprototype.constants import ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT


async def get_calculate_solar_position_overview(
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
    start_time: Annotated[str | None, fastapi_query_start_time] = None,
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = None,
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    solar_position_models: List[SolarPositionModel] = Query(
        [SolarPositionModel.noaa], description="Solar position model(s). Select multiple using Ctrl and left mouse click."
    ),
    solar_incidence_model: Annotated[
        SolarIncidenceModel, fastapi_dependable_solar_incidence_models
    ] = SolarIncidenceModel.iqbal,
    horizon_profile: None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    zero_negative_solar_incidence_angle: Annotated[
        bool, fastapi_query_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,    
    apply_atmospheric_refraction: Annotated[
        bool, fastapi_query_apply_atmospheric_refraction
    ] = True,
    #refracted_solar_zenith: Annotated[
    #    float, fastapi_dependable_refracted_solar_zenith
    #] = math.degrees(REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT),
    solar_time_model: SolarTimeModel = Query(SolarTimeModel.milne),
    perigee_offset: Annotated[float, fastapi_query_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = Query(ECCENTRICITY_CORRECTION_FACTOR),
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    timezone_for_calculations: Annotated[
        Timezone, fastapi_dependable_convert_timezone
    ] = Timezone.UTC,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    user_requested_timestamps: Annotated[
        DatetimeIndex | None, fastapi_dependable_convert_timestamps
    ] = None,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
):
    solar_position_series = calculate_solar_position_overview_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone_for_calculations,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        solar_position_models=solar_position_models,
        solar_incidence_model=solar_incidence_model,
        horizon_profile=horizon_profile,
        shading_model=shading_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )

    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------
    
    response: dict = {}  # type: ignore
    headers = {
        "Content-Disposition": f'attachment; filename="solar_position.json"'
    }
    #response["Timestamps"] = {"Timestamps": user_requested_timestamps}
    response['Results'] = solar_position_series
    
    return ORJSONResponse(response, headers=headers, media_type="application/json")
