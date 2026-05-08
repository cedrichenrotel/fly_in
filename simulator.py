# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  simulator.py                                      :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:35:52 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/08 14:27:31 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from zone import ZoneType
    from drone import Drone
    from graph import Graph
    from algos import AlgoDijkstra
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
            self.trajectory[f'D{n}'] = []
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
            priority_drones = ([d for d in self.drones_id
                               if self.drones_id[d].current_zone.zone_type ==
                               ZoneType.priority])
            other_drones = ([d for d in self.drones_id
                            if self.drones_id[d].current_zone.zone_type !=
                            ZoneType.priority])

            for drone in priority_drones + other_drones:
                current_drone = self.drones_id[drone]

                if current_drone.is_arrived:
                    continue

                if current_drone.in_transit:
                    current_drone.in_transit = False
                    moves.append((drone, current_drone.current_zone,
                                  current_drone.transit_destination))
                    current_drone.transit_destination = None
                    continue

                current_path = self.paths[drone]
                current_index = current_path.index(current_drone.
                                                   current_zone.name)
                next_path = current_path[current_index + 1]
                next_zone = self.graph.dict_zones[next_path]

                connection = self.graph.get_neighbors(current_drone.
                                                      current_zone)

                for conn in connection:
                    if conn.zone_a == next_zone or conn.zone_b == next_zone:

                        nb_drones_entry = len([m for m in moves if m[2] ==
                                               next_zone])
                        nb_drones_exit = len([m for m in moves if m[1] ==
                                              next_zone])
                        nb_current_drone = (next_zone.current_drones -
                                            nb_drones_exit + nb_drones_entry)

                        if (next_zone.zone_type != ZoneType.blocked and
                            len([m for m in moves
                                 if m[1] == current_drone.current_zone and
                                 m[2] == next_zone]) < conn.max_link_capacity
                                and
                                nb_current_drone < next_zone.max_drones):

                            moves.append((drone, current_drone.current_zone,
                                          next_zone))

                            if next_zone.zone_type == ZoneType.restricted:
                                current_drone.in_transit = True
                                current_drone.transit_destination = next_zone
                            break

            for (drone, old_zone, next_zone) in moves:
                old_zone.current_drones -= 1
                self.drones_id[drone].drone_move(next_zone,
                                                 self.graph.end_zone)
                next_zone.current_drones += 1
                self.trajectory[drone].append(next_zone.name)

            self.stock_turns.append([f"{drone}-{next_zone.name}"
                                     for (drone, _, next_zone) in moves])

            self.nb_turn += 1
