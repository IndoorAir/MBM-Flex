from dataclasses import dataclass
from typing import List, Union, Tuple, TypeVar
from .aperture import Aperture, Side
from .transport_paths import TransportPath
import math

Room = TypeVar('Room')

_zero_advection_tolerance: float = 1.0e-5


def transport_path_contains_room(room: Room, transport_path: TransportPath):
    """
    Detect whether a room is included in the transport path
    """
    for t in transport_path.route:
        if (t.aperture.origin is room or t.aperture.destination is room):
            return True
    return False


def is_room_cross_ventilated(room: Room, transport_paths: List[TransportPath], wind_speed: float, wind_direction: float, building_direction_in_radians: float):
    """
    Detect whether a room receives cross-ventilation from any transport path, given wind conditions
    """
    for t in transport_paths:
        if transport_path_contains_room(room, t):
            if (abs(transport_path_windspeed(t, wind_speed, wind_direction, building_direction_in_radians)) > _zero_advection_tolerance):
                return True
    return False


def room_has_outdoor_aperture(room: Room, apertures: List[Aperture]):
    """
    Detect whether a room has any apertures to the outdoors
    """
    return any((a.origin == room and type(a.destination) is Side for a in apertures))


def transport_path_angle_in_radians(transport_path: TransportPath, building_direction_in_radians: float):
    """
    Find the angle of a given transport path, and a given building direction
    if the building direction is 0, then a back->front path will be north and this method will return 0
    """
    offsets = {
        (Side.Front, Side.Back): math.pi,
        (Side.Front, Side.Left): -3.0*math.pi / 4,
        (Side.Front, Side.Right): 3.0*math.pi / 4,

        (Side.Back, Side.Front): 0,
        (Side.Back, Side.Left): -math.pi / 4,
        (Side.Back, Side.Right): math.pi / 4,

        (Side.Left, Side.Front): math.pi / 4,
        (Side.Left, Side.Back): 3 * math.pi / 4,
        (Side.Left, Side.Right): math.pi/2.0,

        (Side.Right, Side.Front): -math.pi / 4,
        (Side.Right, Side.Back): -3 * math.pi / 4,
        (Side.Right, Side.Left): -math.pi/2.0,
    }
    offset = offsets.get((transport_path.start, transport_path.end))
    if offset is None:
        raise ValueError("Invalid direction transition")
    return building_direction_in_radians + offset


def transport_path_windspeed(transport_path: TransportPath,
                             wind_speed: float,
                             wind_direction: float,
                             building_direction_in_radians: float):
    """
    Use windspeed data to find the component of the windspeed along a given transposrt path
    """

    t_p_angle = transport_path_angle_in_radians(transport_path, building_direction_in_radians)
    return wind_speed * math.cos(wind_direction-t_p_angle)


def flow_advection(io_windspd: float, oarea: float, Cd: float, Cp: float, air_density: float):
    '''
    Calculate the advection flow through an opening (door or window), given its area
    and the component of ambient wind passing through it.

    inputs:
        io_windspd = component of the wind through the aperture (m/s)
        oarea = cross section area of the aperture (m2)
        Cd_coeff = discharge coefficient of the aperture
        Cp_coeff = building pressure coefficients
        air_density = air density of dry air (kg/m3)

    returns:
        adv_flow = advection flow (m3/s)

    '''
    # turbulent flow exponent
    flow_m = 0.5

    # pressure differential (in Pa)
    P_upwind = 0.5 * air_density * (io_windspd**2) * Cp[0]
    P_downwind = 0.5 * air_density * (io_windspd**2) * Cp[1]
    delta_P = P_upwind - P_downwind

    # flow coefficient (K)
    flow_coeff = Cd * oarea

    # advection flow (in m3/s)
    adv_flow = flow_coeff * math.sqrt(2/air_density) * (delta_P**flow_m)

    print('|-------> delta_P = ', delta_P)
    print('|-------> flow_coeff = ', flow_coeff)
    print('|-------> adv_flow = ', adv_flow)

    return adv_flow


def flow_exchange(category: int):
    # TODO: this needs some calculation or something
    if category == 1:
        return 0
    elif category == 2:
        return 0
    elif category == 3:
        return 0
    elif category == 4:
        return 0
    else:
        raise Exception("unknown category")


@dataclass
class Fluxes:
    """
        @brief A dataclass to store fluxes between 2 rooms from advection and exchange fluxes
    """
    from_1_to_2: float
    from_2_to_1: float


