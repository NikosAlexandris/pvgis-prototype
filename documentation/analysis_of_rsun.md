# Conversion to Python

## Programs & files

### `rsun_standalone_hourly_opt.cpp`

#### Functions

|       | Function                                | start line | end  | name in Python                                             | Remakrs                                                   |
|-------|-----------------------------------------|------------|------|------------------------------------------------------------|-----------------------------------------------------------|
| - [ ] | systemEfficiency()                      | 75         | 78   |                                                            |                                                           |
| - [ ] | setSystemEfficiency()                   | 79         | 82   |                                                            |                                                           |
| - [ ] | useTimeOffset()                         | 85         | 88   |                                                            |                                                           |
| - [ ] | setUseTimeOffset()                      | 89         | 92   |                                                            |                                                           |
| - [x] | ~~joules2~~ Not used!                   | 98         | 189  |                                                            |                                                           |
| - [x] | joules_onetime()                        | 192        | 284  | to calculate_hourly_radiation.py                           |                                                           |
| - [x] | EnergyContributionPerformanceModelMPP() | 286        | 396  | energy_contribution_performance_model_mpp.py               |                                                           |
| - [x] | optimizeSlope()                         | 400        | 532  | optimise_slope.py                                          |                                                           |
| - [x] | optimizeSlopeAspect()                   | 535        | 868  |                                                            |                                                           |
| - [ ] | main()                                  | 889        | 2013 |                                                            |                                                           |
| - [ ] | joules_with_unshadowed()                | 2025       | 2147 |                                                            |                                                           |
| - [x] | dateFromHour()                          | 2158       | 2205 | get_day_from_hour_of_year() in solar_geometry_variables.py |                                                           |
| - [ ] | updateGeometryYear()                    | 2208       | 2454 |                                                            |                                                           |
| - [x] | calculateGeometryYear()                 | 2456       | 2708 | solar_declination.py                                       | Among others, calculates solar declination based on Jenco |
| - [x] | calculateTotal()                        | 2711       | 2802 |                                                            |                                                           |
| - [x] | calculate()                             | 2805       | 3128 |                                                            |                                                           |

average_SD() -> average_standard_deviation.py

### `rsun_base.c`

#### Functions

| Function                                                           | Start line | End | Notes
|--------------------------------------------------------------------|------------|-----|---------------------------------------------------------------------------------------------------------------------|
| - [ ] brad.c                                                       |            |     | Not used                                                                                                            |
| - [x] brad_angle_irradiance.c                                      |            |     | Defines s0, uses sh : s0 == sh. sh stands for 'solar height/declination' != altitude ?                              |
| - [ ] brad_angle_loss.c                                            |            |     |                                                                                                                     |
| - [ ] brad_angle_loss_with_cs.c                                    |            |     |                                                                                                                     |
| - [ ] drad.c                                                       |            |     |                                                                                                                     |
| - [x] drad.cpp                                                     |            |     |                                                                                                                     |
| - [ ] drad_angle_irradiance.c                                      |            |     |                                                                                                                     |
| - [ ] drad_angle_loss.c                                            |            |     |                                                                                                                     |
| - [x] drad_angle_loss.cpp                                          |            |     |                                                                                                                     |
| - [ ] drad_angle_loss_with_cs.c                                    |            |     |                                                                                                                     |
| - [ ] efficiency.c                                                 |            |     |                                                                                                                     |
| - [ ] efficiency_ww.c                                              |            |     |                                                                                                                     |
| - [ ] initEfficiencyCoeffs.c                                       |            |     |                                                                                                                     |
| - [ ] initEfficiencyCoeffsWind.c                                   |            |     |                                                                                                                     |
| - [ ] SplinesMonthlyTemperature.c                                  |            |     |                                                                                                                     |
| - [x] calculateAngleLoss.c                                         |            |     | Calculates loss to direct horizontal irradiance due to solar declination. Hardcodes incidence angle (AOIConstants)! |
| - [x] calculate_angle_loss.c                                       |            |     | Variable                                                                                                            |
| - [x] com_declin.c                                                 |            |     | Inverts sign of calculated declination due to trigonometry mathematical error!                                      |
| - [x] com_par.c                                                    |            |     | Simpler approximations. How do they compare with others?                                                            |
| - [x] com_par_const.c                                              |            |     |                                                                                                                     |
| - [x] com_sol_const.c                                              |            |     |                                                                                                                     |
| - [ ] correctTemperatureElevation.c                                |            |     |                                                                                                                     |
| - [x] dateFromHour.c                                               |            |     | Complex, not needed                                                                                                 |
| - [ ] dni_rad.c                                                    |            |     |                                                                                                                     |
| - [ ] imageTimeOffset.c                                            |            |     | Complicated calculation of a time offset that adds up to the hour angle for the estimation of solar time            |
| - [x] lumcline2.c                                                  |            |     | Calculates the solar declination based on Jenco                                                                     |
| - [ ] rearrangeHorizon.c                                           |            |     |                                                                                                                     |
| - [ ] satgeo.c                                                     |            |     |                                                                                                                     |
| - [ ] satgeomsgnew.c                                               |            |     |                                                                                                                     |
| - [ ] slotHourOffset.c                                             |            |     |                                                                                                                     |
| - [ ] small_functions_from_start_and_before_calculate_angle_loss.c |            |     |                                                                                                                     |
| - [ ] temperature.c                                                |            |     |                                                                                                                     |

