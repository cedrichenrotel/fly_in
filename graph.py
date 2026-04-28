# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  graph.py                                          :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:35:18 by cehenrot        #+#    #+#               #
#  Updated: 2026/04/28 17:30:11 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from connection import Connection
    from zone import Zone
except ImportError as e:
    print(f"[ERROR] graph.py: {e}")
    sys.exit()


class Graph():
    """contains all the zones and connections"""

    def __init__(self) -> None:

        self.dict_zones = {}
        self.dict_adjacency = {}
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None

    def set_start_zone(self, zone: Zone) -> None:
        self.start_zone = zone

    def set_end_zone(self, zone: Zone) -> None:
        self.end_zone = zone

    """Check that the surrounding area is authorised for the drone"""
    def get_neighbors(self, zone: Zone) -> list:
        lst_neighbors = []

        if zone.name in self.dict_adjacency:
            lst_neighbors = self.dict_adjacency[zone.name]
        return lst_neighbors

    """Add a new field to 'dict_zone' using the name """
    def add_zone(self, zone: Zone) -> None:
        self.dict_zones[zone.name] = zone

    """Add a connection to both zones in dict_adjacency.
        Connections are bidirectional"""
    def add_adjacency(self, connection: Connection) -> None:
        self.dict_adjacency.setdefault(connection.zone_a.name, [])
        self.dict_adjacency[connection.zone_a.name].append(connection)
        self.dict_adjacency.setdefault(connection.zone_b.name, [])
        self.dict_adjacency[connection.zone_b.name].append(connection)
