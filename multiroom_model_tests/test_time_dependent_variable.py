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

from multiroom_model.time_dep_value import TimeDependentValue


class TestTimeDependentValueLinearInterpolation(unittest.TestCase):
    def setUp(self):
        self.data = [
            (0.0, 0.0),
            (1.0, 10.0),
            (2.0, 20.0),
            (3.0, 30.0),
        ]
        self.tdv = TimeDependentValue(self.data, continuous=True)

    def test_times(self):
        self.assertEqual(self.tdv.times(), [0.0, 1.0, 2.0, 3.0])

    def test_values(self):
        self.assertEqual(self.tdv.values(), [0.0, 10.0, 20.0, 30.0])

    def test_value_at_exact_times(self):
        self.assertAlmostEqual(self.tdv.value_at_time(0.0), 0.0)
        self.assertAlmostEqual(self.tdv.value_at_time(1.0), 10.0)
        self.assertAlmostEqual(self.tdv.value_at_time(3.0), 30.0)

    def test_value_at_in_between_times(self):
        self.assertAlmostEqual(self.tdv.value_at_time(0.5), 5.0)
        self.assertAlmostEqual(self.tdv.value_at_time(1.5), 15.0)
        self.assertAlmostEqual(self.tdv.value_at_time(2.5), 25.0)

    def test_value_before_first_time_raises(self):
        with self.assertRaises(Exception) as context:
            self.tdv.value_at_time(-1.0)
        self.assertIn("too early", str(context.exception).lower())

    def test_value_after_last_time_raises(self):
        with self.assertRaises(Exception) as context:
            self.tdv.value_at_time(3.1)
        self.assertIn("too late", str(context.exception).lower())

    def test_invalid_time_order_raises(self):
        with self.assertRaises(Exception) as context:
            TimeDependentValue([(1.0, 10.0), (0.5, 20.0)], continuous=True)
        self.assertIn("times were not in order", str(context.exception).lower())

    def test_single_point(self):
        tdv_single = TimeDependentValue([(2.0, 100.0)], continuous=True)
        self.assertEqual(tdv_single.value_at_time(2.0), 100.0)
        with self.assertRaises(Exception):
            tdv_single.value_at_time(1.9)
        with self.assertRaises(Exception):
            tdv_single.value_at_time(2.1)


class TestTimeDependentDiscontinuous(unittest.TestCase):
    def setUp(self):
        self.data = [
            (0.0, 0.0),
            (1.0, 10.0),
            (2.0, 20.0),
            (3.0, 30.0),
        ]
        self.tdv = TimeDependentValue(self.data, continuous=False)

    def test_times(self):
        self.assertEqual(self.tdv.times(), [0.0, 1.0, 2.0, 3.0])

    def test_values(self):
        self.assertEqual(self.tdv.values(), [0.0, 10.0, 20.0, 30.0])

    def test_value_at_exact_times(self):
        self.assertAlmostEqual(self.tdv.value_at_time(0.0), 0.0)
        self.assertAlmostEqual(self.tdv.value_at_time(1.0), 10.0)
        self.assertAlmostEqual(self.tdv.value_at_time(3.0), 30.0)

    def test_value_at_in_between_times(self):
        self.assertAlmostEqual(self.tdv.value_at_time(0.5), 0)
        self.assertAlmostEqual(self.tdv.value_at_time(1.5), 10.0)
        self.assertAlmostEqual(self.tdv.value_at_time(2.5), 20.0)

    def test_value_before_first_time_raises(self):
        with self.assertRaises(Exception) as context:
            self.tdv.value_at_time(-1.0)
        self.assertIn("too early", str(context.exception).lower())

    def test_value_after_last_time_raises(self):
        with self.assertRaises(Exception) as context:
            self.tdv.value_at_time(3.1)
        self.assertIn("too late", str(context.exception).lower())

    def test_invalid_time_order_raises(self):
        with self.assertRaises(Exception) as context:
            TimeDependentValue([(1.0, 10.0), (0.5, 20.0)], continuous=True)
        self.assertIn("times were not in order", str(context.exception).lower())


if __name__ == '__main__':
    unittest.main()
