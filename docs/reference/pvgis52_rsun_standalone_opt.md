---
title: PVGIS 5.2 backend
tags:
  - Reference
  - PVGIS v5.2
  - Features
  - Functionality
  - Capabilities
  - Archived notes
---

PVGIS 5.2 is powered by `rsun_standalone_hourly_opt.c`.
The structure of its `main()` function is :

1.  Define  `main()`
   ``` c
   double hourlyConsumption[24];
   int main(
           int argc,
           char *argv[]
           )
   ```
   

2.  Initialise variables

   - Declare several variables of different types, including :
     `int`, `bool`, `double`, `float`, and `char` arrays.

   - Initialize some of the variables with specific values.

3.   Parse input arguments

  1. Check the number of command-line arguments (`argc`).
     If the number is less than 2, print a usage message
     and exit the program.

  2. Initialize some variables and assign default values to specific file paths:

     <!-- ```cpp -->
     <!-- slopeInput = 0.; -->
     <!-- day = 0; -->
     <!-- sprintf(consumptionFileName, "%s/battery/%s", DATA_PATH_BASE, DEFAULT_CONSUMPTION_FILE); -->
     <!-- sprintf(coefficientsFilename, "%s/pv/%s", DATA_PATH_BASE, DEFAULT_COEFFICIENTS_FILE); -->
     <!-- sprintf(powerMatrixFile, "%s/pv/%s", DATA_PATH_BASE, DEFAULT_POWER_MATRIX_FILE); -->
     <!-- sprintf(chargeMatrixFile, "%s/battery/%s", DATA_PATH_BASE, DEFAULT_CHARGE_MATRIX_FILE); -->
     <!-- ``` -->

  3. a `while` loop parses the command-line arguments using `getopt`:

     <!-- ```cpp -->
     <!-- while ((c = getopt(argc, argv, "B:a:c:d:e:f:g:h:j:i:k:m:n:o:p:s:t:u:v:x:y:z:blqr")) != -1) -->
     <!-- { -->
     <!--     switch (c) -->
     <!--     { -->
     <!--         // cases for different options -->
     <!--     } -->
     <!-- } -->
     <!-- ``` -->

  4. Handle different command-line options Inside the `switch` statement:
     (`-B`, `-a`, `-c`, `-d`, `-e`, `-f`, `-g`, `-h`, `-j`, `-i`, `-k`, `-l`,
     `-m`, `-n`, `-p`, `-s`, `-u`, `-v`, `-x`, `-o`, `-y`, `-z`, `-b`, `-q`,
     `-t`) and set corresponding variables or performs specific operations.
  
4.   Identify pixel row and column offsets

 1. Check which solar radiation database is requested.
    If it is none of SARAH or SARAH2,
    a _time offset_ is flagged to be set (through a function later on).
    Specifically,
    the code checks if the `databasePrefix` is either "sarah_" or "sarah2_".
    If it is not, `setUseTimeOffset(false)` is called.
    Otherwise, `setUseTimeOffset(true)` is called.
    This function uses a time offset based on the database prefix.

    > At this point, a row and column offset indices are set which point to the
    > pixel locatio to read data from all relevant datasets (elevatin, SIS, SID,
    > temperature, wind speed and direction)

 2. Depending on the user's request,
    sets flags or battery capacity related data are read
    (i.e. hourly consumption data, battery charge matrix, power matrix (?)).

 3. The variables `elevationFileNumberNS` and `elevationFileNumberEW`
    are calculated based on the `fixedData.latitude` and `fixedData.longitude` values.
    These calculations involve
    dividing the difference between $75$ and `fixedData.latitude` by `TILE_SIZE`,
    adding 1 to `elevationFileNumberNS`,
    and assigning `FIRST_EAST_TILE + floor(fixedData.longitude/TILE_SIZE)`
    to `elevationFileNumberEW`.

 4. Set some elevation file indices for the North-South and East-West
    directions.
    These in turn are used to identify the PVGIS _tile_
    within which the user-requested point is located.

    The variables `tileLatNorth` and `tileLonWest` are calculated
    using the `elevationFileNumberNS`, `elevationFileNumberEW`,
    and `TILE_SIZE` values.
    They represent the latitude and longitude of the top-left corner of a tile.

 5. The variables `rowoffset` and `coloffset` are calculated by
    subtracting `fixedData.latitude` from `tileLatNorth`
    and subtracting `tileLonWest` from `fixedData.longitude`, respectively.
    
