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

from typing import List,  Dict, Union, TypeVar
from dataclasses import dataclass
from itertools import combinations
from .aperture import Aperture, Side

Room = TypeVar('Room')


@dataclass
class TransportPathParticipation:
    """
        @brief The involvement of an aperture in a transport path
        If reversed then the 2nd room of the aperture comes first in the transport path
    """
    aperture: Aperture
    reversed: bool = False


@dataclass
class TransportPath:
    """
        @brief A route from a start to an end (probably outside sides of the house)
        Defined by the ordered list of Apertures traversed
    """
    start: Union[Room | Side]
    end: Union[Room | Side]
    route: List[TransportPathParticipation]


def paths_through_building(rooms: List[Room], apertures: List[Aperture]) -> List[TransportPath]:
    """
        @brief Given a list of rooms and a list of apertures joining them (either to each other or the outside)
        Produces a list of the unique transport paths from one outside side of the house to another
        Each path goes through each room only once, preventing cycles
        Note that a path and its exact reversal are NOT both in the list, this is to prevent double-counting paths.
    """

    # build a graph where nodes are either rooms or outsides, and edges are apertures
    @dataclass
    class Node:
        item: Union[Room | Side]
        edges: List

    @dataclass
    class Edge:
        source: Node
        destination: Node
        aperture: TransportPathParticipation

    outsides = [Side.Front, Side.Left, Side.Back, Side.Right]

    graph: Dict[Union[Room | Side], Node] = {}
    for s in outsides:
        graph[s] = Node(item=s, edges=[])
    for r in rooms:
        graph[r] = Node(item=r, edges=[])

    for a in apertures:
        node_1: Node = graph[a.origin]
        node_2: Node = graph[a.destination]
        node_1.edges.append(Edge(source=node_1, destination=node_2, aperture=TransportPathParticipation(a, False)))
        node_2.edges.append(Edge(source=node_2, destination=node_1, aperture=TransportPathParticipation(a, True)))

    # method to find all the paths from one start node to an end node
    def all_paths_between(start_node, end_node) -> List[TransportPath]:
        result: List[TransportPath] = []

        # recursive utility function
        def find_all_paths(current_node: Node, final_destination: Node, visited: List[Node], path: List[TransportPathParticipation]):
            new_visited = visited + [current_node]
            for edge in current_node.edges:
                new_path = path + [edge.aperture]
                if (edge.destination == final_destination):
                    result.append(TransportPath(start=start_node.item, end=end_node.item, route=new_path))
                elif (edge.destination not in visited):
                    find_all_paths(edge.destination, final_destination, new_visited, new_path)

        # we don't want to be able to leave the building and reenter it
        # exclude the outside nodes from path
        excluded_nodes = list(graph[s] for s in outsides)

        # invoke the recursive function
        find_all_paths(start_node, end_node, excluded_nodes, [])
        return result

    # Use this method 6 times to accumulate all routes between the 4 outside nodes, and not their exact reversals
    result: List[TransportPath] = []

    # Use all combinations of 2 of the outside nodes (there are 6 combinations of 2 outside nodes: 4C2=6)
    # We don't use permutations, because that would double-count the paths by reversing the start and end
    for start, end in combinations(outsides, 2):
        result.extend(all_paths_between(graph[start], graph[end]))

    return result
