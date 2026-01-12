# ############################################################################ #
#
# Copyright (c) 2025 Roberto Sommariva, Neil Butcher, Adrian Garcia,
# James Levine, Christian Pfrang.
#
# This file is part of MBM-Flex.
#
# MBM-Flex is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License (https://www.gnu.org/licenses) as
# published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# A copy of the GPLv3 license can be found in the file `LICENSE` at the root of
# the MBM-Flex project.
#
# ############################################################################ #

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
