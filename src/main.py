import sys

try:
    from visualizer import Window
    import arcade
except ImportError as e:
    print(e)
    sys.exit()


def main() -> None:

    try:
        window = Window()
        arcade.run()

        if window.simulator:
            for turn in window.simulator.stock_turns:
                print(' '.join(turn))
                print()
    except KeyboardInterrupt:
        print("[WARNING]: The programme was stopped manually")
        sys.exit()


if __name__ == "__main__":
    main()
