# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  file_parser.py                                    :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 15:02:34 by cehenrot        #+#    #+#               #
#  Updated: 2026/04/29 14:45:12 by cehenrot        ###   ########.fr        #
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


def parse_zone(line: str) -> Zone:
    info = extraction_info(line)
    name_zone = check_name_zone(info[1])
    x = check_coordinate(info[2])
    y = check_coordinate(info[3])
    meta = extract_metadata(info[4:])
    zone = Zone(name_zone, x, y, **meta)
    return zone


def extraction_info(line: str) -> list:

    """split a line in the file to extract the information more effectively"""
    info = line.replace('[', '').replace(']', '').split()
    if len(info) < 4:
        raise Exception("Exctraction_info-> nb info ligne incorrect")
    return info


def check_name_zone(name_zone: str) -> str:

    """checks that there are no '-', then stores the field name in a
        variable """
    name = name_zone
    if '-' in name_zone:
        raise Exception("File_parser-> character not allowed")
    return name


def check_coordinate(coordinate: int) -> int:

    """checks that the value is indeed an integer and stores it in a
        variable"""
    try:
        x = int(coordinate)
        return x
    except ValueError as e:
        raise Exception(f"Check_coordinate-> incorrect value: {e}")


def extract_metadata(lst_meta: list[str]) -> dict:
    dict_meta = {}

    """function that retrieves metadata values (colour, max_drones, etc.) and
         stores them in a dictionary"""
    try:
        for meta in lst_meta:
            key, val = meta.split('=')
            if key == 'color':
                dict_meta['color'] = val
            if key == 'zone':
                dict_meta['zone_type'] = ZoneType(val)
            if key == 'max_drones':
                dict_meta['max_drones'] = int(val)
        return dict_meta
    except ValueError as e:
        raise Exception(f"Extract_metadata-> {e} invalid")


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
                zone = parse_zone(line)
                graph.add_zone(zone)
                graph.set_start_zone(zone)

            elif line.startswith('end_hub:'):
                info = extraction_info(line)
                name_zone = check_name_zone(info[1])
                x = check_coordinate(info[2])
                y = check_coordinate(info[3])
                meta = extract_metadata(info[4:])
                zone = Zone(name_zone, x, y, **meta)
                graph.add_zone(zone)
                graph.set_end_zone(zone)

            elif line.startswith('hub:'):
                info = extraction_info(line)
                name_zone = check_name_zone(info[1])
                x = check_coordinate(info[2])
                y = check_coordinate(info[3])
                meta = extract_metadata(info[4:])
                zone = Zone(name_zone, x, y, **meta)
                graph.add_zone(zone)

            elif line.startswith('connection:'):
                pass
            
    return graph