5.   Select energy model

    !!! danger

        The next section performs several checks and sets a series of variables

    5. The `batterySize` is calculated by dividing `energyCapacity` by 12.

    6. If `useDetailedModel` is equal to 2, `useEfficiency` is set to false.

    7. The function `initEfficiencyCoeffsWind` is called with the `coefficientsFilename` as an argument. 
       It appears to initialize efficiency coefficients related to wind.
    
    
6.   Read elevation data

  1. Set `fixedData.elevation` to $0$
     and read fixed data from a file specified
     by `elevationFilename`, using

     - `rowoffset`
     - `coloffset`
     - `elevationFileNumberNS`
     - and `elevationFileNumberEW`.

  2. Calculate `arrayNumInt`
     by dividing $0.75001$ by `step` and adding 1.

7.   Use horizon data

  If horizon heights are supplied (`useHorizonData()` is set to `true`),
  the code performs the following steps:

  - Check if `horizonStep` is greater than `0`.
    If it is not, print an error message and exit.

  - Set the horizon number of intervals using `setHorizonNumInt()`
    and round `360.00001` divided by `horizonStep`.

  - Allocate memory for `horizonArray` based on the horizon number of
    intervals.

  - If the `horizonInfoType` is:

    - `1`,
    the code reads data from a file specified by `horizonFileName`
    using `ReadHorizonASCII()`.

    - `2`,
    read data from a file specified by `horizonFileName`
    by parsing comma-separated values and store them in `readHorizonArray`.
    Convert then the values from degrees to radians,
    rearrange the array, and assign it to `horizonArray`.

    - Otherwise, read data using `ReadHorizon()`
    based on the latitude, longitude, elevation file numbers,
    and the horizon number of intervals.


8. Set number of hours for iterations

  !!! danger

      Review Me!

  This section initializes the `hourlyVarData` array
  for each hour of each day for the specified range of years.

  1. The variable `numYears` is calculated as the difference between
     `yearEnd` and `yearStart`, plus 1.

  2. The variable `numValsToRead` is initialized to 0. 

     It is used to track the total number of values that need to be read.
     The loop iterates over the years from `yearStart` to `yearEnd` (inclusive)
     and increments `numValsToRead` by 8760 (number of hours in a non-leap year).
     If a year is divisible by 4 (leap year),
     an additional 24 values are added to account for the leap day.

  3. The variables `yearOffset` and `numDaysInYear` are initialized to 0.
     `yearOffset` tracks the offset in the `hourlyVarData` array,
      and `numDaysInYear` represents the number of days in a year
      (365 for non-leap years and 366 for leap years).

  4. The `hourlyVarData` is an array of `pointVarData` structure,
     dynamically allocated with a size of `numValsToRead`.

  5. The loop iterates over each year (`y`) from 0 to `numYears - 1`.

     It calculates the number of days in the current year (`numDaysInYear`)
     based on whether it is a leap year or not.
     If the current year (`yearStart + y`) is divisible by 4,
     it is considered a leap year,
     and `numDaysInYear` is set to 366.
     Else, otherwise, it remains 365.

  6. The inner loop iterates over each day of the current year (`i`)
     from 1 to `numDaysInYear`.

     For each day, it further iterates over each hour (`j`) from 0 to 23.

  7. Inside the innermost loop,
     the `day` field of the `hourlyVarData` structure at the corresponding index
     (`yearOffset + 24 * (i - 1) + j`) is set to the current day (`i`).

     > The `declination` field is commented out in the code.

  8. After the innermost loop completes,
     `yearOffset` is incremented by the product of 24 and `numDaysInYear`.
     It represents the offset for the next year's data.
    
