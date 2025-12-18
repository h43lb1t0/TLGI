import pygame
import sys
from nodes import (
    InputNode,
    OutputNode,
    AndNode,
    OrNode,
    NotNode,
    NandNode,
    NorNode,
    XorNode,
    XnorNode,
)
import levels
import itertools
import json
import os
from enum import Enum

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
LINK_COLOR = (200, 200, 200)

NODE_TYPES = {
    "AndNode": AndNode,
    "OrNode": OrNode,
    "NotNode": NotNode,
    "NandNode": NandNode,
    "NorNode": NorNode,
    "XorNode": XorNode,
    "XnorNode": XnorNode,
    "InputNode": InputNode,
    "OutputNode": OutputNode,
}


class GameState(Enum):
    MENU = 0
    PLAYING = 1
    LEVEL_SELECT = 2


def draw_bezier(surface, start_pos, end_pos, color=LINK_COLOR):
    # Cubic Bezier
    p0 = start_pos
    p3 = end_pos
    # Control points
    dist = abs(p3[0] - p0[0]) * 0.5
    p1 = (p0[0] + dist, p0[1])
    p2 = (p3[0] - dist, p3[1])

    # Draw using approximated small lines
    points = []
    steps = 20
    for t_step in range(steps + 1):
        t = t_step / steps
        # Bezier formula
        x = (
            (1 - t) ** 3 * p0[0]
            + 3 * (1 - t) ** 2 * t * p1[0]
            + 3 * (1 - t) * t**2 * p2[0]
            + t**3 * p3[0]
        )
        y = (
            (1 - t) ** 3 * p0[1]
            + 3 * (1 - t) ** 2 * t * p1[1]
            + 3 * (1 - t) * t**2 * p2[1]
            + t**3 * p3[1]
        )
        points.append((x, y))

    if len(points) > 1:
        pygame.draw.lines(surface, color, False, points, 3)


