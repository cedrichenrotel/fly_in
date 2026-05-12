# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  visualizer.py                                     :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/11 13:34:02 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/12 16:13:48 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from graph import Graph
    # from simulator import Simulator
    import arcade
except ImportError as e:
    print(f"[ERROR] visualizer.py: {e}")
    sys.exit()

MARGIN = 50
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Fly-in Simulator"


class Visualizer(arcade.Window):

    """class designed for viewing drones"""
    def __init__(self, graph: Graph, stock_turn: int) -> None:

        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE
            )

        self.graph = graph
        self.stock_turn: list[list[str]] = stock_turn
        self.current_turn = 0

    def to_pixel(self, x, y, max_x, max_y):
        x_pixel = MARGIN + (x - min_x) * ((SCREEN_WIDTH - 2 * MARGIN) / max_x)
        y_pixel = MARGIN + (y - min_y) * ((SCREEN_HEIGHT - 2 * MARGIN) / max_y)
        return x_pixel, y_pixel

    def on_draw(self) -> None:

        """dessiner les zones, connexions, drones de 0"""

        self.clear()
        current_turn = self.stock_turn[self.current_turn]

        min_x = min(zone.x for zone in self.graph.dict_zones.values()) or 1
        min_y = max(zone.y for zone in self.graph.dict_zones.values()) or 1
        max_x = (max(zone.x for zone in self.graph.dict_zones.values()) - min_x
                 or 1)
        max_y = (max(zone.y for zone in self.graph.dict_zones.values()) - min_y
                 or 1)

        for zone in self.graph.dict_zones.values():
            x_pixel, y_pixel = self.to_pixel(zone.x, zone.y, max_x, max_y)
            color = (
                getattr(arcade.color, zone.color.upper(), arcade.color.WHITE)
                if zone.color else arcade.color.WHITE
            )
            arcade.draw_ellipse_filled(x_pixel, y_pixel, 40, 30, color)
        """display of drones on the map, turn by turn """
        for drone in current_turn:
            zone_name = drone.split('-', 1)[1]
            zone = self.graph.dict_zones[zone_name]

            x_pixel, y_pixel = self.to_pixel(zone.x, zone.y, max_x, max_y)

            arcade.draw_line(x_pixel + 10, y_pixel, x_pixel - 10, y_pixel,
                             arcade.color.BLACK, 3)
            arcade.draw_line(x_pixel, y_pixel + 10, x_pixel, y_pixel - 10,
                             arcade.color.BLACK, 3)

        """Display connections by area"""
        drawn = set()
        """drawn stores already drawn connections
            frozenset ignores order: (a,b) == (b,a) to avoid drawing the
            same line twice"""
        for connections in self.graph.dict_adjacency.values():
            for connection in connections:
                pair = frozenset((connection.zone_a.name,
                                  connection.zone_b.name))
                if pair in drawn:
                    continue
                drawn.add(pair)
                xa, ya = self.to_pixel(connection.zone_a.x, connection.zone_a.y,
                                       max_x, max_y)
                xb, yb = self.to_pixel(connection.zone_b.x, connection.zone_b.y,
                                       max_x, max_y)
                arcade.draw_line(xa, ya, xb, yb, arcade.color.GRAY, 2)


    def on_key_press(self, key: dict, modifiers) -> None:

        """avancer d'un tour avec espace"""
        if key == arcade.key.SPACE:
            print(f"espace! tour: {self.current_turn}")
            if self.current_turn < len(self.stock_turn) - 1:
                self.current_turn += 1  

        elif key == arcade.key.UP:
            print("Touche haut pressée")
        elif key == arcade.key.DOWN:
            print("Touche bas pressée")

    # def on_update(self, delta_time):
