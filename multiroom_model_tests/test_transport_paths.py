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

import unittest

from multiroom_model.aperture import Aperture, Side
from multiroom_model.transport_paths import paths_through_building


class MockRoom:
    pass


class TestTransportPaths(unittest.TestCase):
    def setUp(self):
        self.rooms = [MockRoom() for n in range(9)]

    def test_one_room_one_window(self):
        # One front-side window
        windows = [
            Aperture(self.rooms[0], Side.Front)
        ]

        result = paths_through_building(self.rooms, windows)

        self.assertEqual(len(result), 0)

    def test_one_room_2_windows(self):
        windows = [
            Aperture(self.rooms[0], Side.Front),
            Aperture(self.rooms[0], Side.Back),
        ]

        result = paths_through_building(self.rooms, windows)

        self.assertEqual(len(result), 1)
        self.assertEqual(Side.Front, result[0].start)
        self.assertEqual(Side.Back, result[0].end)

        self.assertEqual(len(result[0].route), 2)
        self.assertEqual(windows[0], result[0].route[0].aperture)
        self.assertTrue(result[0].route[0].reversed)
        self.assertEqual(windows[1], result[0].route[1].aperture)
        self.assertFalse(result[0].route[1].reversed)

    def test_one_room_3_windows(self):
        windows = [
            Aperture(self.rooms[0], Side.Front),
            Aperture(self.rooms[0], Side.Back),
            Aperture(self.rooms[0], Side.Right),
        ]

        result = paths_through_building(self.rooms, windows)

        self.assertEqual(len(result), 3)

        self.assertEqual(Side.Front, result[0].start)
        self.assertEqual(Side.Back, result[0].end)
        self.assertEqual(len(result[0].route), 2)
        self.assertEqual(windows[0], result[0].route[0].aperture)
        self.assertTrue(result[0].route[0].reversed)
        self.assertEqual(windows[1], result[0].route[1].aperture)
        self.assertFalse(result[0].route[1].reversed)

        self.assertEqual(Side.Front, result[1].start)
        self.assertEqual(Side.Right, result[1].end)
        self.assertEqual(len(result[1].route), 2)
        self.assertEqual(windows[0], result[1].route[0].aperture)
        self.assertTrue(result[1].route[0].reversed)
        self.assertEqual(windows[2], result[1].route[1].aperture)
        self.assertFalse(result[1].route[1].reversed)

        self.assertEqual(Side.Back, result[2].start)
        self.assertEqual(Side.Right, result[2].end)
        self.assertEqual(len(result[2].route), 2)
        self.assertEqual(windows[1], result[2].route[0].aperture)
        self.assertTrue(result[2].route[0].reversed)
        self.assertEqual(windows[2], result[2].route[1].aperture)
        self.assertFalse(result[2].route[1].reversed)

    def test_one_room_4_windows(self):
        windows = [
            Aperture(self.rooms[0], Side.Front),
            Aperture(self.rooms[0], Side.Back),
            Aperture(self.rooms[0], Side.Right),
            Aperture(self.rooms[0], Side.Left),
        ]

        result = paths_through_building(self.rooms, windows)

        self.assertEqual(len(result), 6)

    def test_4_room_Y_shape(self):
        windows = [
            Aperture(self.rooms[0], Side.Front, Side.Front),
            Aperture(self.rooms[1], self.rooms[0], Side.Front),
            Aperture(self.rooms[2], self.rooms[1], Side.Front),
            Aperture(self.rooms[3], self.rooms[1], Side.Front),
            Aperture(self.rooms[2], Side.Back, Side.Back),
            Aperture(self.rooms[3], Side.Back, Side.Back)
        ]

        result = paths_through_building(self.rooms, windows)
        #   layout           ^ ^
        #                    # #
        #                     #
        #                     #
        #                     v

        # there should be 2 routes from front to back, each going through 4 windows
        self.assertEqual(len(result), 2)
        for r in result:
            self.assertEqual(Side.Front, r.start)
            self.assertEqual(Side.Back, r.end)
            self.assertEqual(len(r.route), 4)

    def test_7_room_H_shape(self):
        windows = [
            Aperture(self.rooms[0], Side.Front, Side.Front),
            Aperture(self.rooms[1], self.rooms[0], Side.Front),
            Aperture(self.rooms[2], self.rooms[1], Side.Front),
            Aperture(self.rooms[2], Side.Back, Side.Back),


            Aperture(self.rooms[3], Side.Front, Side.Front),
            Aperture(self.rooms[4], self.rooms[3], Side.Front),
            Aperture(self.rooms[5], self.rooms[4], Side.Front),
            Aperture(self.rooms[5], Side.Back, Side.Back),

            Aperture(self.rooms[1], self.rooms[6], Side.Right),
            Aperture(self.rooms[4], self.rooms[6], Side.Left),

        ]

        result = paths_through_building(self.rooms, windows)

        #   layout            ^ ^
        #                     # #
        #                     ###
        #                     # #
        #                     v v

        # there should be 4 routes from front to back, 2 going through 4 windows, 2 going through 6 windows
        self.assertEqual(len(result), 4)
        for r in result:
            self.assertEqual(Side.Front, r.start)
            self.assertEqual(Side.Back, r.end)

        self.assertEqual(len(result[0].route), 4)
        self.assertEqual(len(result[1].route), 6)
        self.assertEqual(len(result[2].route), 4)
        self.assertEqual(len(result[3].route), 6)

    def test_6_room_example(self):
        windows = [
            Aperture(self.rooms[1], Side.Left, Side.Left),
            Aperture(self.rooms[1], self.rooms[2], Side.Right),
            Aperture(self.rooms[2], Side.Back, Side.Back),
            Aperture(self.rooms[2], self.rooms[3], Side.Right),
            Aperture(self.rooms[2], self.rooms[4], Side.Right),
            Aperture(self.rooms[3], Side.Back, Side.Back),
            Aperture(self.rooms[3], Side.Right, Side.Right),
            Aperture(self.rooms[4], Side.Right, Side.Right),
            Aperture(self.rooms[4], self.rooms[5], Side.Front),
            Aperture(self.rooms[5], self.rooms[6], Side.Left),
            Aperture(self.rooms[6], Side.Front, Side.Front)
        ]

        result = paths_through_building(self.rooms, windows)

        a = [r for r in result if Side.Front is r.start and Side.Left is r.end]
        self.assertEqual(len(a), 1)

        a = [r for r in result if Side.Front is r.start and Side.Right is r.end]
        self.assertEqual(len(a), 2)

        a = [r for r in result if Side.Front is r.start and Side.Back is r.end]
        self.assertEqual(len(a), 2)

        a = [r for r in result if Side.Left is r.start and Side.Back is r.end]
        self.assertEqual(len(a), 2)

        a = [r for r in result if Side.Back is r.start and Side.Right is r.end]
        self.assertEqual(len(a), 4)

        a = [r for r in result if Side.Left is r.start and Side.Right is r.end]
        self.assertEqual(len(a), 2)

        self.assertEqual(len(result), 13)