class Button:
    def __init__(self, x, y, w, h, text, callback, color=(70, 70, 70), disabled=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = (
            min(color[0] + 20, 255),
            min(color[1] + 20, 255),
            min(color[2] + 20, 255),
        )
        self.disabled_color = (40, 40, 40)
        self.hovered = False
        self.disabled = disabled

    def check_hover(self, pos):
        if self.disabled:
            return
        self.hovered = self.rect.collidepoint(pos)

    def handle_click(self, pos):
        if self.disabled:
            return False
        if self.rect.collidepoint(pos):
            self.callback()
            return True
        return False

    def render(self, screen, font):
        color = (
            self.disabled_color
            if self.disabled
            else (self.hover_color if self.hovered else self.color)
        )
        pygame.draw.rect(screen, color, self.rect, border_radius=5)

        text_color = (100, 100, 100) if self.disabled else TEXT_COLOR
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


def draw_grid(surface, color=(40, 40, 40), cell_size=40):
    width, height = surface.get_size()
    for x in range(0, width, cell_size):
        pygame.draw.line(surface, color, (x, 0), (x, height))
    for y in range(0, height, cell_size):
        pygame.draw.line(surface, color, (0, y), (width, y))


def try_connect_node(connecting_node, nodes, mouse_pos):
    """
    Attempts to connect the connecting_node to an input port of another node
    at the given mouse_pos.
    Returns True if a drop happened (successful connection or blocked),
    False if no port was targeted.
    """
    for node in nodes:
        if node != connecting_node:
            for port in node.input_ports:
                if port["rect"].collidepoint(mouse_pos):
                    # Rule: Only one connection per input
                    if port["connected_node"] is None:
                        port["connected_node"] = connecting_node
                        return True
                    else:
                        # Port occupied, do not overwrite
                        return True  # drop handled (rejected)
    return False


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        # Use (0,0) and FULLSCREEN to adapt to native resolution
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Logic Nodes")
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.SysFont("Arial", 24)
        self.large_font = pygame.font.SysFont("Arial", 36)
        self.title_font = pygame.font.SysFont("Arial", 72, bold=True)

        self.state = GameState.MENU

        self.nodes = []
        self.buttons = []

        self.current_level_idx = 0
        self.max_unlocked_idx = 0
        self.solutions = {}  # { str(level_id): { 'user_nodes': [], 'connections': [] } }

        self.simulating = False
        self.message = ""
        self.message_color = (255, 255, 255)

        # Interaction state
        self.active_node = None
        self.drag_offset = (0, 0)
        self.connecting_node = None

        self.save_file = "save_game.json"
        self.load_progress()

        self.setup_menu()

    def load_progress(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as f:
                    data = json.load(f)
                    self.max_unlocked_idx = data.get("max_unlocked", 0)
                    self.solutions = data.get("solutions", {})
            except:
                pass

    def save_progress(self):
        with open(self.save_file, "w") as f:
            json.dump(
                {"max_unlocked": self.max_unlocked_idx, "solutions": self.solutions},
                f,
                indent=2,
            )

    def save_current_level_solution(self):
        # Don't save playground state
        if self.current_level_idx == -1:
            return

        level = self.get_current_level()
        if not level:
            return

        input_nodes = [n for n in self.nodes if isinstance(n, InputNode)]
        output_nodes = [n for n in self.nodes if isinstance(n, OutputNode)]
        user_nodes = [
            n for n in self.nodes if n not in input_nodes and n not in output_nodes
        ]

        # Sort fixed nodes to ensure consistent indices
        input_nodes.sort(key=lambda n: n.rect.y)
        output_nodes.sort(key=lambda n: n.rect.y)

        all_ordered = input_nodes + output_nodes + user_nodes
        node_to_idx = {n: i for i, n in enumerate(all_ordered)}

        # Serialize User Nodes
        serialized_nodes = []
        for n in user_nodes:
            serialized_nodes.append(
                {"type": n.__class__.__name__, "x": n.rect.x, "y": n.rect.y}
            )

        # Serialize Connections
        connections = []
        for target_node in all_ordered:
            for port_idx, port in enumerate(target_node.input_ports):
                source_node = port["connected_node"]
                if source_node:
                    connections.append(
                        {
                            "from_idx": node_to_idx[source_node],
                            "to_idx": node_to_idx[target_node],
                            "port_idx": port_idx,
                        }
                    )

        self.solutions[str(level.id)] = {
            "user_nodes": serialized_nodes,
            "connections": connections,
        }
        self.save_progress()

    def get_current_level(self):
        if self.current_level_idx == -1:
            return levels.PLAYGROUND_LEVEL
        if 0 <= self.current_level_idx < len(levels.LEVELS):
            return levels.LEVELS[self.current_level_idx]
        return None

    # --- Menu Methods ---
    def setup_menu(self):
        self.state = GameState.MENU
        self.buttons = []

        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2

        # Play / Continue Button
        play_text = "Continue" if self.max_unlocked_idx > 0 else "New Game"
        self.buttons.append(
            Button(cx - 100, cy - 50, 200, 50, play_text, self.action_play_latest)
        )

        # Level Select
        self.buttons.append(
            Button(cx - 100, cy + 20, 200, 50, "Levels", self.action_go_to_levels)
        )

        # Quit
        self.buttons.append(
            Button(cx - 100, cy + 160, 200, 50, "Quit", self.action_quit)
        )

        # Playground
        self.buttons.append(
            Button(cx - 100, cy + 90, 200, 50, "Playground", self.action_playground)
        )

    def action_play_latest(self):
        self.current_level_idx = self.max_unlocked_idx
        if self.current_level_idx >= len(levels.LEVELS):
            self.current_level_idx = len(levels.LEVELS) - 1
        self.start_level()

    def action_go_to_levels(self):
        self.setup_level_select()

    def action_quit(self):
        self.running = False

    def action_playground(self):
        self.current_level_idx = -1
        self.start_level()

    # --- Level Select Methods ---
    def setup_level_select(self):
        self.state = GameState.LEVEL_SELECT
        self.buttons = []

        cx = self.screen.get_width() // 2

        # Back Button
        self.buttons.append(Button(20, 20, 100, 40, "Back", self.setup_menu))

        # Grid of Levels
        cols = 5
        start_x = 100
        start_y = 150
        w, h = 180, 80
        gap_x, gap_y = 20, 20

        for i, level in enumerate(levels.LEVELS):
            col = i % cols
            row = i // cols
            x = start_x + col * (w + gap_x)
            y = start_y + row * (h + gap_y)

            is_locked = i > self.max_unlocked_idx
            text = f"{level.id}. {level.title}"

            # Helper for closure binding
            def make_level_loader(idx):
                return lambda: self.select_level(idx)

            btn = Button(
                x,
                y,
                w,
                h,
                text,
                make_level_loader(i),
                color=(50, 100, 50) if not is_locked else (50, 50, 50),
                disabled=is_locked,
            )
            self.buttons.append(btn)

    def select_level(self, idx):
        self.current_level_idx = idx
        self.start_level()

    # --- Gameplay Methods ---
    def start_level(self):
        self.state = GameState.PLAYING
        self.simulating = False
        self.nodes.clear()
        self.message = ""
        self.show_hint = False

        level = self.get_current_level()
        if not level:
            return

        # Setup Inputs
        start_y = 200
        spacing = 150
        inputs = []
        for i in range(level.input_count):
            node = InputNode(250, start_y + i * spacing)
            node.title = f"In {chr(65 + i)}"
            inputs.append(node)
            self.nodes.append(node)

        # Setup Outputs
        outputs = []
        for i in range(level.output_count):
            node = OutputNode(1000, 300 + i * 150)
            if level.output_labels and i < len(level.output_labels):
                node.title = level.output_labels[i]
            elif level.output_count > 1:
                node.title = f"Out {i}"
            outputs.append(node)
            self.nodes.append(node)

        # Try Loading Solution
        if str(level.id) in self.solutions:
            sol = self.solutions[str(level.id)]
            user_nodes = []

            # Restore User Nodes
            for n_data in sol.get("user_nodes", []):
                cls = NODE_TYPES.get(n_data["type"])
                if cls:
                    new_node = cls(n_data["x"], n_data["y"])
                    user_nodes.append(new_node)
                    self.nodes.append(new_node)

            # Restore Connections
            all_ordered = inputs + outputs + user_nodes
            for conn in sol.get("connections", []):
                from_idx = conn["from_idx"]
                to_idx = conn["to_idx"]
                port_idx = conn["port_idx"]

                if 0 <= from_idx < len(all_ordered) and 0 <= to_idx < len(all_ordered):
                    src = all_ordered[from_idx]
                    dst = all_ordered[to_idx]
                    if 0 <= port_idx < len(dst.input_ports):
                        dst.input_ports[port_idx]["connected_node"] = src

        self.update_game_buttons()

    def toggle_hint(self):
        self.show_hint = not self.show_hint
        self.update_game_buttons()

    def update_game_buttons(self):
        self.buttons = []
        y_offset = 20

        level = self.get_current_level()
        if not level:
            return

        # Menu/Back
        self.buttons.append(Button(20, y_offset, 140, 40, "Menu", self.setup_menu))
        y_offset += 50

        # Hint Button
        if level.hint:
            hint_text = "Hide Hint" if self.show_hint else "Show Hint"
            self.buttons.append(
                Button(
                    20,
                    y_offset,
                    140,
                    40,
                    hint_text,
                    self.toggle_hint,
                    color=(100, 100, 50),
                )
            )
            y_offset += 50

        # Node spawning buttons
        for node_cls in level.allowed_nodes:
            name = node_cls.__name__.replace("Node", "")
            btn_text = f"Add {name}"
            self.buttons.append(
                Button(20, y_offset, 140, 40, btn_text, self.make_spawn_func(node_cls))
            )
            y_offset += 50

        y_offset += 30

        # Sim Controls
        self.buttons.append(
            Button(20, y_offset, 140, 40, "Play", self.start_sim, (50, 150, 50))
        )
        y_offset += 50
        self.buttons.append(
            Button(20, y_offset, 140, 40, "Stop", self.stop_sim, (150, 50, 50))
        )
        y_offset += 50

        self.buttons.append(
            Button(
                20, y_offset, 140, 40, "Verify", self.run_verification, (50, 50, 150)
            )
        )
        y_offset += 50

        # Level Nav
        h = self.screen.get_height()
        self.buttons.append(
            Button(
                20,
                h - 60,
                60,
                40,
                "<",
                self.prev_level,
                disabled=(self.current_level_idx <= 0),
            )
        )

        next_disabled = (
            (self.current_level_idx >= self.max_unlocked_idx)
            or (self.current_level_idx >= len(levels.LEVELS) - 1)
            or (self.current_level_idx == -1)
        )
        self.buttons.append(
            Button(100, h - 60, 60, 40, ">", self.next_level, disabled=next_disabled)
        )

    def make_spawn_func(self, node_cls):
        def spawn():
            self.nodes.append(node_cls(500, 500))

        return spawn

    def start_sim(self):
        self.simulating = True

    def stop_sim(self):
        self.simulating = False

    def next_level(self):
        if self.current_level_idx < len(levels.LEVELS) - 1:
            if self.current_level_idx < self.max_unlocked_idx:
                self.current_level_idx += 1
                self.start_level()

    def prev_level(self):
        if self.current_level_idx > 0:
            self.current_level_idx -= 1
            self.start_level()

    def run_verification(self):
        level = self.get_current_level()
        if not level:
            return

        if not level.check_func:
            self.message = "No check function for this level."
            return

        input_nodes = [n for n in self.nodes if isinstance(n, InputNode)]
        output_nodes = [n for n in self.nodes if isinstance(n, OutputNode)]

        input_nodes.sort(key=lambda n: n.rect.y)
        output_nodes.sort(key=lambda n: n.rect.y)

        if len(input_nodes) != level.input_count:
            self.message = "Error: Input count mismatch."
            self.message_color = (255, 100, 100)
            return

        if len(output_nodes) != level.output_count:
            self.message = (
                f"Error: Output count mismatch. Expected {level.output_count}."
            )
            self.message_color = (255, 100, 100)
            return

        # 0. Capture Current State
        current_input_values = [n.value for n in input_nodes]

        # 2. Run Exhaustive Verification
        combinations = list(itertools.product([False, True], repeat=level.input_count))

        for inputs in combinations:
            for i, val in enumerate(inputs):
                input_nodes[i].value = val

            for _ in range(50):
                for node in self.nodes:
                    node.process_logic()

            actual_outputs = [n.value for n in output_nodes]
            expected = level.check_func(inputs)

            if not isinstance(expected, (list, tuple)):
                expected = [expected]
            else:
                expected = list(expected)

            if actual_outputs != expected:
                self.message = f"Failed at inputs: {inputs}. Got {actual_outputs}, expected {expected}."
                self.message_color = (255, 100, 100)
                # Restore state before returning
                for i, val in enumerate(current_input_values):
                    input_nodes[i].value = val
                for _ in range(50):
                    for node in self.nodes:
                        node.process_logic()
                return

        # Restore state after successful verification
        for i, val in enumerate(current_input_values):
            input_nodes[i].value = val
        for _ in range(50):
            for node in self.nodes:
                node.process_logic()

        self.message = "Level Complete! Logic Verified."
        self.message_color = (100, 255, 100)

        # Save Solution
        self.save_current_level_solution()

        if self.current_level_idx == self.max_unlocked_idx:
            self.max_unlocked_idx += 1
            self.save_progress()
            self.update_game_buttons()

    # --- Main Loop Methods ---
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.save_current_level_solution()
                        self.setup_menu()
                    elif self.state == GameState.LEVEL_SELECT:
                        self.setup_menu()
                    else:
                        self.running = False

                elif event.key == pygame.K_DELETE and self.state == GameState.PLAYING:
                    to_remove = [
                        n
                        for n in self.nodes
                        if n.selected and not isinstance(n, (InputNode, OutputNode))
                    ]
                    for n in to_remove:
                        self.nodes.remove(n)
                        for other in self.nodes:
                            for port in other.input_ports:
                                if port["connected_node"] == n:
                                    port["connected_node"] = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # UI Buttons
                    ui_handled = False
                    for btn in self.buttons:
                        if btn.handle_click(mouse_pos):
                            ui_handled = True
                            break
                    if ui_handled:
                        continue

                    if self.state == GameState.PLAYING:
                        self.handle_game_click(mouse_pos)

                elif event.button == 3 and self.state == GameState.PLAYING:
                    for node in reversed(self.nodes):
                        if node.rect.collidepoint(mouse_pos):
                            if isinstance(node, InputNode):
                                node.value = not node.value
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.state == GameState.PLAYING:
                    if self.connecting_node:
                        if try_connect_node(
                            self.connecting_node, self.nodes, mouse_pos
                        ):
                            pass
                        self.connecting_node = None

                    if self.active_node:
                        self.active_node.dragging = False
                        self.active_node = None

            elif event.type == pygame.MOUSEMOTION:
                for btn in self.buttons:
                    btn.check_hover(mouse_pos)

                if self.state == GameState.PLAYING:
                    if self.active_node and self.active_node.dragging:
                        self.active_node.rect.x = mouse_pos[0] + self.drag_offset[0]
                        self.active_node.rect.y = mouse_pos[1] + self.drag_offset[1]

    def handle_game_click(self, mouse_pos):
        # 1. Input Ports
        port_clicked = False
        for node in self.nodes:
            for port in node.input_ports:
                if port["rect"].collidepoint(mouse_pos):
                    if port["connected_node"]:
                        self.connecting_node = port["connected_node"]
                        port["connected_node"] = None
                        port_clicked = True
                        break
            if port_clicked:
                break

        if not port_clicked:
            # 2. Output Ports
            for node in self.nodes:
                if node.output_rect.collidepoint(mouse_pos):
                    self.connecting_node = node
                    port_clicked = True
                    break

        if not port_clicked:
            # 3. Bodies
            for node in reversed(self.nodes):
                if node.rect.collidepoint(mouse_pos):
                    self.active_node = node
                    self.active_node.dragging = True
                    self.active_node.selected = True
                    self.drag_offset = (
                        node.rect.x - mouse_pos[0],
                        node.rect.y - mouse_pos[1],
                    )
                    self.nodes.remove(node)
                    self.nodes.append(node)
                    break
            else:
                # 4. BG Click
                for node in self.nodes:
                    node.selected = False

    def update(self):
        if self.state == GameState.PLAYING:
            for node in self.nodes:
                node.update()
                if self.simulating:
                    node.process_logic()

    def draw(self):
        self.screen.fill(BG_COLOR)

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.LEVEL_SELECT:
            self.draw_level_select()
        elif self.state == GameState.PLAYING:
            self.draw_game()

        # UI Buttons (Global for simplicity, but list is updated per state)
        for btn in self.buttons:
            btn.render(self.screen, self.font)

        pygame.display.flip()

    def draw_menu(self):
        # Title
        title_surf = self.title_font.render("LOGIC GATES", True, TEXT_COLOR)
        rect = title_surf.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(title_surf, rect)

    def draw_level_select(self):
        title_surf = self.large_font.render("SELECT LEVEL", True, TEXT_COLOR)
        self.screen.blit(title_surf, (self.screen.get_width() // 2 - 100, 50))

    def draw_game(self):
        draw_grid(self.screen)

        # Level Info
        level = self.get_current_level()
        if level:
            title_surf = self.large_font.render(
                f"Level {level.id}: {level.title}", True, TEXT_COLOR
            )
            self.screen.blit(title_surf, (200, 20))

            lines = level.description.split("\n")
            dy = 60
            for line in lines:
                desc_surf = self.font.render(line, True, (200, 200, 200))
                self.screen.blit(desc_surf, (200, dy))
                dy += 30

            # Draw Hint
            if self.show_hint and level.hint:
                dy += 10
                hint_lines = level.hint.split("\n")
                for line in hint_lines:
                    hint_surf = self.font.render(line, True, (255, 255, 100))
                    self.screen.blit(hint_surf, (200, dy))
                    dy += 30

        # Links
        for node in self.nodes:
            for port in node.input_ports:
                if port["connected_node"]:
                    start = port["connected_node"].output_rect.center
                    end = port["rect"].center
                    draw_bezier(self.screen, start, end)

        # Temp Link
        if self.connecting_node:
            start = self.connecting_node.output_rect.center
            end = pygame.mouse.get_pos()
            draw_bezier(self.screen, start, end, color=(255, 255, 0))

        # Nodes
        for node in self.nodes:
            node.render(self.screen)

        # Message
        if self.message:
            msg_surf = self.large_font.render(self.message, True, self.message_color)
            self.screen.blit(msg_surf, (300, self.screen.get_height() - 60))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