## Reading the source code

This section analysis thoroughly major functions of `rsun3`.

### The `optimizeSlope` function

``` c
double optimizeSlope(
        double aspectInput,
        struct GridGeometry *gridGeom,
        struct SunGeometryConstDay *sunGeom,
        struct SunGeometryVarDay *sunVarGeom,
        struct SunGeometryVarSlope *sunSlopeGeom,
        double *DNI_TOA,
        double *s0,
        struct pointData fixedData,
        struct pointVarData *hourlyVarData,
        double *horizonArray,
        int optimalAngle,
        int axisTrackingType,
        bool useEfficiency,
        int startYear,
        int endYear,
        int numValsToRead
        )
{
    bool iterationProblem=false;
    int iter=0;
    int maxiter=20;
    double slopediff=0.5;
    double newslope;
    double totRad, totRadMinus, totRadPlus;
    double derivative, doublederivative;
    double tolerance=100.;
    double slope=pow(fabs(fixedData.latitude),0.9);
    
    // Initialize
    
    Calculate geometry variables for `slope` -> 
    
        with parameters:
            aspectInput, axisTrackingType,
            fixedData,gridGeom, sunGeom,
            sunVarGeom, sunSlopeGeom,
            s0, horizonArray
    
    Calculate total radiation using the updated geometry variables

        with parameters:

            sunVarGeom, sunSlopeGeom,
            DNI_TOA, s0, fixedData,
            hourlyVarData,
            horizonArray, axisTrackingType,
            useEfficiency, startYear,
            endYear, numValsToRead

    Calculate geometry variables and total radiation "minus"
    for `slope - slopediff` with same parameters as above
    
    Calculate geometry variables and total radiation "plus"
    for `slope + slopediff` with same parameteres as above

    Calculate the derivative of:

        total radiation plus - total radiation "minus" / 2 * slopediff

    while(iter<maxiter)
    {
    
        Calculate the double derivative of:

        total radiation "plus" + total radiation "minus" - 2 * total radiation)
        -----------------------------------------------------------------------
                                        `slopediff`^2

        Calculate `newslope` = `slope` - derivative / double derivative

        if((newslope<-5.)||(newslope>90.))
        {
            // Better try the stepwise method
            newslope=pow(fabs(fixedData.latitude),0.9);
            iterationProblem=true;
            break;
        }

        updateGeometryYear(newslope, aspectInput, axisTrackingType, fixedData,gridGeom, sunGeom,
                sunVarGeom, sunSlopeGeom, s0, horizonArray);
        totRad=calculateTotal( sunVarGeom,sunSlopeGeom,DNI_TOA,s0,fixedData, hourlyVarData,
                horizonArray,
                axisTrackingType, 
                useEfficiency,startYear, endYear, numValsToRead );
        
        updateGeometryYear(newslope-slopediff, aspectInput, axisTrackingType, fixedData,gridGeom, sunGeom,
                sunVarGeom, sunSlopeGeom, s0, horizonArray);
        totRadMinus=calculateTotal( sunVarGeom,sunSlopeGeom,DNI_TOA,s0,fixedData, hourlyVarData,
                horizonArray,
                axisTrackingType, 
                useEfficiency,startYear, endYear, numValsToRead );
        
        updateGeometryYear(newslope+slopediff, aspectInput, axisTrackingType, fixedData,gridGeom,
                sunGeom, sunVarGeom, sunSlopeGeom, s0, horizonArray);
        totRadPlus=calculateTotal( sunVarGeom,sunSlopeGeom,DNI_TOA,s0,fixedData, hourlyVarData,
                horizonArray,
                axisTrackingType, 
                useEfficiency,startYear, endYear, numValsToRead );

        derivative=(totRadPlus-totRadMinus)/(2.*slopediff);
        if((fabs(derivative)<tolerance)||((totRad>totRadPlus)&&(totRad>totRadMinus)))
        {
            break;
        }
        slope=newslope;
        iter++;	
    }
    if((iter>=maxiter)||iterationProblem)
    {
        double oldTotRad,newTotRad;
        double direction;
        // Do the search the old-fashioned way, one step at a time.
        oldTotRad=totRad;
        if(totRadPlus>totRad)
        {
            newTotRad=totRadPlus;
            direction=1.;
        }
        else
        {
            newTotRad=totRadMinus;
            direction=-1.;
        }
        while(newTotRad>oldTotRad&&(newslope>-5.)&&(newslope<90.))
        {
            oldTotRad=newTotRad;
            newslope+=direction;
            updateGeometryYear(newslope, aspectInput, axisTrackingType, fixedData,gridGeom, sunGeom,
                    sunVarGeom, sunSlopeGeom, s0, horizonArray);

            newTotRad=calculateTotal( sunVarGeom,sunSlopeGeom,DNI_TOA,s0,fixedData, hourlyVarData,
                    horizonArray,
                    axisTrackingType, 
                    useEfficiency,startYear, endYear, numValsToRead );
        }
        return newslope-direction;
    }
    //	printf("#Number of iterations: %d\n", iter);
    return newslope;
}
```

