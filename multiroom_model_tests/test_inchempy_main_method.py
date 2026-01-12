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

from multiroom_model.inchem import InChemPyInstance


class TestInChemPyMainMethod(unittest.TestCase):
    def test_inchempy_runs(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            particles=False,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    @unittest.skip("Requires file IO, see TestInChemPyMainClass instead")
    def test_inchempy_runs_with_chem_mech_set(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/mcm_v331.fac",
            particles=False,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    @unittest.skip("Requires file IO, see TestInChemPyMainClass instead")
    def test_inchempy_runs_with_escs_v1_set(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/escs_v1.fac",
            particles=False,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    @unittest.skip("Requires file IO, see TestInChemPyMainClass instead")
    def test_inchempy_runs_with_rcs_2023_set(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/rcs_2023.fac",
            particles=False,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    @unittest.skip("Requires file IO, see TestInChemPyMainClass instead")
    def test_inchempy_runs_with_mcm_subset_set(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/mcm_subset.fac",
            particles=False,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    @unittest.skip("Requires file IO, see TestInChemPyMainClass instead")
    def test_inchempy_runs_with_chem_mech_set_and_additions(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/mcm_v331.fac",
            particles=True,
            INCHEM_additional=True,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    @unittest.skip("Requires file IO, see TestInChemPyMainClass instead")
    def test_inchempy_runs_with_escs_v1_set_and_additions(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/escs_v1.fac",
            particles=True,
            INCHEM_additional=False,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    @unittest.skip("Requires file IO, see TestInChemPyMainClass instead")
    def test_inchempy_runs_with_rcs_2023_set_and_additions(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/rcs_2023.fac",
            particles=True,
            INCHEM_additional=True,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()

    @unittest.skip("Requires file IO, see TestInChemPyMainClass instead")
    def test_inchempy_runs_with_mcm_subset_set_and_additions(self):
        inchem_py_instance: InChemPyInstance = InChemPyInstance(
            filename="chem_mech/mcm_subset.fac",
            particles=True,
            INCHEM_additional=True,
            seconds_to_integrate=180,
            output_graph=False)

        inchem_py_instance.run()


if __name__ == '__main__':
    unittest.main()
