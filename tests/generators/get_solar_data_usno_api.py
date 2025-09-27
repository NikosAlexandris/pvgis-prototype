#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import requests
from requests import exceptions
from datetime import datetime
import json

HTTP_OK = 200
SERVER = "https://aa.usno.navy.mil/api/celnav"

def query_usno(longitude:float, 
               latitude:float, 
               date:datetime)->tuple:
    """Get almanac values for Sun from USNO for a specific place and datetime.
    Note that all values are returned for zone UT1. UT1 and UTC are the practically the same, but they differ by as much as 0.9 seconds.

    Args:
        latitude (float): Latitude value
        longitude (float): Longitude value
        date (datetime): Specific date and time to calculate the position

    Raises:
        exceptions.HTTPError: Raises if HTTP return code is not 200

    Returns:
        tuple: Returns solar azimuth, solar altitude, solar declination, solar hour angle in decimal degrees
    """
    parameters = {
            "date": date.date(),
            "time": date.time(),
            "coords": f"{latitude},{longitude}",
            }
    print("------------------")
    print("Getting data for:")
    print(f"{longitude=}")
    print(f"{latitude=}")
    print(f"{date=}")
    request = requests.get(SERVER, params = parameters)
    print("Done!")
    
    print("Analyzing data...")
    if request.status_code != HTTP_OK:
        raise exceptions.HTTPError(f"Failed retrieving USNO data, server returned HTTP code: {request.status_code} on following URL {request.url}.")
    
    data = json.loads(request.content.decode("utf-8"))
    try:
        solar_data = next(item for item in data['properties']['data'] if item['object'] == 'Sun')
        solar_azimuth = solar_data["almanac_data"]["zn"]
        solar_altitude = solar_data["almanac_data"]["hc"]
        solar_declination = solar_data["almanac_data"]["dec"]
        solar_hour_angle = solar_data["almanac_data"]["gha"]
    except StopIteration:
        solar_azimuth = None
        solar_altitude = None
        solar_declination = None
        solar_hour_angle = None

    print("Done!")
    print("------------------")

    return (solar_azimuth, solar_altitude, solar_declination, solar_hour_angle)