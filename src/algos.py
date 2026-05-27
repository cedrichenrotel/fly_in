# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  algos.py                                          :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/30 14:27:33 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/27 11:12:00 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, Set

try:
    from zone import Zone
    from connection import Connection
    from graph import Graph
    import heapq
except ImportError as e:
    print(f"[ERROR] graph.py: {e}")
    sys.exit()


class Algo(ABC):
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.distances: Dict[str, int] = {}
        self.predecessors: Dict[str, Optional[str]] = {}
        self.start = graph.start_zone

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass

    def reconstruct_path(self,
                         start_zone: Optional['Zone'] = None) -> list[str]:

        """Reconstruct the most direct path from the starting
            point using a list-based algorithm, whilst ensuring
            that the path is valid"""
        if start_zone:
            expected_start: str = start_zone.name
        elif self.graph.start_zone:
            expected_start = self.graph.start_zone.name
        else:
            raise ValueError("Unable to determine the start "
                             "zone: 'start_zone’ and' "
                             "graph.start_zone’ are None.")

        path: List[str] = []
        current: Optional[str] = self.graph.end_zone.name

        while current is not None:
            path.append(current)
            current = self.predecessors.get(current)

        path.reverse()

        if path[0] != expected_start:
            raise Exception("No valid path found")

        return path


class AlgoDijkstra(Algo):
    """
    Preparing the three structures before the algorithm starts.
        - distances -> the minimum known distance required to reach each
            area.
        - predecessors -> stores the areas that have already been visited
            in order to reach the current area.
        - unvisited -> not yet explored
    """
    def initialize(self) -> None:
        self.distances = {vertex: sys.maxsize for vertex in
                          self.graph.dict_zones}

        if self.start is None:
            raise Exception("algo_dijkstra -> The starting point has not been"
                            " defined.")

        self.distances[self.start.name] = 0
        self.predecessors = {vertex: None for vertex in self.graph.dict_zones}
        self.heap: List[Tuple[int, str]] = []

        heapq.heappush(self.heap, (0, self.start.name))

    def run(self) -> None:
        self.initialize()

        while self.heap:
            current_cost, zone = heapq.heappop(self.heap)

            if current_cost > self.distances[zone]:
                continue

            for neighbor in self.graph.get_neighbors(self.graph.
                                                     dict_zones[zone]):

                if zone == neighbor.zone_a.name:
                    new_neighbor = neighbor.zone_b
                else:
                    new_neighbor = neighbor.zone_a

                new_cost = current_cost + new_neighbor.zone_type.cost()

                """course update"""
                if new_cost < self.distances[new_neighbor.name]:
                    self.distances[new_neighbor.name] = new_cost
                    self.predecessors[new_neighbor.name] = zone
                    heapq.heappush(self.heap, (new_cost, new_neighbor.name))


