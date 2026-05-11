# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  visualizer.py                                     :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/11 13:34:02 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/11 18:56:35 by cehenrot        ###   ########.fr        #
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

    def on_draw(self) -> None:

        """dessiner les zones, connexions, drones de 0"""
        self.clear()
        current_turn = self.stock_turn[self.current_turn]
        # arcade.draw_text(current_turn, 100, 300,
        #                  arcade.color.WHITE, 24)
        max_x = max(zone.x for zone in self.graph.dict_zones.values())
        max_y = max(zone.y for zone in self.graph.dict_zones.values())

        for zone in self.graph.dict_zones.values():
            x_pixel = MARGIN + zone.x * ((SCREEN_WIDTH - 2 * MARGIN) / max_x)
            y_pixel = MARGIN + zone.y * ((SCREEN_HEIGHT - 2 * MARGIN) / max_y)

    def on_key_press(self, key: dict, modifiers) -> None:

        """avancer d'un tour avec espace"""
        if key == arcade.key.SPACE:

            if self.current_turn < len(self.stock_turn) - 1:
                self.current_turn += 1
                self.on_draw()

        elif key == arcade.key.UP:
            print("Touche haut pressée")
        elif key == arcade.key.DOWN:
            print("Touche bas pressée")

    # def on_update(self, delta_time):
