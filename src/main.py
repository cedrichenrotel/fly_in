import sys

try:
    from visualizer import Window
    import arcade
except ImportError as e:
    print(e)
    sys.exit()


def main() -> None:

    window = Window()
    arcade.run()

    turns = 0
    if window.simulator:
        for turn in window.simulator.stock_turns:
            print(f"turn {turns}: {', '.join(turn)}")
            print()
            turns += 1


if __name__ == "__main__":
    main()
