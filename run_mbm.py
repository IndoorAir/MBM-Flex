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
# A copy of the GPLv3 license can be found in the file LICENSE at the root of
# the MBM-Flex project.
#
# ############################################################################ #

import math
import pickle
from typing import Dict, List
from multiroom_model.global_settings import GlobalSettings
from multiroom_model.simulation import Simulation, RoomChemistry, Aperture, WindDefinition
from multiroom_model.json_parser import BuildingJSONParser

# Define some global settings which are true for the whole building
if __name__ == '__main__':

    ambient_press = 1013.0   # ambient pressure (mbar) is assumed to be constant, and is the same in all rooms
    ambient_temp = 293.0     # ambient temperature (K) is assumed to be constant
    # ambient air density (assuming dry air), in kg/m3
    rho = (100*ambient_press) / (287.050 * ambient_temp)

    global_settings = GlobalSettings(
        filename='chem_mech/mcm_subset.fac',
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

    # Read the json file for the room and extract all the data we need from it
    input_data = BuildingJSONParser.from_json_file("config_rooms/building.json")

    # the rooms
    rooms_dictionary: Dict[str,RoomChemistry] = input_data["rooms"]

    # the apertures
    apertures: List[Aperture] = input_data['apertures']

    # the definition of the wind
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

    # an initial conditions text file for each room
    initial_conditions = input_data['initial_conditions']

    # Run the simulation starting at time t0
    # Run for a duration of t_total seconds
    # interrupt the inchempy solver to apply the effects of windows every t_interval seconds
    result = simulation.run(
        t0=0,
        t_total=20,
        t_interval=6,
        init_conditions=initial_conditions
    )

    # Save to pickle file

    results_dictionary = dict((key, result[r]) for key, r in rooms_dictionary.items())

    pickle.dump(results_dictionary, open("./results.pkl", "wb"))

    # Make use of results here eg
    # plot tool

    # Demo: Print one of the many results to the output
    species_of_interest = "CO"
    time_of_interest = 9

    print(f"\n\nCO concentration in room 1 after 9 seconds = {results_dictionary['room 1'][species_of_interest][time_of_interest]}")
