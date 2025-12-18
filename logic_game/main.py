import pygame
import sys
from nodes import Node, InputNode, AndNode, OutputNode
import inspect
import nodes as nodes_module

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BG_COLOR = (30, 30, 30)

TEXT_COLOR = (255, 255, 255)
LINK_COLOR = (200, 200, 200)

pygame.init()
pygame.font.init()
FONT = pygame.font.SysFont("Arial", 24)


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
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = (70, 70, 70)
        self.hover_color = (90, 90, 90)
        self.hovered = False

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()
            return True
        return False

    def render(self, screen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        text_surf = FONT.render(self.text, True, TEXT_COLOR)
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


def main():
    # Use (0,0) and FULLSCREEN to adapt to native resolution
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Logic Nodes")
    clock = pygame.time.Clock()

    nodes = []

    simulating = False

    def start_sim():
        nonlocal simulating
        simulating = True

    def stop_sim():
        nonlocal simulating
        simulating = False

    # Dynamic Node Discovery
    node_types = []
    for name, obj in inspect.getmembers(nodes_module):
        if (
            inspect.isclass(obj)
            and issubclass(obj, nodes_module.Node)
            and obj is not nodes_module.Node
        ):
            node_types.append(obj)

    # Helper to create spawn callbacks with closure
    def make_spawn_func(node_cls):
        def spawn():
            # Use default spawning coordinates, maybe stagger them later if needed
            nodes.append(node_cls(400, 300))

        return spawn

    buttons = []
    y_offset = 20

    # Create buttons for each node type
    for node_cls in node_types:
        name = node_cls.__name__.replace("Node", "")
        if name == "Output":
            name = "LED"

        btn_text = f"Add {name}"
        buttons.append(
            Button(20, y_offset, 120, 40, btn_text, make_spawn_func(node_cls))
        )
        y_offset += 50

    # Add Play/Stop buttons at the bottom
    # Add a little spacer
    y_offset += 10
    buttons.append(Button(20, y_offset, 120, 40, "Play", start_sim))
    y_offset += 50
    buttons.append(Button(20, y_offset, 120, 40, "Stop", stop_sim))

    running = True
    active_node = None
    drag_offset = (0, 0)

    connecting_node = None

    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_DELETE:
                    # Delete selected nodes
                    to_remove = [n for n in nodes if n.selected]
                    for n in to_remove:
                        nodes.remove(n)
                        # Remove connections FROM this node in other nodes' input ports
                        for other in nodes:
                            for port in other.input_ports:
                                if port["connected_node"] == n:
                                    port["connected_node"] = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # 0. Check UI Buttons first
                    ui_handled = False
                    for btn in buttons:
                        if btn.handle_click(mouse_pos):
                            ui_handled = True
                            break
                    if ui_handled:
                        continue

                    # 1. Check Input Ports (Disconnecting/Moving a connection)
                    port_clicked = False
                    for node in nodes:
                        for port in node.input_ports:
                            if port["rect"].collidepoint(mouse_pos):
                                if port["connected_node"]:
                                    # Pick up the connection
                                    connecting_node = port["connected_node"]
                                    port["connected_node"] = None
                                    port_clicked = True
                                    break
                        if port_clicked:
                            break

                    if not port_clicked:
                        # 2. Check Output Ports (Starting a connection)
                        for node in nodes:
                            if node.output_rect.collidepoint(mouse_pos):
                                connecting_node = node
                                port_clicked = True
                                break

                    if not port_clicked:
                        # 2. Check Bodies (Dragging)
                        for node in reversed(nodes):
                            if node.rect.collidepoint(mouse_pos):
                                active_node = node
                                active_node.dragging = True
                                active_node.selected = True
                                drag_offset = (
                                    node.rect.x - mouse_pos[0],
                                    node.rect.y - mouse_pos[1],
                                )
                                # Bring to front
                                nodes.remove(node)
                                nodes.append(node)
                                break
                        else:
                            # 3. Background Click
                            for node in nodes:
                                node.selected = False

                elif event.button == 3:  # Right click (toggle value for inputs)
                    for node in reversed(nodes):
                        if node.rect.collidepoint(mouse_pos):
                            if isinstance(node, InputNode):
                                node.value = not node.value
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if connecting_node:
                        # Check if dropped on an INPUT port
                        if try_connect_node(connecting_node, nodes, mouse_pos):
                            pass  # Connection successful
                        connecting_node = None

                    if active_node:
                        active_node.dragging = False
                        active_node = None

            elif event.type == pygame.MOUSEMOTION:
                for btn in buttons:
                    btn.check_hover(mouse_pos)

                if active_node and active_node.dragging:
                    active_node.rect.x = mouse_pos[0] + drag_offset[0]
                    active_node.rect.y = mouse_pos[1] + drag_offset[1]

        # Update
        for node in nodes:
            node.update()
            if simulating:
                node.process_logic()

        # Render
        screen.fill(BG_COLOR)
        draw_grid(screen)

        # Draw existing links
        for node in nodes:
            for port in node.input_ports:
                if port["connected_node"]:
                    start = port["connected_node"].output_rect.center
                    end = port["rect"].center
                    draw_bezier(screen, start, end)

        # Draw temporary link
        if connecting_node:
            start = connecting_node.output_rect.center
            end = mouse_pos
            draw_bezier(screen, start, end, color=(255, 255, 0))

        for node in nodes:
            node.render(screen)

        # Draw UI
        for btn in buttons:
            btn.render(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
