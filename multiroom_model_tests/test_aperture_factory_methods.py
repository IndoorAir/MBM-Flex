import unittest
from multiroom_model.aperture_factory import build_apertures, build_apertures_from_double_definition, build_wind_definition
from multiroom_model.time_dep_value import TimeDependentValue
from multiroom_model.aperture import Aperture, Side


class MockRoom:
    pass


class TestAperturePopulation(unittest.TestCase):

    def test_build_apertures(self):
        rooms = dict((i, MockRoom()) for i in range(1, 10))
        apertures = build_apertures("config_rooms/mr_tcon_building.csv", rooms)
        self.assertEqual(len(apertures), 25, "Expected 25 apertures")

        self.assertEqual(apertures[0].origin, rooms[1])
        self.assertEqual(apertures[0].destination, Side.Front)
        self.assertEqual(apertures[0].area, 0.000344)

        self.assertEqual(apertures[21].origin, rooms[8])
        self.assertEqual(apertures[21].destination, rooms[9])
        self.assertEqual(apertures[21].area, 0.010618)

        self.assertEqual(apertures[23].origin, rooms[9])
        self.assertEqual(apertures[23].destination, Side.Right)
        self.assertEqual(apertures[23].area, 0.000232)

        self.assertEqual(apertures[24].origin, rooms[9])
        self.assertEqual(apertures[24].destination, rooms[8])
        self.assertEqual(apertures[24].area, 0.010618)

    @classmethod
    def setUpClass(cls):
        cls.rooms = dict((i, MockRoom()) for i in range(1, 10))
        cls.apertures = build_apertures_from_double_definition("config_rooms/mr_tcon_building.csv", cls.rooms)

    def test_number_of_apertures(self):
        self.assertEqual(len(self.apertures), 18, "Expected 18 apertures")

    def test_apertures(self):
        self.assertEqual(self.apertures[0].origin, self.rooms[1])
        self.assertEqual(self.apertures[0].destination, Side.Front)
        self.assertEqual(self.apertures[0].area, 0.000344)

        self.assertEqual(self.apertures[15].origin, self.rooms[8])
        self.assertEqual(self.apertures[15].destination, self.rooms[9])
        self.assertEqual(self.apertures[15].area, 0.010618)

        self.assertEqual(self.apertures[17].origin, self.rooms[9])
        self.assertEqual(self.apertures[17].destination, Side.Right)
        self.assertEqual(self.apertures[17].area, 0.000232)


class TestWindDefinitionPopulation(unittest.TestCase):

    def test_times(self):
        wind_definition = build_wind_definition("config_rooms/mr_tvar_wind_params.csv")
        self.assertIsInstance(wind_definition.wind_speed, TimeDependentValue)
        self.assertEqual(len(wind_definition.wind_speed.times()), 24)
        self.assertIsInstance(wind_definition.wind_direction, TimeDependentValue)
        self.assertEqual(len(wind_definition.wind_direction.times()), 24)
