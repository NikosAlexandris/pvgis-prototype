# from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_noaa
# from pvgisprototype.algorithms.pvis.fractional_year import calculate_fractional_year_pvis
from pvgisprototype.constants import ALTITUDE_NAME, POSITION_ALGORITHM_NAME, UNIT_NAME


def model_fractional_year():
    """Model fractional year"""
    pass


def calculate_fractional_year(longitude,
                            latitude,
                            timestamp,
                            timezone,
                            model,
                            apply_atmospheric_refraction,
                            refracted_solar_zenith,
                            solar_time_model,
                            time_offset_global,
                            hour_offset,
                            perigee_offset,
                            eccentricity_correction_factor,
                            time_output_units,
                            angle_units,
                            angle_output_units,
                            models,
                            SolarPositionModels,
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
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                time_output_units=time_output_units,
                angle_units=angle_units,
                angle_output_units=angle_output_units,
            )
            results.append(
                {
                    POSITION_ALGORITHM_NAME: model.value,
                    ALTITUDE_NAME: getattr(fractional_year, angle_output_units),
                    UNIT_NAME: angle_output_units,  # Don't trust me -- Redesign Me!
                }
            )

    return results
