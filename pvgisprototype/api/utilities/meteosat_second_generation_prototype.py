import pyproj
from pyproj import CRS, Transformer
import math
from rasterio import features
from shapely.geometry import Point, shape


def is_point_in_meteosat(lat, lon, geostationary_raster):
    """
    """
    pass

def is_point_in_mfg(
        line,
        col,
        latitude,
        longitude,  # in radians
        maxx=maxx,
        maxy=maxy,
        nav_cres=500,
        nav_lres=500,	
        nav_coff=2501,
        nav_loff=2500,
        ):
    """
    """
    pass
    longitude=longitude - 57,  # in radians
    # Create a point from the lat/lon
    point = Point(lon, lat)

    # Define the geostationary projection
    # You may need to adjust the parameters for your specific satellite image
    geostationary = pyproj.Proj(proj='geos', h='35785831', lon_0='0', lat_0='0')

    # Define the geographic projection (lat/lon)
    geographic = pyproj.Proj(proj='latlong', datum='WGS84')

    # Get the bounds of the raster in geographic coordinates
    left, bottom, right, top = geostationary_raster.bounds
    left, bottom = pyproj.transform(geostationary, geographic, left, bottom)
    right, top = pyproj.transform(geostationary, geographic, right, top)

    # Create a shape from the raster bounds
    raster_shape = shape({'type': 'Polygon', 'coordinates': [[(left, bottom), (left, top), (right, top), (right, bottom), (left, bottom)]]})

    # Check if the point is within the shape
    return raster_shape.contains(point)


def is_point_in_msg(
        latitude,
        longitude,
        maxx,
        maxy,
        nav_res,
        nav_coff,
        nav_loff,
        ):
    # Constants for MSG satellite
    h = 42164  # altitude of the geostationary orbit
    R_EQ = 6378.169  # Earth's equatorial radius
    R_POL = 6356.5838  # Earth's polar radius

    # Calculate derived constants
    R_EQ_SQR = R_EQ * R_EQ
    R_POL_SQR = R_POL * R_POL
    R_NOM = h - R_EQ

    # Apply the corrections for MSG satellite
    if nav_res == 222:
        nav_res = 222.623596
        hrv = 3
    elif nav_res == 667:
        nav_res = 667.2044067
        hrv = 1
    else:
        raise ValueError(f'Invalid Line and Column Resolution: {NAV_RES}')

    # Create the MSG geostationary projection
    msg_crs = CRS.from_proj4('+proj=geos +h={h} +a={a} +b={b} +lon_0=0'.format(h=h, a=R_EQ, b=R_POL))
    wgs84_crs = CRS.from_epsg(4326)

    # Create the transformer
    transformer = Transformer.from_crs(wgs84_crs, msg_crs, always_xy=True)

    # Transform the point to the MSG projection
    x, y = transformer.transform(lon, lat)

    # Compute column and line
    column = nav_coff - (x * hrv * 3712 / 17.832 * (180.0 / math.pi))
    line = nav_loff - (y * hrv * 3712 / 17.832 * (180.0 / math.pi))

    # Return if the point is inside the raster
    return 0 <= round(column) < maxx and 0 <= round(line) < maxy
