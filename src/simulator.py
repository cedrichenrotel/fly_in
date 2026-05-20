# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  simulator.py                                      :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:35:52 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/20 17:51:52 by cehenrot        ###   ########.fr        #
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
        self.drones_id: dict[str, Drone] = {}
        self.paths: list = []
        self.trajectory: dict = {}
        self.nb_turn: int = 0
        self.distances_from_goal: dict[str, int] = {}

    def init_drone(self) -> None:
        """init_drone: creates all drones in the start_zone"""
        nb_drone = self.graph.nb_drone
        if nb_drone is None:
            raise ValueError("The starting point of the graph has not been set.")

        start_zone = self.graph.start_zone
        if start_zone is None:
            raise ValueError("Simulator -> start_zone is None; unable to initialise the drones")

        for n in range(1, nb_drone + 1):
            self.trajectory[f'D{n}'] = []
            self.drones_id[f"D{n}"] = Drone(f"D{n}", start_zone)
            start_zone.current_drones += 1

    def init_run(self) -> None:
        """assigning a perfectly weighted base path and tracking distances"""
        # Pré-calcul parfait des distances depuis l'objectif vers chaque nœud
        algo_dijkstra = AlgoDijkstra(self.graph)
        algo_dijkstra.start = self.graph.end_zone
        algo_dijkstra.run()
        self.distances_from_goal = algo_dijkstra.distances

        # Premier calcul du chemin optimal global
        algo_a = AlgoAstar(self.graph, self.distances_from_goal)
        algo_a.run()
        base_path = algo_a.reconstruct_path()

        for drone in self.drones_id.values():
            drone.path = list(base_path)

    def run_drones(self) -> None:
        """run_drones — optimized loop to clear bottlenecks instantly"""
        while not all(drone.is_arrived for drone in self.drones_id.values()):

            moves: list[tuple] = []
            
            # OPTIMISATION FLUX : On trie en priorité absolue les drones proches de l'arrivée 
            # ou dans des zones prioritaires pour libérer l'espace devant (Aspiration du trafic)
            sorted_drones = sorted(
                self.drones_id.keys(),
                key=lambda d: (
                    0 if self.drones_id[d].current_zone.zone_type == ZoneType.priority else 1,
                    self.distances_from_goal.get(self.drones_id[d].current_zone.name, 999)
                )
            )

            for drone in sorted_drones:
                current_drone = self.drones_id[drone]

                if current_drone.is_arrived:
                    continue

                if current_drone.in_transit:
                    current_drone.in_transit = False
                    moves.append((
                        drone, current_drone.current_zone,
                        current_drone.transit_destination,
                        current_drone.transit_conn_name
                    ))
                    current_drone.transit_destination = None
                    continue

                current_path = current_drone.path
                current_index = current_path.index(current_drone.current_zone.name)

                old_zone = current_drone.current_zone
                next_path = current_path[current_index + 1]
                next_zone = self.graph.dict_zones[next_path]
                connection = self.graph.get_neighbors(current_drone.current_zone)

                moved = False
                for conn in connection:
                    if conn.zone_a == next_zone or conn.zone_b == next_zone:
                        
                        nb_drones_entry = len([m for m in moves if m[2] == next_zone])
                        nb_drones_exit = len([m for m in moves if m[1] == next_zone])
                        nb_current_drone = next_zone.current_drones + nb_drones_entry - nb_drones_exit

                        if (next_zone.zone_type != ZoneType.blocked and
                            len([m for m in moves if m[1] == old_zone and m[2] == next_zone]) < conn.max_link_capacity and
                            nb_current_drone < next_zone.max_drones):

                            if next_zone.zone_type == ZoneType.restricted:
                                current_drone.in_transit = True
                                current_drone.transit_destination = next_zone
                                current_drone.transit_conn_name = conn.name
                                moves.append((drone, old_zone, next_zone, conn.name))
                            else:
                                moves.append((drone, old_zone, next_zone, None))
                            moved = True
                            break
                
                # --- REPLANIFICATION AGRESSIVE (Si le drone de tête est bloqué) ---
                if not moved:
                    blocked_zones = set()
                    for z_name, zone in self.graph.dict_zones.items():
                        # On considère une zone bloquée uniquement si elle est AU MAXIMUM de sa capacité ce tour-ci
                        # et qu'aucun drone ne la quitte.
                        nb_entry = len([m for m in moves if m[2] == zone])
                        nb_exit = len([m for m in moves if m[1] == zone])
                        if (zone.current_drones + nb_entry - nb_exit) >= zone.max_drones:
                            blocked_zones.add(z_name)

                    algo_a = AlgoAstar(self.graph, self.distances_from_goal)
                    algo_a.start = current_drone.current_zone
                    algo_a.run(blocked_zones=blocked_zones)

                    try:
                        new_path = algo_a.reconstruct_path(start_zone=current_drone.current_zone)
                        current_drone.path = new_path
                        
                        next_path = new_path[1]
                        next_zone = self.graph.dict_zones[next_path]
                        
                        # Tentative d'engagement immédiat dans la déviation pour gagner 1 tour précieux
                        for conn in connection:
                            if conn.zone_a == next_zone or conn.zone_b == next_zone:
                                nb_entry = len([m for m in moves if m[2] == next_zone])
                                nb_exit = len([m for m in moves if m[1] == next_zone])
                                nb_current_drone = next_zone.current_drones + nb_entry - nb_exit
                                
                                if (next_zone.zone_type != ZoneType.blocked and
                                    len([m for m in moves if m[1] == old_zone and m[2] == next_zone]) < conn.max_link_capacity and
                                    nb_current_drone < next_zone.max_drones):
                                    
                                    if next_zone.zone_type == ZoneType.restricted:
                                        current_drone.in_transit = True
                                        current_drone.transit_destination = next_zone
                                        current_drone.transit_conn_name = conn.name
                                        moves.append((drone, old_zone, next_zone, conn.name))
                                    else:
                                        moves.append((drone, old_zone, next_zone, None))
                                    break
                    except Exception:
                        pass

            for (drone, old_zone, next_zone, _) in moves:
                old_zone.current_drones -= 1
                self.drones_id[drone].drone_move(next_zone, self.graph.end_zone)
                next_zone.current_drones += 1
                self.trajectory[drone].append(next_zone.name)

            self.stock_turns.append([
                f"{drone}-{conn_name if conn_name else next_zone.name}"
                for (drone, _, next_zone, conn_name) in moves
            ])

            self.nb_turn += 1