# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  zone.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 17:33:51 by cehenrot        #+#    #+#               #
#  Updated: 2026/04/28 15:18:38 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from enum import Enum


class ZoneType(Enum):
    normal = 'normal'
    blocked = 'blocked'
    restricted = 'restricted'
    priority = 'priority'


class Zone():
    '''Represents a zone/hub in the drone network.'''

    def __init__(self, name: str, x: int, y: int,
                 zone_type: ZoneType = ZoneType.normal,
                 color: str | None = None, max_drone: int = 1) -> None:

        '''Initialize a Zone with its attributes.'''

        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drone = max_drone
