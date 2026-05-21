# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  simulator.py                                      :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:35:52 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/21 11:34:27 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from drone import Drone
    from graph import Graph
    from typing import List, Dict, Tuple
    from algos import AlgoDijkstra, AlgoAstar
except ImportError as e:
    print(f"[ERROR] simulator.py: {e}")
    sys.exit()


class Simulator():

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.stock_turns: list[list[str]] = []
        self.drones_id: dict[str, Drone] = {}
        self.paths: list = []
        self.trajectory: dict = {}
        self.nb_turn: int = 0
        self.distances_from_goal: dict[str, int] = {}

    def init_drone(self) -> None:
        """init_drone: creates all drones in the start_zone"""
        nb_drone = self.graph.nb_drone
        if nb_drone is None:
            raise ValueError("The starting point of the graph has not"
                             "been set.")

        start_zone = self.graph.start_zone
        if start_zone is None:
            raise ValueError("Simulator -> start_zone is None; unable to"
                             "initialise the drones")

        for n in range(1, nb_drone + 1):
            self.trajectory[f'D{n}'] = []
            self.drones_id[f"D{n}"] = Drone(f"D{n}", start_zone)
            start_zone.current_drones += 1

    def init_run(self) -> None:
        """Comprehensive preventive planning by time and space."""
        algo_dijkstra = AlgoDijkstra(self.graph)
        algo_dijkstra.start = self.graph.end_zone
        algo_dijkstra.run()
        self.distances_from_goal = algo_dijkstra.distances

        space_time_reservation: Dict[Tuple[str, int], int] = {}

        for _, drone in self.drones_id.items():
            algo_a = AlgoAstar(self.graph, self.distances_from_goal)
            algo_a.run(space_time_reservation=space_time_reservation)

            st_path = algo_a.get_reconstructed_path()

            for zone_name, turn in st_path:
                if (zone_name != self.graph.start_zone.name and
                   zone_name != self.graph.end_zone.name):
                    space_time_reservation[(zone_name, turn)] = (
                        space_time_reservation.get((zone_name, turn), 0) + 1
                        )

            max_turn: int = st_path[-1][1]
            timeline: List[str] = [self.graph.start_zone.name] * (max_turn + 1)

            for i in range(len(st_path) - 1):
                z_curr, t_curr = st_path[i]
                z_next, t_next = st_path[i + 1]

                for t in range(t_curr, t_next):
                    if (t_next - t_curr) == 2 and t == t_curr:
                        conn_name = ""
                        for conn in self.graph.get_neighbors(
                            self.graph.dict_zones[z_curr]
                             ):
                            if (conn.zone_a.name == z_next or
                               conn.zone_b.name == z_next):
                                conn_name = conn.name
                                break
                        timeline[t + 1] = conn_name
                    else:
                        timeline[t + 1] = z_next

            drone.path = timeline

    def run_drones(self) -> None:
        """Generates turn-by-turn output based on the ideal
            racing lines."""
        max_turns = max(len(d.path) for d in self.drones_id.values())

        for turn in range(1, max_turns):
            moves: List[str] = []

            for d_id, drone in self.drones_id.items():
                if turn >= len(drone.path):
                    continue

                current_pos = drone.path[turn]
                prev_pos = drone.path[turn - 1]

                if current_pos != prev_pos:
                    if prev_pos == self.graph.end_zone.name:
                        continue
                    moves.append(f"{d_id}-{current_pos}")

            if moves:
                self.stock_turns.append(moves)

        self.nb_turn = len(self.stock_turns)
