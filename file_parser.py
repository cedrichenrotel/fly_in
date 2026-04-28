# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  file_parser.py                                    :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 15:02:34 by cehenrot        #+#    #+#               #
#  Updated: 2026/04/28 18:44:41 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from drone import Drone
    from zone import Zone
    from graph import Graph
    from connection import Connection
except ImportError as e:
    print(f"[ERROR] file_parser.py: {e}")
    sys.exit()


def parse_file(file: str) -> Graph:
    graph = Graph()

    with open(file) as f:
        if not f:
            raise Exception(f"[WARNING]: Empty file: {file}")
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('nb_drones:'):
                key, value = line.split(':')
                try:
                    nb_drone = int(value)
                    if nb_drone <= 0:
                        raise Exception("[WARNING]-> nb_drones: value <= 0")
                except ValueError:
                    raise Exception("[WARNING]-> nb_drones: value unknown")
                    sys.exit()
                pass
            elif line.startswith('start_hub:'):
                pass
            elif line.startswith('end_hub:'):
                pass
            elif line.startswith('hub:'):
                pass
            elif line.startswith('connection:'):
                pass
            
    return graph