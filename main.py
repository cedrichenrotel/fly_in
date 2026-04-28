# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  main.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42lyon.fr>     +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 15:03:24 by cehenrot        #+#    #+#               #
#  Updated: 2026/04/27 17:18:16 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys
from file_parser import parse_file


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
