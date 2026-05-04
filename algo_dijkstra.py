# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  algo_dijkstra.py                                  :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/30 14:27:33 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/04 15:07:03 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from zone import Zone
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
        self.distances[self.start.name] = 0
        self.predecessors = {vertex: None for vertex in self.graph.dict_zones}
        self.heap = []
        heapq.heappush(self.heap, (0, self.start.name))

    def run(self) -> None:
        while self.heap:
            cost, zone = heapq.heappop(self.heap)
            if cost > self.distances[zone]:
                continue
            for neighbor in self.graph.get_neighbors(zone):

                """Find the neighbour (on the other end of the connection)"""
                new_neighbor: Zone = neighbor.zone_a
                if zone == neighbor.zone_a.name:
                    new_neighbor: Zone = neighbor.zone_b
                new_cost = cost + new_neighbor.zone_type.cost()

                """course update"""
                if new_cost < self.distances[new_neighbor.name]:
                    self.distances[new_neighbor.name] = new_cost
                    self.predecessors[new_neighbor.name] = zone
                    heapq.heappush(self.heap, (new_cost, new_neighbor.name))

    def reconstruct_path(self) -> list:

        """route from the arrival area to the departure area to find the
            shortest route"""
        path = []
        current = self.graph.end_zone.name

        while current is not None:
            path.append(current)
            current = self.predecessors[current]
        path.reverse()
        return path
