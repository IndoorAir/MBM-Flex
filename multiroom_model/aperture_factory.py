from typing import List, Dict, TypeVar
from .aperture import Aperture, Side
from .wind_definition import WindDefinition, TimeDependentValue
from pandas import read_csv, isnull


Room = TypeVar('Room')


def build_apertures(csv_file: str, rooms: Dict[int, Room]) -> List[Aperture]:
    """
    Use a csv variables file to populate a list of apertures
    """

    tcon_building = read_csv(csv_file)

    naperture = len(tcon_building['floor'])  # number of apertures

    floor = tcon_building['floor'].tolist()
    rorig = tcon_building['rorig'].tolist()
    rdest = tcon_building['rdest'].tolist()
    oarea = tcon_building['oarea'].tolist()
    oside = tcon_building['oside'].tolist()
    oheight = tcon_building['oheight'].tolist()

    result = []

    for i in range(naperture):

        room_1 = rooms[rorig[i]]
        if not isnull(oside[i]):
            side: Side = Side[oside[i]]
            room_2 = rooms.get(rdest[i], side)
        else:
            side: Side = Side.Unknown
            room_2 = rooms[rdest[i]]

        result.append(Aperture(
            origin=room_1,
            destination=room_2,
            area=oarea[i],
            side_of_room_1=side
        ))

    return result


def build_apertures_from_double_definition(csv_file: str, rooms: Dict[int, Room]) -> List[Aperture]:
    """
    Use a csv variables file to populate a list of apertures
    This assumes that apertures between 2 rooms will appear twice in the csv file
    It validates that assumption then only returns the first of the 2 apertures 
    """
    apertures = build_apertures(csv_file, rooms)

    result = []
    while len(apertures) > 0:
        aperture: Aperture = apertures[0]
        if (type(aperture.destination) is Side):
            result.append(aperture)
            apertures.remove(aperture)
        else:
            matching_apertures: List[Aperture] = [a for a in apertures if a.destination ==
                                                  aperture.origin and a.origin == aperture.destination]
            assert (len(matching_apertures) == 1)
            matching_aperture: Aperture = matching_apertures[0]
            assert (matching_aperture.area == aperture.area)
            result.append(aperture)
            apertures.remove(aperture)
            apertures.remove(matching_aperture)

    return result


def build_wind_definition(csv_file: str, in_radians: bool = False) -> WindDefinition:
    """
    Use a csv variables file to populate a wind definition
    """
    wind_params = read_csv(csv_file)

    times = wind_params["seconds_from_midnight"]
    wind_speed = TimeDependentValue(list(zip(times, wind_params["wind_speed"])), continuous=True)
    wind_direction = TimeDependentValue(list(zip(times, wind_params["wind_direction"])), continuous=True)

    return WindDefinition(
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        in_radians=in_radians
    )
