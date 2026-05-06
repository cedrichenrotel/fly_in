# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  drone.py                                          :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:31:49 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/06 09:28:47 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from zone import Zone
except ImportError as e:
    print(f"[ERROR] drone.py: {e}")
    sys.exit()


class Drone():
    """allows the system to send information regarding the drone’s current
    position and whether it has successfully reached its destination"""

    def __init__(self, drone_id: str, current_zone: Zone,
                 is_arrived: bool = False) -> None:
        self.drone_id = drone_id
        self.current_zone = current_zone
        self.is_arrived = is_arrived

    """Check the drone's position and see if it has reached its destination"""
    def drone_move(self, zone: Zone, hub_end: Zone) -> None:
        self.current_zone = zone
        if self.current_zone.name == hub_end.name:
            self.is_arrived = True
        else:
            self.is_arrived = False
