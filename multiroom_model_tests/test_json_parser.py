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

from multiroom_model.json_parser import BuildingJSONParser, RoomChemistryJSONBuilder
from multiroom_model.room_chemistry import RoomChemistry
from multiroom_model.time_dep_value import TimeDependentValue
from multiroom_model.bracketed_value import TimeBracketedValue
from multiroom_model.surface_composition import SurfaceComposition


class BaseTestJSON(unittest.TestCase):
    results = None

    @classmethod
    def setUpClass(cls):
        if cls is BaseTestJSON:
            raise unittest.SkipTest("Base class — skipping")
        cls.rooms = cls.results["rooms"]

    def test_number_of_rooms(self):
        self.assertEqual(len(self.results["rooms"]), 9, "Expected 9 rooms")

    def test_number_of_apertures(self):
        self.assertEqual(len(self.results["apertures"]), 18, "Expected 18 apertures")

    def test_room_basic_fields(self):
        for room_id, room in self.rooms.items():
            with self.subTest(room_id=room_id):
                self.assertIsInstance(room, RoomChemistry)
                self.assertIsInstance(room.volume_in_m3, (int, float))
                self.assertGreater(room.volume_in_m3, 0)
                self.assertIsInstance(room.surf_area_in_m2, (int, float))
                self.assertIsInstance(room.glass_type, str)
                self.assertIsInstance(room.light_type, str)

    def test_composition_fields_and_sum(self):
        for room_id, room in self.rooms.items():
            with self.subTest(room_id=room_id):
                comp = room.composition
                self.assertIsInstance(comp, SurfaceComposition)
                for mat_name, value in vars(comp).items():
                    self.assertIsInstance(value, (int, float), f"{mat_name} should be a number")
                    self.assertGreaterEqual(value, 0, f"{mat_name} should be >= 0")
                    self.assertLessEqual(value, 100, f"{mat_name} should be <= 100")
                total = sum(vars(comp).values())
                self.assertAlmostEqual(total, 100.0, delta=1.0, msg=f"Room {room_id} has bad composition sum: {total}%")

    def test_edge_case_compositions(self):
        room5 = self.rooms["room 5"]
        room7 = self.rooms["room 7"]
        room8 = self.rooms["room 8"]

        self.assertEqual(room5.composition.soft, 0)
        self.assertEqual(room5.composition.other, 0)
        self.assertEqual(room7.composition.wood, 40)
        self.assertEqual(room8.composition.lino, 50)
        self.assertEqual(room8.composition.plastic, 18)

    def test_rooms_exact_values(self):
        expected_data = {
            "room 1": {"volume_in_m3": 10, "surf_area_in_m2": 29.7, "light_type": "Incand", "glass_type": "glass_C"},
            "room 2": {"volume_in_m3": 37.5, "surf_area_in_m2": 81, "light_type": "LED", "glass_type": "no_sunlight"},
            "room 3": {"volume_in_m3": 32.4, "surf_area_in_m2": 61.8, "light_type": "UFT", "glass_type": "low_emissivity"},
            "room 4": {"volume_in_m3": 40.5, "surf_area_in_m2": 81.3, "light_type": "CFT", "glass_type": "low_emissivity_film"},
            "room 5": {"volume_in_m3": 24.5, "surf_area_in_m2": 51.1, "light_type": "FT", "glass_type": "no_sunlight"},
            "room 6": {"volume_in_m3": 31.6, "surf_area_in_m2": 98.3, "light_type": "CFL", "glass_type": "low_emissivity"},
            "room 7": {"volume_in_m3": 22.5, "surf_area_in_m2": 48, "light_type": "Incand", "glass_type": "low_emissivity_film"},
            "room 8": {"volume_in_m3": 50.4, "surf_area_in_m2": 86.4, "light_type": "UFT", "glass_type": "glass_C"},
            "room 9": {"volume_in_m3": 132, "surf_area_in_m2": 158, "light_type": "Incand", "glass_type": "no_sunlight"},
        }

        for room_num, expected in expected_data.items():
            with self.subTest(room=room_num):
                room = self.rooms[room_num]
                self.assertEqual(room.volume_in_m3, expected["volume_in_m3"])
                self.assertAlmostEqual(room.surf_area_in_m2, expected["surf_area_in_m2"])
                self.assertEqual(room.light_type, expected["light_type"])
                self.assertEqual(room.glass_type, expected["glass_type"])

    def test_populate_emissions(self):
            room = self.rooms["room 1"]
            self.assertTrue(hasattr(room, 'emissions'))
            self.assertEqual(len(room.emissions), 2)
            self.assertTrue("LIMONENE" in room.emissions)
            self.assertTrue("BPINENE" in room.emissions)
            for species, tvalue in room.emissions.items():
                self.assertIsInstance(tvalue, TimeBracketedValue, f"{species} should be TimeBracketedValue")

            self.assertEqual(len(room.emissions["LIMONENE"].values()), 1)
            self.assertEqual(len(room.emissions["BPINENE"].values()), 1)


            self.assertEqual(room.emissions["LIMONENE"].values()[0][0], 46800)
            self.assertEqual(room.emissions["BPINENE"].values()[0][0], 46800)

            self.assertEqual(room.emissions["LIMONENE"].values()[0][1], 50400)
            self.assertEqual(room.emissions["BPINENE"].values()[0][1], 50400)

            self.assertEqual(room.emissions["LIMONENE"].values()[0][2], 5.00E+08)
            self.assertEqual(room.emissions["BPINENE"].values()[0][2], 5.00E+10)

    def test_populate_tvar(self):
        for room in self.rooms.values():
            self.assertIsInstance(room.temp_in_kelvin, TimeDependentValue)
            self.assertIsInstance(room.rh_in_percent, TimeDependentValue)
            self.assertIsInstance(room.airchange_in_per_second, TimeDependentValue)
            self.assertIsInstance(room.light_switch, TimeDependentValue)

    def test_populate_expos(self):
        for room in self.rooms.values():
            self.assertIsInstance(room.n_adults, TimeDependentValue)
            self.assertIsInstance(room.n_children, TimeDependentValue)


class TestJSONReferencingRoomFiles(BaseTestJSON):
    results = BuildingJSONParser.from_json_file("config_rooms/building.json")


class TestJSONWithRoomFiles(BaseTestJSON):
    rooms_files = {
        "room 1": "config_rooms/room_1.json",
        "room 2": "config_rooms/room_2.json",
        "room 3": "config_rooms/room_3.json",
        "room 4": "config_rooms/room_4.json",
        "room 5": "config_rooms/room_5.json",
        "room 6": "config_rooms/room_6.json",
        "room 7": "config_rooms/room_7.json",
        "room 8": "config_rooms/room_8.json",
        "room 9": "config_rooms/room_9.json",
    }
    results = BuildingJSONParser.from_json_files("config_rooms/building.json", rooms_files)
