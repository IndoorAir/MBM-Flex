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

from typing import List, Tuple
from .global_settings import GlobalSettings
from .room_chemistry import RoomChemistry
from .inchem import generate_main_class, run_main_class
from .time_dep_value import TimeDependentValue


def interpret_light_on_times(room_mrlswitch: List[Tuple[float, float]], end_of_total_integration: float) -> List[List[int]]:

    light_on_times = []

    for i in range(len(room_mrlswitch.values())-1):
        if (room_mrlswitch.values()[i] == 1):
            light_on_times.append([room_mrlswitch.times()[i], room_mrlswitch.times()[i+1]])
    if (room_mrlswitch.values()[-1] == 1):
        light_on_times.append([room_mrlswitch.times()[-1], room_mrlswitch.values()[0]+3600.0])

    return light_on_times


class RoomInchemPyEvolver:
    """
        @brief A class which can evolve the state of species in a room using Inchem py
        Initialization generates the jacobeans, then running updates species.

    """

    inchem = None
    room: RoomChemistry = None
    global_settings: GlobalSettings = None
    const_dict: dict = None

    def __init__(self, room: RoomChemistry, global_settings: GlobalSettings, const_dict: dict = None):

        # Store the room and settings
        self.room = room
        self.global_settings = global_settings

        # If the const dict is not provided, use this default one
        self.const_dict = const_dict or {
            'O2': 0.2095,
            'N2': 0.7809,
            'H2': 550e-9,
            'saero': 1.3e-2  # aerosol surface area concentration
        }

        # Change the rooms emisions into the format of dictionary which inchempy understands
        timed_emissions = hasattr(room, "emissions")
        if timed_emissions:
            timed_inputs = {k: v.values() for k, v in room.emissions.items()}
        else:
            timed_inputs = None

        #Generate an inchempy instance, (including calculating the jacobians for later use)
        self.inchem = generate_main_class(
            filename=self.global_settings.filename,
            INCHEM_additional=self.global_settings.INCHEM_additional,
            particles=self.global_settings.particles,
            constrained_file=self.global_settings.constrained_file,
            output_folder=self.global_settings.output_folder,
            dt=self.global_settings.dt,
            volume=room.volume_in_m3,
            surface_area=room.surface_area_dictionary(),
            const_dict=self.const_dict,
            H2O2_dep=self.global_settings.H2O2_dep,
            O3_dep=self.global_settings.O3_dep,
            custom=self.global_settings.custom,
            timed_emissions=timed_emissions,
            timed_inputs=timed_inputs,
            custom_filename=self.global_settings.custom_filename
        )

    def run(self, t0, seconds_to_integrate, initial_dataframe=None, initial_text_file=None, const_dict: dict = None):
        '''
        @brief: Runs the inchempy simulation for one precise time interval, initial conditions, and a const_dict
        returns [output_data, integration_times]
        '''

        # Interpret the 2 options for ways to define initial conditions
        initials_from_run = initial_dataframe is not None
        initial_conditions_gas = initial_text_file

        # use the start time to look up the numbers of children and adults
        adults = self.room.n_adults.value_at_time(t0)
        children = self.room.n_children.value_at_time(t0)

        # use the start time to look up the values for humidity and temperature
        rel_humidity = self.room.rh_in_percent.value_at_time(t0)
        room_temperature = self.room.temp_in_kelvin.value_at_time(t0)

        # We always use linear interpolation on the temperatures
        spline = 'Linear'

        #Hard coded pressure
        ambient_press = 1013.0

        #Using the pressure and temperature, we calculate a number-density M
        M = ((100*ambient_press)/(8.3144626*room_temperature))*(6.0221408e23/1e6)  # number density (molecule cm^-3)

        # Now we know M, we can update the const dictionary for the standard gasses
        cd = const_dict or {
            'O2': 0.2095*M,
            'N2': 0.7809*M,
            'H2': 550e-9*M,
            'saero': 1.3e-2  # aerosol surface area concentration
        }


        # Change the rooms time dependent properties to lists and dictionaries which inchempy understands
        light_on_times = interpret_light_on_times(self.room.light_switch, t0+seconds_to_integrate)
        temperatures = list(zip(self.room.temp_in_kelvin.times(), self.room.temp_in_kelvin.values()))
        ACRate_dict = dict(zip(self.room.airchange_in_per_second.times(), self.room.airchange_in_per_second.values()))

        # Change the rooms emisions into the format of dictionary which inchempy understands
        timed_emissions = hasattr(self.room, "emissions")
        if timed_emissions:
            timed_inputs = {k: v.values() for k, v in self.room.emissions.items()}
        else:
            timed_inputs = None

        # Run the inchempy instance with these properties, times and initial conditions
        result = run_main_class(self.inchem,
                                t0=t0,
                                seconds_to_integrate=seconds_to_integrate,
                                dt=self.global_settings.dt,
                                timed_emissions=timed_emissions,
                                timed_inputs=timed_inputs,
                                spline=spline,
                                temperatures=temperatures,
                                rel_humidity=rel_humidity,
                                const_dict=cd,
                                M=M,
                                light_type=self.room.light_type,
                                glass=self.room.glass_type,
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
        return result
