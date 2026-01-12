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

import math
import unittest

from unittest.mock import Mock, patch
from multiroom_model.aperture_calculations import (
    transport_path_contains_room,
    room_has_outdoor_aperture,
    transport_path_angle_in_radians,
    transport_path_windspeed,
    flow_advection,
    flow_exchange,
    ApertureCalculation,
    Fluxes,
)
from multiroom_model.aperture import Side, Aperture
from multiroom_model.transport_paths import paths_through_building
from multiroom_model.wind_definition import WindDefinition


class MockRoom:
    pass


class TestApertureCalculations(unittest.TestCase):
    def setUp(self):
        room1 = MockRoom()
        room2 = MockRoom()
        room3 = MockRoom()
        room4 = MockRoom()
        aperture1 = Aperture(origin=room1, destination=Side.Front)
        aperture2 = Aperture(origin=room1, destination=room2)
        aperture3 = Aperture(origin=room2, destination=room3)
        aperture4 = Aperture(origin=room3, destination=room4)
        aperture5 = Aperture(origin=room4, destination=Side.Back)

        self.rooms = [room1, room2, room3, room4]
        self.apertures = [aperture1, aperture2, aperture3, aperture4, aperture5]
        self.transport_path = paths_through_building(self.rooms, self.apertures)[0]

    def test_transport_path_contains_room(self):
        for r in self.rooms:
            self.assertTrue(transport_path_contains_room(r, self.transport_path))

    def test_room_has_outdoor_aperture_true(self):
        self.assertTrue(room_has_outdoor_aperture(self.rooms[0], self.apertures))
        self.assertFalse(room_has_outdoor_aperture(self.rooms[1], self.apertures))
        self.assertFalse(room_has_outdoor_aperture(self.rooms[2], self.apertures))
        self.assertTrue(room_has_outdoor_aperture(self.rooms[3], self.apertures))

    def test_transport_path_angle_in_radians(self):
        angle = transport_path_angle_in_radians(self.transport_path, math.radians(45))
        self.assertAlmostEqual(angle, math.radians(45+180))

    def test_transport_path_windspeed(self):
        wind_speed = 10.0
        building_dir = 0

        for wind_direction in 10, 30, 50, 70, 90, 100, 140, 190, 230, 260, 300, 320, 350, 360, 400:
            wind_direction_in_radians = math.radians(wind_direction)
            result = transport_path_windspeed(self.transport_path, wind_speed, wind_direction_in_radians, building_dir)
            self.assertAlmostEqual(result, wind_speed * math.cos(wind_direction_in_radians-math.pi))

        building_dir = math.pi

        for wind_direction in 10, 30, 50, 70, 90, 100, 140, 190, 230, 260, 300, 320, 350, 360, 400:
            wind_direction_in_radians = math.radians(wind_direction)
            result = transport_path_windspeed(self.transport_path, wind_speed, wind_direction_in_radians, building_dir)
            self.assertAlmostEqual(result, wind_speed * math.cos(wind_direction_in_radians))

    def test_flow_advection_positive_flow(self):
        result = flow_advection(
            io_windspd=3.0,
            oarea=1.0,
            Cd=0.6,
            Cp=(0.8, 0.2),
            air_density=1.2
        )
        assert result > 0

    def test_flow_advection_zero_pressure_difference(self):
        result = flow_advection(
            io_windspd=3.0,
            oarea=1.0,
            Cd=0.6,
            Cp=(0.0, 0.0),
            air_density=1.2
        )
        self.assertAlmostEqual(result, 0.0)

    def test_flow_exchange_known_values(self):
        assert flow_exchange(1) == 0
        assert flow_exchange(2) == 0
        assert flow_exchange(3) == 0
        assert flow_exchange(4) == 0
        with self.assertRaises(Exception):
            flow_exchange(999)


