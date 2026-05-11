# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  visualizer.py                                     :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/11 13:34:02 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/11 14:20:15 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    # from graph import Graph
    # from simulator import Simulator
    import arcade
except ImportError as e:
    print(f"[ERROR] visualizer.py: {e}")
    sys.exit()


class Visualizer(arcade.Window):
    """class designed for viewing drones"""
    def __init__(self, graph, stock_turn) -> None:

        super().__init__(800, 600, "Fly-in Simulator")
        self.graph = graph
        self.stock_turn = stock_turn

    def on_draw(self) -> None:

        """dessiner les zones, connexions, drones"""
        pass

    def on_key_press(self, key, modifiers) -> None:

        """avancer d'un tour avec espace"""
        pass