9.   Read {term}`SIS` and {term}`SID` data, compute global irradiance

  !!! danger

      - reads `sis` and `sid` data, computes the difference between the values
        and stores them in the `hourlyVarData` array.

      - calculates the total irradiation by summing the `sis` values
        and assigns a value of $1$ to each element in the
        `spectralCorrectionValues` array.

  In detail

  1. The `sisVals` and `sidVals`
     arrays are dynamically allocated with sizes of `numValsToRead`.
     These arrays will store the values read from the data files.

  2. The `dailyName` string is formatted using `dailyPrefix`
     and `databasePrefix` to create the filename for the `sis` data file.

  3. The function `ReadTimeSeriesDataFileBZ2()`
     reads the data from the `sis` file,
     storing the values in the `sisVals` array.

     The function takes several parameters,
     includes the `sisVals` array, geographical information,
     year range, and filename.

  4. The `dailyName` string is formatted
     to create the filename for the `sid` data file.

  5. The function `ReadTimeSeriesDataFileBZ2()` reads data from the `sid` file,
     storing the values in the `sidVals` array.

  6. A variable `sisSum` is initialized to $0$.
     and then used to calculate the total irradiation from the `sis` values.

  7. A loop iterates over each value in `numValsToRead`.

     For each value,

     - the `beamCoefficient` field of the corresponding `hourlyVarData` structure 
       is set to the corresponding `sidVals` value,

     - and the `diffCoefficient` field is set to the difference
       between the corresponding `sisVals` and `sidVals` values.

  9. If the `sisVals` value for the current index is greater than 0,
     it is added to `sisSum`.

  10. The `sisVals` and `sidVals` arrays are freed using the `free()` function
      to release the memory allocated for them.

  11. A loop sets each value in the `spectralCorrectionValues` array to 1.
      This array has a size of 12.
    
10. Read spectral correction values, temperature & wind speed time series

  !!! danger

      This section reads temperature and wind speed data,
      assigns the values to the `hourlyVarData` array,
      and prepares for the calculation of geometry for the entire year.

  1. The code checks if `useEfficiency`, `useDetailedModel`,
     or `outputTemperatures` is true.
     If any of these conditions are met,
     the code proceeds to execute the following steps.

  2. A variable `readOK` is initialized to `0`
     and used to check if the reading of spectral data was successful.

  3. The variable `numTempToRead` is calculated as `numValsToRead`
     divided by `TEMPERATURE_INTERVAL`.

     ``` cpp
     int numTempToRead=numValsToRead/TEMPERATURE_INTERVAL;
     ```

  4. If `spectralCorrection` is true, the code attempts to read spectral correction values from a data file using the function `ReadDataFileFloat()`

     The filename and other parameters are provided to the function.
     If reading the file is successful (`readOK` is $0$),
     the spectral correction values are stored in the `spectralCorrectionValues` array.
     Otherwise, all values in the array are set to 1.

  5. An array `readTempVals` is dynamically allocated with a size of `(numTempToRead + 1)`.

     It will store the temperature values read from a data file.

  6. The `dailyName` string is formatted to create thefile name for the temperature data file.

  7. The function `ReadTimeSeriesDataFileBZ2()` is called to read the temperature data into the `readTempVals` array.

     The function takes several parameters, including geographical information, year range, time interval, and file name.

  8. Similarly, an array `readWindVals` is dynamically allocated with a size of `(numTempToRead + 1)`.

     It will store the wind speed values read from a data file.

  9. The `dailyName` string is formatted again to create the filename for the wind speed data file.

  10. The function `ReadTimeSeriesDataFileBZ2()` is called again to read the wind speed data into the `readWindVals` array.

  11. There is commented-out code that performs some calculations related to temperature elevation correction and hourly interpolation. However, this code has been removed and replaced with a simpler approach in the next step.

  12. Instead of performing the temperature elevation correction and hourly interpolation, the code directly assigns the read temperature and wind speed values to the corresponding fields in the `hourlyVarData` array. This is done in a loop that iterates over `numTempToRead`.

  13. The variable `numdays` is calculated as `numValsToRead` divided by 24, representing the number of days in the data.

  14. An array `radiationVals` is dynamically allocated with a size of `numValsToRead`.

      It will store the calculated radiation values.

  15. The function `calculateGeometryYear()` is called to calculate the geometry for the entire year.

      The function takes various parameters, including:
      - slope,
      - aspect,
      - tracking type,
      - location data,
      - and arrays for storing geometry information.
        
11.  Calculate solar geometry variables

