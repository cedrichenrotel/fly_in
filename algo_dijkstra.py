# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  algo_dijkstra.py                                  :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/30 14:27:33 by cehenrot        #+#    #+#               #
#  Updated: 2026/04/30 16:20:51 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from graph import Graph
except ImportError as e:
    print(f"[ERROR] graph.py: {e}")
    sys.exit()

"""Dijkstra's algorithm"""

def initialize(graph, start):

    """
    Preparing the three structures before the algorithm starts.
        - distances -> the minimum known distance required to reach each area.
        - predecessors -> stores the areas that have already been visited in 
          order to reach the current area.
        - unvisited -> not yet explored
    """
    distances = {vertex: sys.maxsize for vertex in graph.dict_zones}
    distances[start] = 0
    predecessors = {vertex: None for vertex in graph.dict_zones}
    unvisited = set(graph.dict_zones)
    return distances, predecessors, unvisited


