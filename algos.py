# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  algos.py                                          :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/30 14:27:33 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/07 15:03:54 by cehenrot        ###   ########.fr        #
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

    def reconstruct_path(self) -> list[str]:
        if self.graph.end_zone is None:
            raise Exception("Destination (end_zone) non définie.")

        path: List[str] = []
        current: Optional[str] = self.graph.end_zone.name

        while current is not None:
            path.append(current)
            current = self.predecessors.get(current)

        path.reverse()
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
    def heuristic(self, zone_name: str) -> int:
        if self.graph.end_zone is None:
            raise Exception("class AlgoAstar: end_zone not defined")

        z_a = self.graph.dict_zones[zone_name]
        z_b = self.graph.end_zone

        return abs(z_a.x - z_b.x) + abs(z_a.y - z_b.y)\

    def initialize(self) -> None:
        pass

    def run(self) -> None:
        pass
