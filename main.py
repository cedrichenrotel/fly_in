# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  main.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 15:03:24 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/05 08:11:47 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys
from file_parser import parse_file
from simulator import Simulator


def main() -> None:

    try:
        if len(sys.argv) != 2:
            raise Exception("[WARNING]: Incorrect number of arguments")
        file = sys.argv[1]
        graph = parse_file(file)
    except Exception as e:
        print(f"[ERROR]: {e}")


if __name__ == "__main__":
    main()
