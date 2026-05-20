# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  simulator.py                                      :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:35:52 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/20 14:48:18 by cehenrot        ###   ########.fr        #
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
        algo_dijkstra = AlgoDijkstra(self.graph)
        algo_dijkstra.start = self.graph.end_zone
        algo_dijkstra.run()

        self.distances_from_goal = algo_dijkstra.distances

        algo_a = AlgoAstar(self.graph, self.distances_from_goal)
        algo_a.run()
        base_path = algo_a.reconstruct_path()

        for drone in self.drones_id.values():
            drone.path = list(base_path)

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
                current_index = current_path.index(current_drone.
                                                   current_zone.name)

                old_zone = current_drone.current_zone
                next_path = current_path[current_index + 1]
                next_zone = self.graph.dict_zones[next_path]
                connection = self.graph.get_neighbors(current_drone.
                                                      current_zone)

                for conn in connection:
                    if conn.zone_a == next_zone or conn.zone_b == next_zone:
                        
                        # Drones qui ont déjà prévu de venir dans la zone au cours de ce tour
                        nb_drones_entry = len([
                            m for m in moves if m[2] == next_zone
                        ])

                        # Drones qui ont prévu de partir de cette zone au cours de ce tour
                        nb_drones_exit = len([
                            m for m in moves if m[1] == next_zone
                        ])

                        # CALCUL CORRIGÉ : Actuels + Entrées - Sorties
                        nb_current_drone = (
                            next_zone.current_drones + nb_drones_entry - nb_drones_exit
                        )

                        # Vérification des contraintes de la zone et de la liaison
                        if (next_zone.zone_type != ZoneType.blocked and
                            len([m for m in moves
                                 if m[1] == old_zone and
                                 m[2] == next_zone]) < conn.max_link_capacity
                                and
                                nb_current_drone < next_zone.max_drones):

                            if next_zone.zone_type == ZoneType.restricted:
                                current_drone.in_transit = True
                                current_drone.transit_destination = next_zone
                                # Sauvegarde indispensable du nom de la connexion pour le tour d'après !
                                current_drone.transit_conn_name = conn.name
                                
                                moves.append((
                                    drone, old_zone, next_zone, conn.name
                                ))
                            else:
                                moves.append((
                                    drone, old_zone, next_zone, None
                                ))
                            break
                else:
                    blocked_zones = set()
                    for z_name, zone in self.graph.dict_zones.items():
                        if zone.current_drones >= zone.max_drones:
                            blocked_zones.add(z_name)

                    algo_a = AlgoAstar(self.graph,
                                       self.distances_from_goal)
                    algo_a.start = current_drone.current_zone

                    algo_a.run(blocked_zones=blocked_zones)

                    try:
                        new_path = algo_a.reconstruct_path(
                            start_zone=current_drone.current_zone
                        )
                        current_drone.path = new_path
                        
                        # --- OPTIMISATION FLUIDITÉ ---
                        # On met à jour directement sa prochaine cible avec son nouveau chemin
                        next_path = new_path[1] # L'index 0 est sa position actuelle, l'index 1 est sa nouvelle cible
                        next_zone = self.graph.dict_zones[next_path]
                        
                        # On lui donne une chance de s'engager tout de suite sur cette nouvelle voie libre !
                        for conn in connection:
                            if conn.zone_a == next_zone or conn.zone_b == next_zone:
                                # (On refait la même validation rapide de sécurité)
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
                                    break
                    except Exception:
                        pass #

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
