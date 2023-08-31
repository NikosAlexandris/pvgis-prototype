from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_noaa
from pvgisprototype.algorithms.pvis.fractional_year import calculate_fractional_year_pvis


def model_fractional_year(
):
    """ Model fractional year"""
    pass


def calculate_fractional_year(
):
    pass
    results = []
    for model in models:
        if model != SolarPositionModels.all:  # ignore 'all' in the enumeration
            fractional_year = model_fractional_year(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                model=model,
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
            )
            results.append({
                'Model': model.value,
                'Altitude': fractional_year.value,
                'Units': fractional_year.unit,  # Don't trust me -- Redesign Me!
            })

    return results
