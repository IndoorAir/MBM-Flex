import math
import unittest
from unittest.mock import Mock, patch

from multiroom_model.aperture_calculations import Fluxes
from multiroom_model.global_settings import GlobalSettings
from multiroom_model.room_chemistry import RoomChemistry
from multiroom_model.room_inchempy_evolver import RoomInchemPyEvolver
from multiroom_model.room_factory import (
    build_rooms,
    populate_room_with_emissions_file,
    populate_room_with_tvar_file,
    populate_room_with_expos_file
)

from multiroom_model.aperture_flow_calculations import ApertureFlowCalculator


class TestApertureFlowCalculations(unittest.TestCase):

    @classmethod
    def generate_a_dataframe(cls):
        rooms = build_rooms("config_rooms/mr_tcon_room_params.csv")
        room_ids = list(rooms.keys())
        for i, room in rooms.items():
            populate_room_with_emissions_file(room, f"config_rooms/mr_room_emis_params_{i}.csv")
            populate_room_with_tvar_file(room, f"config_rooms/mr_tvar_room_params_{i}.csv")
            populate_room_with_expos_file(room, f"config_rooms/mr_tvar_expos_params_{i}.csv")
        global_settings = GlobalSettings(
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
        room: RoomChemistry = rooms[2]

        evolver = RoomInchemPyEvolver(room, global_settings)

        evolver.inchem.species

        output_data, _ = evolver.run(
            t0=0,
            seconds_to_integrate=0,
            initial_text_file='initial_concentrations.txt'
        )
        return output_data, evolver.inchem.species

    @classmethod
    def setUpClass(cls):
        cls.dataframe, cls.species = cls.generate_a_dataframe()
        cls.sample_species = ["CO", "NO3", "H2O2", "PART100"]

    def test_species(self):
        calculator = ApertureFlowCalculator(self.dataframe.columns)

        out_vars_without_out = list(map(lambda i: i[: -3], calculator.outdoor_var_list))

        print(len(self.dataframe.columns))
        print(len(self.species))
        print(len(calculator.indoor_var_list))
        print(len(calculator.outdoor_var_list))

        for s in self.sample_species:
            self.assertIn(s, self.species)
            self.assertIn(s, self.dataframe.columns)
            self.assertIn(s, calculator.indoor_var_list)
            self.assertIn(f"{s}OUT", calculator.outdoor_var_list)
            self.assertIn(s, out_vars_without_out)

        for s in calculator.indoor_var_list:
            pass
            # self.assertIn(s, self.species)

        for s in out_vars_without_out:
            pass
            # self.assertIn(s, calculator.indoor_var_list)

    def test_exchange_transfer_between_rooms_with_matching_concentration(self):
        calculator = ApertureFlowCalculator(self.dataframe.columns)

        origin_volume = 100
        destination_volume = 76

        origin_concentration = self.dataframe.iloc[-1, :]
        destination_concentration = self.dataframe.iloc[-1, :]

        exchange_flux = Fluxes(0.2, 0.2)
        delta_time = 2.14

        room_1_concentration_change, room_2_concentration_change = calculator.concentration_changes(
            exchange_flux,
            delta_time,
            origin_concentration,
            destination_concentration,
            origin_volume,
            destination_volume)

        for label, value in room_1_concentration_change.items():
            self.assertIn(label, calculator.indoor_var_list)
            self.assertEqual(value, 0)

        for label, value in room_2_concentration_change.items():
            self.assertIn(label, calculator.indoor_var_list)
            self.assertEqual(value, 0)

    def test_exchange_transfer_between_rooms_with_concentration_difference(self):
        calculator = ApertureFlowCalculator(self.dataframe.columns)

        origin_volume = 100
        destination_volume = 76

        origin_concentration = self.dataframe.iloc[-1, :]
        destination_concentration = self.dataframe.iloc[-1, :]

        destination_concentration.loc["CO"] += 10

        exchange_flux = Fluxes(0.2, 0.2)
        delta_time = 2.14

        room_1_concentration_change, room_2_concentration_change = calculator.concentration_changes(
            exchange_flux,
            delta_time,
            origin_concentration,
            destination_concentration,
            origin_volume,
            destination_volume)

        absolute_CO_change = 0.2*2.14*10

        for label, value in room_1_concentration_change.items():

            expected_change = 0 if label != "CO" else absolute_CO_change/origin_volume

            self.assertIn(label, calculator.indoor_var_list)
            self.assertEqual(value, expected_change, f"wrong concentration change for {label}")

        for label, value in room_2_concentration_change.items():

            expected_change = 0 if label != "CO" else -absolute_CO_change/destination_volume

            self.assertIn(label, calculator.indoor_var_list)
            self.assertEqual(value, expected_change, f"wrong concentration change for {label}")

    def test_advection_transfer_between_rooms_with_matching_concentration(self):
        calculator = ApertureFlowCalculator(self.dataframe.columns)

        origin_volume = 100
        destination_volume = 76

        origin_concentration = self.dataframe.iloc[-1, :]
        destination_concentration = self.dataframe.iloc[-1, :]

        with self.subTest("flow from room 1 to room 2"):
            exchange_flux = Fluxes(0.4, 0)
            delta_time = 2.14

            room_1_concentration_change, room_2_concentration_change = calculator.concentration_changes(
                exchange_flux,
                delta_time,
                origin_concentration,
                destination_concentration,
                origin_volume,
                destination_volume)

            for label, value in room_1_concentration_change.items():
                # everything is departing from room 1, hence dependence on origin_concentration
                expected_change = -0.4*2.14*origin_concentration.loc[label]/origin_volume
                self.assertIn(label, calculator.indoor_var_list)
                self.assertEqual(value, expected_change)

            for label, value in room_2_concentration_change.items():
                # everything is moving from room 1, hence dependence on origin_concentration
                expected_change = 0.4*2.14*origin_concentration.loc[label]/destination_volume
                self.assertIn(label, calculator.indoor_var_list)
                self.assertEqual(value, expected_change)

        with self.subTest("flow from room 2 to room 1"):
            exchange_flux = Fluxes(0, 0.4)

            room_1_concentration_change, room_2_concentration_change = calculator.concentration_changes(
                exchange_flux,
                delta_time,
                origin_concentration,
                destination_concentration,
                origin_volume,
                destination_volume)

            for label, value in room_1_concentration_change.items():
                # everything is departing from room 2, hence dependence on origin_concentration
                expected_change = 0.4*2.14*destination_concentration.loc[label]/origin_volume
                self.assertIn(label, calculator.indoor_var_list)
                self.assertEqual(value, expected_change)

            for label, value in room_2_concentration_change.items():
                # everything is moving from room 2, hence dependence on origin_concentration
                expected_change = -0.4*2.14*destination_concentration.loc[label]/destination_volume
                self.assertIn(label, calculator.indoor_var_list)
                self.assertEqual(value, expected_change)

    def test_advection_transfer_between_rooms_with_concentration_difference(self):
        calculator = ApertureFlowCalculator(self.dataframe.columns)

        origin_volume = 100
        destination_volume = 76

        origin_concentration = self.dataframe.iloc[-1, :]
        destination_concentration = self.dataframe.iloc[-1, :]

        destination_concentration.loc["CO"] += 10

        with self.subTest("flow from room 1 to room 2"):
            exchange_flux = Fluxes(0.4, 0)
            delta_time = 2.14

            room_1_concentration_change, room_2_concentration_change = calculator.concentration_changes(
                exchange_flux,
                delta_time,
                origin_concentration,
                destination_concentration,
                origin_volume,
                destination_volume)

            for label, value in room_1_concentration_change.items():
                # everything is departing from room 1, hence dependence on origin_concentration
                expected_change = -0.4*2.14*origin_concentration.loc[label]/origin_volume
                self.assertIn(label, calculator.indoor_var_list)
                self.assertEqual(value, expected_change)

            for label, value in room_2_concentration_change.items():
                # everything is moving from room 1, hence dependence on origin_concentration
                expected_change = 0.4*2.14*origin_concentration.loc[label]/destination_volume
                self.assertIn(label, calculator.indoor_var_list)
                self.assertEqual(value, expected_change)

        with self.subTest("flow from room 2 to room 1"):
            exchange_flux = Fluxes(0, 0.4)

            room_1_concentration_change, room_2_concentration_change = calculator.concentration_changes(
                exchange_flux,
                delta_time,
                origin_concentration,
                destination_concentration,
                origin_volume,
                destination_volume)

            for label, value in room_1_concentration_change.items():
                # everything is departing from room 2, hence dependence on origin_concentration
                expected_change = 0.4*2.14*destination_concentration.loc[label]/origin_volume
                self.assertIn(label, calculator.indoor_var_list)
                self.assertEqual(value, expected_change)

            for label, value in room_2_concentration_change.items():
                # everything is moving from room 2, hence dependence on origin_concentration
                expected_change = -0.4*2.14*destination_concentration.loc[label]/destination_volume
                self.assertIn(label, calculator.indoor_var_list)
                self.assertEqual(value, expected_change)

    def test_advection_transfer_to_outdoor(self):
        calculator = ApertureFlowCalculator(self.dataframe.columns)

        origin_volume = 100

        origin_concentration = self.dataframe.iloc[-1, :]

        exchange_flux = Fluxes(0.4, 0)
        delta_time = 2.14

        room_1_concentration_change = calculator.outdoor_concentration_changes(
            exchange_flux,
            delta_time,
            origin_concentration,
            origin_volume)

        for label, value in room_1_concentration_change.items():
            self.assertIn(label, origin_concentration.keys())
            expected_change = -2.14*0.4*origin_concentration.loc[label]/origin_volume
            self.assertEqual(value, expected_change, f"wrong concentration change for {label}")

    def test_advection_transfer_from_outdoor(self):
        calculator = ApertureFlowCalculator(self.dataframe.columns)

        origin_volume = 100

        origin_concentration = self.dataframe.iloc[-1, :]

        exchange_flux = Fluxes(0, 0.4)
        delta_time = 2.14

        room_1_concentration_change = calculator.outdoor_concentration_changes(
            exchange_flux,
            delta_time,
            origin_concentration,
            origin_volume)

        for label, value in room_1_concentration_change.items():
            self.assertIn(label, origin_concentration.keys())
            expected_change = 2.14*0.4*origin_concentration.loc[f"{label}OUT"] / \
                origin_volume if f"{label}OUT" in calculator.outdoor_var_list else 0
            self.assertEqual(value, expected_change, f"wrong concentration change for {label}")

    def test_exchange_transfer_to_outdoor(self):
        calculator = ApertureFlowCalculator(self.dataframe.columns)

        origin_volume = 100

        origin_concentration = self.dataframe.iloc[-1, :]

        exchange_flux = Fluxes(0.2, 0.2)
        delta_time = 2.14

        room_1_concentration_change = calculator.outdoor_concentration_changes(
            exchange_flux,
            delta_time,
            origin_concentration,
            origin_volume)

        for label, value in room_1_concentration_change.items():

            expected_outwards_change = -2.14*0.2*origin_concentration.loc[label]

            expected_inwards_change = 2.14*0.2*origin_concentration.loc[f"{label}OUT"] \
                if f"{label}OUT" in calculator.outdoor_var_list else 0

            self.assertIn(label, origin_concentration.keys())
            self.assertEqual(value, (expected_inwards_change+expected_outwards_change) /
                             origin_volume, f"wrong concentration change for {label}")