### The `main` function

PVGIS evaluates and tracks the performance of a solar power system.
The superset algorithm that powers PVGIS
is programmed in the `main()` function
in the `rsun_standalone_hourly_opt.cpp` file.
It is complex
and makes use of different models of power calculations,
each suited to different use cases.


#### Overview

It does the following:

1. define the `main()` function

2. initialise variables

3. parse input arguments

4. identify pixel row and column offsets

5. select energy model

6. read elevation data

7. use horizon data

8. set number of hours for iterations

9. read SIS and SID data,
   compute global irradiance

10. read :
    - spectral correction values
    - temperature time series
    - wind speed time series

11. calculate solar geometry variables

12. optimise slope if requested

13. optimise slope and aspect if requested

14. set slope and aspect depending on tracking type

15. calculate total radiation

16. calculate system performance

    1. set up

    2. select detailed model 2

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

    3. select detailed model 1

        1. Use the specific function `EnergyContributionPerformanceModelMPP()`
           to calculate energy contributions
           and adjust the battery charge state
      
        2. Track the battery's :
           - full and empty states,
           - power wasted,
           - total energy,
           - charge state

    4. select simple model

        1. Calculate the power produced based on radiation and nominal power

        2. Adjust the battery's charge state based on the power produced
           and consumed
        
        3. Track battery's :
           - full and empty states,
           - power wasted,
           - total energy,
           - charge state

    5. print performance details and statistics

17. close the `main()` function


#### Analysis

##### Initialise variables

The beginning of the `main` function

- declares several variables of different types, including :
  `int`, `bool`, `double`, `float`, and `char` arrays.

