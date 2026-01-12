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

from multiroom_model.global_settings import GlobalSettings
from multiroom_model.json_parser import BuildingJSONParser
from multiroom_model.room_chemistry import RoomChemistry
from multiroom_model.room_inchempy_evolver import RoomInchemPyEvolver


class TestRoomEvolverClass(unittest.TestCase):
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
            dt=0.2,
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

    def test_room__evolver_class(self):
        room: RoomChemistry = self.rooms[2]

        evolver = RoomInchemPyEvolver(room, self.global_settings)

        output_data, integration_times = evolver.run(
            t0=0,
            seconds_to_integrate=10,
            initial_text_file='initial_concentrations.txt'
        )

    def test_room__evolver_class_run_twice(self):
        room: RoomChemistry = self.rooms[2]

        evolver = RoomInchemPyEvolver(room, self.global_settings)

        output_data, integration_times = evolver.run(
            t0=0,
            seconds_to_integrate=10,
            initial_text_file='initial_concentrations.txt'
        )

        output_data_part2, integration_times_part2 = evolver.run(
            t0=10,
            seconds_to_integrate=10,
            initial_dataframe=output_data
        )
