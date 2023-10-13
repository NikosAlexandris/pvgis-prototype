from devtools import debug
from rich import print
from pvgisprototype.cli.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND
from datetime import datetime
from math import sin
from math import asin
from math import cos
from math import atan
import numpy as np
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.api.irradiance.direct import adjust_elevation
from pvgisprototype.validation.parameters import BaseTimestampSeriesModel
import typer
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from typing import Annotated
from typing import Optional
from typing import Union
from typing import Sequence
from typing import List
from pvgisprototype.api.geometry.solar_altitude_time_series import model_solar_altitude_time_series
from pvgisprototype.api.geometry.solar_declination_time_series import model_solar_declination_time_series
from pvgisprototype.api.geometry.solar_time_time_series import model_solar_time_time_series
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours_time_series
from pvgisprototype.api.irradiance.extraterrestrial_time_series import calculate_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_convert_longitude_360
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer_parameters import typer_option_optical_air_mass_series
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_argument_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_declination_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_days_in_a_year
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_verbose

from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_FACTOR_UNIT
from pvgisprototype.constants import OPTICAL_AIR_MASS_UNIT
from pvgisprototype.constants import RAYLEIGH_OPTICAL_THICKNESS_UNIT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_series_to_radians_if_requested

from zoneinfo import ZoneInfo
from pvgisprototype import SolarAltitude
from pvgisprototype import RefractedSolarAltitude
from pvgisprototype import OpticalAirMass
from pvgisprototype import RayleighThickness
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.irradiance.models import DirectIrradianceComponents
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from pvgisprototype.api.geometry.models import SolarIncidenceModels
from pvgisprototype.cli.series import select_time_series
# from pvgisprototype.api.series.utilities import select_location_time_series
from pathlib import Path

from pvgisprototype.validation.functions import CalculateOpticalAirMassTimeSeriesInputModel
from pvgisprototype.validation.functions import validate_with_pydantic


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the direct solar radiation for a time series",
)