- initializes some of the variables with specific values

- and parses command-line arguments.

  1. Checks the number of command-line arguments (`argc`).

    If the number is less than 2, it prints a usage message and exits the program.

  2. Initializes some variables and assigns default values to specific file paths:

  ```cpp
  slopeInput = 0.;
  day = 0;
  sprintf(consumptionFileName, "%s/battery/%s", DATA_PATH_BASE, DEFAULT_CONSUMPTION_FILE);
  sprintf(coefficientsFilename, "%s/pv/%s", DATA_PATH_BASE, DEFAULT_COEFFICIENTS_FILE);
  sprintf(powerMatrixFile, "%s/pv/%s", DATA_PATH_BASE, DEFAULT_POWER_MATRIX_FILE);
  sprintf(chargeMatrixFile, "%s/battery/%s", DATA_PATH_BASE, DEFAULT_CHARGE_MATRIX_FILE);
  ```

  3. a `while` loop parses the command-line arguments using `getopt`:

   ```cpp
   while ((c = getopt(argc, argv, "B:a:c:d:e:f:g:h:j:i:k:m:n:o:p:s:t:u:v:x:y:z:blqr")) != -1)
   {
       switch (c)
       {
           // cases for different options
       }
   }
   ```

   4. Inside the `switch` statement,
   it handles different command-line options
   (`-B`, `-a`, `-c`, `-d`, `-e`, `-f`, `-g`, `-h`, `-j`, `-i`, `-k`, `-l`, `-m`, `-n`, `-p`, `-s`, `-u`, `-v`, `-x`, `-o`, `-y`, `-z`, `-b`, `-q`, `-t`)
   and sets corresponding variables or performs specific operations.

##### Various checks

The next section performs several checks and sets a series of variables

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

-. Depending on the user's request,
   sets flags or battery capacity related data are read
   (i.e. hourly consumption data, battery charge matrix, power matrix (?)).

2. The variables `elevationFileNumberNS` and `elevationFileNumberEW`
   are calculated based on the `fixedData.latitude` and `fixedData.longitude` values.
   These calculations involve
   dividing the difference between $75$ and `fixedData.latitude` by `TILE_SIZE`,
   adding 1 to `elevationFileNumberNS`,
   and assigning `FIRST_EAST_TILE + floor(fixedData.longitude/TILE_SIZE)`
   to `elevationFileNumberEW`.

3. Set some elevation file indices for the North-South and East-West
   directions.
   These in turn are used to identify the PVGIS _tile_
   within which the user-requested point is located.

   The variables `tileLatNorth` and `tileLonWest` are calculated
   using the `elevationFileNumberNS`, `elevationFileNumberEW`,
   and `TILE_SIZE` values.
   They represent the latitude and longitude of the top-left corner of a tile.

4. The variables `rowoffset` and `coloffset` are calculated by
   subtracting `fixedData.latitude` from `tileLatNorth`
   and subtracting `tileLonWest` from `fixedData.longitude`, respectively.

5. The `batterySize` is calculated by dividing `energyCapacity` by 12.

6. If `useDetailedModel` is equal to 2, `useEfficiency` is set to false.

7. The function `initEfficiencyCoeffsWind` is called with the `coefficientsFilename` as an argument. 
   It appears to initialize efficiency coefficients related to wind.

##### More checks

1. `printSystemPerformance`

   - If the variable `printSystemPerformance` is true,
     the code reads hourly consumption data
     from a file specified by `consumptionFileName`.

   - If the reading is unsuccessful
     (the return value of `ReadASCIIOrString()` is not 0),
     an error message is printed and the program exits.
   
   - Otherwise, the `hourlyConsumption` array is populated
     by multiplying each element of `hourlyConsumptionRead`
     with `energyConsumption`.

