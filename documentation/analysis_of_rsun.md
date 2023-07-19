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