class ApertureCalculation:
    """
        @brief A class which performs the calculations of advection flow, category and exchange flow of an aperture

    """
    @dataclass
    class Contribution:
        """
            @brief A contribution to the advection flow coming from one transport path
            @variable path: the path giving the contribution
            @variable reversed: whether this particular aperture is reversed along the path
            @variable position_down_path: how far along the path this aperture appears on a scale from 0 to 1
        """
        path: TransportPath
        reversed: bool
        position_down_path: float

    aperture: Aperture = None
    transport_paths: List[TransportPath] = []
    is_outdoor_aperture: bool = False
    has_room_with_outdoor_aperture: bool = False
    building_direction_in_radians: float
    air_density: float = 0
    building_pressure_coefficients: Tuple[float, float] = 0, 0
    contributions: List[Contribution] = []

    def __init__(self,
                 aperture: Aperture,
                 transport_paths: List[TransportPath],
                 all_apertures: List[Aperture],
                 building_direction_in_radians: float = 0,
                 air_density: float = 0,
                 building_pressure_coefficients: Tuple[float, float] = (0, 0)):
        self.aperture = aperture
        self.transport_paths = transport_paths
        self.is_outdoor_aperture = (type(aperture.destination) is Side)
        self.has_room_with_outdoor_aperture = room_has_outdoor_aperture(
            aperture.origin, all_apertures) or room_has_outdoor_aperture(aperture.destination, all_apertures)
        self.building_direction_in_radians = building_direction_in_radians
        self.air_density = air_density
        self.building_pressure_coefficients = building_pressure_coefficients
        self.contributions = self._build_contributions(aperture, transport_paths)

        if (building_pressure_coefficients[0] < building_pressure_coefficients[1]):
            raise Exception("The higher building pressure coefficient should come first")

    @classmethod
    def _build_contributions(cls, aperture: Aperture, transport_paths: List[TransportPath]) -> List[Contribution]:
        """
        Each transport path may give a contribution to the flow through this aperture
        """
        result = []
        for tp in transport_paths:
            for i, r in enumerate(tp.route):
                #  If this aperture is along the path, then add a contribution to the result
                if r.aperture == aperture:
                    # Store some extra data so the parameters needed later can be quickly accessed
                    # Whether this aperture is reversed along the path
                    # How far down the path this aperture is (scale from 0 to 1)
                    result.append(cls.Contribution(
                        path=tp,
                        reversed=r.reversed,
                        position_down_path=i/(len(tp.route)-1)
                    ))
        return result

    def has_advection_flow(self, wind_speed: float, wind_direction: float):
        """
        detect whether given wind conditions cause any advection flow
        """
        for contribution in self.contributions:
            value = transport_path_windspeed(contribution.path, wind_speed,
                                             wind_direction, self.building_direction_in_radians)
            if abs(value) > _zero_advection_tolerance:
                return True
        return False

    def advection_flow_rate(self, wind_speed: float, wind_direction: float):
        """
        the advection flow resulting from given wind conditions
        """
        sum = 0
        for contribution in self.contributions:
            path_windspeed = transport_path_windspeed(contribution.path,
                                                      wind_speed,
                                                      wind_direction,
                                                      self.building_direction_in_radians)

            position = contribution.position_down_path if path_windspeed > 0 else 1.0-contribution.position_down_path

            path_wind_direction_sign = -1 if path_windspeed < 0 else 1
            aperture_reversed_sign = -1 if contribution.reversed else 1
            flow_advection_sign = path_wind_direction_sign*aperture_reversed_sign

            discharge_coefficient = 0.7/(1.0 + position)

            flow_advection_magnitude = flow_advection(path_windspeed,
                                  self.aperture.area,
                                  discharge_coefficient,
                                  self.building_pressure_coefficients,
                                  self.air_density)
            
            sum += flow_advection_sign * flow_advection_magnitude

        return sum

    def exchange_category(self, wind_speed: float, wind_direction: float):
        """
        the exchange category resulting from given wind conditions
        in priority order:
        1) if either room is cross-ventilated by the wind
        2) if this aperture goes to the outside 
        3) if this aperture goes to a room with a connection to outside ("costal" room)
        4) if this aperture is none of the above (between 2 "landlocked" rooms)
        """
        if is_room_cross_ventilated(self.aperture.origin,
                                    self.transport_paths,
                                    wind_speed,
                                    wind_direction,
                                    self.building_direction_in_radians):
            return 1
        elif is_room_cross_ventilated(self.aperture.destination,
                                      self.transport_paths,
                                      wind_speed,
                                      wind_direction,
                                      self.building_direction_in_radians):
            return 1
        elif self.is_outdoor_aperture:
            return 2
        elif self.has_room_with_outdoor_aperture:
            return 3
        else:
            return 4

    def exchange_flow_rate(self, wind_speed: float, wind_direction: float):
        """
        the exchange flow rate resulting from given wind conditions
        """
        category = self.exchange_category(wind_speed, wind_direction)
        return flow_exchange(category)

    def trans_matrix_contributions(self, wind_speed: float, wind_direction_in_radians: float):
        """
        the advection or exchange fluxes resulting from given wind conditions
        """

        advection = self.advection_flow_rate(wind_speed, wind_direction_in_radians)
        if (advection > _zero_advection_tolerance):
            # Advection flow from room 1 to room 2

            return Fluxes(
                from_1_to_2=advection,
                from_2_to_1=0
            )

        elif (advection < -_zero_advection_tolerance):
            # Advection flow from room 2 to room 1

            return Fluxes(
                from_1_to_2=0,
                from_2_to_1=-advection
            )

        else:
            # No Advection flow, use exchange flow instead
            exchange = self.exchange_flow_rate(wind_speed, wind_direction_in_radians)

            return Fluxes(
                from_1_to_2=exchange,
                from_2_to_1=exchange
            )