2. `useDetailedModel`

   - If `useDetailedModel` is greater than 0,
     the code reads charge matrix data from a file
     specified by `chargeMatrixFile` and initializes the corresponding variables
     - `chargeCurrents`,
     - `chargeStates`,
     - `chargeMatrix`
     - `batterySize`
     - and `batteryCutoff`

   - If `useDetailedModel` is equal to 2,
     the code reads matrix data from a file specified by `powerMatrixFile`
     and initializes the following variables
     - `irradiances`,
     - `temperatures`,
     - `voltages`,
     - `powerMatrix`

  - If `optimalAngle` is true and `axisTrackingType` is either $2$, $1$, or $4$,
    an error message is printed indicating that optimum angles
    can only be calculated for tracking types $3$ and $5$.
    The program then exits.

3. The code sets `fixedData.elevation` to $0$ and reads fixed data from a file specified by `elevationFilename`, using

   - `rowoffset`
   - `coloffset`
   - `elevationFileNumberNS`
   - and `elevationFileNumberEW`.

6. The variable `arrayNumInt` is calculated by dividing $0.75001$
   by `step` and adding 1.

##### Use of horizon heights

If horizon heights are supplied (`useHorizonData()` is set to `true`),
the code performs the following steps:

- Checks if `horizonStep` is greater than `0`.
  If it is not, an error message is printed, and the program exits.

- Sets the horizon number of intervals using `setHorizonNumInt()`
  and rounds `360.00001` divided by `horizonStep`.

- Allocates memory for `horizonArray` based on the horizon number of intervals.

- Depending on the `horizonInfoType`:

    - If it is `1`,
    the code reads data from a file specified by `horizonFileName`
    using `ReadHorizonASCII()`.

    - If it is `2`,
    the code reads data from a file specified by `horizonFileName`
    by parsing comma-separated values and storing them in `readHorizonArray`.
    It then converts the values from degrees to radians,
    rearranges the array, and assigns it to `horizonArray`.

    - Otherwise, the code reads data using `ReadHorizon()`
    based on the latitude, longitude, elevation file numbers,
    and the horizon number of intervals.

##### Number of hourly values to consider

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

##### Read `SIS` and `SID` data

This section 

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

##### Read temperature & wind speed

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

##### Calculate solar declination

> - `sh` input to `brad_angle_irradiance()`
> <-- `s0` from `joules_onetime()`
> <-- from `calculate()` 
> <-- from `calculateTotal()`

`s0` and, then, the `sh`
is the solar _height_ or _declination_
input argument to `brad_angle_irradiance`.
It is **not** the solar _altitude_.

`s0` is the input to :

```
brad_angle_irradiance(
                    s0,
                    &bh,
                    sunVarGeom,
                    sunRadVar,
                    beam_values
                    );
```

which corresponds to `sh` in its definition :

```
double brad_angle_irradiance(
        double sh,
        double *bh,
        struct SunGeometryVarDay *sunVarGeom,
        struct SolarRadVar *sunRadVar,
        double *radiations
        )
```

`s0` comes from :

```
/* Calculate at various inclinations, start with 0. */
        joules_onetime(
                useEfficiency,
                temperature,
                windSpeed,
                s0[geomPos],
                sunVarGeom+geomPos,
                sunSlopeGeom+geomPos,
                &sunRadVar,
                &gridGeom,
                horizonArray,
                dayRadiationVals
                );
```

whose definition is


```
void joules_onetime(
        bool useEfficiency,
        double temperature,
        double windSpeed,
        double s0,
        struct SunGeometryVarDay *sunVarGeom,
        struct SunGeometryVarSlope *sunSlopeGeom,
        struct SolarRadVar *sunRadVar,
        struct GridGeometry *gridGeom,
        double *horizonArray,
        double *hourRadiationVals
        )
```

which is used in :

```
double calculate(
        struct SunGeometryVarDay *sunVarGeom,
        struct SunGeometryVarSlope *sunSlopeGeom,
        double *DNI_TOA,
        double *s0,
        struct pointData fixedData,
        struct pointVarData *varData,
        double *horizonArray,
        int optimalAngle,
        int axisTrackingType,
        bool useEfficiency,
        int outputOption,
        int startYear,
        int endYear,
        int numVals,
        float *spectralCorrectionValues,
        double *radiationVals
        )
```

