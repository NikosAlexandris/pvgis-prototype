import numpy as np
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.api.irradiance.direct import adjust_elevation
from pvgisprototype.validation.parameters import BaseTimestampSeriesModel
import typer
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.api.geometry.models import SolarTimeModels
from typing import Annotated
from typing import Optional
from typing import List
# from pvgisprototype.api.irradiance.extraterrestrial_time_series import calculate_extraterrestrial_normal_irradiance_time_series

from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer_parameters import typer_option_optical_air_mass_series
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
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
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT

from zoneinfo import ZoneInfo


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the direct solar radiation for a time series",
)


def correct_linke_turbidity_factor_time_series(
    linke_turbidity_factor_series,#: np.ndarray
):
    """Vectorized function to calculate the air mass 2 Linke atmospheric turbidity factor for a time series.
    
    Parameters:
    - linke_turbidity_factor_series (np.ndarray): The Linke turbidity factors as a numpy array.
    
    Returns:
    - np.ndarray: The corrected Linke turbidity factors as a numpy array.
    """
    
    return -0.8662 * linke_turbidity_factor_series


def calculate_refracted_solar_altitude_time_series(
    solar_altitude_series,#: np.ndarray,
    angle_input_units: str = 'degrees',
    angle_output_units: str = 'radians',
):
    """Adjust the solar altitude angle for atmospheric refraction for a time series of solar altitudes.
    
    This function is vectorized to handle arrays of solar altitudes.
    """
    if angle_input_units != "degrees":
        raise ValueError("Only degrees are supported for angle_input_units.")

    solar_altitude_values = np.array(
        [solar_altitude.value for solar_altitude in solar_altitude_series]
    )
    atmospheric_refraction = (
        0.061359
        * (
            0.1594
            + 1.123 * solar_altitude_values
            + 0.065656 * np.power(solar_altitude_values, 2)
        )
        / (
            1
            + 28.9344 * solar_altitude_values
            + 277.3971 * np.power(solar_altitude_values, 2)
        )
    )
    refracted_solar_altitude_values = solar_altitude_values + atmospheric_refraction
    refracted_solar_altitude_series = [
        RefractedSolarAltitude(value=value, unit="radians") for value in refracted_solar_altitude_values
    ]
    refracted_solar_altitude_series = [
        convert_to_degrees_if_requested(altitude, angle_output_units)
        for altitude in refracted_solar_altitude_series
    ]

    return refracted_solar_altitude_series


def calculate_optical_air_mass_time_series(
    elevation,#: np.ndarray,
    refracted_solar_altitude_series,#: np.ndarray,
    angle_units: str = 'radians',
):
    """Vectorized function to approximate the relative optical air mass for a time series."""
    optical_air_masse_series = adjust_elevation(elevation) / (
        np.sin(refracted_solar_altitude_series)
        + 0.50572
        * np.power((refracted_solar_altitude_series + 6.07995), -1.6364)
    )
    
    return optical_air_mass_series


def rayleigh_optical_thickness_time_series(
    optical_air_mass_series,#: np.ndarray,
):
    """ """
    rayleigh_thickness_series = np.zeros_like(optical_air_mass_series)
    smaller_than_20 = optical_air_mass_series <= 20
    larger_than_20 = optical_air_mass_series > 20
    rayleigh_thickness_series[smaller_than_20] = 1 / (
        6.6296
        + 1.7513 * optical_air_mass_series[smaller_than_20]
        - 0.1202 * np.power(optical_air_mass_series[smaller_than_20], 2)
        + 0.0065 * np.power(optical_air_mass_series[smaller_than_20], 3)
        - 0.00013 * np.power(optical_air_mass_series[smaller_than_20], 4)
    )
    rayleigh_thickness_series[larger_than_20] = 1 / (
        10.4 + 0.718 * optical_air_mass_series[mask2]
    )

    return rayleigh_thickness_series


@app.command('normal-series', no_args_is_help=True)
def calculate_direct_normal_irradiance_time_series(
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps],
    linke_turbidity_factor_series: Annotated[List[float], typer_option_linke_turbidity_factor_series],#: np.ndarray,
    optical_air_mass_series: Annotated[List[float], typer_option_optical_air_mass_series],#: np.ndarray,
    solar_constant: float = SOLAR_CONSTANT,
    days_in_a_year: float = DAYS_IN_A_YEAR,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_SERIES_FLAG_DEFAULT,
):
    """ """
    print(timestamps)
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_time_series(
            timestamps=timestamps,
            solar_constant=solar_constant,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            random_days=random_days,
        )
    )
    corrected_linke_turbidity_factors = correct_linke_turbidity_factor_time_series(
        linke_turbidity_factor_series
    )
    rayleigh_thickness_series = rayleigh_optical_thickness_time_series(
        optical_air_mass_series
    )
    direct_normal_irradiance_series = (
        extraterrestrial_normal_irradiance_series
        * np.exp(
            corrected_linke_turbidity_factors
            * optical_air_mass_series
            * rayleigh_thickness_series
        )
    )
    typer.echo(f'Direct normal irradiance series: {direct_normal_irradiance_series}')  # B0c

    return direct_normal_irradiance_series

import numpy.typing as npt

@app.command('horizontal-series', no_args_is_help=True)
def calculate_direct_horizontal_irradiance_time_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[BaseTimestampSeriesModel, typer_argument_timestamps],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,#Annotated[Optional[ZoneInfo], typer_option_timezone] = None,
    linke_turbidity_factor_series = None,#: Annotated[Optional[np.ndarray], typer_option_linke_turbidity_factor_series] = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365,  # 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[int, typer_option_verbose]= False,
) -> np.ndarray:
    """ """
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_time_model=solar_time_model,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        )
    
    # expects solar altitude in degrees! -------------------------------------
    expected_solar_altitude_units = 'degrees'
    solar_altitude_series_in_degrees = convert_series_to_degrees_if_requested(
            solar_altitude_series,
            expected_solar_altitude_units=expected_solar_altitude_units,  # Here!
            )
    # refracted_solar_altitude, refracted_solar_altitude_units = calculate_refracted_solar_altitude(
    refracted_solar_altitude_series = calculate_refracted_solar_altitude_time_series(
            solar_altitude_series=solar_altitude_series_in_degrees,
            angle_input_units=expected_solar_altitude_units,
            angle_output_units='radians',  # Here in radians!
            )
    optical_air_mass_series = calculate_optical_air_mass_time_series(
            elevation=elevation,
            refracted_solar_altitude_series=refracted_solar_altitude_series,
            angle_units='degrees',  # and Here!
            )
    # --------------------------------------expects solar altitude in degrees!
    direct_normal_irradiance_series = calculate_direct_normal_irradiance_time_series(
        timestamps=timestamps,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        optical_air_mass_series=optical_air_mass_series,
        solar_constant=solar_constant,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
    direct_horizontal_irradiance_series = direct_normal_irradiance_series * np.sin(solar_altitude_series)

    # table_with_inputs = convert_dictionary_to_table(locals())
    # console.print(table_with_inputs)
    typer.echo(f'Direct horizontal irradiance series: {direct_horizontal_irradiance_series}')  # B0c

    return direct_horizontal_irradiance_series
