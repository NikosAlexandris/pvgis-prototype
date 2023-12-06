from pathlib import Path
from typing import Optional
from numpy.typing import NDArray
from datetime import datetime

import numpy as np
import math

from pvgisprototype.algorithms.pvis.constants import STANDARD_CONDITIONS_EFFECTIVE_IRRADIANCE
from pvgisprototype.algorithms.pvis.constants import ELECTRON_CHARGE
from pvgisprototype.algorithms.pvis.constants import MINIMUM_SPECTRAL_MISMATCH
from pvgisprototype.algorithms.pvis.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE  # why not calculate it?
from pvgisprototype.algorithms.pvis.constants import BAND_LIMITS
from pvgisprototype.algorithms.pvis.constants import PHOTON_ENERGIES
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import MINUTES
from pvgisprototype.constants import SYSTEM_EFFICIENCY_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
# from pvgisprototype.api.irradiance.extraterrestrial import calculate_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.api.irradiance.direct import calculate_direct_inclined_irradiance_time_series_pvgis
from pvgisprototype.api.irradiance.diffuse import calculate_diffuse_inclined_irradiance_time_series
from pvgisprototype.api.irradiance.reflected import calculate_ground_reflected_inclined_irradiance_time_series
from pvgisprototype.api.irradiance.shade import is_surface_in_shade_time_series
from pvgisprototype.api.geometry.incidence_series import model_solar_incidence_time_series
from pvgisprototype.api.geometry.altitude_series import model_solar_altitude_time_series
from pvgisprototype.api.irradiance.efficiency import calculate_pv_efficiency_time_series
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.algorithms.pvis.read import read_spectral_response
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.geometry.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SolarIncidenceModels
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithm
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT


# # Macros as functions
# def amax1(arg1, arg2):
#     return max(arg1, arg2)

# def amin1(arg1, arg2):
#     return min(arg1, arg2)

# def distance1(x1, x2, y1, y2):
#     return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def calculate_average_photon_energy(  # series ?
    global_irradiance_series_up_to_1050,
    photon_flux_density,
    electron_charge = ELECTRON_CHARGE,
):
    """
    The Average Photon Energy (APE) characterises the energetic distribution
    in an irradiance spectrum. It is calculated by dividing the irradiance
    [W/m² or eV/m²/sec] by the photon flux density [number of photons/m²/sec].

    Notes
    -----
    From [1]_ :

        "The average photon energy is a useful parameter for examining spectral
        effects on the performance of amorphous silicon cells. It is strongly
        correlated with the useful fraction, but is a device independent
        parameter that does not require knowledge of the absorption profile of
        a given device.

        It is possible to examine the purely spectral performance of amorphous
        silicon devices after removing temperature effects from the data.
        Single junction devices show a linear increase in corrected ISC/Gtotal
        as the received radiation becomes more blue shifted, as a greater
        proportion of the insolation lies within its absorption window.
        
        Double and triple junction devices do not vary linearly. The devices
        investigated here reach maxima at 1.72 and 1.7 eV, respectively. As the
        received spectrum becomes either red or blue shifted from this ideal,
        performance drops off due to mismatch between the absorption profile
        and the received spectrum. The output of multijunction devices is
        essentially limited by the layer generating the least current. The
        performance of triple junction cells is more susceptible to changes in
        the incident spectrum than double junction cells, although this will be
        countermanded with lower degradation in the case of a-Si devices.
        
        The maximum spectral performance of multijunction devices occurs at
        APEs higher than the APE where most energy is received. There is an
        opportunity to improve the spectral performance of multijunction
        devices such that they are most efficient at APEs where the majority of
        the energy is delivered.

    References
    ----------
    .. [1] Jardine, C.N. & Gottschalg, Ralph & Betts, Thomas & Infield, David.
      (2002). Influence of Spectral Effects on the Performance of Multijunction
      Amorphous Silicon Cells. to be published.
    """
    # name it series ?
    average_photon_energy = (
        global_irradiance_series_up_to_1050 / photon_flux_density * electron_charge
    )

    return average_photon_energy  # series