which in turn is used in `main()`
where `s0` is initialised as :

    `double s0[8760];`

and is then populated when runnning :

```
calculateGeometryYear(
            slopeInput,
            aspectInput,
            axisTrackingType,
            fixedData,
            &gridGeom,
            &sunGeom,
            sunVarGeom,
            sunSlopeGeom,
            DNI_TOA,
            s0,
            horizonArray
    );
```

during a for loop :

```
for(int pos=0; pos < 8760; pos++)
```

by the `lumcline2()` function! 


##### Tilt & orientation

This section of the code 

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

   > **Important** in this function is that
   it calculates the _solar declination_ using the method presented by Jenco.

2. If `optimalAngle` is `2`,
   optimise both the slope and aspect angles.

   - Call `optimizeSlopeAspect()` with various parameters
     to determine the optimal slope and aspect.

   - Store the calculated values in the variables `newslope` and `newaspect`.

3. Print the values of slope and azimuth depending on the `axisTrackingType`.

   `axisTrackingType` =

   - `0` indicates a fixed tilt system,
     thus print both the slope and azimuth.

   - `3` or `5` indicates a single-axis tracking system,
     thus print only the slope.

   - _any other value_ indicates a system without tracking,
   this do not print any of the angle values.

##### Total radiation

Finally, call the `calculate()` function
with various parameters (geometry, data, and options)
to calculate the total radiation and store it in the variable `totRad`.

> **Important** in this function is that,
unlike the `updateGeometryYear` and the `calculateGeometryYear` functions,
it calculates the _solar declination_ based on an alternative method.
That is, it does not use method presented by Jenco.
This other method, uses a hardcoded angle of incidence (see `AOIConstants`)
which does not account for a more realistic approximation of the sun's position.

#####  Performance & energy consumption

This section of the code calculates and analyzes the performance of a PV system
based on solar radiation data and energy consumption.

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

    1. Detailed model calculation if `useDetailedModel` is `2`

    This section performs detailed calculations using a Newton-Raphson method
    for the given number of days `numdays`.

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

    2. Performance model calculation if `useDetailedModel` is `1`

    This section uses the `EnergyContributionPerformanceModelMPP` model to
    calculate the power contributions and losses for the given number of days.

   - An inner loop (inside the parent loop) iterates over the 24 hours of each
     day.
   
   - The performance model calculates the energy contribution, energy not
     captured, energy into and from the battery, and power missing.

   - Similar to the detailed model, statistics are updated based on these
     calculations.

    3. Simple model calculation if `useDetailedModel` is not `1` (n)or `2`

###### Energy model

If `useDetailedModel` is equal to `2`,
the code executes the detailed model calculation.

1. Initialization:

   - Various variables are declared to store intermediate values during the
   calculations, such as:

   `currFuncVal`,
   `voltFuncVal`,
   `currFuncDeriv`,
   `voltFuncDeriv`,
   `loadCurrent`,
   `locRadiation`,
   `locTemperature`,
   `residual`,
   `voltage`,
   `current`,
   `newcurrent`,
   `newvoltage`,
   `cableResistance`,
   `dampingFactor`,
   and `funcval`.

2. Loop over days:

   - The loop iterates `numdays` times.
   
   - If the sum of radiation values for a particular day (`sumDays[i]`)
     is less than or equal to `0`, the loop skips to the next iteration.
   
   - An inner loop iterates over the 24 hours of each day.

3. Power production calculation:

   - Check if the `locRadiation` value (radiation for the current hour)
     is below a the cutoff value `RADIATION_CUTOFF`.

   - If the radiation is below the cutoff,
     the `powerProduced` is set to `0`, indicating no power is produced.
   
   - If the radiation is above the cutoff,
     perform a detailed power production calculation
     using the Newton-Raphson method.
   
   - The calculations involve
     updating the voltage and current values iteratively
     until the convergence criterion `residual` is met.
   
   - The power produced is calculated as the product of voltage and current.