def correct_linke_turbidity_factor_time_series(
    linke_turbidity_factor_series: Union[
        List[LinkeTurbidityFactor], LinkeTurbidityFactor
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    verbose: int = 0,
) -> Union[List[LinkeTurbidityFactor], LinkeTurbidityFactor]:
    """
    Vectorized function to calculate the air mass 2 Linke atmospheric turbidity factor for a time series.

    Parameters:
    - linke_turbidity_factor_series (List[LinkeTurbidityFactor] or LinkeTurbidityFactor): 
      The Linke turbidity factors as a list of LinkeTurbidityFactor objects or a single object.

    Returns:
    - List[LinkeTurbidityFactor] or LinkeTurbidityFactor: 
      The corrected Linke turbidity factors as a list of LinkeTurbidityFactor objects or a single object.
    """
    is_scalar = False
    if isinstance(linke_turbidity_factor_series, LinkeTurbidityFactor):
        is_scalar = True
        linke_turbidity_factor_series = [linke_turbidity_factor_series.value]
    else:
        linke_turbidity_factor_series = [factor.value for factor in linke_turbidity_factor_series]

    # Convert to NumPy array
    linke_turbidity_factor_series_array = np.array(linke_turbidity_factor_series)

    # Perform calculations
    corrected_linke_turbidity_factors_array = -0.8662 * linke_turbidity_factor_series_array

    if verbose == 4:
        debug(locals())

    # Convert back to custom data class objects
    if is_scalar:
        return LinkeTurbidityFactor(value=corrected_linke_turbidity_factors_array[0], unit=LINKE_TURBIDITY_FACTOR_UNIT)
    else:
        return [LinkeTurbidityFactor(value=value, unit=LINKE_TURBIDITY_FACTOR_UNIT) for value in corrected_linke_turbidity_factors_array]


def calculate_refracted_solar_altitude_time_series(
    solar_altitude_series,#: np.ndarray,
    angle_input_units: str = 'degrees',
    angle_output_units: str = 'radians',
    verbose: int = 0,
):
    """Adjust the solar altitude angle for atmospheric refraction for a time series.
    
    Note
    ----
    This function is vectorized to handle arrays of solar altitudes.
    """
    if angle_input_units != "degrees":
        raise ValueError("Only degrees are supported for angle_input_units.")

    is_scalar = False
    if isinstance(solar_altitude_series, SolarAltitude):
        is_scalar = True
        solar_altitude_series = [solar_altitude_series.value]
    else:
        solar_altitude_series = [altitude.value for altitude in solar_altitude_series]

    # Unpack SolarAltitude objects to NumPy Arrays ----------------------- vvv
    solar_altitude_series_array = np.array(solar_altitude_series)
    # ------------------------------------------------------------------------

    atmospheric_refraction = (
        0.061359
        * (
            0.1594
            + 1.123 * solar_altitude_series_array
            + 0.065656 * np.power(solar_altitude_series_array, 2)
        )
        / (
            1
            + 28.9344 * solar_altitude_series_array
            + 277.3971 * np.power(solar_altitude_series_array, 2)
        )
    )
    refracted_solar_altitude_series_array = (
        solar_altitude_series_array + atmospheric_refraction
    )

    # Pack results back to SolarAltitude objects -----------------------------
    if not is_scalar:
        refracted_solar_altitude_series = [
            RefractedSolarAltitude(value=value, unit="degrees")
            for value in refracted_solar_altitude_series_array
        ]
    else:
        refracted_solar_altitude_series = RefractedSolarAltitude(
            value=refracted_solar_altitude_series_array[0], unit="degrees"
        )
    # -------------------------------------------------------------------- ^^^
    
    refracted_solar_altitude_series = convert_series_to_radians_if_requested(
        refracted_solar_altitude_series, angle_output_units
    )

    if verbose == 4:
        debug(locals())

    return refracted_solar_altitude_series


@validate_with_pydantic(CalculateOpticalAirMassTimeSeriesInputModel)
def calculate_optical_air_mass_time_series(
    elevation: Annotated[float, typer_argument_elevation],
    refracted_solar_altitude_series: Union[RefractedSolarAltitude, Sequence[RefractedSolarAltitude]],
    verbose: Annotated[int, typer_option_verbose] = 0,
):
    """Vectorized function to approximate the relative optical air mass for a time series."""
    is_scalar = False
    if isinstance(refracted_solar_altitude_series, RefractedSolarAltitude):
        is_scalar = True
        refracted_solar_altitude_series = [refracted_solar_altitude_series.value]
    else:
        refracted_solar_altitude_series = [altitude.value for altitude in refracted_solar_altitude_series]
    
    # Unpack RefractedSolarAltitude objects to a NumPy array
    refracted_solar_altitude_series_array = np.array(refracted_solar_altitude_series)
    adjusted_elevation = adjust_elevation(elevation.value)
    optical_air_mass_series = adjusted_elevation.value / (
        np.sin(refracted_solar_altitude_series_array)
        + 0.50572
        * np.power((refracted_solar_altitude_series_array + 6.07995), -1.6364)
    )
    
    # Repack results back into custom objects
    if not is_scalar:
        optical_air_mass_series = [OpticalAirMass(value=value, unit=OPTICAL_AIR_MASS_UNIT) for value in optical_air_mass_series]
    else:
        optical_air_mass_series = OpticalAirMass(value=optical_air_mass_series[0], unit=OPTICAL_AIR_MASS_UNIT)

    if verbose == 4:
        debug(locals())
    if verbose > 1:
        print(f'Optical air mass series : {optical_air_mass_series}')

    return optical_air_mass_series


def rayleigh_optical_thickness_time_series(
    optical_air_mass_series,  #: np.ndarray,
    verbose: int = 0,
):
    """Vectorized function to calculate Rayleigh optical thickness for a time series."""
    
    # Check if input is scalar or array-like
    is_scalar = False
    if isinstance(optical_air_mass_series, OpticalAirMass):
        is_scalar = True
        optical_air_mass_series = [optical_air_mass_series.value]
    else:
        optical_air_mass_series = [air_mass.value for air_mass in optical_air_mass_series]
    
    # Unpack OpticalAirMass objects to a NumPy array
    optical_air_mass_series_array = np.array(optical_air_mass_series)
    
    # Perform calculations
    rayleigh_thickness_series_array = np.zeros_like(optical_air_mass_series_array)
    smaller_than_20 = optical_air_mass_series_array <= 20
    larger_than_20 = optical_air_mass_series_array > 20
    rayleigh_thickness_series_array[smaller_than_20] = 1 / (
        6.6296
        + 1.7513 * optical_air_mass_series_array[smaller_than_20]
        - 0.1202 * np.power(optical_air_mass_series_array[smaller_than_20], 2)
        + 0.0065 * np.power(optical_air_mass_series_array[smaller_than_20], 3)
        - 0.00013 * np.power(optical_air_mass_series_array[smaller_than_20], 4)
    )
    rayleigh_thickness_series_array[larger_than_20] = 1 / (
        10.4 + 0.718 * optical_air_mass_series_array[larger_than_20]
    )
    
    # Repack results back into custom objects
    if not is_scalar:
        rayleigh_thickness_series = [
            RayleighThickness(value=value, unit=RAYLEIGH_OPTICAL_THICKNESS_UNIT)
            for value in rayleigh_thickness_series_array
        ]
    else:
        rayleigh_thickness_series = RayleighThickness(
            value=rayleigh_thickness_series_array[0],
            unit=RAYLEIGH_OPTICAL_THICKNESS_UNIT,
        )

    if verbose == 4:
        debug(locals())
    if verbose > 1:
        print(f'Rayleigh thickness series : {rayleigh_thickness_series}')

    return rayleigh_thickness_series


@app.command('normal-series', no_args_is_help=True)
def calculate_direct_normal_irradiance_time_series(
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps],
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    linke_turbidity_factor_series: Annotated[List[float], typer_option_linke_turbidity_factor_series] = None,#: np.ndarray,
    optical_air_mass_series: Annotated[List[float], typer_option_optical_air_mass_series] = None,#: np.ndarray,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_SERIES_FLAG_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """ """
   # Unpack custom objects to NumPy arrays
    optical_air_mass_series_array = np.array([oam.value for oam in optical_air_mass_series])

    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_time_series(
            timestamps=timestamps,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            random_days=random_days,
        )
    )
    corrected_linke_turbidity_factor_series = correct_linke_turbidity_factor_time_series(
        linke_turbidity_factor_series,
        verbose=verbose,
    )
    rayleigh_thickness_series = rayleigh_optical_thickness_time_series(
        optical_air_mass_series,
        verbose=verbose,
    )

    # Unpack the custom objects into NumPy arrays
    linke_turbidity_factor_series_array = np.array([x.value for x in linke_turbidity_factor_series])
    corrected_linke_turbidity_factor_series_array = np.array([x.value for x in corrected_linke_turbidity_factor_series])
    optical_air_mass_series_array = np.array([x.value for x in optical_air_mass_series])
    rayleigh_thickness_series_array = np.array([x.value for x in rayleigh_thickness_series])

    # Calculate
    direct_normal_irradiance_series = (
        extraterrestrial_normal_irradiance_series
        * np.exp(
            corrected_linke_turbidity_factor_series_array
            * optical_air_mass_series_array
            * rayleigh_thickness_series_array
        )
    )

    if verbose == 4:
        debug(locals())
    results = {
        'Normal': direct_normal_irradiance_series,
        }
    if verbose > 1:
        extended_results = {
        'Extra. normal': extraterrestrial_normal_irradiance_series,
        'Rayleigh': rayleigh_thickness_series_array,
        'Air mass': np.array([x.value for x in optical_air_mass_series]),
        'Correct Linke': corrected_linke_turbidity_factor_series_array,
        'Linke': linke_turbidity_factor_series_array,
        }
        results = results | extended_results

    print_irradiance_table_2(
        timestamps=timestamps,
        dictionary=results,
        title='Direct normal irradiance series',
        rounding_places=rounding_places,
        verbose=verbose,
    )

    return direct_normal_irradiance_series


