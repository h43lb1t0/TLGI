import pygame
import os

NODE_COLOR = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)

_FONT = None
_IMAGES = {}


def get_font():
    global _FONT
    if _FONT is None:
        if not pygame.font.get_init():
            pygame.font.init()
        _FONT = pygame.font.SysFont("Arial", 24)
    return _FONT


def load_image(filename):
    if filename not in _IMAGES:
        path = os.path.join(os.path.dirname(__file__), "assets", filename)
        try:
            image = pygame.image.load(path)
            _IMAGES[filename] = image
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
            _IMAGES[filename] = None
    return _IMAGES[filename]


class Node:
    def __init__(self, x, y, w=150, h=80, title="Node", image_file=None, symbol=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.color = NODE_COLOR
        # List of dicts: {'rect': pygame.Rect, 'connected_node': None}
        self.input_ports = []
        self.value = 0
        self.selected = False
        self.dragging = False
        self.image_file = image_file
        self.symbol = symbol

        # Output Port (only one usually)
        self.output_rect = pygame.Rect(0, 0, 20, 20)
        self._update_ports()

    def setup_inputs(self, count):
        self.input_ports = []
        for _ in range(count):
            self.input_ports.append(
                {"rect": pygame.Rect(0, 0, 20, 20), "connected_node": None}
            )
        self._update_ports()

    def _update_ports(self):
        # Output on right
        self.output_rect.center = (self.rect.right, self.rect.centery)

        # Inputs on left, distributed evenly
        if self.input_ports:
            # Distribute along the height on the left edge
            # space available = h
            # step = h / (n+1)
            step = self.rect.height / (len(self.input_ports) + 1)
            for i, port in enumerate(self.input_ports):
                cy = self.rect.top + step * (i + 1)
                port["rect"].center = (self.rect.left, cy)

    def update(self):
        self._update_ports()

    def process_logic(self):
        pass

    def render(self, screen):
        # Draw Image if available
        image = load_image(self.image_file) if self.image_file else None

        if image:
            # Scale image to rect
            scaled_image = pygame.transform.scale(
                image, (self.rect.width, self.rect.height)
            )
            screen.blit(scaled_image, self.rect.topleft)
            # Draw selection border
            if self.selected:
                pygame.draw.rect(screen, (200, 200, 255), self.rect, 3, border_radius=8)

            # Manually render symbol
            if self.symbol:
                # Use a larger font for the symbol
                symbol_font = pygame.font.SysFont("Arial", 32)
                symbol_surf = symbol_font.render(self.symbol, True, (0, 0, 0))
                # Center the symbol
                symbol_rect = symbol_surf.get_rect(center=self.rect.center)
                screen.blit(symbol_surf, symbol_rect)
        else:
            # Fallback to rect
            color = (150, 150, 180) if self.selected else self.color
            pygame.draw.rect(screen, color, self.rect, border_radius=8)
            pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=8)

        if not image:
            text_surf = get_font().render(
                f"{self.title}: {self.value}", True, TEXT_COLOR
            )
            screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))

        # Render Output Port (Yellow)
        pygame.draw.circle(screen, (255, 200, 0), self.output_rect.center, 8)

        # Render Input Ports (Blue)
        for port in self.input_ports:
            pygame.draw.circle(screen, (0, 200, 255), port["rect"].center, 8)


class InputNode(Node):
    def __init__(self, x, y, value=False):
        super().__init__(x, y, title="Input")
        self.value = value
        self.color = (50, 100, 150)

    def update(self):
        super().update()

    # InputNode logic is handled by user interaction (mouse clicks),
    # so process_logic can remain empty or be used for other things if needed.

    def render(self, screen):
        # Override render to show True/False
        # InputNode usually doesn't have an SVG in the assets list provided, so keep default style
        color = (150, 150, 180) if self.selected else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=8)

        # Render Title
        val_str = str(self.value)
        text_surf = get_font().render(f"{self.title}: {val_str}", True, TEXT_COLOR)
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))

        # Render Output Port (Yellow if ON, else Dark)
        port_color = (255, 255, 0) if self.value else (100, 100, 0)
        pygame.draw.circle(screen, port_color, self.output_rect.center, 8)


class AndNode(Node):
    def __init__(self, x, y):
        super().__init__(
            x, y, title="AND", image_file="IEC_2in_1out_neg0.svg", symbol="&"
        )
        self.color = (150, 100, 50)
        self.setup_inputs(2)

    def update(self):
        super().update()

    def process_logic(self):
        if not self.input_ports:
            self.value = False
            return

        input_node_1 = self.input_ports[0]["connected_node"]
        input_node_2 = self.input_ports[1]["connected_node"]

        val1 = input_node_1.value if input_node_1 else False
        val2 = input_node_2.value if input_node_2 else False

        self.value = val1 and val2


