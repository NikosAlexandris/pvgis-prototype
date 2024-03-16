def noaa(
    ctx: typer.Context,
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """
    """
    # Initialize with None ---------------------------------------------------
    user_requested_timestamp = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---
    
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        timezone = utc_zoneinfo
        typer.echo(f'Input timestamp & zone ({user_requested_timestamp} & {user_requested_timezone}) converted to {timestamp} for all internal calculations!')

    solar_position_calculations = calculate_noaa_solar_position(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    # Convert output timestamp back to the user-requested timezone
    try:
        timestamp = user_requested_timestamp
        timezone = user_requested_timezone
    except:
        print(f'I guess there where no user requested timestamp and zone')

    print_noaa_solar_position_table(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_position_calculations=solar_position_calculations, 
        rounding_places=rounding_places,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )


