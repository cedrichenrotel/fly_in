# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  main.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/04/27 15:03:24 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/06 13:15:02 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from file_parser import parse_file
    from simulator import Simulator
except ImportError as e:
    print(f"[ERROR] main.py: {e}")
    sys.exit()


def main() -> None:

    try:
        if len(sys.argv) != 2:
            raise Exception("[WARNING]: Incorrect number of arguments")
        file = sys.argv[1]
        graph = parse_file(file)

        simulator = Simulator(graph)
        simulator.init_drone()
        simulator.init_run()
        simulator.run_drones()

        print("___SIMULATION RESULTS___")
        print(f"\nNumber of turn: {simulator.nb_turn}")
        print()

        for turn in simulator.stock_turns:
            print(turn)

    except Exception as e:
        print(f"[ERROR]: main.py -> {e}")


if __name__ == "__main__":
    main()
