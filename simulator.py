# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  simulator.py                                      :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:35:52 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/06 17:36:51 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from zone import ZoneType
    from drone import Drone
    from graph import Graph
    from algo_dijkstra import AlgoDijkstra
except ImportError as e:
    print(f"[ERROR] simulator.py: {e}")
    sys.exit()


class Simulator():

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.stock_turns: list[list[str]] = []
        self.drones_id: dict = {}
        self.paths: dict = {}
        self.trajectory: dict = {}
        self.nb_turn: int = 0

    def init_drone(self) -> None:
        """init_drone: creates all drones in the start_zone"""

        nb_drone = self.graph.nb_drone

        if nb_drone is None:
            raise ValueError("The starting point of the graph has not been "
                             "set.")

        start_zone = self.graph.start_zone

        if start_zone is None:
            raise ValueError("Simulator -> start_zone is None; unable to "
                             "initialise the drones")

        for n in range(1, nb_drone + 1):
            self.drones_id[f"D{n}"] = Drone(f"D{n}", start_zone)

        start_zone.current_drones += 1

    def init_run(self) -> None:
        """assigning a single path to all drones"""

        algo = AlgoDijkstra(self.graph)
        algo.run()
        path = algo.reconstruct_path()
        for drone in self.drones_id:
            self.paths[drone] = path.copy()

    def run_drones(self) -> None:
        """run_drones — loops through each turn and moves each drone"""

        while not all(drone.is_arrived for drone in self.drones_id.values()):

            moves: list[tuple] = []

            for drone in self.drones_id:

                current_drone = self.drones_id[drone]

                """Do not tamper with the drones once they have reached their
                    destination"""
                if current_drone.is_arrived:
                    continue

                current_path = self.paths[drone]

                current_index = current_path.index(current_drone.
                                                   current_zone.name)

                next_path = current_path[current_index + 1]
                next_zone = self.graph.dict_zones[next_path]

                """If the next zone is not blocked and no other drone has
                    already reserved that zone for this turn, then the planned
                    move (drone, current_zone, next_zone) is added to the list
                    of moves for the turn."""
                if (next_zone.zone_type != ZoneType.blocked and
                   next_zone not in [m[2] for m in moves]):
                    moves.append((drone, current_drone.current_zone,
                                  next_zone))

            for (drone, old_zone, next_zone) in moves:
                old_zone.current_drones -= 1
                self.drones_id[drone].drone_move(next_zone,
                                                 self.graph.end_zone)
                next_zone.current_drones += 1
                self.trajectory[drone].append(next_zone.name)
            """record the drone's flight paths for each round"""
            self.stock_turns.append([f"{drone}-{next_zone.name}"
                                     for (drone, _, next_zone) in moves])

            self.nb_turn += 1
