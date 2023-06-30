import typer
from typing import Annotated
from typing import Optional
from .conversions import convert_to_radians

# from: rsun_base.c
# function: imageTimeOffset
def get_image_offset(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        ) -> float:
    """
    """
    return 0


def get_image_offset_TO_IMPLEMENT(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        ) -> float:
    """
    """
    # line
    # column
    # nav_cres
    # nav_lres
    # nav_coff
    # nav_loff
    # maxx
    # maxy
    # time_offset
    # latitude*=deg2rad;
    # longitude*=deg2rad;
    maxx = maxy = 5000
    location_in_meteosat = is_point_in_meteosat(
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
                )
    if(longitude > np.radians(40)) and location_in_satgeo:
        time_offset = (maxy - line) * (25 / maxy) / 60 - 0.5
    else:
        maxx = maxy = 3712
        satgeomsgnew(
                     latitude,
                     longitude,
                     maxx=maxx,
                     maxy=maxy,
                     nav_res=667,
                     nav_coff=1857,	
                     nav_loff=1856,	
                     )
        if location_in_msg:
            time_offset = (maxy - line) * (12 / maxy) / 60

    return time_offset