class AlgoAstar(Algo):
    """
    A* adapted for spacetime.
    Finds an optimal path by avoiding future collisions using a
    global reservation table.
    """
    def __init__(self, graph: Graph,
                 distances_from_goal: Dict[str, int]) -> None:
        super().__init__(graph)
        self.distances_from_goal = distances_from_goal

    def heuristic(self, zone_name: str) -> int:
        if self.distances_from_goal is None:
            raise Exception("class AlgoAstar: end_zone not defined")
        return self.distances_from_goal.get(zone_name, 0)

    def initialize(self) -> None:
        self.dict_distances: Dict[Tuple[str, int], int] = {}
        self.dict_predecessors: Dict[Tuple[str, int],
                                     Optional[Tuple[str, int]]] = {}
        self.heap: List[Tuple[int, int, str, int]] = []

    def run(self, space_time_reservation: Optional[dict] = None) -> None:
        """
        Calculates the quickest route, taking into account
        the occupancy of zones and turn-by-turn connections.
        """
        if space_time_reservation is None:
            space_time_reservation = {}

        self.initialize()

        start_name = self.start.name
        start_heuristic = self.heuristic(start_name)
        self.dict_distances[(start_name, 0)] = 0
        self.dict_predecessors[(start_name, 0)] = None

        heapq.heappush(self.heap, (start_heuristic, 0, start_name, 0))
        visited: Set[Tuple[str, int]] = set()

        while self.heap:
            _, current_cost, zone, turn = heapq.heappop(self.heap)

            max_turns = len(self.graph.dict_zones) * self.graph.nb_drone * 10
            if turn > max_turns:
                continue

            if zone == self.graph.end_zone.name:
                self.end_node = (zone, turn)
                return

            if (zone, turn) in visited:
                continue
            visited.add((zone, turn))

            is_start_or_end: bool = (zone == self.graph.start_zone.name or
                                     zone == self.graph.end_zone.name)
            zone_obj = self.graph.dict_zones[zone]

            space_time_res: Optional[int] = space_time_reservation.get((
                zone,
                turn + 1), 0)

            if (is_start_or_end or space_time_res < zone_obj.max_drones):

                prev_node = self.dict_predecessors.get((zone, turn))
                is_in_transit = (prev_node is not None and
                                 turn - prev_node[1] == 2)

                if not is_in_transit:
                    wait_node = (zone, turn + 1)

                    if current_cost + 1 < self.dict_distances.get(wait_node,
                                                                  sys.maxsize):
                        self.dict_distances[wait_node] = current_cost + 1
                        self.dict_predecessors[wait_node] = (zone, turn)
                        priority = current_cost + 1 + self.heuristic(zone)
                        heapq.heappush(self.heap, (priority,
                                                   current_cost + 1,
                                                   zone,
                                                   turn + 1))

            get_graph: list[Connection] = self.graph.get_neighbors(
                self.graph.dict_zones[zone])

            for neighbor in get_graph:
                new_neighbor: Zone = (
                    neighbor.zone_b
                    if zone == neighbor.zone_a.name
                    else neighbor.zone_a
                    )
                if new_neighbor.zone_type.name == "blocked":
                    continue

                cost: int = new_neighbor.zone_type.cost()
                arrival_turn: int = turn + cost
                neighbor_node: tuple[str, int] = (new_neighbor.name,
                                                  arrival_turn)

                is_neighbor_end: bool = (new_neighbor.name ==
                                         self.graph.end_zone.name)
                current_occupancy: int = space_time_reservation.get(
                    neighbor_node,
                    0
                    )

                current_conn_occupancy: int = space_time_reservation.get(
                    (neighbor.name, turn), 0)

                if (is_neighbor_end or
                        (current_occupancy < new_neighbor.max_drones and
                         current_conn_occupancy < neighbor.max_link_capacity)):

                    if (current_cost + cost <
                       self.dict_distances.get(neighbor_node, sys.maxsize)):

                        self.dict_distances[neighbor_node] = (current_cost +
                                                              cost)
                        self.dict_predecessors[neighbor_node] = (zone, turn)

                        priority_bonus = (-1
                                          if new_neighbor.zone_type.name ==
                                          "priority" else 0)
                        priority = (current_cost +
                                    cost +
                                    self.heuristic(new_neighbor.name) +
                                    priority_bonus)
                        heapq.heappush(self.heap, (priority,
                                                   current_cost + cost,
                                                   new_neighbor.name,
                                                   arrival_turn))
        if not hasattr(self, 'end_node'):
            raise Exception("Astar -> No path found")

    def get_reconstructed_path(self) -> List[Tuple[str, int]]:
        """Reconstructs the path as pairs (zone, turn)."""
        path: List[Tuple[str, int]] = []
        current: Optional[Tuple[str, int]] = getattr(self, "end_node", None)

        while current is not None:
            path.append(current)
            current = self.dict_predecessors.get(current)

        path.reverse()
        return path
