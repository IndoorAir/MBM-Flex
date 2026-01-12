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

import pickle
import unittest

from multiroom_model.global_settings import GlobalSettings
from multiroom_model.json_parser import BuildingJSONParser
from multiroom_model.simulation import Simulation


class TestTwoRoomSimulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        building = BuildingJSONParser.from_json_file("config_rooms/building.json")
        cls.rooms = list(building['rooms'].values())

        cls.global_settings = GlobalSettings(
            filename='chem_mech/mcm_subset.fac',
            INCHEM_additional=False,
            particles=True,
            constrained_file=None,
            output_folder=None,
            dt=1.0,
            H2O2_dep=False,
            O3_dep=False,
            custom=False,
            custom_filename=None,
            diurnal=True,
            city='London_urban',
            date='21-06-2020',
            lat=45.4,
            path=None,
            reactions_output=False
        )

    def test_9_room_simulation(self):
        rooms = self.rooms

        simulation = Simulation(
            global_settings=self.global_settings,
            rooms=rooms,
            apertures=[])

        initial_conditions = dict([(r, 'initial_concentrations.txt') for r in rooms])

        result = simulation.run(
            t0=0.0,
            t_total=25,
            t_interval=3.0,
            init_conditions=initial_conditions
        )

        for r in rooms:

            self.assertEqual(result[r].index[0], 0.0)
            self.assertEqual(result[r].index[1], 1.0)
            self.assertEqual(result[r].index[2], 2.0)
            self.assertEqual(result[r].index[3], 3.0)

            self.assertEqual(result[r].index[4], 3.0)

            self.assertEqual(result[r].index[-3], 24.0)
            self.assertEqual(result[r].index[-2], 24.0)
            self.assertEqual(result[r].index[-1], 25.0)
            self.assertEqual(len(result[r].index), int(25/1)+1+int(25/3))

    @unittest.skip("Test is very long")
    def test_9_room_simulation_full_length(self):
        rooms = self.rooms

        self.global_settings.dt = 100

        simulation = Simulation(
            global_settings=self.global_settings,
            rooms=rooms,
            apertures=[])

        initial_conditions = dict([(r, 'initial_concentrations.txt') for r in rooms])

        result = simulation.run(
            t0=0.0,
            t_total=8280,
            t_interval=1500,
            init_conditions=initial_conditions
        )

        d = dict([(f"Room {i+1}", result[r]) for i, r in enumerate(rooms)])

        # pickle.dump(d, open(f"C:/temp/room_data/room_results.pkl","wb"))
