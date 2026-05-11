# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  simulator.py                                      :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:35:52 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/11 13:27:26 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from zone import ZoneType
    from drone import Drone
    from graph import Graph
    from algos import AlgoDijkstra, AlgoAstar
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

        algo_d = AlgoDijkstra(self.graph)
        algo_d.run()

        path1 = algo_d.reconstruct_path()

        gate = self.graph.dict_zones[path1[1]]
        original_type = gate.zone_type
        gate.zone_type = ZoneType.blocked

        algo_a = AlgoAstar(self.graph)
        algo_a.run()

        try:
            path2 = algo_a.reconstruct_path()
            if len(path2) > len(path1):
                raise Exception("path2 too long")
        except Exception as e:
            print(f"failled:{e}")
            gate.zone_type = original_type
            for drone in self.drones_id:
                self.paths[drone] = path1.copy()
            return

        gate.zone_type = original_type

        for i, drone in enumerate(self.drones_id):
            if i % 2 == 0:
                self.paths[drone] = path1.copy()
            else:
                self.paths[drone] = path2.copy()

    def run_drones(self) -> None:

        """run_drones — loops through each turn and moves each drone"""
        while not all(drone.is_arrived for drone in self.drones_id.values()):

            moves: list[tuple] = []
            priority_drones = ([
                d for d in self.drones_id
                if self.drones_id[d].current_zone.zone_type ==
                ZoneType.priority
                ])
            other_drones = ([
                d for d in self.drones_id
                if self.drones_id[d].current_zone.zone_type !=
                ZoneType.priority
                ])

            for drone in priority_drones + other_drones:

                current_drone = self.drones_id[drone]

                if current_drone.is_arrived:
                    continue

                current_path = self.paths[drone]
                current_index = current_path.index(current_drone.
                                                   current_zone.name)

                old_zone = current_drone.current_zone
                next_path = current_path[current_index + 1]
                next_zone = self.graph.dict_zones[next_path]
                connection = self.graph.get_neighbors(current_drone.
                                                      current_zone)

                if current_drone.in_transit:
                    current_drone.in_transit = False

                    moves.append((
                        drone, current_drone.current_zone,
                        current_drone.transit_destination,
                        current_drone.transit_conn_name
                        ))

                    current_drone.transit_destination = None
                    continue

                for conn in connection:
                    if conn.zone_a == next_zone or conn.zone_b == next_zone:
                        nb_drones_entry = len([
                            m for m in moves if m[2] == next_zone
                            ])

                        nb_drones_exit = len([
                            m for m in moves if m[1] == next_zone
                            ])

                        nb_current_drone = (
                            next_zone.current_drones - nb_drones_exit +
                            nb_drones_entry
                            )

                        if (next_zone.zone_type != ZoneType.blocked and
                            len([m for m in moves
                                 if m[1] == old_zone and
                                 m[2] == next_zone]) < conn.max_link_capacity
                                and
                                nb_current_drone < next_zone.max_drones):

                            if next_zone.zone_type == ZoneType.restricted:
                                current_drone.in_transit = True

                                current_drone.transit_destination = next_zone
                                moves.append((
                                    drone,
                                    old_zone,
                                    next_zone,
                                    conn.name
                                ))

                            else:
                                moves.append((
                                    drone,
                                    old_zone,
                                    next_zone,
                                    None
                                ))
                            break

            for (drone, old_zone, next_zone, _) in moves:
                old_zone.current_drones -= 1
                self.drones_id[drone].drone_move(next_zone,
                                                 self.graph.end_zone)
                next_zone.current_drones += 1
                self.trajectory[drone].append(next_zone.name)

            self.stock_turns.append([
                f"{drone}-{conn_name if conn_name else next_zone.name}"
                for (drone, _, next_zone, conn_name) in moves
                ])

            self.nb_turn += 1
