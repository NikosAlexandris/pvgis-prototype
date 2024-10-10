from datetime import datetime
from pathlib import Path

import numpy as np

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.algorithms.pvis.constants import BAND_LIMITS
from pvgisprototype.algorithms.pvis.read import read_spectral_response
from pvgisprototype.algorithms.pvis.spectral_factor import calculate_spectral_factor
from pvgisprototype.api.irradiance.diffuse.inclined import (
    calculate_diffuse_inclined_irradiance_series,
)
from pvgisprototype.api.irradiance.direct.inclined import (
    calculate_direct_inclined_irradiance_series_pvgis,
)
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.irradiance.reflected import (
    calculate_ground_reflected_inclined_irradiance_series,
)
from pvgisprototype.api.irradiance.shade import is_surface_in_shade_series
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.incidence import model_solar_incidence_series
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.power.efficiency import calculate_pv_efficiency_series
from pvgisprototype.api.power.efficiency_coefficients import (
    EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT,
)
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    MINUTES,
    PERIGEE_OFFSET,
    RADIANS,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    TEMPERATURE_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
)


def calculate_spectrally_resolved_global_inclined_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: datetime | None = None,
    timezone: str | None = None,
    spectrally_resolved_global_horizontal_irradiance_series: Path | None = None,  # global_spectral_radiation,  # g_rad_spec
    spectrally_resolved_direct_horizontal_irradiance_series: Path | None = None,  # direct_spectral_radiation,  # d_rad_spec,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodForInexactMatches = None,
    tolerance: float | None = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    surface_tilt: float | None = SURFACE_TILT_DEFAULT,
    surface_orientation: float | None = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: float | None = ALBEDO_DEFAULT,
    apply_angular_loss_factor: bool = True,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.jenco,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    # module_temperature,
    # horizonpointer,
    time_output_units: str = MINUTES,
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """
    Calculate the photovoltaic power output over a location (latitude), surface
    and atmospheric conditions, and an arbitrary period of time based on
    spectrally resolved direct (beam), diffuse, reflected solar irradiation and
    ambient temperature to account for the varying effects of the solar
    spectrum. Considering shadowing effects of the local topography are
    optionally incorporated. The solar geometry relevant parameters
    (e.g.sunrise and sunset, declination, extraterrestrial irradiance, daylight
    length) can be optionally saved in a file.
    """
    # Initialize arrays ?
    spectrally_resolved_direct_irradiance_series = np.zeros_like(
        spectrally_resolved_global_horizontal_irradiance_series
    )
    spectrally_resolved_diffuse_irradiance_series = np.zeros_like(
        spectrally_resolved_global_horizontal_irradiance_series
    )
    spectrally_resolved_reflected_irradiance_series = np.zeros_like(
        spectrally_resolved_global_horizontal_irradiance_series
    )

    # In r.pv_spec : s0 = lumcline2()
    solar_incidence_series = model_solar_incidence_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_incidence_model=solar_incidence_model,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=0,
    )
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=0,
    )
    sun_above_horizon = solar_altitude_series.value > 0  # or : .radians ?
    positive_solar_incidence = solar_incidence_series.radians > 0
    surface_in_shade = is_surface_in_shade_series(solar_altitude_series.value)
    surface_not_in_shade = ~surface_in_shade
    positive_solar_incidence_and_surface_not_in_shade = np.logical_and(
        positive_solar_incidence, surface_not_in_shade
    )

    if not np.any(sun_above_horizon):
        spectrally_resolved_global_irradiance_series = 0

    else:  # if np.any(positive_solar_altitude)
        # We don't need a for loop! ==========================================
        # for spectral_band_number in range(1, number_of_spectral_bands + 1):
        # We don't need a for loop! ==========================================

        # The following stems from PVGIS' C/C++ source code ==================

        # Is it necessary ?
        # Is it possible for the direct component to be greater than the global one ?
        # Does it imply issues in the input data ?

        spectrally_resolved_global_horizontal_irradiance_series[
            spectrally_resolved_global_horizontal_irradiance_series < 0
        ] = 0

        spectrally_resolved_direct_horizontal_irradiance_series = np.minimum(
            spectrally_resolved_global_horizontal_irradiance_series,
            spectrally_resolved_direct_horizontal_irradiance_series,
        )
        # Above stems from PVGIS' C/C++ source code =========================

        if not np.any(
            positive_solar_incidence_and_surface_not_in_shade
        ):  # get the direct irradiance
            spectrally_resolved_direct_irradiance_series = 0
            spectrally_resolved_direct_horizontal_irradiance_series = 0

        else:
            # sunRadVar["cbh"] = global_spectral_radiation[spectral_band_number]
            # sunRadVar["cdh"] = direct_spectral_radiation[spectral_band_number]

            # extraterrestrial_normal_irradiance_series = EXTRATERRESTRIAL_NORMAL_IRRADIANCE[spectral_band_number]
            # extraterrestrial_normal_irradiance_series = (
            #     calculate_extraterrestrial_normal_irradiance_series(
            #         timestamps=timestamps,
            #         solar_constant=solar_constant,
            #         perigee_offset=perigee_offset,
            #         eccentricity_correction_factor=eccentricity_correction_factor,
            #     )
            # )

            # following is in r.pv_spec : `ra`
            spectrally_resolved_direct_irradiance_series[
                positive_solar_incidence_and_surface_not_in_shade
            ] = (
                calculate_direct_inclined_irradiance_series_pvgis(
                    longitude=longitude,
                    latitude=latitude,
                    elevation=elevation,
                    timestamps=timestamps,
                    timezone=timezone,
                    direct_horizontal_component=spectrally_resolved_direct_horizontal_irradiance_series,
                    mask_and_scale=mask_and_scale,
                    neighbor_lookup=neighbor_lookup,
                    tolerance=tolerance,
                    in_memory=in_memory,
                    surface_tilt=surface_tilt,
                    surface_orientation=surface_orientation,
                    linke_turbidity_factor_series=linke_turbidity_factor_series,
                    apply_atmospheric_refraction=apply_atmospheric_refraction,
                    refracted_solar_zenith=refracted_solar_zenith,
                    apply_angular_loss_factor=apply_angular_loss_factor,
                    solar_position_model=solar_position_model,
                    solar_incidence_model=solar_incidence_model,
                    solar_time_model=solar_time_model,
                    solar_constant=solar_constant,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                    time_output_units=time_output_units,
                    angle_units=angle_units,
                    angle_output_units=angle_output_units,
                    verbose=0,  # no verbosity here by choice!
                )
            )[
                positive_solar_incidence_and_surface_not_in_shade
            ]

        # Calculate diffuse and reflected irradiance for sun above horizon
        spectrally_resolved_diffuse_irradiance_series[sun_above_horizon] = (
            calculate_diffuse_inclined_irradiance_series(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                timestamps=timestamps,
                timezone=timezone,
                surface_tilt=surface_tilt,
                surface_orientation=surface_orientation,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                global_horizontal_component=spectrally_resolved_global_horizontal_irradiance_series,
                direct_horizontal_component=spectrally_resolved_direct_horizontal_irradiance_series,
                apply_angular_loss_factor=apply_angular_loss_factor,
                solar_position_model=solar_position_model,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                time_output_units=time_output_units,
                angle_units=angle_units,
                angle_output_units=angle_output_units,
                neighbor_lookup=neighbor_lookup,
                verbose=0,  # no verbosity here by choice!
            )[sun_above_horizon]
        )

        spectrally_resolved_reflected_irradiance_series[sun_above_horizon] = (
            calculate_ground_reflected_inclined_irradiance_series(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                timestamps=timestamps,
                timezone=timezone,
                surface_tilt=surface_tilt,
                surface_orientation=surface_orientation,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                albedo=albedo,
                direct_horizontal_component=spectrally_resolved_direct_horizontal_irradiance_series,
                apply_angular_loss_factor=apply_angular_loss_factor,
                solar_position_model=solar_position_model,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                time_output_units=time_output_units,
                angle_units=angle_units,
                angle_output_units=angle_output_units,
                verbose=0,  # no verbosity here by choice!
            )[sun_above_horizon]
        )

        spectrally_resolved_global_irradiance_series = (
            spectrally_resolved_direct_irradiance_series
            + spectrally_resolved_diffuse_irradiance_series
            + spectrally_resolved_reflected_irradiance_series
        )

    return spectrally_resolved_global_irradiance_series