4. Battery charge state update:

   - The `chargeState` is updated
     by adding the power produced and subtracting the hourly consumption.

   - If the charge state is negative, indicating insufficient energy,
     the battery is considered empty for the day.
     The deficit power is added to the `powerMissing` variable,
     and the charge state is set to zero.
   
   - If the charge state exceeds the energy capacity,
     indicating excess energy, the battery is considered full for the day.
     The excess power is calculated as the difference between the charge state
     and the energy capacity,
     and it contributes to the `powerOvershoot` variable.
     The charge state is clamped to the energy capacity.
   
   - If the charge state is within the capacity, no power is wasted.

5. Accumulating statistics:

   - The `totalEnergy` is updated by adding the net power produced
     (accounting for wasted power).

   - The monthly statistics `totalEnergyMonth` and `powerOvershootMonth`
     are updated.

###### Energy Contribution Performance Model MPP

> This section calculates the energy contribution from the PV system and losses, tracks the battery charge state, and accumulates statistics related to the battery's fullness, emptiness, energy production, and energy loss for each day and month for the given number of days based on a performance model (`EnergyContributionPerformanceModelMPP`)

If `useDetailedModel` is equal to 1,
run a different detailed calculation model.

1. Initialization:

   - Various variables are declared to store intermediate values during the calculations, such as
   - `energyContribution`,
   - `energyNotcaptured`,
   - `energyIntoBattery`,
   - `energyFromBattery`,
   - and `powerMissing`

2. Loop over days:

   - The loop iterates `numdays` times.
   - Inside the loop, there is an inner loop iterating over the $24$ hours for each day.

3. Power production calculation:

   - The function (`EnergyContributionPerformanceModelMPP`) calculates the energy contribution from the PV system for a given hour.

   - The function takes into account the
     - nominal power of the PV system,
     - battery size,
     - hourly consumption,
     - radiation,
     - charge states,
     - and charge currents

   - The function calculates various parameters such as
     - energy contribution,
     - energy not captured,
     - energy into the battery,
     - energy from the battery,
     - and power missing 

   - If the battery is empty for the day, the function returns a value of $1$

4. Battery charge state update:

   - If the battery is empty for the day, the `batteryEmptyThisDay` variable is set to true.

   - If there is energy not captured (indicating excess power that cannot be stored),
     the battery is considered full for the day.
     The excess power contributes to the `powerOvershoot` variable,
     and the charge state is set to the energy capacity.

   - The `totalEnergy` is updated by adding the energy contribution.

5. Accumulating statistics:

   - The monthly statistics (`totalEnergyMonth` and `powerOvershootMonth`) are updated.

   - The loop also counts the number of days the battery is full (`daysBatteryFull`) and the number of days the battery is empty for each month (`daysBatteryEmptyMonths`).

   - The overall statistics, such as the number of days in each month (`monthCounts`), total number of days, percentage of days the battery was full, average energy lost when the battery was full, average potential energy production per month, average energy lost per month, average potential energy production, and percentage of energy lost, are printed at the end.

###### Simple model

> This section simulates power generation, consumption, and battery behavior for a specific number of days, accumulating statistics such as total energy produced, battery full/empty days, and charge state distribution.

When `useDetailedModel` is neither 2 nor 1,
the code uses a simpler model.
It iterates over the number of days `numdays`
and Within each iteration of the loop,
the code calculates
the power production,
the consumption,
and battery charge state
for each hour of the day.

1. The variables `batteryFullThisDay` and `batteryEmptyThisDay` are set to
   false at the beginning of each day.

