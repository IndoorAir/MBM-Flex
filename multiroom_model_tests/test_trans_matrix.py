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

import numpy as np
import unittest
import math

from multiroom_model.json_parser import BuildingJSONParser
from multiroom_model.aperture_calculations import Side
from multiroom_model.simulation import Simulation, Aperture, WindDefinition
from multiroom_model.global_settings import GlobalSettings
from multiroom_model.aperture_calculations import flow_advection
from multiroom_model.time_dep_value import TimeDependentValue


class TestTransMatrix(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        building = BuildingJSONParser.from_json_file("config_rooms/building.json")
        cls.rooms = list(building['rooms'].values())
        cls.apertures = building['apertures']
        cls.wind_definition = building['wind']

        ambient_press = 1013.0   # ambient pressure (mbar) is assumed to be constant, and is the same in all rooms
        ambient_temp = 293.0     # ambient temperature (K) is assumed to be constant

        rho = (100*ambient_press) / (287.050 * ambient_temp)  # ambient air density (assuming dry air), in kg/m3

        cls.global_settings = GlobalSettings(
            filename='chem_mech/escs_v1.fac',
            INCHEM_additional=False,
            particles=True,
            constrained_file=None,
            output_folder=None,
            dt=1,
            H2O2_dep=False,
            O3_dep=False,
            custom=False,
            custom_filename=None,
            diurnal=True,
            city='London_urban',
            date='21-06-2020',
            lat=45.4,
            path=None,
            reactions_output=False,
            building_direction_in_radians=math.radians(180),
            air_density=rho,
            upwind_pressure_coefficient=0.3,
            downwind_pressure_coefficient=-0.2
        )

    def flow_advection(self, wind_speed, area, position):
        return flow_advection(wind_speed,
                              area,
                              0.7/(1+position),
                              (self.global_settings.upwind_pressure_coefficient,
                               self.global_settings.downwind_pressure_coefficient),
                              self.global_settings.air_density)

    def test_trans_matrix(self):

        simulation = Simulation(self.global_settings, self.rooms, self.apertures, self.wind_definition)

        for time in (0, 46805, 82800, ):
            matrix = simulation.trans_matrix(time)

            print(np.transpose(matrix.nonzero()))
            print(len(np.transpose(matrix.nonzero())))
            print(len(self.apertures))

            self.assertEqual(matrix.shape, (10, 10))

            self.assertFalse(np.isnan(matrix.max()))
            self.assertFalse(np.isnan(matrix.min()))
            print(matrix)

    def test_one_room(self):

        rooms = [self.rooms[0],]

        apertures = [
            Aperture(self.rooms[0], Side.Front, 10),
            Aperture(self.rooms[0], Side.Back, 10),
        ]

        wind_definition = WindDefinition(TimeDependentValue([(0, 1),], True), TimeDependentValue([(0, 0),], True))

        simulation = Simulation(self.global_settings, rooms, apertures, wind_definition)

        matrix = simulation.trans_matrix(0)

        print(matrix)
        self.assertEqual(matrix.shape, (2, 2))

        self.assertEqual(matrix[0, 0], 0)
        self.assertEqual(matrix[1, 1], 0)

        self.assertGreater(matrix[0, 1], 0)
        self.assertGreater(matrix[1, 0], 0)

        self.assertEqual(matrix[0, 1], self.flow_advection(1, 10, 0))
        self.assertEqual(matrix[1, 0], self.flow_advection(1, 10, 1))
