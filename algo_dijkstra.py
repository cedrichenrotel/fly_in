# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  algo_dijkstra.py                                  :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/30 14:27:33 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/06 14:47:06 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from graph import Graph
    import heapq
except ImportError as e:
    print(f"[ERROR] graph.py: {e}")
    sys.exit()

"""Dijkstra's algorithm"""


class AlgoDijkstra():
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.start = graph.start_zone
        self.initialize()

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
        self.heap: list = []
        heapq.heappush(self.heap, (0, self.start.name))

    def run(self) -> None:
        while self.heap:
            current_cost, zone = heapq.heappop(self.heap)

            if current_cost > self.distances[zone]:
                continue

            for neighbor_info in self.graph.get_neighbors(zone):

                neighbor_name, _ = neighbor_info

                """Find the neighbour (on the other end of the connection)"""
                new_neighbor = self.graph.dict_zones.get(neighbor_name)

                if new_neighbor is None:
                    continue

                new_cost = current_cost + new_neighbor.zone_type.cost()

                """course update"""
                if new_cost < self.distances[new_neighbor.name]:
                    self.distances[new_neighbor.name] = new_cost
                    self.predecessors[new_neighbor.name] = zone
                    heapq.heappush(self.heap, (new_cost, new_neighbor.name))

    def reconstruct_path(self) -> list[str]:

        """route from the arrival area to the departure area to find the
            shortest route"""

        current: str | None = None

        if self.graph.end_zone is None:
            raise Exception("The destination zone (end_zone) is not defined in"
                            " the graph.")

        current = self.graph.end_zone.name

        path: list[str] = []

        while current is not None:
            path.append(current)
            current = self.predecessors.get(current)

        path.reverse()

        return path