def calculate_spectral_photovoltaic_power_output(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: datetime | None = None,
    timezone: str | None = None,
    spectrally_resolved_global_horizontal_irradiance_series: Path | None = None,  # global_spectral_radiation,  # g_rad_spec
    spectrally_resolved_direct_horizontal_irradiance_series: Path | None = None,  # direct_spectral_radiation,  # d_rad_spec,
    number_of_junctions: int = 1,
    spectral_response_data: Path | None = None,
    standard_conditions_response: Path | None = None,  #: float = 1,  # STCresponse : read from external data
    # extraterrestrial_normal_irradiance_series,  # spectral_ext,
    temperature_series: np.ndarray = np.array(
        TEMPERATURE_DEFAULT
    ),  # pres_temperature ?
    wind_speed_series: np.ndarray = np.array(WIND_SPEED_DEFAULT),
    mask_and_scale: bool = False,
    neighbor_lookup: MethodForInexactMatches | None = None,
    tolerance: float | None = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    surface_tilt: float | None = SURFACE_TILT_DEFAULT,
    surface_orientation: float | None = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: float | None = ALBEDO_DEFAULT,
    apply_angular_loss_factor: bool = True,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.jenco,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    # module_temperature,
    # horizonpointer,
    time_output_units: str = MINUTES,
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    system_efficiency: float | None = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: PhotovoltaicModulePerformanceModel = None,
    temperature_model: ModuleTemperatureAlgorithm = None,
    efficiency: float | None = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """
    Calculate the photovoltaic power output over a location (latitude), surface
    and atmospheric conditions, and an arbitrary period of time based on
    spectrally resolved direct (beam), diffuse, reflected solar irradiation and
    ambient temperature to account for the varying effects of the solar
    spectrum. Considering shadowing effects of the local topography are
    optionally incorporated. The solar geometry relevant parameters
    (e.g.sunrise and sunset, declination, extraterrestrial irradiance, daylight
    length) can be optionally saved in a file.
    """
    spectrally_resolved_global_irradiance_series = calculate_spectrally_resolved_global_inclined_irradiance_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        spectrally_resolved_global_horizontal_irradiance_series=spectrally_resolved_global_horizontal_irradiance_series,
        spectrally_resolved_direct_horizontal_irradiance_series=spectrally_resolved_direct_horizontal_irradiance_series,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
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
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        system_efficiency=system_efficiency,
        power_model=power_model,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
    )

    # In PVGIS' source code :
    # if spectral_band_number < 19:
    # global_power_1050 += global_spectral_power[spectral_band_number]

    index_1050 = np.max(np.where(BAND_LIMITS < 1050)[0])
    global_irradiance_series_up_to_1050 = spectrally_resolved_global_irradiance_series[
        :, index_1050
    ].sum()
    bandwidths = np.diff(BAND_LIMITS)
    spectral_power_density_up_to_1050 = global_irradiance_series_up_to_1050 / bandwidths

    spectral_response_data = read_spectral_response(spectral_response_data)
    spectral_response_wavelengths = spectral_response_data[0]  # response_wavelengths,
    spectral_response = spectral_response_data[1]
    standard_conditions_response = spectral_response_data[2]  # STCresponse

    spectral_factor = calculate_spectral_factor(
        global_total_power=spectrally_resolved_global_irradiance_series,
        spectral_power_density=spectral_power_density_up_to_1050,  # !
        number_of_junctions=number_of_junctions,
        response_wavelengths=spectral_response_wavelengths,
        spectral_response=spectral_response,
        standard_conditions_response=standard_conditions_response,
    )
    spectrally_resolved_photovoltaic_power = (
        spectrally_resolved_global_irradiance_series * spectral_factor
    )

    if efficiency:  # user-set
        efficiency_coefficient_series = calculate_pv_efficiency_series(
            irradiance_series=spectrally_resolved_global_irradiance_series,  # global_total_power,
            spectrally_factor=spectral_factor,  # internally will do *= global_total_power
            temperature_series=temperature_series,  # pres_temperature,
            model_constants=EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT,
            standard_test_temperature=TEMPERATURE_DEFAULT,
            wind_speed_series=wind_speed_series,
            power_model=power_model,
            temperature_model=temperature_model,
            verbose=0,  # no verbosity here by choice!
        )
        spectrally_resolved_photovoltaic_power *= efficiency_coefficient_series

    return spectrally_resolved_photovoltaic_power
