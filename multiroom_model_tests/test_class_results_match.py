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
import pickle

from modules.inchem_main_class import InChemPyMainClass
from multiroom_model.inchem import generate_main_class, run_main_class
from multiroom_model.inchem import InChemPyInstance
from numpy.testing import assert_allclose


class TestInChemPyClassResults(unittest.TestCase):
    # def test_run_inchem_py_to_get_results(self):
    #    inchem_py_instance: InChemPyInstance = InChemPyInstance(
    #        particles=False,
    #        INCHEM_additional=False,
    #        seconds_to_integrate=360,
    #        output_graph=False)
    #
    #    inchem_py_instance.run()

    #def test_run_inchem_py_to_get_results(self):
    #    inchem_py_instance: InChemPyInstance = InChemPyInstance(
    #        particles=False,
    #        INCHEM_additional=False,
    #        seconds_to_integrate=180,
    #        output_graph=False)
    #    inchem_py_instance.run()
    #    inchem_py_instance = InChemPyInstance(
    #        particles=False,
    #        INCHEM_additional=False,
    #        initials_from_run=True,
    #        t0=180,
    #        seconds_to_integrate=180,
    #        output_graph=False)
    #    inchem_py_instance.run()

    def benchmark_results(self):
        with open('multiroom_model_tests/test_run_inchem_py_to_get_results.pickle', 'rb') as file:
            result = pickle.load(file)
        return result

    def test_single_phase_run_results_repeatable(self):
        inchem_main_class: InChemPyMainClass= generate_main_class(
            particles=False,
            INCHEM_additional=False)


        output_concentrations_A, _ = run_main_class(inchem_main_class,
            initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

        output_concentrations_B, _ = run_main_class(inchem_main_class,
            initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

        self.assertEqual(4, len(output_concentrations_A))
        self.assertEqual(4, len(output_concentrations_B))

        for species in inchem_main_class.species:
            self.assertEqual(output_concentrations_A.get(species)[0.0],
                             output_concentrations_B.get(species)[0.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations_A.get(species)[60.0],
                             output_concentrations_B.get(species)[60.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations_A.get(species)[120.0],
                             output_concentrations_B.get(species)[120.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations_A.get(species)[180.0],
                             output_concentrations_B.get(species)[180.0], f"species check failed: {species}")

    def test_single_phase_run_results_match_double_phase(self):
        inchem_main_class: InChemPyMainClass= generate_main_class(
            particles=False,
            INCHEM_additional=False)

        output_concentrations_A1, _ = run_main_class(inchem_main_class,
            initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)

        output_concentrations_A2, _ = run_main_class(inchem_main_class,
            initials_from_run= True, initial_dataframe= output_concentrations_A1, t0=180, seconds_to_integrate=180)

        output_concentrations_B, _ = run_main_class(inchem_main_class,
            initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=360)

        self.assertEqual(4, len(output_concentrations_A1))
        self.assertEqual(4, len(output_concentrations_A2))
        self.assertEqual(7, len(output_concentrations_B))

        for species in inchem_main_class.species:
            self.assertEqual(output_concentrations_A1.get(species)[0.0],
                             output_concentrations_B.get(species)[0.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations_A1.get(species)[60.0],
                             output_concentrations_B.get(species)[60.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations_A1.get(species)[120.0],
                             output_concentrations_B.get(species)[120.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations_A1.get(species)[180.0],
                             output_concentrations_B.get(species)[180.0], f"species check failed: {species}")

            assert_allclose(output_concentrations_A2.get(species)[180.0],
                            output_concentrations_B.get(species)[180.0],
                            rtol=1.0e-3, atol=1.0e-17, err_msg=f"species check failed: {species}")
            assert_allclose(output_concentrations_A2.get(species)[240.0],
                            output_concentrations_B.get(species)[240.0],
                            rtol=1.0e-3, atol=1.0e-17, err_msg=f"species check failed: {species}")
            assert_allclose(output_concentrations_A2.get(species)[300.0],
                            output_concentrations_B.get(species)[300.0],
                            rtol=1.0e-3, atol=1.0e-17, err_msg=f"species check failed: {species}")
            assert_allclose(output_concentrations_A2.get(species)[360.0],
                            output_concentrations_B.get(species)[360.0],
                            rtol=1.0e-3, atol=1.0e-17, err_msg=f"species check failed: {species}")

    def test_single_phase_run_matches_instance(self):
        inchem_main_class: InChemPyMainClass= generate_main_class(
            particles=False,
            INCHEM_additional=False)


        output_concentrations, _ = run_main_class(inchem_main_class,
            initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=360)

        benchmark_concentrations = self.benchmark_results()

        for species in inchem_main_class.species:
            self.assertEqual(output_concentrations.get(species)[0.0],
                             benchmark_concentrations.get(species)[0.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations.get(species)[60.0],
                             benchmark_concentrations.get(species)[60.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations.get(species)[120.0],
                             benchmark_concentrations.get(species)[120.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations.get(species)[180.0],
                             benchmark_concentrations.get(species)[180.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations.get(species)[240.0],
                             benchmark_concentrations.get(species)[240.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations.get(species)[300.0],
                             benchmark_concentrations.get(species)[300.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations.get(species)[360.0],
                             benchmark_concentrations.get(species)[360.0], f"species check failed: {species}")

    def test_double_phase_run_matches_instance(self):
        inchem_main_class: InChemPyMainClass= generate_main_class(
            particles=False,
            INCHEM_additional=False)


        interim_concentrations, _ = run_main_class(inchem_main_class,
            initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)
        output_concentrations, _ = run_main_class(inchem_main_class,
            initials_from_run= True, initial_dataframe=interim_concentrations, t0=180, seconds_to_integrate=180)

        benchmark_concentrations = self.benchmark_results()

        for species in inchem_main_class.species:
            self.assertEqual(interim_concentrations.get(species)[0.0],
                             benchmark_concentrations.get(species)[0.0], f"species check failed: {species}")
            self.assertEqual(interim_concentrations.get(species)[60.0],
                             benchmark_concentrations.get(species)[60.0], f"species check failed: {species}")
            self.assertEqual(interim_concentrations.get(species)[120.0],
                             benchmark_concentrations.get(species)[120.0], f"species check failed: {species}")
            self.assertEqual(interim_concentrations.get(species)[180.0],
                             benchmark_concentrations.get(species)[180.0], f"species check failed: {species}")
            assert_allclose(output_concentrations.get(species)[240.0],
                            benchmark_concentrations.get(species)[240.0],
                            rtol=1.0e-3, atol=1.0e-17, err_msg=f"species check failed: {species}")
            assert_allclose(output_concentrations.get(species)[300.0],
                            benchmark_concentrations.get(species)[300.0],
                            rtol=1.0e-3, atol=1.0e-17, err_msg=f"species check failed: {species}")
            assert_allclose(output_concentrations.get(species)[360.0],
                            benchmark_concentrations.get(species)[360.0],
                            rtol=1.0e-3, atol=1.0e-17, err_msg=f"species check failed: {species}")

    def test_double_phase_run_matches_double_phase_instance(self):
        inchem_main_class: InChemPyMainClass= generate_main_class(
            particles=False,
            INCHEM_additional=False)


        interim_concentrations, _ = run_main_class(inchem_main_class,
            initial_conditions_gas='initial_concentrations.txt', seconds_to_integrate=180)
        output_concentrations, _ = run_main_class(inchem_main_class,
            initials_from_run= True, initial_dataframe=interim_concentrations, t0=180, seconds_to_integrate=180)

        with open('multiroom_model_tests/run_0_to_180.pickle', 'rb') as file:
            benchmark_1 = pickle.load(file)

        with open('multiroom_model_tests//run_180_to_360.pickle', 'rb') as file:
            benchamark_2 = pickle.load(file)

        for species in inchem_main_class.species:
            self.assertEqual(interim_concentrations.get(species)[0.0],
                             benchmark_1.get(species)[0.0], f"species check failed: {species}")
            self.assertEqual(interim_concentrations.get(species)[60.0],
                             benchmark_1.get(species)[60.0], f"species check failed: {species}")
            self.assertEqual(interim_concentrations.get(species)[120.0],
                             benchmark_1.get(species)[120.0], f"species check failed: {species}")
            self.assertEqual(interim_concentrations.get(species)[180.0],
                             benchmark_1.get(species)[180.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations.get(species)[180.0],
                             benchamark_2.get(species)[180.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations.get(species)[240.0],
                             benchamark_2.get(species)[240.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations.get(species)[300.0],
                             benchamark_2.get(species)[300.0], f"species check failed: {species}")
            self.assertEqual(output_concentrations.get(species)[360.0],
                             benchamark_2.get(species)[360.0], f"species check failed: {species}")
