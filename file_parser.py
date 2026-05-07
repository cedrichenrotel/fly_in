# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  file_parser.py                                    :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 15:02:34 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/07 11:38:34 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from zone import Zone, ZoneType
    from graph import Graph
    from connection import Connection
except ImportError as e:
    print(f"[ERROR] file_parser.py: {e}")
    sys.exit()


def extraction_info(line: str) -> list:

    """split a line in the file to extract the information more effectively"""
    info = line.replace('[', '').replace(']', '').split()
    if info[0] == 'connection:':
        if len(info) < 2:
            raise Exception(f"Exctraction_info-> nb info connection "
                            f"ncorrect {info} number: {len(info)}")
    else:
        if len(info) < 4:
            raise Exception(f"Exctraction_info-> nb info ligne "
                            f"incorrect {info} number: {len(info)}")
    return info


def parse_zone(line: str) -> Zone:
    info = extraction_info(line)
    name_zone = check_name_zone(info[1])
    x = check_coordinate(info[2])
    y = check_coordinate(info[3])
    meta = extract_metadata(info[4:])
    zone = Zone(name_zone, x, y, **meta)
    return zone


def check_name_zone(name_zone: str) -> str:

    """checks that there are no '-', then stores the field name in a
        variable """
    name = name_zone
    if '-' in name_zone:
        raise Exception("File_parser-> character not allowed")
    return name


def check_coordinate(coordinate: str) -> int:

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
                dict_meta['zone_type'] = ZoneType[val].name
            if key == 'max_drones':
                dict_meta['max_drones'] = int(val)
        return dict_meta
    except ValueError as e:
        raise Exception(f"Extract_metadata-> {e} invalid")


def parse_file(file: str) -> Graph:
    graph = Graph()
    set_zones = set()

    """Parse a map file and build a Graph object."""
    with open(file) as f:
        if not f:
            raise Exception(f"[WARNING]: Empty file: {file}")
        for line in f:
            line = line.strip()
            line = line.split('#')[0]
            if not line:
                continue
            if line.startswith('nb_drones:'):
                _, value = line.split(':')
                try:
                    nb_drone = int(value)
                    if nb_drone <= 0:
                        raise Exception("Parser-file-> nb_drones: value <= 0")
                except ValueError:
                    raise Exception("Parser-file-> nb_drones: value unknown")
                graph.nb_drone = nb_drone

            elif line.startswith('start_hub:'):
                zone = parse_zone(line)
                graph.add_zone(zone)
                graph.set_start_zone(zone)

            elif line.startswith('end_hub:'):
                zone = parse_zone(line)
                graph.add_zone(zone)
                graph.set_end_zone(zone)

            elif line.startswith('hub:'):
                zone = parse_zone(line)
                graph.add_zone(zone)

            elif line.startswith('connection:'):
                info = extraction_info(line)
                zone_a, zone_b = info[1].split('-')
                if (zone_a not in graph.dict_zones or
                   zone_b not in graph.dict_zones):
                    raise Exception("Parser-file-> connection coordinate "
                                    "unknown")

                if frozenset((zone_a, zone_b)) in set_zones:
                    raise Exception("Parser-file-> The same connection appears"
                                    " more than once")
                set_zones.add(frozenset((zone_a, zone_b)))

                obj_zone_a = graph.dict_zones[zone_a]
                obj_zone_b = graph.dict_zones[zone_b]

                max_link_capacity = 1
                if len(info) > 2:
                    try:
                        key, value = info[2].split("=")
                        if key == 'max_link_capacity':
                            max_link_capacity = int(value)
                            if max_link_capacity <= 0:
                                raise Exception(f"max_link_capacity <= 0, "
                                                f"value: {max_link_capacity}")
                    except ValueError as e:
                        raise Exception(f"Max_link_capacity is not value, "
                                        f"value: {e}")
                connection = Connection(obj_zone_a, obj_zone_b,
                                        max_link_capacity)

                graph.add_adjacency(connection)

        if graph.start_zone is None:
            raise Exception("Parser-file-> no start_hub found")
        if graph.end_zone is None:
            raise Exception("Parser-file-> no end_hub found")
        if graph.nb_drone == 0:
            raise Exception("Parser-file-> no nb_drones found")
    return graph