@app.command('horizontal-series', no_args_is_help=True)
def calculate_direct_horizontal_irradiance_time_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps],
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,#Annotated[Optional[ZoneInfo], typer_option_timezone] = None,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SolarPositionModels.noaa,
    linke_turbidity_factor_series: Annotated[List[float], typer_option_linke_turbidity_factor_series] = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> np.ndarray:
    """ """
    solar_altitude_series = model_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    solar_altitude_series_array = np.array([x.value for x in solar_altitude_series])
    
    # expects solar altitude in degrees! ----------------------------------vvv
    expected_solar_altitude_units = "degrees"
    solar_altitude_series_in_degrees = convert_series_to_degrees_if_requested(
        solar_altitude_series,
        angle_output_units=expected_solar_altitude_units,  # Here!
    )

    # refracted_solar_altitude, refracted_solar_altitude_units = calculate_refracted_solar_altitude(
    refracted_solar_altitude_series = calculate_refracted_solar_altitude_time_series(
        solar_altitude_series=solar_altitude_series_in_degrees,
        angle_input_units=expected_solar_altitude_units,
        angle_output_units="radians",  # Here in radians!
        verbose=verbose,
    )
    optical_air_mass_series = calculate_optical_air_mass_time_series(
        elevation=elevation,
        refracted_solar_altitude_series=refracted_solar_altitude_series,
        verbose=verbose,
    )
    # ^^^ --------------------------------- expects solar altitude in degrees!

    direct_normal_irradiance_series = calculate_direct_normal_irradiance_time_series(
        timestamps=timestamps,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        optical_air_mass_series=optical_air_mass_series,
        solar_constant=solar_constant,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        verbose=0,
    )

    # Mask conditions -------------------------------------------------------
    mask_solar_altitude_positive = solar_altitude_series_array > 0
    mask_not_in_shade = np.full_like(solar_altitude_series_array, True)  # Stub, replace with actual condition
    mask = np.logical_and.reduce((mask_solar_altitude_positive, mask_not_in_shade))

    # Initialize the direct irradiance series to zeros
    direct_horizontal_irradiance_series = np.zeros_like(solar_altitude_series_array)
    if np.any(mask):
        # direct_horizontal_irradiance_series = direct_normal_irradiance_series * np.sin(solar_altitude_series_array)
        direct_horizontal_irradiance_series[mask] = (
            direct_normal_irradiance_series * np.sin(solar_altitude_series_array)
        )[mask]

    if verbose == 4:
        debug(locals())

    results = {
            "Horizontal": direct_horizontal_irradiance_series,
    }
    if verbose > 1:
        extended_results = {
            'Normal': direct_normal_irradiance_series,
            "Air mass": np.array([x.value for x in optical_air_mass_series]),
            "Refracted alt.": np.array( [x.value for x in refracted_solar_altitude_series]) if apply_atmospheric_refraction else np.array(["-"]),
            "Altitude": solar_altitude_series_array,
        }
        results = results | extended_results

    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    print_irradiance_table_2(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        dictionary=results,
        title='Direct horizontal irradiance series',
        rounding_places=rounding_places,
        verbose=verbose,
    )

    return direct_horizontal_irradiance_series


