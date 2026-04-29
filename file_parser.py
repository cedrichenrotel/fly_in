# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  file_parser.py                                    :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 15:02:34 by cehenrot        #+#    #+#               #
#  Updated: 2026/04/29 11:44:41 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from drone import Drone
    from zone import Zone, ZoneType
    from graph import Graph
    from connection import Connection
except ImportError as e:
    print(f"[ERROR] file_parser.py: {e}")
    sys.exit()


def parse_file(file: str) -> Graph:
    graph = Graph()

    """Parse a map file and build a Graph object."""
    with open(file) as f:
        if not f:
            raise Exception(f"[WARNING]: Empty file: {file}")
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('nb_drones:'):
                _, value = line.split(':')
                try:
                    nb_drone = int(value)
                    if nb_drone <= 0:
                        raise Exception("File_parser-> nb_drones: value <= 0")
                except ValueError:
                    raise Exception("File_parser-> nb_drones: value unknown")

            elif line.startswith('start_hub:'):
                info = line.replace('[', '').replace(']', '').split()
                if len(info) < 5:
                    raise Exception("File_parser-> nb info ligne incorrect")
                name_zone = info[1]
                if '-' in name_zone:
                    raise Exception("File_parser-> character not allowed")
                try:
                    x = int(info[2])
                    y = int(info[3])
                except ValueError as e:
                    raise Exception(f"File_parser-> incorrect value: {e}")
                try:
                    for meta in info[4:]:
                        key, val = meta.split('=')
                        if key == 'color':
                            color = val
                        if key == 'zone':
                            zone_type = ZoneType(val)
                        if key == 'max_drones':
                            max_drone = int(val)
                except ValueError as e:
                    raise Exception(f"File_parser-> {e} invalid")

                zone = Zone(name_zone, x, y, zone_type, color, max_drone)
                print(info[4:])
                pass
            elif line.startswith('end_hub:'):
                pass
            elif line.startswith('hub:'):
                pass
            elif line.startswith('connection:'):
                pass
            
    return graph