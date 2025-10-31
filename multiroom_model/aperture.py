from typing import Union, TypeVar
from enum import Enum

Room = TypeVar('Room')


class Side(Enum):
    """
        @brief A side of of the building or a side of a room on which an aperture is situated.
    """

    Unknown = 0
    Front = 1
    Back = 2
    Left = 3
    Right = 4
    Upward = 5
    Downward = 6


class Aperture:
    """
        @brief An aperture either between 2 rooms, or from the room to the outside
        May include the side of the room where the aperture is situated
    """

    def __init__(self, origin: Room, destination: Union[Room | Side], area: float = 0, side_of_room_1: Side = Side.Unknown):
        self.origin = origin
        self.destination = destination
        self.side_of_room_1 = side_of_room_1
        self.area = area