class TestApertureCalculationsWithWind(unittest.TestCase):
    def setUp(self):
        room1 = MockRoom()
        room2 = MockRoom()
        room3 = MockRoom()
        room4 = MockRoom()
        aperture1 = Aperture(origin=room1, destination=Side.Front)
        aperture2 = Aperture(origin=room1, destination=room2)
        aperture3 = Aperture(origin=room2, destination=room3)
        aperture4 = Aperture(origin=room3, destination=room4)
        aperture5 = Aperture(origin=room4, destination=Side.Back)

        self.rooms = [room1, room2, room3, room4]
        self.apertures = [aperture1, aperture2, aperture3, aperture4, aperture5]
        self.transport_path = paths_through_building(self.rooms, self.apertures)[0]

        self.calculations = list(
            ApertureCalculation(a, [self.transport_path], self.apertures, building_direction_in_radians= math.radians(0))
            for a in self.apertures)

    def test_calculation_construction(self):
        for c in self.calculations:
            self.assertEqual(len(c.contributions), 1)

    def test_has_advection_flow_true(self):
        for c in self.calculations:
            self.assertTrue(c.has_advection_flow(wind_speed=10, wind_direction=0))
            self.assertTrue(c.has_advection_flow(wind_speed=10, wind_direction=math.pi))
            self.assertTrue(c.has_advection_flow(wind_speed=10, wind_direction=math.pi/4.0))
            self.assertTrue(c.has_advection_flow(wind_speed=10, wind_direction=-math.pi/4.0))
            self.assertFalse(c.has_advection_flow(wind_speed=0, wind_direction=0))
            self.assertFalse(c.has_advection_flow(wind_speed=10, wind_direction=math.pi/2.0))
            self.assertFalse(c.has_advection_flow(wind_speed=10, wind_direction=-math.pi/2.0))

    @patch('multiroom_model.aperture_calculations.flow_advection')
    def test_advection_flow_rate(self, mock):
        mock.return_value = 1.234


        with self.subTest("flow angle 0 start"):
            rate = self.calculations[0].advection_flow_rate(10.0, 0)
            self.assertAlmostEqual(rate, 1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertAlmostEqual(windspeed, -10)
            self.assertEqual(Cd, 0.7/(1+1))

        with self.subTest("flow angle 45 start"):
            rate = self.calculations[0].advection_flow_rate(10.0, math.pi/4.0)
            self.assertAlmostEqual(rate, 1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertAlmostEqual(windspeed, -10/math.sqrt(2))
            self.assertEqual(Cd, 0.7/(1+1))

        with self.subTest("flow angle 135 start"):
            rate = self.calculations[0].advection_flow_rate(10.0, 3.0*math.pi/4.0)
            self.assertAlmostEqual(rate, -1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertAlmostEqual(windspeed, 10/math.sqrt(2))
            self.assertEqual(Cd, 0.7/(1+0))

        with self.subTest("flow angle 90 start"):
            rate = self.calculations[0].advection_flow_rate(10.0, math.pi/2.0)
            self.assertAlmostEqual(rate, -1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertAlmostEqual(windspeed, 0)
            self.assertEqual(Cd, 0.7/(1+0))

        with self.subTest("flow angle 180 start"):
            rate = self.calculations[0].advection_flow_rate(10.0, math.pi)
            self.assertAlmostEqual(rate, -1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertEqual(windspeed, 10)
            self.assertEqual(Cd, 0.7/(1+0))

        with self.subTest("flow angle 0 mid"):
            mock.return_value = 1.234

            rate = self.calculations[2].advection_flow_rate(10.0, 0)
            self.assertAlmostEqual(rate, -1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertEqual(windspeed, -10)
            self.assertEqual(Cd, 0.7/(1+0.5))

        with self.subTest("flow angle 45 mid"):
            rate = self.calculations[2].advection_flow_rate(10.0, math.pi/4.0)
            self.assertAlmostEqual(rate, -1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertAlmostEqual(windspeed, -10/math.sqrt(2))
            self.assertEqual(Cd, 0.7/(1+0.5))

        with self.subTest("flow angle 90 mid"):
            rate = self.calculations[2].advection_flow_rate(10.0, math.pi/2.0)
            self.assertAlmostEqual(rate, 1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertAlmostEqual(windspeed, 0)
            self.assertEqual(Cd, 0.7/(1+0.5))

        with self.subTest("flow angle 180 mid"):
            rate = self.calculations[2].advection_flow_rate(10.0, math.pi)
            self.assertAlmostEqual(rate, 1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertEqual(windspeed, 10)
            self.assertEqual(Cd, 0.7/(1+0.5))

        with self.subTest("flow angle 0 end"):
            mock.return_value = 1.234

            rate = self.calculations[4].advection_flow_rate(10.0, 0)
            self.assertAlmostEqual(rate, -1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertEqual(windspeed, -10)
            self.assertEqual(Cd, 0.7/(1+0))

        with self.subTest("flow angle 45 end"):
            rate = self.calculations[4].advection_flow_rate(10.0, math.pi/4.0)
            self.assertAlmostEqual(rate, -1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertAlmostEqual(windspeed, -10/math.sqrt(2))
            self.assertEqual(Cd, 0.7/(1+0))

        with self.subTest("flow angle 90 end"):
            rate = self.calculations[4].advection_flow_rate(10.0, math.pi/2.0)
            self.assertAlmostEqual(rate, 1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertAlmostEqual(windspeed, 0)
            self.assertEqual(Cd, 0.7/(1+1))

        with self.subTest("flow angle 180 end"):
            rate = self.calculations[4].advection_flow_rate(10.0, math.pi)
            self.assertAlmostEqual(rate, 1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertEqual(windspeed, 10)
            self.assertEqual(Cd, 0.7/(1+1))

    @patch('multiroom_model.aperture_calculations.flow_advection')
    def test_advection_flow_rate_2(self, mock):
        mock.return_value = 1.234

        def test(aperture_index, angle, position):
            reversed_sign = -1 if aperture_index==0 else 1
            calculation = self.calculations[aperture_index]
            rate = calculation.advection_flow_rate(10.0, angle)

            expected_wind = 10 * math.cos(angle-math.pi)

            wind_sign = -1 if expected_wind<0 else 1

            self.assertAlmostEqual(rate, reversed_sign*wind_sign*1.234)

            args, _ = mock.call_args
            windspeed, _, Cd, _, _ = args

            self.assertEqual(windspeed, expected_wind)
            self.assertEqual(Cd, 0.7/(1+position))


        with self.subTest("flow angle 0 start"):
            test(0, 0.0, 1.0)

        with self.subTest("flow angle 45 start"):
            test(0, math.pi/4.0, 1.0)

        with self.subTest("flow angle 135 start"):
            test(0, 3.0*math.pi/4.0, 0.0)

        with self.subTest("flow angle 90 start"):
            test(0, math.pi/2.0, 0.0)

        with self.subTest("flow angle 180 start"):
            test(0, math.pi, 0.0)

        with self.subTest("flow angle 0 mid"):
            test(2, 0, 0.5)

        with self.subTest("flow angle 45 mid"):
            test(2, math.pi/4.0, 0.5)

        with self.subTest("flow angle 90 mid"):
            test(2, math.pi/2.0, 0.5)

        with self.subTest("flow angle 180 mid"):
            test(2, math.pi, 0.5)

        with self.subTest("flow angle 0 end"):
            test(4, 0, 0)

        with self.subTest("flow angle 45 end"):
            test(4, math.pi/4.0, 0.0)

        with self.subTest("flow angle 90 end"):
            test(4, math.pi/2.0, 1.0)

        with self.subTest("flow angle 180 end"):
            test(4, math.pi, 1.0)

    def test_exchange_category(self):
        # everything cross ventilated if the wind is in the correct direction
        for c in self.calculations:
            self.assertEqual(c.exchange_category(wind_speed=10, wind_direction=0), 1)
        # Otherwise:
        # windows to the outside
        self.assertEqual(self.calculations[0].exchange_category(wind_speed=10, wind_direction=math.pi/2), 2)
        self.assertEqual(self.calculations[4].exchange_category(wind_speed=10, wind_direction=math.pi/2), 2)
        # have a "costal" room
        self.assertEqual(self.calculations[1].exchange_category(wind_speed=10, wind_direction=math.pi/2), 3)
        self.assertEqual(self.calculations[3].exchange_category(wind_speed=10, wind_direction=math.pi/2), 3)
        # between "landlocked" rooms
        self.assertEqual(self.calculations[2].exchange_category(wind_speed=10, wind_direction=math.pi/2), 4)

    @patch('multiroom_model.aperture_calculations.flow_exchange')
    def test_exchange_flow_rate(self, mock):
        mock.return_value = 1.234
        # everything cross ventilated if the wind is in the correct direction
        for c in self.calculations:
            self.assertEqual(c.exchange_flow_rate(wind_speed=10, wind_direction=0), 1.234)
            catagory = mock.call_args[0][0]
            self.assertEqual(catagory, 1)
        # Otherwise:
        # windows to the outside
        self.assertEqual(self.calculations[0].exchange_flow_rate(wind_speed=10, wind_direction=math.pi/2), 1.234)
        self.assertEqual(mock.call_args[0][0], 2)
        self.assertEqual(self.calculations[4].exchange_flow_rate(wind_speed=10, wind_direction=math.pi/2), 1.234)
        self.assertEqual(mock.call_args[0][0], 2)
        # have a "costal" room
        self.assertEqual(self.calculations[1].exchange_flow_rate(wind_speed=10, wind_direction=math.pi/2), 1.234)
        self.assertEqual(mock.call_args[0][0], 3)
        self.assertEqual(self.calculations[3].exchange_flow_rate(wind_speed=10, wind_direction=math.pi/2), 1.234)
        self.assertEqual(mock.call_args[0][0], 3)
        # between "landlocked" rooms
        self.assertEqual(self.calculations[2].exchange_flow_rate(wind_speed=10, wind_direction=math.pi/2), 1.234)
        self.assertEqual(mock.call_args[0][0], 4)

    @patch('multiroom_model.aperture_calculations.flow_advection')
    @patch('multiroom_model.aperture_calculations.flow_exchange')
    def test_trans_matrix_contributions(self, mock_flow_exchange, mock_flow_advection):
        mock_flow_advection.side_effect = lambda *args, **kwargs: args[0]*1.234
        mock_flow_exchange.return_value = 0.123

        with self.subTest("positive advection flow"):
            result = self.calculations[0].trans_matrix_contributions(1,0)

            windspeed, _, Cd, _, _ = mock_flow_advection.call_args[0]
            self.assertEqual(windspeed, -1)
            self.assertEqual(Cd, 0.7/(1+1))

            self.assertEqual(result.from_1_to_2, 0)
            self.assertEqual(result.from_2_to_1, 1.234)

            result = self.calculations[4].trans_matrix_contributions(1,0)

            windspeed, _, Cd, _, _ = mock_flow_advection.call_args[0]
            self.assertEqual(windspeed, -1)
            self.assertEqual(Cd, 0.7/(1+0))

            self.assertEqual(result.from_1_to_2, 1.234)
            self.assertEqual(result.from_2_to_1, 0)

        with self.subTest("negative advection flow"):
            result = self.calculations[0].trans_matrix_contributions(1, math.pi)

            windspeed, _, Cd, _, _ = mock_flow_advection.call_args[0]
            self.assertEqual(windspeed, 1)
            self.assertEqual(Cd, 0.7/(1+0))

            self.assertEqual(result.from_1_to_2, 0)
            self.assertEqual(result.from_2_to_1, 1.234)

            result = self.calculations[4].trans_matrix_contributions(1, math.pi)

            windspeed, _, Cd, _, _ = mock_flow_advection.call_args[0]
            self.assertEqual(windspeed, 1)
            self.assertEqual(Cd, 0.7/(1+1))

            self.assertEqual(result.from_1_to_2, 1.234)
            self.assertEqual(result.from_2_to_1, 0)

        with self.subTest("exchange flow"):

            result = self.calculations[0].trans_matrix_contributions(1,math.pi/2.0)
            self.assertEqual(result.from_1_to_2, 0.123)
            self.assertEqual(result.from_2_to_1, 0.123)
            catagory = mock_flow_exchange.call_args[0][0]
            self.assertEqual(catagory, 2)

            result = self.calculations[1].trans_matrix_contributions(1,math.pi/2.0)
            catagory = mock_flow_exchange.call_args[0][0]
            self.assertEqual(catagory, 3)
            self.assertEqual(result.from_1_to_2, 0.123)
            self.assertEqual(result.from_2_to_1, 0.123)

            result = self.calculations[2].trans_matrix_contributions(1,math.pi/2.0)
            catagory = mock_flow_exchange.call_args[0][0]
            self.assertEqual(catagory, 4)
            self.assertEqual(result.from_1_to_2, 0.123)
            self.assertEqual(result.from_2_to_1, 0.123)

            result = self.calculations[3].trans_matrix_contributions(1,math.pi/2.0)
            catagory = mock_flow_exchange.call_args[0][0]
            self.assertEqual(catagory, 3)
            self.assertEqual(result.from_1_to_2, 0.123)
            self.assertEqual(result.from_2_to_1, 0.123)

            result = self.calculations[4].trans_matrix_contributions(1,math.pi/2.0)
            catagory = mock_flow_exchange.call_args[0][0]
            self.assertEqual(catagory, 2)
            self.assertEqual(result.from_1_to_2, 0.123)
            self.assertEqual(result.from_2_to_1, 0.123)
