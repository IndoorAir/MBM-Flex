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

# ############################################################################ #
#                            MBM-Flex main script
#
# Define the global settings of the simulation and of the whole building, the
# time control of the simulation, and the name of the output directory.
#
# The characteristics of the building and of each individual room are set in the
# 'config_rooms/' directory. The initial conditions in each individual room are
# set in the 'config_chem/' directory.
# ############################################################################ #

import os
import math
import pickle
from datetime import datetime
from typing import Dict, List
from multiroom_model.global_settings import GlobalSettings
from multiroom_model.simulation import Simulation, RoomChemistry, Aperture, WindDefinition
from multiroom_model.json_parser import BuildingJSONParser

# ############################################################################ #

if __name__ == '__main__':

    # ambient pressure (mbar) is assumed to be constant, and is the same in all rooms
    ambient_press = 1013.0

    # ambient temperature (K) is assumed to be constant
    ambient_temp = 293.0

    # ambient air density (assuming dry air), in kg/m3
    rho = (100*ambient_press) / (287.050 * ambient_temp)

    # Simulation settings
    global_settings = GlobalSettings(
        filename='chem_mech/rcs_2023.fac',
        INCHEM_additional=False,
        particles=False,
        constrained_file=None,
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

    # Simulation time control (in seconds)
    # - start_time: starting time of the simulation (0 is midnight)
    # - total_time: total duration of the simulation
    # - transport_interval: how often inter-room transport is applied
    start_time=0
    total_time=20
    transport_interval=6

    # Name of the folder where the model results will be saved. The folder name
    # will be automatically prefixed with the date and time of the simulation.
    mbm_output='output'

    # ############################################################################ #
    # DO NOT CHANGE THE CODE BELOW                                                 #
    # ############################################################################ #

    # Read the json file for each room and extract all the data we need from it
    input_data = BuildingJSONParser.from_json_file("config_rooms/building.json")

    # Definition of the rooms
    rooms_dictionary: Dict[str,RoomChemistry] = input_data["rooms"]

    # Definition of the apertures
    apertures: List[Aperture] = input_data['apertures']

    # Definition of the wind
    wind_definition: WindDefinition = input_data['wind']

    # We dont need the keys of the rooms anymore now we have populated them
    rooms: List[RoomChemistry] = list(rooms_dictionary.values())

    # Build the simulation class
    # This step will build jacobeans for each of the rooms in preparation for running later
    simulation = Simulation(
        global_settings=global_settings,
        rooms=rooms,
        apertures=apertures,
        wind_definition=wind_definition)

    # An initial conditions text file for each room
    initial_conditions = input_data['initial_conditions']

    # Run the simulation starting at time t0 for a duration of t_total seconds
    # Interrupt the inchempy solver to apply transport every t_interval seconds
    result = simulation.run(
        t0=start_time,
        t_total=total_time,
        t_interval=transport_interval,
        init_conditions=initial_conditions
    )

    results_dictionary = dict((key, result[r]) for key, r in rooms_dictionary.items())

    # Save results to pickle file
    mbm_output_dir = ('%s_%s' % (datetime.now().strftime('%y%m%d_%H%M%S'), mbm_output))
    os.mkdir('%s/%s' % (os.getcwd(), mbm_output_dir))
    pickle.dump(results_dictionary, open('%s/mbm_results.pkl' % mbm_output_dir, "wb"))
