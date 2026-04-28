# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  connection.py                                     :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:37:58 by cehenrot        #+#    #+#               #
#  Updated: 2026/04/28 17:00:32 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from zone import Zone
except ImportError as e:
    print(f"[ERROR] connection.py: {e}")
    sys.exit()


class Connection():

    '''Represents a bidirectional connection between two zones.'''

    def __init__(self, zone_a: Zone, zone_b: Zone, current_drone: int = 0,
                 max_link_capacity: int = 1) -> None:

        '''Initialize a Zone with its attributes.'''

        self.zone_a = zone_a
        self.zone_b = zone_b
        self.current_drone = current_drone
        self.max_link_capacity = max_link_capacity
