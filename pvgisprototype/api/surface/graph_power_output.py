from pvgisprototype import (TemperatureSeries, WindSpeedSeries, SpectralFactorSeries, LinkeTurbidityFactor,
                             Longitude, Latitude, Elevation, SurfaceOrientation, SurfaceTilt,
                            )
                            
from pvgisprototype.constants import (SPECTRAL_FACTOR_DEFAULT,TEMPERATURE_DEFAULT,
                                       WIND_SPEED_DEFAULT,LINKE_TURBIDITY_TIME_SERIES_DEFAULT,)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.power.broadband import calculate_photovoltaic_power_output_series
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode
from pandas import DatetimeIndex
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
import numpy
import math


def graph_power_output(longitude: Longitude,
                    latitude: Latitude,
                    elevation: float, #change it to Elevation
                    timestamps: DatetimeIndex, 
                    timezone: ZoneInfo = ZoneInfo('UTC'),
                    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
                    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
                    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
                    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
                    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING, 
                    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
                    surface_orientation: SurfaceOrientation = SurfaceOrientation(value = math.radians(180), unit = 'radians'),
                    surface_tilt: SurfaceTilt = SurfaceTilt(value = math.radians(45), unit = 'radians'),
                    min_surface_orientation: float = SurfaceOrientation().min_radians,
                    max_surface_orientation: float = SurfaceOrientation().max_radians,
                    min_surface_tilt: float = SurfaceTilt().min_radians,
                    max_surface_tilt: float = SurfaceTilt().max_radians,
                    optimal_surface_tilt : float = 0,
                    optimal_surface_orientation: float = 0,
                    optimal_pv_power: float = 0,
                    ):

    mean_power_output_values =[]

    if mode == SurfacePositionOptimizerMode.Tilt:

        surface_tilt_values = numpy.linspace(min_surface_tilt, max_surface_tilt, num=50)

        for surface_tilt_value in surface_tilt_values:
            mean_power_output = calculate_photovoltaic_power_output_series(longitude = longitude, 
                                                                    latitude = latitude, 
                                                                    elevation = elevation, timestamps = timestamps, 
                                                                    timezone = timezone, spectral_factor_series = spectral_factor_series, 
                                                                    photovoltaic_module = photovoltaic_module, 
                                                                    temperature_series = temperature_series,
                                                                    wind_speed_series = wind_speed_series, 
                                                                    linke_turbidity_factor_series = linke_turbidity_factor_series, 
                                                                    surface_orientation = surface_orientation.value, 
                                                                    surface_tilt = surface_tilt_value
                                                                    ).value.mean()
            mean_power_output_values.append(mean_power_output)
        surface_tilt_values_degrees = numpy.linspace(math.degrees(min_surface_tilt), math.degrees(max_surface_tilt), num=50)
        mean_power_output_values = numpy.array(mean_power_output_values)
        plt.plot(surface_tilt_values_degrees, mean_power_output_values)
        plt.plot(math.degrees(optimal_surface_tilt), optimal_pv_power,'ro',markersize=10)
        plt.xlabel("Tilt angle (degrees)", fontsize=12)
        #plt.ylabel("Power (kW)", fontsize=12)     
        plt.yticks(fontsize=12)
        plt.xticks(fontsize=12)
        #plt.legend(["PV power","Max PV power for optimal tilt"], loc="lower right")
        plt.show()
        

    if mode.value == SurfacePositionOptimizerMode.Orientation:

        surface_orientation_values = numpy.linspace(min_surface_orientation, max_surface_orientation, num=50)

        for surface_orientation_value in surface_orientation_values:
            mean_power_output = calculate_photovoltaic_power_output_series(longitude = longitude, 
                                                                    latitude = latitude, 
                                                                    elevation = elevation, timestamps = timestamps, 
                                                                    timezone = timezone, spectral_factor_series = spectral_factor_series, 
                                                                    photovoltaic_module = photovoltaic_module, 
                                                                    temperature_series = temperature_series,
                                                                    wind_speed_series = wind_speed_series, 
                                                                    linke_turbidity_factor_series = linke_turbidity_factor_series, 
                                                                    surface_orientation = SurfaceOrientation(value=surface_orientation_value, unit = 'radians'), 
                                                                    surface_tilt = SurfaceTilt(value=surface_tilt.value, unit = 'radians')
                                                                    ).value.mean()
            mean_power_output_values.append(mean_power_output)

        mean_power_output_values = numpy.array(mean_power_output_values)
        plt.plot(surface_tilt_values, mean_power_output_values)
        plt.plot(optimal_surface_tilt, optimal_pv_power,'ro')
        plt.xlabel("Tilt angle (radians)", fontsize=12)
        #plt.ylabel("Power (kW)", fontsize=12)     
        plt.yticks(fontsize=12)
        plt.xticks(fontsize=12)
        plt.legend(["PV power","Max PV power for optimal tilt"], loc="lower right")
        plt.show()


    if mode.value == SurfacePositionOptimizerMode.Orientation_and_Tilt:

        surface_tilt_values = numpy.linspace(min_surface_tilt, max_surface_tilt, num=10)
        surface_orientation_values = numpy.linspace(min_surface_orientation, max_surface_orientation, num=10)   
        
        for i in range(0,len(surface_tilt_values)):
            mean_power_output_values.append([])
            for j in range(0,len(surface_orientation_values)):
                mean_power_output = calculate_photovoltaic_power_output_series(longitude = longitude, 
                                                                        latitude = latitude, 
                                                                        elevation = elevation, timestamps = timestamps, 
                                                                        timezone = timezone, spectral_factor_series = spectral_factor_series, 
                                                                        photovoltaic_module = photovoltaic_module, 
                                                                        temperature_series = temperature_series,
                                                                        wind_speed_series = wind_speed_series, 
                                                                        linke_turbidity_factor_series = linke_turbidity_factor_series, 
                                                                        surface_orientation = surface_orientation_values[j],  
                                                                        surface_tilt = surface_tilt_values[i],
                                                                        ).value.mean()
                mean_power_output_values[i].append(mean_power_output)

        mean_power_output_values = numpy.array(mean_power_output_values)
        surface_tilt_values = numpy.linspace(math.degrees(min_surface_tilt), math.degrees(max_surface_tilt), num=10)
        surface_orientation_values = numpy.linspace(math.degrees(min_surface_orientation), math.degrees(max_surface_orientation), num=10)   
        x,y = numpy.meshgrid(surface_tilt_values,surface_orientation_values)
        
        fig = plt.figure(figsize=(10,10))

        ax = fig.add_subplot(1,1,1, projection='3d')
        ax.scatter(math.degrees(optimal_surface_tilt),math.degrees(optimal_surface_orientation),optimal_pv_power, s=100,color='red')
        ax.plot_surface(x, y, mean_power_output_values,  cmap='viridis',alpha=.5)
        #ax.view_init(50, 70)
        ax.view_init(40, 60)
        ax.invert_yaxis()
        ax.xaxis.set_tick_params(labelsize=12)
        ax.yaxis.set_tick_params(labelsize=12)
        ax.set_xlabel('Tilt angle (degrees)', fontsize=12)
        ax.set_ylabel('Orientation angle (degrees)',fontsize=12)
        ax.set_zlabel('Power (kW)',fontsize=12)
        ax.legend(["Max PV power for optimal tilt-orientation","PV power"], loc="upper left")

        plt.show()
