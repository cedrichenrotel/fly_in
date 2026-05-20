# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  algos.py                                          :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/30 14:27:33 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/20 14:51:47 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple

try:
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

    def reconstruct_path(self, start_zone=None) -> list[str]:

        expected_start = (
            start_zone.name
            if start_zone
            else self.graph.start_zone.name
            )

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

    """A* prioritises areas that have:
        A low cost from the start AND a short estimated distance to
        the destination"""
    def __init__(self, graph: Graph,
                 distances_from_goal: Dict[str, int]) -> None:
        super().__init__(graph)
        self.distances_from_goal = distances_from_goal

    def heuristic(self, zone_name: str) -> int:
        if self.distances_from_goal is None:
            raise Exception("class AlgoAstar: end_zone not defined")

        return self.distances_from_goal(zone_name, 0)

    def initialize(self) -> None:
        self.distances = {vertex: sys.maxsize for vertex in
                          self.graph.dict_zones}

        if self.start is None:
            raise Exception("algo_astar -> The starting point has not been"
                            " defined.")

        start_heuristic = self.heuristic(self.start.name)

        self.distances[self.start.name] = 0
        self.predecessors = {vertex: None for vertex in self.graph.dict_zones}
        self.heap: List[Tuple[int, int, str]] = []

        heapq.heappush(self.heap, (start_heuristic, 0, self.start.name))

    def run(self, blocked_zones: Optional[set] = None) -> None:
        if blocked_zones is None:
            blocked_zones = set()

        self.initialize()

        while self.heap:
            _, current_cost, zone = heapq.heappop(self.heap)

            if current_cost > self.distances[zone]:
                continue

            for neighbor in self.graph.get_neighbors(self.graph.
                                                     dict_zones[zone]):

                if zone == neighbor.zone_a.name:
                    new_neighbor = neighbor.zone_b
                else:
                    new_neighbor = neighbor.zone_a

                penalty = 999 if new_neighbor.name in blocked_zones else 0
                new_cost = current_cost + new_neighbor.zone_type.cost() + penalty
                """course update"""
                if new_cost < self.distances[new_neighbor.name]:
                    self.distances[new_neighbor.name] = new_cost
                    self.predecessors[new_neighbor.name] = zone
                    new_priority = new_cost + self.heuristic(new_neighbor.name)
                    heapq.heappush(self.heap, (new_priority, new_cost,
                                               new_neighbor.name))