class NotNode(Node):
    def __init__(self, x, y):
        super().__init__(
            x, y, title="NOT", image_file="IEC_1in_1out_neg1.svg", symbol="1"
        )
        self.color = (150, 100, 50)
        self.setup_inputs(1)

    def update(self):
        super().update()

    def process_logic(self):
        input = self.input_ports[0]["connected_node"]
        self.value = not input.value if input else False


class OrNode(Node):
    def __init__(self, x, y):
        super().__init__(
            x, y, title="OR", image_file="IEC_2in_1out_neg0.svg", symbol="≥1"
        )
        self.color = (150, 100, 50)
        self.setup_inputs(2)

    def update(self):
        super().update()

    def process_logic(self):
        if not self.input_ports:
            self.value = False
            return

        input_node_1 = self.input_ports[0]["connected_node"]
        input_node_2 = self.input_ports[1]["connected_node"]

        val1 = input_node_1.value if input_node_1 else False
        val2 = input_node_2.value if input_node_2 else False

        self.value = val1 or val2


class NandNode(Node):
    def __init__(self, x, y):
        super().__init__(
            x, y, title="NAND", image_file="IEC_2in_1out_neg1.svg", symbol="&"
        )
        self.color = (150, 100, 50)
        self.setup_inputs(2)

    def update(self):
        super().update()

    def process_logic(self):
        if not self.input_ports:
            self.value = False
            return

        input_node_1 = self.input_ports[0]["connected_node"]
        input_node_2 = self.input_ports[1]["connected_node"]

        val1 = input_node_1.value if input_node_1 else False
        val2 = input_node_2.value if input_node_2 else False

        self.value = not (val1 and val2)


class NorNode(Node):
    def __init__(self, x, y):
        super().__init__(
            x, y, title="NOR", image_file="IEC_2in_1out_neg1.svg", symbol="≥1"
        )
        self.color = (150, 100, 50)
        self.setup_inputs(2)

    def update(self):
        super().update()

    def process_logic(self):
        if not self.input_ports:
            self.value = False
            return

        input_node_1 = self.input_ports[0]["connected_node"]
        input_node_2 = self.input_ports[1]["connected_node"]

        val1 = input_node_1.value if input_node_1 else False
        val2 = input_node_2.value if input_node_2 else False

        self.value = not (val1 or val2)


class XorNode(Node):
    def __init__(self, x, y):
        super().__init__(
            x, y, title="XOR", image_file="IEC_2in_1out_neg0.svg", symbol="=1"
        )
        self.color = (150, 100, 50)
        self.setup_inputs(2)

    def update(self):
        super().update()

    def process_logic(self):
        if not self.input_ports:
            self.value = False
            return

        input_node_1 = self.input_ports[0]["connected_node"]
        input_node_2 = self.input_ports[1]["connected_node"]

        val1 = input_node_1.value if input_node_1 else False
        val2 = input_node_2.value if input_node_2 else False

        self.value = val1 != val2


class XnorNode(Node):
    def __init__(self, x, y):
        super().__init__(
            x, y, title="XNOR", image_file="IEC_2in_1out_neg1.svg", symbol="=1"
        )
        self.color = (150, 100, 50)
        self.setup_inputs(2)

    def update(self):
        super().update()

    def process_logic(self):
        if not self.input_ports:
            self.value = False
            return

        input_node_1 = self.input_ports[0]["connected_node"]
        input_node_2 = self.input_ports[1]["connected_node"]

        val1 = input_node_1.value if input_node_1 else False
        val2 = input_node_2.value if input_node_2 else False

        self.value = val1 == val2


class OutputNode(Node):
    def __init__(self, x, y):
        super().__init__(x, y, title="LED")
        self.color = (50, 50, 50)
        self.setup_inputs(1)

    def update(self):
        super().update()

    def process_logic(self):
        if self.input_ports and self.input_ports[0]["connected_node"]:
            self.value = self.input_ports[0]["connected_node"].value
        else:
            self.value = False

    def render(self, screen):
        # OutputNode usually doesn't have an SVG in the assets list provided, so keep default style
        color = (150, 150, 180) if self.selected else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=8)

        # Draw LED Light
        center = (self.rect.centerx, self.rect.centery)
        radius = 20
        led_color = (255, 50, 50) if self.value else (80, 20, 20)
        pygame.draw.circle(screen, led_color, center, radius)

        # Glow effect
        if self.value:
            pygame.draw.circle(screen, (255, 100, 100), center, radius + 5, 2)

        # Render Title
        text_surf = get_font().render(f"{self.title}: {self.value}", True, TEXT_COLOR)
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 50))

        # Render Input Ports (Blue)
        for port in self.input_ports:
            pygame.draw.circle(screen, (0, 200, 255), port["rect"].center, 8)
