# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  visualizer.py                                     :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: cehenrot <cehenrot@student.42.fr>         +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/11 13:34:02 by cehenrot        #+#    #+#               #
#  Updated: 2026/05/18 11:48:07 by cehenrot        ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import sys

try:
    from collections import defaultdict
    from file_parser import parse_file
    from simulator import Simulator
    from graph import Graph
    from pathlib import Path
    import arcade
except ImportError as e:
    print(f"[ERROR] visualizer.py: {e}")
    sys.exit()

MARGIN: int = 50
SCREEN_WIDTH: int = 1000
SCREEN_HEIGHT: int = 800
SCREEN_TITLE: str = "Fly-in Simulator"
PADDING: int = 20
BTN_W: int = 200
BTN_H: int = 50


class MenuView(arcade.View):

    def __init__(self) -> None:

        """creating the menu from the menu card"""
        super().__init__()
        self.list_maps: list[Path] = self.get_map_file("maps")
        self.select_map: int = 0
        self.maps_diff: list[dict] = self.choice_diff_maps()
        self.menu = arcade.load_texture("image/menu.png")
        self.positions = self.calculate_positions(list(self.maps_diff.keys()))
        self.selected_diff: str = ""

    def get_map_file(self, directory: str = "maps") -> list[Path]:

        """Retrieves a list of all .txt files in the specified folder."""
        folder = Path(directory)
        if not folder.exists():
            print(f"[ERROR] The folder “{directory}” cannot be found.")
            return []

        maps = list(folder.glob("**/*.txt"))
        return maps

    def choice_diff_maps(self) -> list[dict]:

        """Storing .txt files by difficulty"""
        dict_maps = defaultdict(list)

        for path_file in self.list_maps:
            difficulty = path_file.parent.name
            dict_maps[difficulty].append(path_file)
        return dict_maps

    def calculate_positions(self, items: list) -> dict[str, tuple[int, int,
                                                                  int]]:

        """This method allows you to centre text """
        position: dict[str, tuple[int, int, int]] = {}
        espacement = SCREEN_HEIGHT // (len(items) + 1)

        for i, difficulty in enumerate(items):
            label = (difficulty.stem if hasattr(difficulty, 'stem')
                     else str(difficulty))
            text_width = (arcade.Text(label, 0, 0, arcade.color.GOLD, 25)
                          .content_width)
            y = SCREEN_HEIGHT - espacement * (i + 1)
            x = SCREEN_WIDTH // 2
            position[difficulty] = (x, y, text_width + PADDING)

        return position

    def on_draw(self) -> None:

        self.window.clear()
        arcade.draw_texture_rect(
            self.menu,
            arcade.LRBT(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
            )
        if not self.selected_diff:
            for difficulty, _ in self.maps_diff.items():
                x, y, btn_w = self.positions[difficulty]
                arcade.draw_text(difficulty, x, y, arcade.color.GOLD, 25,
                                 anchor_x="center", anchor_y="center")
                arcade.draw_rect_outline(
                    arcade.LRBT(x - btn_w // 2, x + btn_w // 2,
                                y - BTN_H // 2, y + BTN_H // 2),
                    arcade.color.GOLD,
                    2,
                )
        else:
            choice_positions = self.maps_diff[self.selected_diff]
            map_positions = self.calculate_positions(choice_positions)
            for map in self.maps_diff[self.selected_diff]:
                x, y, btn_w = map_positions[map]
                arcade.draw_text(map.stem, x, y, arcade.color.GOLD, 25,
                                 anchor_x="center", anchor_y="center")
                arcade.draw_rect_outline(
                    arcade.LRBT(x - btn_w // 2, x + btn_w // 2,
                                y - BTN_H // 2, y + BTN_H // 2),
                    arcade.color.GOLD,
                    2,
                )

    def on_mouse_press(self, x: int, y: int, _: int, __: int) -> None:
        """This function allows you to click on the difficulty level in
            the menu"""
        if not self.selected_diff:
            for difficulty, (px, py, _) in self.positions.items():
                if abs(x - px) < 100 and abs(y - py) < 20:
                    self.selected_diff = difficulty
        else:
            choice_positions = self.maps_diff[self.selected_diff]
            map_positions = self.calculate_positions(choice_positions)
            for map_file in self.maps_diff[self.selected_diff]:
                px, py, _ = map_positions[map_file]
                if abs(x - px) < 100 and abs(y - py) < 20:
                    graph = parse_file(map_file)
                    simulator = Simulator(graph)
                    simulator.init_drone()
                    simulator.init_run()
                    simulator.run_drones()
                    simulationview = SimulationView(graph,
                                                    simulator.stock_turns)
                    self.window.show_view(simulationview)


class Window(arcade.Window):

    def __init__(self) -> None:

        """allows you to perform two operations:
        Create the Arcade window (size, title)
        Display the first view (the menu)"""
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE
            )
        self.show_view(MenuView())


class SimulationView(arcade.View):

    def __init__(self, graph: Graph, stock_turn: list[list[str]]) -> None:

        """class designed for viewing drones"""
        super().__init__()
        self.graph = graph
        self.sprite_list = arcade.SpriteList()
        self.stock_turn = stock_turn
        self.current_turn: int = 0
        self.turn_text: object = arcade.Text(
            "Tour: 0",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            16
            )
        self.simulation_finished: bool = False
        self.valid_text: object = arcade.Text(
            "",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.GOLD,
            50,
            anchor_x="center",
            anchor_y="center"
            )
        self.min_x = min(zone.x for zone in self.graph.dict_zones.values())
        self.min_y = min(zone.y for zone in self.graph.dict_zones.values())
        self.max_x = (max(zone.x for zone in self.graph.dict_zones.values())
                      - self.min_x or 1)
        self.max_y = (max(zone.y for zone in self.graph.dict_zones.values())
                      - self.min_y or 1)

        self.time_since_last_turn = 0.0
        self.turn_speed = 0.5
        self.drone_positions: dict = {}
        self.target_positions: dict = {}
        self.background = arcade.load_texture("image/background.png")
        self.drone_texture = arcade.load_texture("image/drone.png")

        self.drone_sprites: dict[str, arcade.Sprite] = {}
        for i in range(1, self.graph.nb_drone + 1):
            sprite = arcade.Sprite()
            sprite.texture = self.drone_texture
            sprite.scale = 0.035
            self.drone_sprites[f"D{i}"] = sprite

            x_pixel, y_pixel = self.to_pixel(
                self.graph.start_zone.x,
                self.graph.start_zone.y,
                self.min_x,
                self.min_y,
                self.max_x,
                self.max_y
                )
            sprite.center_x = x_pixel
            sprite.center_y = y_pixel

        for sprite in self.drone_sprites.values():
            self.sprite_list.append(sprite)

    def to_pixel(self, x, y, min_x, min_y, max_x, max_y):

        x_pixel = MARGIN + (x - min_x) * ((SCREEN_WIDTH - 2 * MARGIN) / max_x)
        y_pixel = MARGIN + (y - min_y) * ((SCREEN_HEIGHT - 2 * MARGIN) / max_y)
        return x_pixel, y_pixel

    def draw_zones(self) -> None:

        """display the areas in these colours"""
        for zone in self.graph.dict_zones.values():
            x_pixel, y_pixel = self.to_pixel(
                zone.x,
                zone.y,
                self.min_x,
                self.min_y,
                self.max_x,
                self.max_y
                )
            color = (
                getattr(arcade.color, zone.color.upper(), arcade.color.WHITE)
                if zone.color else arcade.color.WHITE
            )
            arcade.draw_ellipse_filled(x_pixel, y_pixel, 40, 30, color)

    def draw_connections(self) -> None:

        """Display connections by area,
            drawn stores already drawn connections
            frozenset ignores order: (a,b) == (b,a) to avoid drawing the
            same line twice"""
        drawn = set()

        for connections in self.graph.dict_adjacency.values():
            for connection in connections:
                pair = frozenset((connection.zone_a.name,
                                  connection.zone_b.name))
                if pair in drawn:
                    continue
                drawn.add(pair)
                xa, ya = self.to_pixel(
                    connection.zone_a.x,
                    connection.zone_a.y,
                    self.min_x,
                    self.min_y,
                    self.max_x,
                    self.max_y
                    )
                xb, yb = self.to_pixel(
                    connection.zone_b.x,
                    connection.zone_b.y,
                    self.min_x,
                    self.min_y,
                    self.max_x,
                    self.max_y
                    )
                arcade.draw_line(xa, ya, xb, yb, arcade.color.GRAY, 5)

    def draw_drones(self) -> None:

        """display of drones on the map, turn by turn """
        self.sprite_list.draw()

    def on_draw(self) -> None:

        """dessiner les zones, connexions, drones de 0"""
        self.window.clear()
        arcade.draw_texture_rect(self.background,
                                 arcade.LRBT(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
                                 )
        self.turn_text.value = f"tour: {self.current_turn}"
        self.turn_text.draw()
        self.draw_connections()
        self.draw_zones()
        self.draw_drones()

        if self.simulation_finished is True:
            self.valid_text.value = "-- FINISH --"
            self.valid_text.draw()

    def on_update(self, delta_time) -> None:

        """The entire logic for updating the simulator.
            param delt a_time: Time elapsed since the last update
            (in seconds).
            Typically, around 1/60th of a second."""
        current_turn = self.stock_turn[self.current_turn]
        all_arrived = True

        for drone in current_turn:
            zone_name = drone.split('-', 1)[1]
            if '-' in zone_name:
                name_a, name_b = zone_name.split('-')
                zone_a = self.graph.dict_zones[name_a]
                zone_b = self.graph.dict_zones[name_b]

                target_x = (zone_a.x + zone_b.x) / 2
                target_y = (zone_a.y + zone_b.y) / 2
            else:
                zone = self.graph.dict_zones[zone_name]
                target_x = zone.x
                target_y = zone.y

            self.target_positions[drone.split('-', 1)[0]] = (
                (target_x,
                 target_y)
                 )

        for drone_name, sprite in self.drone_sprites.items():
            if drone_name in self.target_positions:
                target = self.target_positions[drone_name]
                x_pixel, y_pixel = self.to_pixel(target[0],
                                                 target[1],
                                                 self.min_x, self.min_y,
                                                 self.max_x, self.max_y)
                sprite.center_x += (x_pixel - sprite.center_x) * 0.1
                sprite.center_y += (y_pixel - sprite.center_y) * 0.1
                distance = (((sprite.center_x - x_pixel)**2 +
                             (sprite.center_y - y_pixel)**2) ** 0.5)
                if distance > 2.0:
                    all_arrived = False

        if all_arrived:
            if self.current_turn < len(self.stock_turn) - 1:
                self.current_turn += 1
            else:
                self.simulation_finished = True

    def on_key_press(self, key: int, _) -> None:

        if key == arcade.key.ESCAPE:
            arcade.exit()
