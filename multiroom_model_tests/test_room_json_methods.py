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
import pyjson5

from multiroom_model.surface_composition import SurfaceComposition
from multiroom_model.room_chemistry import RoomChemistry
from multiroom_model.time_dep_value import TimeDependentValue
from multiroom_model.bracketed_value import TimeBracketedValue
from multiroom_model.json_parser import RoomChemistryJSONBuilder


EXPLICIT_JSON = r'''
{
  "volume_in_m3": 10.0,
  "surf_area_in_m2": 29.7,
  "light_type": "Incand",
  "glass_type": "glass_C",
  "composition": {
    "soft": 0.0,
    "paint": 40.0,
    "wood": 10.0,
    "metal": 5.0,
    "concrete": 0.0,
    "paper": 0.0,
    "lino": 0.0,
    "plastic": 0.0,
    "human": 0.0,
    "glass": 45.0,
    "other": 0.0
  },
  "temp_in_kelvin": {
    "values": [
      [ 0, 288.15 ],
      [ 25200, 288.15 ],
      [ 50400, 294.15 ]
    ]
  },
  "rh_in_percent": {
    "values": [
      [ 0, 45.0 ],
      [ 25200, 45.0 ],
      [ 50400, 40.0 ]
    ]
  },
  "airchange_in_per_second": {
    "values": [
      [0, 0.5 ],
      [86400, 1.0 ]
    ]
  },
  "light_switch": {
    "values": [
      [ 0,0 ],
      [ 25200, 1 ],
      [ 50400, 0 ]
    ]
  },
  "emissions": {
    "LIMONENE": {
      "values": [
        { "start": 46800, "end": 50400, "value": 5.00E+08 }
      ]
    },
    "BPINENE": {
      "values": [
        { "start": 46800, "end": 50400, "value": 5.00E+10 }
      ]
    }
  },
  "n_adults": {
    "values": [
      [ 0,      0 ],
      [ 3600,   0 ],
      [ 7200,   0 ],
      [ 10800,  0 ],
      [ 14400,  0 ],
      [ 18000,  0 ],
      [ 21600,  1 ],
      [ 25200,  1 ],
      [ 28800,  1 ],
      [ 32400,  1 ],
      [ 36000,  1 ],
      [ 39600,  1 ],
      [ 43200,  1 ],
      [ 46800,  1 ],
      [ 50400,  1 ],
      [ 54000,  1 ],
      [ 57600,  1 ],
      [ 61200,  0 ],
      [ 64800,  0 ],
      [ 68400,  0 ],
      [ 72000,  0 ],
      [ 75600,  0 ],
      [ 79200,  0 ],
      [ 82800,  0 ]
    ]
  },
  "n_children": {
    "values": [
      [0,       0],
      [3600,    0],
      [7200,    0],
      [10800,   0],
      [14400,   0],
      [18000,   0],
      [21600,   0],
      [25200,   0],
      [28800,   0],
      [32400,   0],
      [36000,   0],
      [39600,   0],
      [43200,   0],
      [46800,   0],
      [50400,   0],
      [54000,   0],
      [57600,   0],
      [61200,   0],
      [64800,   0],
      [68400,   0],
      [72000,   0],
      [75600,   0],
      [79200,   0],
      [82800,   0],
    ]
  }
}
'''


class TestRoomChemistryFromJson(unittest.TestCase):
    def setUp(self):
        self.room = RoomChemistryJSONBuilder.from_dict(pyjson5.loads(EXPLICIT_JSON))

    def test_basic_fields(self):
        self.assertAlmostEqual(self.room.volume_in_m3, 10.0)
        self.assertAlmostEqual(self.room.surf_area_in_m2, 29.7)
        self.assertEqual(self.room.light_type, "Incand")
        self.assertEqual(self.room.glass_type, "glass_C")

    def test_composition_explicit(self):
        comp = self.room.composition
        self.assertIsInstance(comp, SurfaceComposition)
        self.assertAlmostEqual(comp.soft, 0.0)
        self.assertAlmostEqual(comp.paint, 40.0)
        self.assertAlmostEqual(comp.wood, 10.0)
        self.assertAlmostEqual(comp.metal, 5.0)
        self.assertAlmostEqual(comp.concrete, 0.0)
        self.assertAlmostEqual(comp.paper, 0.0)
        self.assertAlmostEqual(comp.lino, 0.0)
        self.assertAlmostEqual(comp.plastic, 0.0)
        self.assertAlmostEqual(comp.human, 0.0)
        self.assertAlmostEqual(comp.glass, 45.0)
        self.assertAlmostEqual(comp.other, 0.0)

    def test_time_dependent_values(self):
        self.assertIsNotNone(self.room.temp_in_kelvin)
        self.assertIsInstance(self.room.temp_in_kelvin, TimeDependentValue)
        times = self.room.temp_in_kelvin.times()
        vals = self.room.temp_in_kelvin.values()
        self.assertEqual(len(times), 4)
        self.assertEqual(len(vals), 4)
        self.assertAlmostEqual(times[0], 0.0)
        self.assertAlmostEqual(vals[0], 288.15)

        self.assertIsNotNone(self.room.rh_in_percent)
        self.assertIsInstance(self.room.rh_in_percent, TimeDependentValue)
        self.assertEqual(len(self.room.rh_in_percent.times()), 4)

        self.assertIsNotNone(self.room.airchange_in_per_second)
        self.assertIsInstance(self.room.airchange_in_per_second, TimeDependentValue)
        self.assertEqual(len(self.room.airchange_in_per_second.times()), 4)

        self.assertIsNotNone(self.room.light_switch)
        self.assertIsInstance(self.room.light_switch, TimeDependentValue)
        self.assertEqual(len(self.room.light_switch.times()), 3)
        self.assertEqual(self.room.light_switch.values(), [0.0, 1.0, 0.0])

    def test_emissions_parsed_as_bracketed(self):
        self.assertTrue(hasattr(self.room, "emissions"))
        emis = self.room.emissions
        self.assertIn("LIMONENE", emis)
        self.assertIn("BPINENE", emis)
        self.assertIsInstance(emis["LIMONENE"], TimeBracketedValue)
        self.assertIsInstance(emis["BPINENE"], TimeBracketedValue)

        lim_vals = emis["LIMONENE"].values()
        bpin_vals = emis["BPINENE"].values()
        self.assertEqual(len(lim_vals), 1)
        self.assertEqual(len(bpin_vals), 1)

        self.assertAlmostEqual(lim_vals[0][0], 46800.0)
        self.assertAlmostEqual(lim_vals[0][1], 50400.0)
        self.assertAlmostEqual(lim_vals[0][2], 5.00e8)

        self.assertAlmostEqual(bpin_vals[0][0], 46800.0)
        self.assertAlmostEqual(bpin_vals[0][1], 50400.0)
        self.assertAlmostEqual(bpin_vals[0][2], 5.00e10)

    def test_people_counts(self):
        self.assertIsNotNone(self.room.n_adults)
        self.assertIsNotNone(self.room.n_children)
        self.assertIsInstance(self.room.n_adults, TimeDependentValue)
        self.assertIsInstance(self.room.n_children, TimeDependentValue)
        self.assertEqual(len(self.room.n_adults.times()), 24)
        self.assertEqual(len(self.room.n_children.times()), 24)
