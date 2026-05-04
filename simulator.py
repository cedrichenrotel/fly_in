# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  simulator.py                                      :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:35:52 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/04 18:33:55 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from drone import Drone
    from graph import Graph
    from algo_dijkstra import AlgoDijkstra
except ImportError as e:
    print(f"[ERROR] simulator.py: {e}")
    sys.exit()


class Simulator():

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.drones = {}
        self.path = {}
        self.nb_turn = 0

    def init_drone(self) -> None:
        nb_drone = self.graph.nb_drone

        for n in range(1, nb_drone + 1):
            self.drones[f"D{n}"] = self.graph.start_zone