12.  Optimise slope if requested
    !!! danger

        1. If `optimalAngle` is `1`.

           optimise the slope for a given aspect.

           1. Call `optimizeSlope()` with various parameters
           to calculate the optimal slope and store it the variable `calculatedSlope`.

           2. If `calculatedSlope` is very small (`< 0.01`)
           or the latitude close to `0`,
           indicating convergence problems or issues with the optimization,
           a small default slope value of `0.001` is assigned to `newslope`.

           3. If the calculated slope is valid, it is assigned to `newslope`.

           4. Call `updateGeometryYear()` to update the geometry variables
           based on the new slope using, however, the existing aspect value.

           > **Important** in this function is that it calculates the
           _solar incidence_ angle using the method presented by {cite}`Jenvco1992`
           {eq}`equation-for-solar-incidence-angle-jenvco-1992`.
    

        -   `optimizeSlope()`

13. Optimise slope and aspect if requested

    !!! danger

    2. If `optimalAngle` is `2`,
       optimise both the slope and aspect angles.

       - Call `optimizeSlopeAspect()` with various parameters
         to determine the optimal slope and aspect.

       - Store the calculated values in the variables `newslope` and `newaspect`.
    

14. Set slope and aspect depending on tracking type

    !!! danger

    3. Print the values of slope and azimuth depending on the `axisTrackingType`.

       `axisTrackingType` =

       - `0` indicates a fixed tilt system,
         thus print both the slope and azimuth.

       - `3` or `5` indicates a single-axis tracking system,
         thus print only the slope.

       - _any other value_ indicates a system without tracking,
       this do not print any of the angle values.
    

15.  Calculate total radiation

    !!! danger

        Finally, call the `calculate()` function
        with various parameters (geometry, data, and options)
        to calculate the total radiation and store it in the variable `totRad`.

        > **Important** in this function is that,
        unlike the `updateGeometryYear` and the `calculateGeometryYear` functions,
        it calculates the _solar incidence_ 
        based on an alternative method.
        That is, it does _not_ use method presented by {cite}`Jenvco1992`.
        This other method, uses a hardcoded angle of incidence (see `AOIConstants`)
        which does not account for a more realistic approximation of the sun's position.
    

    -   Calculate hourly radiation `joules_onetime()`
       `calculate()` calls the following `joules_onetime()` function :

       The function expects several input parameters like :
           `use_efficiency`, `temperature`, `wind_speed`,
           `solar_incidence`, `sun_geometry`, `sun_surface_geometry`, 
           `solar_radiation_variables`, `grid_geometry`, `horizon_heights`,
           and `hour_radiation_values`.

       and initialize various variables including arrays for
          `direct_radiation`, `diffuse_radiation` and `reflected_radiation`.
          to store calculated values.


       info "The function's algorithmic structure"

           1. If the sun is above the horizon
              (`solar_altitude > 0`)
              proceed with checking for low sun angles.

              1. If the sun's altitude is below 0.04
                 (`solar altitude < 0.04`)
                 which indicates very low sun angles,
                 the direct (beam) radiation is negligible and therefore
                 **set the direct horizontal irradiance** to zero.

              2. If the sun's altitude is above 0.04
                 (`solar altitude > 0.04`)
                 and the area is not in the shade,
                 **calculate the direct** (beam) **irradiance**
                 incident on a tilted surface.

           2. Calculate the _diffuse_ and _reflected_ irradiance
              (`drad_angle_irradiance()`)
              regardless of whether the area is in the shade or not.

           3. Calculate the _total_ irradiance
              as the **sum of** the direct, diffuse and reflected irradiance.

           4. If using efficiency coefficients is asked
              (`use_efficiency` is `True`),
              calculate the efficiency coefficient as the product of
              the _system efficiency_
              and the efficiency as a function of the temperature and wind speed.

           5. Else, set the efficiency coefficient to the system efficiency.

           6. Calculate the effective hourly radiation
              by applying the efficiency coefficient
              to the beam, diffuse, and reflected radiation.
       

