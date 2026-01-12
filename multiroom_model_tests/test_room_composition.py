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

from multiroom_model.surface_composition import SurfaceComposition  # Change this to match your file/module name


class TestRoomComposition(unittest.TestCase):

    def test_default_initialization(self):
        rc = SurfaceComposition()
        self.assertAlmostEqual(rc.other, 100.0)
        self.assertEqual(rc.surface_area_dictionary(100.0)['OTHER'], 100.0)

    def test_correct_sum_explicit_other(self):
        rc = SurfaceComposition(soft=10, paint=10, wood=10, metal=10, concrete=10,
                             paper=10, lino=10, plastic=10, glass=10, human=5, other=5)
        self.assertAlmostEqual(rc.other, 5.0)
        total_area = sum(rc.surface_area_dictionary(100.0).values())
        self.assertAlmostEqual(total_area, 100.0)

    def test_auto_other_calculation(self):
        rc = SurfaceComposition(soft=10, paint=10, wood=10, metal=10, concrete=10,
                             paper=10, lino=10, plastic=10, glass=10, human=5)
        self.assertAlmostEqual(rc.other, 5.0)
        total_area = sum(rc.surface_area_dictionary(100.0).values())
        self.assertAlmostEqual(total_area, 100.0)

    def test_raises_if_sum_above_100(self):
        with self.assertRaises(ValueError):
            SurfaceComposition(soft=50, paint=30, wood=30, other=10)  # Total = 120

    def test_raises_if_sum_below_100_and_other_given(self):
        with self.assertRaises(ValueError):
            SurfaceComposition(soft=20, paint=20, wood=20, other=10)  # Total = 70

    def test_invalid_material_values(self):
        with self.assertRaises(ValueError):
            SurfaceComposition(soft=-10, paint=10, wood=10, other=90)  # Negative soft

        with self.assertRaises(ValueError):
            SurfaceComposition(soft=101)  # Soft > 100

    def test_surface_area_dictionary_scaling(self):
        rc = SurfaceComposition(soft=50, wood=50)
        area_dict = rc.surface_area_dictionary(200.0)
        self.assertAlmostEqual(area_dict['SOFT'], 100.0)
        self.assertAlmostEqual(area_dict['WOOD'], 100.0)

    def test_all_materials_specified(self):
        rc = SurfaceComposition(
            soft=5, paint=5, wood=5, metal=5, concrete=5, paper=5,
            lino=5, plastic=5, glass=5, human=5, other=50)
        total = sum(rc.surface_area_dictionary(100.0).values())
        self.assertAlmostEqual(total, 100.0)


if __name__ == '__main__':
    unittest.main()