def integrate_spectrum_response(
    spectral_response_frequencies: NDArray[np.float64] = None,
    spectral_response: NDArray[np.float64] = None,
    kato_limits: NDArray[np.float64] = None,
    spectral_power_density: NDArray[np.float64] = None,
) -> float:
    """ """
    m = 0
    n = 0
    # nu_high = float()
    # response_low = float()
    # response_high = float()
    photovoltaic_power = 0
    response_low = spectral_response[0]
    # nu_low = float()
    nu_low = spectral_response_frequencies[0]

    number_of_response_values = len(spectral_response_frequencies)
    number_of_kato_limits = len(kato_limits)

    while n < number_of_response_values - 1:
        if spectral_response_frequencies[n + 1] < kato_limits[m + 1]:
            nu_high = spectral_response_frequencies[n + 1]
            response_high = spectral_response[n + 1]

        else:
            nu_high = kato_limits[m + 1]
            response_high = spectral_response[n] + (
                nu_high - spectral_response_frequencies[n]
            ) / (
                spectral_response_frequencies[n + 1] - spectral_response_frequencies[n]
            ) * (
                spectral_response[n + 1] - spectral_response[n]
            )
        photovoltaic_power += (
            spectrum_power[m]
            * 0.5
            * (response_high + response_low)
            * (nu_high - nu_low)
        )

        if spectral_response_frequencies[n + 1] < kato_limits[m + 1]:
            n += 1
        else:
            m += 1

        nu_low = nu_high
        response_low = response_high

    return photovoltaic_power


def determine_minimum_spectral_mismatch(
    response_wavelengths,
    spectral_response,
    number_of_junctions: int,
    spectral_power_density,
):
    """
    Returns
    -------
    minimum_spectral_mismatch: float

    minimum_junction:

        By Kirchoff’s Law the overall current produced by the device is only
        equal to the smallest current produced by an individual junction. This
        means that the least productive layer in a multi-junction device limits
        the performance of a multijunction cell [1]_

    References
    ----------
    .. [1] Jardine, C.N. & Gottschalg, Ralph & Betts, Thomas & Infield, David.
      (2002). Influence of Spectral Effects on the Performance of Multijunction
      Amorphous Silicon Cells. to be published.
    """
    for junction in range(number_of_junctions):
        spectral_mismatch = integrate_spectrum_response(
                spectral_response_frequencies=response_wavelengths,
                spectral_response=spectral_response,
                kato_limits=junction,
                spectral_power_density=spectral_power_density,
        )
        if spectral_mismatch < minimum_spectral_mismatch:
            minimum_spectral_mismatch = spectral_mismatch
            minimum_junction = junction

    return minimum_spectral_mismatch, minimum_junction


def determine_spectral_factor(
    minimum_spectral_mismatch,
    global_total_power,
    standard_conditions_response,
):
    spectral_factor = (
        minimum_spectral_mismatch * STANDARD_CONDITIONS_EFFECTIVE_IRRADIANCE /
        (global_total_power * standard_conditions_response)
    )

    return spectral_factor