2. A nested loop iterates over each hour of the day (from 0 to 23).

   - Power production is calculated based on the radiation values and the
     nominal power:
   
     ``` c
     powerProduced = radiationVals[24*i+h]*nomPower;
     ```

   - The charge state of the battery is updated by adding the power produced
     and subtracting the hourly consumption:

     ``` c
     chargeState+=powerProduced-hourlyConsumption[h];
     ```

   - If the charge state

     - is negative (indicating that the battery is empty),
     the `batteryEmptyThisDay` flag is set to true,
     the deficit power is added to `powerMissing`,
     and the charge state is set to `0`.

       ``` c
       if(chargeState<0)
       {
           batteryEmptyThisDay=true;
           powerMissing-=chargeState;
           chargeState=0.;
       }
       ```

     - exceeds the energy capacity of the battery
     (indicating that the battery is full),
     the `batteryFullThisDay` flag is set to true,
     the excess power is calculated,
     and the charge state is capped at the energy capacity.

       ```
       if(chargeState>energyCapacity)
       {
           batteryFullThisDay=true;
           powerWasted = chargeState-energyCapacity;
           powerOvershoot+=powerWasted;
           powerOvershootMonth[month]+=powerWasted;
           chargeState=energyCapacity;
       }
       ```

   - Else, if the charge state is within the energy capacity, no power is wasted.

     ```
     else
     {
         powerWasted = 0.;
     }
     ```

4. The total energy produced minus the wasted power is accumulated in `totalEnergy` and `totalEnergyMonth[month]`.

5. The charge state is used to determine an index for updating a charge histogram.

   ```
   totalEnergy+= powerProduced - powerWasted;
   totalEnergyMonth[month] += powerProduced - powerWasted;
   index = (int) (10*(chargeState/energyCapacity));
   if(index==10)
       index--;
   chargeHistogram[index]++;
   ```

6. After the loop over hours, various counters and flags are updated based on the state of the battery for the day.

     ```
     count++;
     monthCounts[month]++;
     if(batteryFullThisDay)
     {
         daysBatteryFull++;
         daysBatteryFullMonths[month]++;
     }
     if(batteryEmptyThisDay)
     {
         daysBatteryEmptyMonths[month]++;
     }
     ```

   - The `posInYear` counter is incremented, indicating progress within the year.

   - If `posInYear` reaches the last day of the current month (`lastDayInMonth[month]`), the month is incremented.

   - If `posInYear` reaches 365, indicating the end of the year, `posInYear` is reset to 0 and `month` is reset to 0.

     ```
     posInYear++;
     
     if(posInYear==lastDayInMonth[month])
     {
         month++;
     }
     if(posInYear==365)
     {
         posInYear=0;
         month=0;
     }
     ```

##### Statistics and metrics

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

```
for(int j=0;j<12;j++)
{
    printf("Number of days in month %d: %d \n", 
            j+1, monthCounts[j]);
}


printf("Total number of days: %d\n", count);
for(int j=0;j<12;j++)
{
    printf("Number of days with battery full in month %d: %d \n",
            j+1, daysBatteryFullMonths[j]);
}

printf("Percentage of days the battery was full: %.2f\n", 
        100.*daysBatteryFull/count);
if(daysBatteryFull>0)
{
    printf("Average energy lost when battery was full: %.2f Wh/day\n", 
            powerOvershoot/daysBatteryFull);
}

else
{
    printf("Average energy lost when battery was full: 0.0 Wh/day\n");
}

int totNumDaysEmpty=0;
for(int j=0;j<12;j++)
{
    printf("Average potential energy production and energy lost for month %d: %.2f, %.2f Wh/day\n", 
            j+1, totalEnergyMonth[j]/monthCounts[j], powerOvershootMonth[j]/monthCounts[j]);
}

printf("Average potential energy production: %.2f Wh/day\n", totalEnergy/count);
printf("Percentage of energy lost : %.2f\n", 100*powerOvershoot/totalEnergy);

for(int j=0;j<12;j++)
{
    printf("Number of days with missing power in month %d: %d \n", j+1, daysBatteryEmptyMonths[j]);
    totNumDaysEmpty+=daysBatteryEmptyMonths[j];
}

printf("Charge State histogram:\n");
for(int j=0;j<10;j++)
{
    printf("%d to %d %% of charge: %d\n", 10*j, 10*(j+1), chargeHistogram[j]);
}
if(totNumDaysEmpty>0)
{
    printf("Percentage of days when battery was empty: %.2f\n",
            100.*totNumDaysEmpty/count);
    printf("Average energy missing when battery was empty: %.2f Wh/day\n", 
            powerMissing/totNumDaysEmpty);
}
```
