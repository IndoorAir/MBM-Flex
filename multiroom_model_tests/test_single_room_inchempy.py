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
from multiroom_model.inchem import generate_main_class, run_main_class
from multiroom_model.room_inchempy_evolver import interpret_light_on_times


class TestAssembleAllRoomsFromCSV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        building = BuildingJSONParser.from_json_file("config_rooms/building.json")
        cls.rooms = list(building['rooms'].values())

        cls.global_settings = GlobalSettings(
            filename='chem_mech/mcm_subset.fac',
            INCHEM_additional=False,
            particles=False,
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

    def test_room_inchempy(self):
        room: RoomChemistry = self.rooms[1]

        timed_emissions = hasattr(room, "emissions")
        if timed_emissions:
            timed_inputs = {k: v.values() for k, v in room.emissions.items()}
        else:
            timed_inputs = None

        const_dict = {
            'O2': 0.2095,
            'N2': 0.7809,
            'H2': 550e-9,
            'saero': 1.3e-2  # aerosol surface area concentration
        }

        inchem = generate_main_class(
            filename=self.global_settings.filename,
            INCHEM_additional=self.global_settings.INCHEM_additional,
            particles=self.global_settings.particles,
            constrained_file=self.global_settings.constrained_file,
            output_folder=self.global_settings.output_folder,
            dt=self.global_settings.dt,
            volume=room.volume_in_m3,
            surface_area=room.surface_area_dictionary(),
            const_dict=const_dict,
            H2O2_dep=self.global_settings.H2O2_dep,
            O3_dep=self.global_settings.O3_dep,
            custom=self.global_settings.custom,
            timed_emissions=timed_emissions,
            timed_inputs=timed_inputs,
            custom_filename=self.global_settings.custom_filename
        )
        t0 = 0
        seconds_to_integrate = 10
        initial_dataframe = None
        initials_from_run = False
        initial_conditions_gas = 'initial_concentrations.txt'

        adults = room.n_adults.value_at_time(t0)
        children = room.n_children.value_at_time(t0)

        rel_humidity = room.rh_in_percent.value_at_time(t0)
        room_temperature = room.temp_in_kelvin.value_at_time(t0)
        spline = 'Linear'
        ambient_press = 1013.0
        M = ((100*ambient_press)/(8.3144626*room_temperature))*(6.0221408e23/1e6)  # number density (molecule cm^-3)
        # print('mrt=',mrt,'M=',M)

        # Place any parameter that needs to remain constant in the below dictionary.
        const_dict = {
            'O2': 0.2095*M,
            'N2': 0.7809*M,
            'H2': 550e-9*M,
            'saero': 1.3e-2  # aerosol surface area concentration
        }
        light_on_times = interpret_light_on_times(room.light_switch, t0+seconds_to_integrate)
        temperatures = list(zip(room.temp_in_kelvin.times(), room.temp_in_kelvin.values()))
        ACRate_dict = dict(zip(room.airchange_in_per_second.times(), room.airchange_in_per_second.values()))

        result = run_main_class(inchem,
                                t0=t0,
                                seconds_to_integrate=seconds_to_integrate,
                                dt=self.global_settings.dt,
                                timed_emissions=timed_emissions,
                                timed_inputs=timed_inputs,
                                spline=spline,
                                temperatures=temperatures,
                                rel_humidity=rel_humidity,
                                const_dict=const_dict,
                                M=M,
                                light_type=room.light_type,
                                glass=room.glass_type,
                                diurnal=self.global_settings.diurnal,
                                city=self.global_settings.city,
                                date=self.global_settings.date,
                                lat=self.global_settings.lat,
                                ACRate_dict=ACRate_dict,
                                light_on_times=light_on_times,
                                initial_conditions_gas=initial_conditions_gas,
                                initials_from_run=initials_from_run,
                                path=self.global_settings.path,
                                adults=adults,
                                children=children,
                                output_folder=self.global_settings.output_folder,
                                reactions_output=self.global_settings.reactions_output,
                                initial_dataframe=initial_dataframe
                                )