def calculate_spectral_photovoltaic_power_output(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: Optional[datetime] = None,
    start_time: Optional[datetime] = None,
    frequency: Optional[str] = None,
    end_time: Optional[datetime] = None,
    timezone: Optional[str] = None,
    random_time_series: bool = False,
    spectrally_resolved_global_horizontal_irradiance_series: Optional[Path] = None, #global_spectral_radiation,  # g_rad_spec
    spectrally_resolved_direct_horizontal_irradiance_series: Optional[Path] = None, # direct_spectral_radiation,  # d_rad_spec,
    number_of_junctions: int = 1,
    spectral_response_data: Path = None,
    standard_conditions_response: Optional[Path] = None,  #: float = 1,  # STCresponse : read from external data
    # extraterrestrial_normal_irradiance_series,  # spectral_ext,
    minimum_spectral_mismatch = MINIMUM_SPECTRAL_MISMATCH,
    temperature_series: np.ndarray = np.array(TEMPERATURE_DEFAULT),  # pres_temperature ?
    wind_speed_series: np.ndarray = np.array(WIND_SPEED_DEFAULT),
    mask_and_scale: bool = False,
    neighbor_lookup: MethodsForInexactMatches = None,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    surface_tilt: Optional[float] = SURFACE_TILT_DEFAULT,
    surface_orientation: Optional[float] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,  
    apply_atmospheric_refraction: Optional[bool] = True,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Optional[float] = 2,
    apply_angular_loss_factor: Optional[bool] = True,
    solar_position_model: SolarPositionModels = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModels = SolarIncidenceModels.jenco,
    solar_time_model: SolarTimeModels = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    # module_temperature,
    # horizonpointer,
    time_output_units: str = MINUTES,
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    system_efficiency: Optional[float] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: PVModuleEfficiencyAlgorithm = None,
    temperature_model: ModuleTemperatureAlgorithm = None,
    efficiency: Optional[float] = None,
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
    solar_incidence_series = model_solar_incidence_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        random_time_series=random_time_series,
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
    solar_altitude_series = model_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=0,
    )
    sun_above_horizon = solar_altitude_series.value > 0  # or : .radians ?
    positive_solar_incidence = solar_incidence_series.radians > 0
    surface_in_shade = is_surface_in_shade_time_series(solar_altitude_series.value)
    surface_not_in_shade = ~surface_in_shade
    positive_solar_incidence_and_surface_not_in_shade = np.logical_and(
        positive_solar_incidence, surface_not_in_shade
    )

    if not np.any(sun_above_horizon):
        spectrally_resolved_photovoltaic_power = 0

    else:  # if np.any(positive_solar_altitude)

        # We don't need a for loop! ==========================================
        # for spectral_band_number in range(1, number_of_spectral_bands + 1):
        # We don't need a for loop! ==========================================

        # The following stems from PVGIS' C/C++ source code ==================

        # Is it necessary ?
        # Is it possible for the direct component to be greater than the global one ?
        # Does it imply issues in the input data ?

        spectrally_resolved_global_horizontal_irradiance_series[spectrally_resolved_global_horizontal_irradiance_series < 0] = 0

        spectrally_resolved_direct_horizontal_irradiance_series = np.minimum(
            spectrally_resolved_global_horizontal_irradiance_series, spectrally_resolved_direct_horizontal_irradiance_series
        )
        # Above stems from PVGIS' C/C++ source code =========================

        if not np.any(positive_solar_incidence_and_surface_not_in_shade):  # get the direct irradiance
            # direct_spectral_power[spectral_band_number] = 0.0
            direct_spectral_power = 0
            # direct_horizontal_component = 0.0
            direct_horizontal_component = 0

        else:
            # sunRadVar["cbh"] = global_spectral_radiation[spectral_band_number]
            # sunRadVar["cdh"] = direct_spectral_radiation[spectral_band_number]

            # extraterrestrial_normal_irradiance_series = EXTRATERRESTRIAL_NORMAL_IRRADIANCE[spectral_band_number]
            # extraterrestrial_normal_irradiance_series = (
            #     calculate_extraterrestrial_normal_irradiance_time_series(
            #         timestamps=timestamps,
            #         solar_constant=solar_constant,
            #         perigee_offset=perigee_offset,
            #         eccentricity_correction_factor=eccentricity_correction_factor,
            #         random_days=random_days,
            #     )
            # )

            # following is in r.pv_spec : `ra`
            spectrally_resolved_direct_irradiance_series[positive_solar_incidence_and_surface_not_in_shade] = (
                calculate_direct_inclined_irradiance_time_series_pvgis(
                    longitude=longitude,
                    latitude=latitude,
                    elevation=elevation,
                    timestamps=timestamps,
                    start_time=start_time,
                    end_time=end_time,
                    timezone=timezone,
                    random_time_series=random_time_series,
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
                    time_offset_global=time_offset_global,
                    hour_offset=hour_offset,
                    solar_constant=solar_constant,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                    time_output_units=time_output_units,
                    angle_units=angle_units,
                    angle_output_units=angle_output_units,
                    verbose=0,  # no verbosity here by choice!
                )
            )[positive_solar_incidence_and_surface_not_in_shade]

        # Calculate diffuse and reflected irradiance for sun above horizon
        spectrally_resolved_diffuse_irradiance_series[
            sun_above_horizon
        ] = calculate_diffuse_inclined_irradiance_time_series(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            timestamps=timestamps,
            start_time=start_time,
            end_time=end_time,
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
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            neighbor_lookup=neighbor_lookup,
            verbose=0,  # no verbosity here by choice!
        )[
            sun_above_horizon
        ]

        spectrally_resolved_reflected_irradiance_series[
            sun_above_horizon
        ] = calculate_ground_reflected_inclined_irradiance_time_series(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            timestamps=timestamps,
            start_time=start_time,
            end_time=end_time,
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
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            verbose=0,  # no verbosity here by choice!
        )[
            sun_above_horizon
        ]

        spectrally_resolved_global_irradiance_series = (
            spectrally_resolved_direct_irradiance_series
            + spectrally_resolved_diffuse_irradiance_series
            + spectrally_resolved_reflected_irradiance_series
        )

        # In PVGIS' source code :
        # if spectral_band_number < 19:
            # number_of_photons += (
            #     global_spectral_power[spectral_band_number]
            #     / photon_energies[spectral_band_number]
            # )
            # global_power_1050 += global_spectral_power[spectral_band_number]

        index_1050 = np.max(np.where(BAND_LIMITS < 1050)[0])
        photon_energies_up_to_1050 = PHOTON_ENERGIES[index_1050]
        number_of_photons_up_to_1050 = spectrally_resolved_global_irradiance_series[:, index_1050] / photon_energies_up_to_1050
        global_irradiance_series_up_to_1050 = spectrally_resolved_global_irradiance_series[:, index_1050].sum()

        average_photon_energy = calculate_average_photon_energy(
            global_power_1050=global_irradiance_series_up_to_1050,
            photon_flux_density=number_of_photons_up_to_1050,
            electron_charge=ELECTRON_CHARGE,
        )

        bandwidths = np.diff(BAND_LIMITS)
        spectral_power_density_up_to_1050 = global_irradiance_series_up_to_1050 / bandwidths

        spectral_response_data = read_spectral_response(spectral_response_data)
        wavelengths = spectral_response_data[0]  # response_wavelengths,
        spectral_response = spectral_response_data[1]
        standard_conditions_response = spectral_response_data[2]  # STCresponse
        (
            minimum_spectral_mismatch,
            minimum_junction,
        ) = determine_minimum_spectral_mismatch(
            response_wavelengths=wavelengths,
            spectral_response=spectral_response,
            number_of_junctions=number_of_junctions,
            spectral_power_density=spectral_power_density_up_to_1050,
        )
        spectral_factor = determine_spectral_factor(
                minimum_spectral_mismatch=minimum_spectral_mismatch,
                global_total_power=spectrally_resolved_global_irradiance_series,
                standard_conditions_response=standard_conditions_response,
        )

        spectrally_resolved_photovoltaic_power = spectrally_resolved_global_irradiance_series * spectral_factor

        if efficiency:  # user-set
            efficiency_coefficient_series = calculate_pv_efficiency_time_series(
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

    return spectrally_resolved_photovoltaic_power, minimum_junction
