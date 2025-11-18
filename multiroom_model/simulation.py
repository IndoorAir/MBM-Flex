from typing import List, Tuple, Dict, Any
import math

from .aperture_flow_calculations import ApertureFlowCalculator
from .room_chemistry import RoomChemistry
from .aperture import Aperture, Side
from .room_inchempy_evolver import RoomInchemPyEvolver
from .aperture_calculations import ApertureCalculation
from .transport_paths import paths_through_building
from .global_settings import GlobalSettings
from .wind_definition import WindDefinition
import pandas as pd
import numpy as np
from multiprocess import Pool, cpu_count


def yellow_text(str):
    return f"\033[93m{str}\033[0m"


class Simulation:
    """
        @brief A class which can evolve the state of species in a set of rooms and apertures

    """

    def __init__(self,
                 global_settings: GlobalSettings,
                 rooms: List[RoomChemistry],
                 apertures: List[Aperture],
                 wind_definition: WindDefinition = None,
                 cpu_count: int = cpu_count()):
        """
        @brief Initialize the Simulation with
        details about the building, rooms and apertures.

        @param global_settings: Settings for the simulation which are independent of any one room or aperture.
        @param rooms: Information about the rooms.
        @param apertures: Information about the apertures.
        @param cpu_count: Cap on the number of processes to use when solving with multiprocess.
        """

        # Number of cores to use in multiprocessing
        self._cpu_count = cpu_count

        self._global_settings = global_settings
        self._rooms = rooms
        self._apertures = apertures
        self._wind_definition = wind_definition

        with Pool(self._cpu_count) as pool:

            # For each room, build a room_evolver (performed in parallel)
            args = [(r, self._global_settings) for r in self._rooms]
            self._room_evolvers: List[RoomInchemPyEvolver] = pool.starmap(self.build_room_evolver_starmap, args)

            # For each aperture, build an ApertureCalculation (performed in parallel)
            transport_paths = paths_through_building(self._rooms, self._apertures)
            args = [(w, transport_paths, self._apertures, self._rooms, self._global_settings) for w in self._apertures]
            self._aperture_calculators: List[ApertureCalculation] = pool.starmap(
                self.build_aperture_calculator_starmap, args)

    def run(self, init_conditions: dict, t0: float, t_total: float, t_interval: float):
        """
        @brief run the simulation over a time interval.

        @param init_conditions: The starting state of the rooms, as a dictionary of text files.
        @param t0: The time to start the simulation at.
        @param t_total: Duration to simulate.
        @param t_interval: How often to apply the effect of windows.
        """

        t_final: float = t0+t_total

        with Pool(self._cpu_count) as pool:

            # First step
            # using the init_conditions, perform a solve on each room (performed in parallel)
            room_results, solved_time = self._evolve_rooms(pool, t0, t_interval,
                                                           [init_conditions[r] for r in self._rooms], True)

            # Cumulate the results for this step and others into a cumulative results dictionary
            cumulative_room_results: Dict[RoomChemistry, pd.DataFrame] = dict(
                [(r, room_results[i].copy()) for i, r in enumerate(self._rooms)])

            # Use the aperture results to adjust the room results into the input for the next iteration
            initial_condition = self._apply_wind(pool, solved_time, t_interval, room_results)

            # Loop of incrementing time by t_interval and performing the operations
            # Stop when another increment would take it over the total
            while (solved_time+t_interval <= t_final):

                # Use the initial conditions and solve for the next time interval  (performed in parallel)
                room_results, solved_time = self._evolve_rooms(pool, solved_time, t_interval, initial_condition)
                # Add the new results to the cumulative result for all times
                cumulative_room_results = dict(
                    [(r, pd.concat([cumulative_room_results[r], room_results[i]], axis=0)) for i, r in enumerate(self._rooms)])

                # Use the aperture results to adjust the room results into appropriate initial conditions for the next iteration
                initial_condition = self._apply_wind(pool, solved_time, t_interval, room_results)

            # Final step  if there is any time smaller than a single interval left to be solved
            if solved_time < t_final:

                final_t_interval = t_final-solved_time

                room_results, solved_time = self._evolve_rooms(pool, solved_time, final_t_interval, initial_condition)

                # Add the new results to the cumulative result for all times
                cumulative_room_results = dict(
                    [(r, pd.concat([cumulative_room_results[r], room_results[i]], axis=0)) for i, r in enumerate(self._rooms)])

        return cumulative_room_results

    def wind_state(self, time):
        """
        Determine the wind speed and direction (in radians)
        """
        if self._wind_definition is None:
            return 0, 0
        else:
            wind_speed = self._wind_definition.wind_speed.value_at_time(time)
            wind_direction = self._wind_definition.wind_direction.value_at_time(time)
            wind_direction_in_radians = wind_direction if self._wind_definition.in_radians else math.radians(
                wind_direction)
            return wind_speed, wind_direction_in_radians

    def _apply_wind(self, pool, time, t_interval, room_results):
        """
        Applies the effect of the wind, to alter the state of the rooms
        Uses the pool to calculate the impact of each aperture on the room concentrations
        Applies these changes to the concentrations
        Return the new room concentrations
        """
        # Determine the properties of the wind at this time
        wind_speed, wind_direction_in_radians = self.wind_state(time)
        # For each aperture  calculate a aperture result  (performed in parallel)
        args = [(w, wind_speed, wind_direction_in_radians, t_interval, room_results, time)
                for w in self._aperture_calculators]
        aperture_results = pool.starmap(self.run_aperture_calculation_starmap, args)
        # Use the aperture results to adjust the room results into the input for the next iteration
        return self.apply_aperture_results(room_results, aperture_results, time)

    def _evolve_rooms(self, pool, t0, t_interval, initial_condition, txt_file=False):
        """
        Evolves each of the rooms independently for one interval of time
        Uses the pool to calculate the new concentration in each room
        Return the new room concentrations, and the time at which these are true
        """
        # Use the initial conditions (text or dataframe) to produce new room results using the room evolvers
        args = [(self._room_evolvers[i], t0, t_interval, initial_condition[i], txt_file) for i in range(len(self._rooms))]
        room_results = pool.starmap(self.run_room_evolver_starmap, args)
        # Check that each room resulted in a result at the final time
        # If a room failed to complete, then raise the exception
        success = True
        for i, r in enumerate(room_results):
            if r.index[-1] != t0+t_interval:
                success = False
                print(yellow_text(f"Simulation incomplete for room {i}, only ran to time {r.index[-1]}, expected {t0+t_interval}"))
        if not success:
            raise Exception(f"Simulation incomplete")
        # This results in a new time which we have solved to
        return room_results, t0+t_interval

    def trans_matrix(self, time: float):
        """
        @brief calculate the whole trans matrix at a given time.

        @param time: The time to calculate at.
        """
        # Determine the properties of the wind at this time
        wind_speed, wind_direction_in_radians = self.wind_state(time)
        size = len(self._rooms)+1

        # Make a result numpy matrix
        result = np.zeros((size, size))

        # For each aperture calculate the flux and add it to the resultant matrix
        for c in self._aperture_calculators:
            aperture_calculator, origin_index, destination_index, _, _ = c
            is_outdoor_aperture = destination_index is None
            i = origin_index+1
            j = 0 if is_outdoor_aperture else destination_index+1
            f = aperture_calculator.trans_matrix_contributions(wind_speed, wind_direction_in_radians)
            result[i, j] += f.from_1_to_2
            result[j, i] += f.from_2_to_1

        return result

    @staticmethod
    def apply_aperture_results(room_results, aperture_results, solved_time):
        """
        Applies the effect of the aperture results, to alter the state of the rooms
        Return the new room concentrations at the final time
        """
        # Make a new result from the current result at the solved time
        result = [result.loc[[solved_time], :].astype(float) for result in room_results]
        # Go through all the aperture results
        for room_1_concentration_change, room_2_concentration_change, origin_index, destination_index in aperture_results:
            # Adjust the concentrations of room_1 int the new results
            new_room_1_value = result[origin_index].loc[solved_time, :].add(
                room_1_concentration_change, fill_value=0.0)
            result[origin_index].loc[solved_time, :] = new_room_1_value
            # If there is a room 2, adjust the concentrations of room_2 int the new results
            if (destination_index is not None):
                new_room_2_value = result[destination_index].loc[solved_time, :].add(
                    room_2_concentration_change, fill_value=0.0)
                result[destination_index].loc[solved_time, :] = new_room_2_value

        # TODO: Do something here about the risk of negative concentrations
        # for example: `result = [r.clip(lower=0).fillna(0) for r in result]`

        # If a room concentration fell below 0, print a warning
        for i, r in enumerate(result):
            solved_time_result = r.loc[solved_time, :]
            negative_solved_time_result = solved_time_result[solved_time_result < 0]
            negative_species = negative_solved_time_result.index.tolist()
            if negative_species:
                species_str = ", ".join(negative_species)
                print(
                    yellow_text(f"Warning: Aperture effects resulted in a negative concentration in room {i} at time {solved_time}. Species: {species_str}")
                )

        # return the augmented results
        return result

    @staticmethod
    def build_room_evolver_starmap(room, global_settings):
        """
        Create one room evolver
        """
        return RoomInchemPyEvolver(room, global_settings)

    @staticmethod
    def run_room_evolver_starmap(evolver, t0, t_interval, initial_condition, txt_file):
        """
        Use the room evolver to calculate new room concentrations
        Start with an initial dataframe of concentrations or an initial text file
        """
        if (txt_file):
            df, _ = evolver.run(t0=t0, seconds_to_integrate=t_interval, initial_text_file=initial_condition)
        else:
            df, _ = evolver.run(t0=t0, seconds_to_integrate=t_interval, initial_dataframe=initial_condition)
        return df

    @staticmethod
    def build_aperture_calculator_starmap(aperture, transport_paths, apertures, rooms, global_settings):
        """
        Create one ApertureCalculation and the accompanying data to use it
        """
        origin_index = rooms.index(aperture.origin)
        destination_index = None if type(aperture.destination) == Side else rooms.index(aperture.destination)
        origin_volume = aperture.origin.volume_in_m3
        destination_volume = None if type(aperture.destination) == Side else aperture.destination.volume_in_m3
        calculator = ApertureCalculation(aperture,
                                         transport_paths,
                                         apertures,
                                         global_settings.building_direction_in_radians,
                                         global_settings.air_density,
                                         (global_settings.upwind_pressure_coefficient,
                                          global_settings.downwind_pressure_coefficient))
        return calculator, origin_index, destination_index, origin_volume, destination_volume

    @staticmethod
    def run_aperture_calculation_starmap(aperture_calculator_data,
                                         wind_speed, wind_direction,
                                         delta_time,
                                         room_results,
                                         solved_time):
        """
        Use the aperture calculation to:
        - calculate a flux based on the current wind
        - use an ApertureFlowCalculator to calculate the concentration changes
        - return the concentration changes, and the room indices they need to be applied to

        This does not apply the concentration changes, the changes can't be done in parallel
        """
        aperture_calculator, origin_index, destination_index, origin_volume, destination_volume = aperture_calculator_data

        # Calculate the flux relating to this aperture
        flux = aperture_calculator.trans_matrix_contributions(wind_speed, wind_direction)

        # build a flow calculator
        calculator = ApertureFlowCalculator(room_results[origin_index].columns)

        # switch depending on whether the aperture goes outside
        is_outdoor_aperture = (destination_index is None)
        if (is_outdoor_aperture):
            # For an outside aperture, only one concentration is used as an input
            origin_concentration = room_results[origin_index].loc[solved_time, :]
            origin_concentration_change = calculator.outdoor_concentration_changes(
                flux,
                delta_time,
                origin_concentration,
                origin_volume)
            # For an outside aperture, only one concentration change is calculated
            return origin_concentration_change, None, origin_index, None
        else:
            # For an indoor aperture, one concentration per room is used as an input
            origin_concentration = room_results[origin_index].loc[solved_time, :]
            destination_concentration = room_results[destination_index].loc[solved_time, :]
            origin_concentration_change, destination_concentration_change = calculator.concentration_changes(
                flux,
                delta_time,
                origin_concentration,
                destination_concentration,
                origin_volume,
                destination_volume)
            # For an indoor aperture, one concentration change per room is calculated
            return origin_concentration_change, destination_concentration_change, origin_index, destination_index