@app.command('inclined-series', no_args_is_help=True)
def calculate_direct_inclined_irradiance_time_series_pvgis(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps],
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    direct_horizontal_component: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    nearest_neighbor_lookup: Annotated[bool, typer_option_nearest_neighbor_lookup] = False,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    surface_tilt: Annotated[Optional[float], typer_option_surface_tilt] = SURFACE_TILT_DEFAULT,
    surface_orientation: Annotated[Optional[float], typer_option_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: Annotated[List[float], typer_option_linke_turbidity_factor_series] = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SolarPositionModels.noaa,
    solar_incidence_model: Annotated[SolarIncidenceModels, typer_option_solar_incidence_model] = SolarIncidenceModels.jenco,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.milne,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the direct irradiance incident on a tilted surface [W*m-2] 

    This function implements the algorithm described by Hofierka
    :cite:`p:hofierka2002`.

    Notes
    -----
              B   ⋅ sin ⎛δ   ⎞                    
               hc       ⎝ exp⎠         ⎛ W ⎞
        B   = ────────────────     in  ⎜───⎟
         ic       sin ⎛h ⎞             ⎜ -2⎟           
                      ⎝ 0⎠             ⎝m  ⎠           
    """
    solar_incidence_series = model_solar_incidence_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        random_time_series=random_time_series,
        solar_incidence_model=solar_incidence_model,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    solar_incidence_series_array = np.array([x.value for x in solar_incidence_series])
    solar_altitude_series = model_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    solar_altitude_series_array = np.array([solar_altitude.radians for solar_altitude in solar_altitude_series])

    #

    if not direct_horizontal_component:
        print(f'Modelling irradiance...')
        direct_horizontal_irradiance_series = calculate_direct_horizontal_irradiance_time_series(
            longitude=longitude,  # required by some of the solar time algorithms
            latitude=latitude,
            elevation=elevation,
            timestamps=timestamps,
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
            solar_position_model=solar_position_model,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith,
            solar_time_model=solar_time_model,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_constant=solar_constant,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            rounding_places=rounding_places,
            verbose=0,  # no verbosity here by choice!
        )
    else:  # read from a time series dataset
        print(f'Reading from external dataset...')
        # time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        longitude_for_selection = convert_float_to_degrees_if_requested(longitude, 'degrees')
        latitude_for_selection = convert_float_to_degrees_if_requested(latitude, 'degrees')
        direct_horizontal_irradiance_series = select_time_series(
            time_series=direct_horizontal_component,
            longitude=longitude_for_selection,
            latitude=latitude_for_selection,
            timestamps=timestamps,
            start_time=start_time,
            end_time=end_time,
            convert_longitude_360=convert_longitude_360,
            nearest_neighbor_lookup=nearest_neighbor_lookup,
            inexact_matches_method=inexact_matches_method,
            tolerance=tolerance,
            mask_and_scale=mask_and_scale,
            in_memory=in_memory,
            verbose=verbose,
        )

    try:
        modified_direct_horizontal_irradiance_series = (
            direct_horizontal_irradiance_series
            * sine_solar_incidence_angle_series
            / sine_solar_altitude_series
        )
    except ZeroDivisionError:
        logging.error(f"Error: Division by zero in calculating the direct inclined irradiance!")
        print("Is the solar altitude angle zero?")
        # should this return something? Like in r.sun's simpler's approach?
        raise ValueError

    # "Simpler" way to calculate the inclined solar declination?
    if solar_incidence_model == 'PVGIS':

        # In the old C source code, the following runs if:
        # --------------------------------- Review & Add ?
            # 1. surface is NOT shaded
            # 3. solar declination > 0
        # --------------------------------- Review & Add ?

        try:
            angular_loss_factor_series = calculate_angular_loss_factor_for_direct_irradiance_series(
                    sine_solar_incidence_angle_series,
                    angle_of_incidence_constant = 0.155,
                    )
            direct_inclined_irradiance_series = modified_direct_horizontal_irradiance_series * angular_loss_factor
            print(f'Direct inclined irradiance series: {direct_inclined_irradiance_series} (based on PVGIS)')  # B0c

            return direct_inclined_irradiance

        # Else, the following runs:
        # --------------------------------- Review & Add ?
            # 1. surface is shaded
            # 3. solar declination = 0
        # --------------------------------- Review & Add ?
        except ZeroDivisionError as e:
            logging.error(f"Which Error? {e}")
            raise ValueError

    results = {
        "Direct": direct_inclined_irradiance_series,
    }
    if np.any(direct_inclined_irradiance_series < 0):
        print("[red]Warning: Negative values found in `direct_inclined_irradiance_series`![/red]")

    if verbose > 2:
        extended_results = {
            "Loss": 1 - angular_loss_factor_series if apply_angular_loss_factor else ['-'],
            "Horizontal": direct_horizontal_irradiance_series,
            'Incidence': convert_series_to_degrees_if_requested(solar_incidence_series_array, angle_output_units),
            'Tilt': convert_float_to_degrees_if_requested(surface_tilt, angle_output_units),
            'Orientation': convert_float_to_degrees_if_requested(surface_orientation, angle_output_units),
            'Altitude': convert_series_to_degrees_if_requested(solar_altitude_series_array, angle_output_units),
        }
        results = results | extended_results

    if verbose > 3:
        more_extended_results = {
            'Irradiance source': 'External data' if direct_horizontal_component else 'Model (Hofierka, 2002)',
            'Incidence algorithm': solar_incidence_model.value,
            'Positioning': solar_position_model.value,
            'Timing': solar_time_model.value,
            # "Shade": in_shade,
        }
        results = results | more_extended_results
    if verbose == 4:
        debug(locals())

