"""
A function based on a C function named `optimizeSlopeAspect` defined in 
"""

from total_radiation import calculate_total_radiation

# from: rsun_standalone_hourly_opt.cpp
# function name: optimizeSlopeAspect
def optimise_slope_aspect(
        grid_geometry,
        sun_geometry_constants,
        sun_geometry_variables,
        sun_surface_geometry,
        top_of_atmosphere_direct_normal_irradiance,
        solar_constant,
        location,
        hourly_location_solar_attributes,
        horizon_heights,
        optimal_inclination,
        axis_tracking_type,
        efficiency,
        start_year,
        end_year,
        number_of_values_to_read
        ):
    """Optimise the inclination (slope) and orientation (aspect) angles for
    maximizing the output of a photovoltaic system over a specified time period.

    The function takes various input parameters
    and performs an iterative optimization process
    to find the optimal values for slope and aspect.

    Notes
    -----
    A breakdown of the main steps and variables in the function:

    1. Initialization:

       - Initialize variables and parameters, such as iteration counters, maximum iterations, delta (a small increment for numerical derivatives), tolerance, and initial values for slope and aspect.
       - Calculate the maximum and minimum slope values based on latitude.

    2. Calculate initial total radiation:

       - Update the geometry (slope and aspect) using the initial values.
       - Calculate the total radiation for the given geometry over the specified time period.

    3. Calculate derivatives:

       - Perturb the slope and aspect angles by delta and calculate the total radiation for each perturbed angle.
       - Use the perturbed values to calculate the derivatives of total radiation with respect to slope and aspect.

    4. Iterative optimization:

       - Enter a while loop that runs until a maximum number of iterations is reached or convergence is achieved.
       - Calculate second-order derivatives using perturbed slope and aspect angles.
       - Update the slope and aspect using the derivatives to find the new values.
       - Calculate the total radiation for the new geometry.
       - Check for convergence by calculating the magnitude of the derivative vector and comparing it to the tolerance.
       - If convergence is achieved, exit the loop.

    5. Handling non-convergence:

       - If the maximum number of iterations is reached or there are issues with convergence, use a stepwise method to search for the optimal slope and aspect angles.
       - Try different slope angles while keeping the aspect fixed and record the total radiation for each slope.
       - Select the slope angle that maximizes the total radiation.
       - Repeat the process for different aspect angles, trying to maximize the total radiation.
       - Fine-tune the slope angle further to optimize the result.

    6. Output:

       - Store the optimized slope and aspect angles in the "returnslope" and "returnaspect" variables, respectively.

    The function uses a combination of numerical optimization techniques, including derivatives and stepwise searching, to find the optimal slope and aspect angles for maximizing the PV output over the specified time period.
    """
    iterationProblem = False
    delta = 0.005
    iter = 0
    maxiter = 20
    new_slope = 0.0
    new_aspectt = 0.0
    minslope = 0.0
    maxslope = 0.0
    (
        total_radiation,
        total_radiation_minus_slope,
        total_radiation_plus_slope,
        total_radiation_minus_aspect,
        total_radiation_plus_aspect
    ) = 0.0, 0.0, 0.0, 0.0, 0.0
    (
        total_radiation_minus_slope_minus_aspect,
        total_radiation_minus_slope_plus_aspect,
        total_radiation_plus_slope_minus_aspect,
        total_radiation_plus_slope_plus_aspect 
    ) = 0.0, 0.0, 0.0, 0.0

    derivatives = [0.0, 0.0]
    doublederivatives = [0.0, 0.0, 0.0]
    tolerance = 100.0
    slope = pow(abs(location.latitude), 0.95)
    aspect = 180.0 if location.latitude < 0.0 else 0.0
    maxslope = slope + 10.0
    minslope = slope - 10.0

    # Initialize
    updateGeometryYear(
            slope,
            aspect,
            axis_tracking_type,
            location,
            grid_geometry,
            sun_geometry_constants,
            sun_geometry_variables,
            sun_surface_geometry,
            solar_constant,
            horizon_heights
            )

    # calcuate the total radiation
    total_radiation = calculate_total_radiation(
            sun_geometry_variables,
            sun_surface_geometry,
            top_of_atmosphere_direct_normal_irradiance,
            solar_constant,
            location,
            hourly_location_solar_attributes,
            horizon_heights,
            axis_tracking_type,
            efficiency,
            start_year,
            end_year,
            number_of_values_to_read
            )
    
    # Subtract delta from slope & recalculate total radiation
    updateGeometryYear(slope - delta, aspect, axis_tracking_type, location,
                       grid_geometry, sun_geometry_constants,
                       sun_geometry_variables, sun_surface_geometry,
                       solar_constant, horizon_heights)
    
    total_radiation_minus_slope = calculate_total_radiation( sun_geometry_variables,
                                               sun_surface_geometry,
                                               top_of_atmosphere_direct_normal_irradiance,
                                               solar_constant, location,
                                               hourly_location_solar_attributes,
                                               horizon_heights,
                                               axis_tracking_type, efficiency,
                                               start_year, end_year,
                                               number_of_values_to_read)
    
    # Add delta to slope & recalculate total radiation
    updateGeometryYear(slope + delta, aspect, axis_tracking_type, location,
                       grid_geometry, sun_geometry_constants,
                       sun_geometry_variables, sun_surface_geometry,
                       solar_constant, horizon_heights)
    
    total_radiation_plus_slope = calculate_total_radiation( sun_geometry_variables,
                                              sun_surface_geometry,
                                              top_of_atmosphere_direct_normal_irradiance,
                                              solar_constant, location,
                                              hourly_location_solar_attributes,
                                              horizon_heights,
                                              axis_tracking_type, efficiency,
                                              start_year, end_year,
                                              number_of_values_to_read)
    
    # Subtract delta from aspect & recalculate total radiation
    updateGeometryYear(slope, aspect - delta, axis_tracking_type, location,
                       grid_geometry, sun_geometry_constants,
                       sun_geometry_variables, sun_surface_geometry,
                       solar_constant, horizon_heights)
    
    total_radiation_minus_aspect = calculate_total_radiation( sun_geometry_variables,
                                                sun_surface_geometry,
                                                top_of_atmosphere_direct_normal_irradiance,
                                                solar_constant, location,
                                                hourly_location_solar_attributes,
                                                horizon_heights,
                                                axis_tracking_type, efficiency,
                                                start_year, end_year,
                                                number_of_values_to_read)
    
    # Add delta to aspect & recalculate total radiation
    updateGeometryYear(slope, aspect + delta, axis_tracking_type, location,
                       grid_geometry, sun_geometry_constants,
                       sun_geometry_variables, sun_surface_geometry,
                       solar_constant, horizon_heights)
    
    total_radiation_plus_aspect = calculate_total_radiation( sun_geometry_variables,
                                               sun_surface_geometry,
                                               top_of_atmosphere_direct_normal_irradiance,
                                               solar_constant, location,
                                               hourly_location_solar_attributes,
                                               horizon_heights,
                                               axis_tracking_type, efficiency,
                                               start_year, end_year,
                                               number_of_values_to_read)

    while tolerance > 0.001 and iter < maxiter:
        if iter > 0:
            if derivatives[0] != 0.0:
                new_slope = slope - derivatives[1] / derivatives[0]
            else:
                new_slope = slope

            if doublederivatives[0] != 0.0:
                new_aspectt = aspect - doublederivatives[1] / doublederivatives[0]
            else:
                new_aspectt = aspect

            # check if new_slope is outside the range
            if new_slope > maxslope or new_slope < minslope:
                new_slope = slope

            # check if new_aspectt is outside the range
            if new_aspectt > 360.0 or new_aspectt < -360.0:
                new_aspectt = aspect

            # update the geometry with the new values
            updateGeometryYear(new_slope, new_aspectt, axis_tracking_type,
                               location, grid_geometry, sun_geometry_constants,
                               sun_geometry_variables, sun_surface_geometry,
                               solar_constant, horizon_heights)

            # calculate total radiation for the new geometry
            total_radiation = calculate_total_radiation( sun_geometry_variables,
                                             sun_surface_geometry,
                                             top_of_atmosphere_direct_normal_irradiance,
                                             solar_constant, location,
                                             hourly_location_solar_attributes,
                                             horizon_heights,
                                             axis_tracking_type, efficiency,
                                             start_year, end_year,
                                             number_of_values_to_read)

        # calculate the partial derivatives
        derivatives[0] = (total_radiation_minus_slope - total_radiation_plus_slope) / (2.0 * delta)
        derivatives[1] = (total_radiation_minus_aspect - total_radiation_plus_aspect) / (2.0 * delta)

        # calculate the double derivatives
        doublederivatives[0] = (
                total_radiation_minus_slope_minus_aspect
                - total_radiation_plus_slope_minus_aspect
                - total_radiation_minus_slope_plus_aspect
                + total_radiation_plus_slope_plus_aspect
                ) / (4.0 * delta * delta)

        doublederivatives[1] = (
                total_radiation_minus_slope_minus_aspect
                - total_radiation_plus_slope_minus_aspect
                + total_radiation_minus_slope_plus_aspect
                - total_radiation_plus_slope_plus_aspect
                ) / (4.0 * delta * delta)

        doublederivatives[2] = (
                total_radiation_minus_slope_minus_aspect
                + total_radiation_plus_slope_minus_aspect
                - total_radiation_minus_slope_plus_aspect
                - total_radiation_plus_slope_plus_aspect
                ) / (4.0 * delta * delta)

        # update the geometry and radiation values for the next iteration
        slope = new_slope
        aspect = new_aspectt
        total_radiation_minus_slope = total_radiation_plus_slope
        total_radiation_minus_aspect = total_radiation_plus_aspect
        total_radiation_plus_slope = calculate_total_radiation(sun_geometry_variables,
                                                  sun_surface_geometry,
                                                  top_of_atmosphere_direct_normal_irradiance,
                                                  solar_constant, location,
                                                  hourly_location_solar_attributes,
                                                  horizon_heights,
                                                  axis_tracking_type,
                                                  efficiency, start_year,
                                                  end_year,
                                                  number_of_values_to_read)
        total_radiation_plus_aspect = calculate_total_radiation(sun_geometry_variables,
                                                   sun_surface_geometry,
                                                   top_of_atmosphere_direct_normal_irradiance,
                                                   solar_constant, location,
                                                   hourly_location_solar_attributes,
                                                   horizon_heights,
                                                   axis_tracking_type,
                                                   efficiency, start_year,
                                                   end_year,
                                                   number_of_values_to_read)
        
        # update the tolerance
        tolerance = abs(derivatives[0]) + abs(derivatives[1])

        iter += 1

    # Return the optimized slope and aspect
    return slope, aspect