16. Calculate system performance

  In this section, the code calculates and analyzes
  the performance of a PV system based on solar radiation data
  and energy consumption.

  !!! danger

      1. Initialization:

         - Various variables are declared, such as:

              - `powerWasted`,
              - `powerProduced`,
              - `posInYear`,
              - `powerOvershootMonth`,
              - `totalEnergyMonth`,
              - and `sumDays`.
         
         - The `sumDays` array is initialized with zeros.

         - Several arrays are initialized with zeros, including:

              - `monthCounts`,
              - `daysBatteryFullMonths`,
              - `daysBatteryEmptyMonths`,
              - `powerOvershootMonth`,
              - `totalEnergyMonth`

         - The `chargeHistogram` array is initialized with zeros.

         - The nominal power variable `nomPower`
         is calculated based on the `useDetailedModel` flag and `pvPower` value.

      2. Calculation loop:

         - The loop iterates `numValsToRead` times.
         - The `sumDays` array is populated by summing the radiation values
           (`radiationVals`) for each day.
         - Two nested loops iterate over the 12 months and set their respective
           counters to zero.

      3. Energy model
  

  1.  Set up
     !!! danger

         1. Detailed model calculation if `useDetailedModel` is `2`

         This section performs detailed calculations using a Newton-Raphson
         method for the given number of days `numdays`.

         - An inner loop (inside the parent loop) iterates over the 24 hours of each
           day.

         - Various calculations are performed to determine the power produced by the
           solar system, including the temperature coefficient, voltage, current, and
           polynomial fits.

         - The charge state of the battery is updated based on the power produced and
           consumed.

         - If the charge state exceeds the energy capacity, it is clamped to the
           maximum, and the excess power is considered wasted.

         - Statistics related to power overshot, power wasted, total energy, and
           charge state distribution are updated.
         
  2.   Select detailed model 2

      !!! danger

          2. Performance model calculation if `useDetailedModel` is `1`

          This section uses the `EnergyContributionPerformanceModelMPP` model to
          calculate the power contributions and losses for the given number of days.

         - An inner loop (inside the parent loop) iterates over the 24 hours of each
           day.
         
         - The performance model calculates the energy contribution, energy not
           captured, energy into and from the battery, and power missing.

         - Similar to the detailed model, statistics are updated based on these
           calculations.
          

          1. If there is radiation on the day,
             calculate the power produced
             using polynomial fits and a Newton-Raphson iterative process?

          2. Adjust the battery charge state
             based on the power produced and consumed

          3. Track battery's :
             - full and empty states,
             - power wasted,
             - total energy,
             - charge state

  3.   Select detailed model 1

      ```{danger}
      3. Simple model calculation if `useDetailedModel` is not `1` (n)or `2`
      ```

      1. Use the specific function `EnergyContributionPerformanceModelMPP()`
         to calculate energy contributions
         and adjust the battery charge state
    
      2. Track the battery's :
         - full and empty states,
         - power wasted,
         - total energy,
         - charge state

  4.   Select simple model

      1. Calculate the power produced based on radiation and nominal power

      2. Adjust the battery's charge state based on the power produced
         and consumed
      
      3. Track battery's :
         - full and empty states,
         - power wasted,
         - total energy,
         - charge state

  5. Statistics and metrics

     !!! danger

         In the final section of the main function,
         various statistics and metrics are printed.

         - `monthCounts` : the number of days for each month 

         - `count`: the total number of days simulated

         - `daysBatteryFullMonths` : the number of days with a full battery for each month

         - `100.*daysBatteryFull/count` : the percentage of days when the battery was full

         - `powerOvershoot/daysBatteryFull` **if** `daysBatteryFull > 0` :
           the average energy lost per day when the battery was full

           > Otherwise, a message indicating zero energy loss is printed.

         - `totalEnergyMonth[j]/monthCounts[j]` and `powerOvershootMonth[j]/monthCounts[j]` :
           the average potential energy production and energy lost per day for each month

         - `totalEnergy/count` : the average potential energy production per day

         - `100*powerOvershoot/totalEnergy` : the percentage of energy lost

         - `daysBatteryEmptyMonths` : the number of days with missing power for each month

         - The charge state histogram showing the number of occurrences for each charge state range
           (0-9%, 10-19%, ..., 90-99%).

         - `100.*totNumDaysEmpty/count` and `powerMissing/totNumDaysEmpty` **if** `totNumDaysEmpty > 0` :
           the percentage of days when the battery was empty
           and the average energy missing per day when the battery was empty 
           **if** there were days when the battery was empty

      Print performance details and statistics

17. Return `0` and close `main()`
