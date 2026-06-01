# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  file_parser.py                                    :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 15:02:34 by cehenrot        #+#    #+#               #
#  Updated: 2026/06/01 15:14:57 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from error import ParseError
    from zone import Zone, ZoneType
    from graph import Graph
    from connection import Connection
except ImportError as e:
    print(f"[ERROR] file_parser.py: {e}")
    sys.exit()


class FileParser():

    def __init__(self) -> None:
        pass

    def extraction_info(self, line: str, line_num: int) -> list:

        """split a line in the file to extract the information more
            effectively"""
        crochet_open = '[' in line
        crochet_close = ']' in line

        if crochet_open or crochet_close:
            if not crochet_open:
                raise ParseError(f"Line {line_num}: missing crochet "
                                 "open '['")
            if not crochet_close:
                raise ParseError(f"Line {line_num}: missing crochets "
                                 "close ']'")
            if line.index('[') > line.index(']'):
                raise ParseError(f"Line {line_num}: ']' before '['")
            if line.count('[') > 1 or line.count(']') > 1:
                raise ParseError(f"Line {line_num}: multiple crochets")

        line_brut = line.split()
        inside_brackets = False

        for part in line_brut:
            if '[' in part:
                inside_brackets = True
                continue
            if ']' in part:
                inside_brackets = False
                continue
            if not inside_brackets and '=' in part:
                raise ValueError(f"Line {line_num}: Metadata must be "
                                 "enclosed in brackets '[]'")

        info = line.replace('[', '').replace(']', '').split()
        if info[0] == 'connection:':
            if len(info) < 2:
                raise ValueError(f"Exctraction_info-> nb info connection "
                                 f"ncorrect {info} number: {len(info)}")
        else:
            if len(info) < 4:
                raise ValueError(f"Exctraction_info-> nb info ligne "
                                 f"incorrect {info} number: {len(info)}")
        return info

    def parse_zone(self, line: str, line_num: int) -> Zone:
        info = self.extraction_info(line, line_num)
        name_zone = self.check_name_zone(info[1], line_num)
        x = self.check_coordinate(info[2], line_num)
        y = self.check_coordinate(info[3], line_num)
        meta = self.extract_metadata(info[4:], line_num)
        zone = Zone(name_zone, x, y, **meta)
        return zone

    def check_name_zone(self, name_zone: str, line_num: int) -> str:

        """checks that there are no '-', then stores the field name in a
            variable """
        name = name_zone
        if '-' in name_zone:
            raise ParseError(f"line {line_num}: File_parser-> character "
                             "not allowed")
        return name

    def check_coordinate(self, coordinate: str, line_num: int) -> int:

        """checks that the value is indeed an integer and stores it in a
            variable"""
        try:
            x = int(coordinate)
            return x
        except ValueError as e:
            raise ValueError(f"line {line_num}: Check_coordinate-> "
                             f"incorrect value: {e}")

    def extract_metadata(self, st_meta: list[str], line_num: int) -> dict:
        dict_meta: dict[str, object] = {}

        """function that retrieves metadata values (colour, max_drones, etc.)
            and stores them in a dictionary"""
        try:
            for meta in st_meta:
                key, val = meta.split('=')
                if key == 'color':
                    dict_meta['color'] = val
                elif key == 'zone':
                    dict_meta['zone_type'] = ZoneType[val]
                elif key == 'max_drones':
                    max_drones = int(val)
                    if max_drones <= 0:
                        raise ValueError("Value of 'max_drone' is "
                                         "not positive")
                    dict_meta['max_drones'] = max_drones
                else:
                    raise ParseError(f"Ligne {line_num}: metadata unknown")
            return dict_meta
        except KeyError:
            raise KeyError(f"line {line_num}: invalid zone type: {val}")
        except ValueError as e:
            raise ValueError(f"line {line_num}: Extract_metadata-> {e}")

    def check_doublon_zone(self, zone: Zone, set_name_zone: set[str],
                           line_num: int) -> None:

        if zone.name in set_name_zone:
            raise ParseError(f"Line {line_num}: duplicate zone "
                             f"name '{zone.name}'")

        set_name_zone.add(zone.name)

    def parse_file(self, file: str) -> Graph:

        """Parse a map file and build a Graph object."""
        graph = Graph()
        set_zones = set()
        set_name_zone: set[str] = set()

        with open(file) as f:
            empty: bool = True
            dup_nb_drone: bool = False
            start = False
            end = False

            for line_num, line in enumerate(f, start=1):
                empty = False
                line = line.strip()
                line = line.split('#')[0]
                if not line:
                    continue
                if not dup_nb_drone and not line.startswith('nb_drones:'):
                    raise ParseError(f"Line {line_num}: 'nb_drones' must be "
                                     "defined first")
                if line.startswith('nb_drones:'):
                    _, value = line.split(':')
                    try:
                        nb_drone = int(value)
                    except ValueError:
                        raise ValueError(f"Line: {line_num}: Nb_drones: "
                                         "value unknown")

                    if nb_drone <= 0:
                        raise ValueError(f"Line{line_num}: Nb_drones: "
                                         "value <= 0")
                    if nb_drone > 100:
                        raise ValueError(f"Line{line_num}: Nb_drones: "
                                         "value > 100")
                    if dup_nb_drone:
                        raise ParseError(f"Line{line_num}: 'nb_drones' "
                                         "is a duplicate")
                    dup_nb_drone = True

                    graph.nb_drone = nb_drone

                elif line.startswith('start_hub:'):
                    if not start:
                        zone = self.parse_zone(line, line_num)

                        self.check_doublon_zone(zone, set_name_zone, line_num)

                        graph.add_zone(zone)
                        graph.set_start_zone(zone)
                        start = True
                    else:
                        raise ParseError(f"line {line_num}: "
                                         "Duplicate start_hub")

                elif line.startswith('end_hub:'):
                    if not end:
                        zone = self.parse_zone(line, line_num)

                        self.check_doublon_zone(zone, set_name_zone, line_num)

                        graph.add_zone(zone)
                        graph.set_end_zone(zone)
                        end = True
                    else:
                        raise ParseError(f"line {line_num}: "
                                         "Duplicate end_hub")

                elif line.startswith('hub:'):
                    zone = self.parse_zone(line, line_num)

                    self.check_doublon_zone(zone, set_name_zone, line_num)

                    graph.add_zone(zone)

                elif line.startswith('connection:'):
                    info = self.extraction_info(line, line_num)
                    zone_a, zone_b = info[1].split('-', maxsplit=1)

                    if (zone_a not in graph.dict_zones or
                       zone_b not in graph.dict_zones):
                        raise KeyError(f"Line {line_num}: "
                                       "Connection coordinate unknown")

                    if frozenset((zone_a, zone_b)) in set_zones:
                        raise ParseError(f"Line {line_num}: Parser-file-> "
                                         "The same connection appears more "
                                         "than once"
                                         )

                    set_zones.add(frozenset((zone_a, zone_b)))

                    obj_zone_a = graph.dict_zones[zone_a]
                    obj_zone_b = graph.dict_zones[zone_b]

                    max_link_capacity = 1
                    if len(info) > 2:
                        try:
                            key, value = info[2].split("=")
                            if key == 'max_link_capacity':
                                max_link_capacity = int(value)
                            else:
                                raise ParseError(f"Line {line_num}: "
                                                 "incorrectly written maxlink "
                                                 "capacity")
                        except ValueError as e:
                            raise ValueError(f"Line {line_num}: "
                                             "Max_link_capacity"
                                             f" is not value, value: {e}"
                                             )

                        if max_link_capacity <= 0:
                            raise ValueError(f"Line {line_num}: "
                                             "Max_link_capacity <= 0, "
                                             "value: "
                                             f"{max_link_capacity}"
                                             )

                    connection = Connection(
                        obj_zone_a,
                        obj_zone_b,
                        0,
                        max_link_capacity
                        )

                    graph.add_adjacency(connection)
            if empty:
                raise ValueError(f"Empty file: {file}")

            if graph.start_zone is None:
                raise ParseError("Parser-file: no start_hub found")
            if graph.end_zone is None:
                raise ParseError("Parser-file: no end_hub found")
            if not graph.dict_adjacency:
                raise ParseError(f"line {line_num}: Parser-> no "
                                 "connections found in file")
        return graph
