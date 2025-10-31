import unittest
import math
from multiroom_model.aperture_factory import build_apertures_from_double_definition, build_wind_definition
from multiroom_model.transport_paths import paths_through_building
from multiroom_model.room_factory import (
    build_rooms,
    populate_room_with_emissions_file,
    populate_room_with_tvar_file,
    populate_room_with_expos_file
)
from multiroom_model.aperture_calculations import ApertureCalculation, Side
from multiroom_model.simulation import Simulation
from multiroom_model.global_settings import GlobalSettings


class TestBuildingSimulation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rooms = build_rooms("config_rooms/mr_tcon_room_params.csv")

        for i, room in cls.rooms.items():
            populate_room_with_emissions_file(room, f"config_rooms/mr_room_emis_params_{i}.csv")
            populate_room_with_tvar_file(room, f"config_rooms/mr_tvar_room_params_{i}.csv")
            populate_room_with_expos_file(room, f"config_rooms/mr_tvar_expos_params_{i}.csv")

        cls.apertures = build_apertures_from_double_definition("config_rooms/mr_tcon_building.csv", cls.rooms)
        cls.wind_definition = build_wind_definition("config_rooms/mr_tvar_wind_params.csv")
        cls.rooms = list(cls.rooms.values())

        ambient_press = 1013.0   # ambient pressure (mbar) is assumed to be constant, and is the same in all rooms
        ambient_temp = 293.0     # ambient temperature (K) is assumed to be constant
        
        rho = (100*ambient_press) / (287.050 * ambient_temp) # ambient air density (assuming dry air), in kg/m3

        cls.global_settings = GlobalSettings(
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
        cls.simulation = Simulation(cls.global_settings, cls.rooms, cls.apertures, cls.wind_definition)

    def test_aperture_calculations(self):

        transport_paths = paths_through_building(self.rooms, self.apertures)
        self.assertEqual(len(transport_paths), 21)

        calculators = [
            ApertureCalculation(a, transport_paths,
                                self.apertures,
                                self.global_settings.building_direction_in_radians,
                                self.global_settings.air_density,
                                (self.global_settings.upwind_pressure_coefficient,
                                 self.global_settings.downwind_pressure_coefficient))
            for a in self.apertures]

        for i in range(len(calculators)):
            calculator = calculators[i]

            sim_calc, origin_index, destination_index, _, _ = self.simulation._aperture_calculators[i]

            self.assertTrue(type(origin_index) is int)
            self.assertEqual(self.rooms.index(calculator.aperture.origin), origin_index)
            if (calculator.is_outdoor_aperture):
                self.assertTrue(type(calculator.aperture.destination) is Side)
                self.assertTrue(destination_index is None)
            else:
                self.assertTrue(type(destination_index) is int)
                self.assertEqual(self.rooms.index(calculator.aperture.destination), destination_index)

            self.assertFalse(calculator.has_advection_flow(0, 0))
            self.assertFalse(sim_calc.has_advection_flow(0, 0))
            self.assertEqual(calculator.has_advection_flow(0, 0), sim_calc.has_advection_flow(0, 0))
            self.assertEqual(calculator.exchange_category(0, 0), sim_calc.exchange_category(0, 0))
            self.assertEqual(calculator.exchange_flow_rate(0, 0), sim_calc.exchange_flow_rate(0, 0))
            self.assertEqual(calculator.trans_matrix_contributions(0, 0).from_1_to_2,
                             sim_calc.trans_matrix_contributions(0, 0).from_1_to_2)
            self.assertEqual(calculator.trans_matrix_contributions(0, 0).from_2_to_1,
                             sim_calc.trans_matrix_contributions(0, 0).from_2_to_1)

            self.assertTrue(calculator.has_advection_flow(1, 0))
            self.assertTrue(sim_calc.has_advection_flow(1, 0))
            self.assertEqual(calculator.exchange_category(1, 0), sim_calc.exchange_category(1, 0))
            self.assertEqual(calculator.has_advection_flow(1, 0), sim_calc.has_advection_flow(1, 0))
            self.assertEqual(calculator.advection_flow_rate(1, 0), sim_calc.advection_flow_rate(1, 0))
            self.assertEqual(calculator.trans_matrix_contributions(1, 0).from_1_to_2,
                             sim_calc.trans_matrix_contributions(1, 0).from_1_to_2)
            self.assertEqual(calculator.trans_matrix_contributions(1, 0).from_2_to_1,
                             sim_calc.trans_matrix_contributions(1, 0).from_2_to_1)


    def test_running(self):
        
        initial_conditions = dict([(r, 'initial_concentrations.txt') for r in self.rooms])

        result = self.simulation.run(
            t0=0.0,
            t_total=25,
            t_interval=3.0,
            init_conditions=initial_conditions
        )
