Implement time series support for NOAA's solar geometry equations (_in dependency order_) : 

- [x] Fractional year  
- [x] Equation of time 
- [ ] Time offset      
- [x] True solar time  -- **partially since time offset is not yet vectorised!**
- [x] Solar hour angle 
- [x] Solar declination
- [x] Solar zenith     
- [x] Solar altitude   
- [x] Solar azimuth

Also to support ?

- [ ] events.py
- [ ] event_hour_angle.py
- [ ] event_time.py
- [ ] local_time.py


| Quantity            | Implementation         | Requires                                                      | Required by                                   |
| ------------------- | ---------------------- | ------------------------------------------------------------- | --------------------------------------------- |
| Fractional year     | fractional_year.py     | Timestamp (+ time zone ? ) [^*]                               | Equation of time, solar declination           |
| Equation of time    | equation_of_time.py    | Fractional year                                               | Time offset                                   |
| Time offset         | time_offset.py         | Equation of time                                              | True solar time                               |
| True solar time     | solar_time.py          | Time offset                                                   | Solar hour angle                              |
| Solar hour angle    | solar_hour_angle.py    | True solar time                                               | Solar zenith, Solar altitude, Solar azimuth   |
| Solar declination   | solar_declination.py   | Fractional year                                               | Solar zenith                                  |
| Solar zenith        | solar_zenith.py        | Solar declination, Solar hour angle, Atmospheric refraction   | Solar altitude                                |
| Solar altitude      | solar_altitude.py      | Solar hour angle, Solar zenith                                | Solar position                                |
| Solar azimuth       | solar_azimuth.py       | Solar declination, Solar hour angle, Solar zenith             | Solar position                                |

[^*]: If the timezone is such that after conversion to UTC it changes the day, then this is indeed required ?
