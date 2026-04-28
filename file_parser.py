# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  file_parser.py                                    :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 15:02:34 by cehenrot        #+#    #+#               #
#  Updated: 2026/04/27 17:38:30 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from drone import
from zone import
from graph import
from simulator import
from connection import 


def parse_file(file: str) -> 'graph':
    with open(file) as f:
        fd = f.read()
        if not fd:
            raise Exception(f"[WARNING]: Empty file: {file}")
            
    return 