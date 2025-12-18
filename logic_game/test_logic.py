import unittest
import sys
import os

# Ensure we can import nodes
sys.path.append(os.getcwd())

try:
    import pygame
    # Initialize pygame types for Rect to work if needed, though Rect usually works without init
except ImportError:
    print("Pygame not found, cannot run tests properly as nodes depend on it.")
    sys.exit(1)

from nodes import InputNode, AndNode, OutputNode


class TestLogicNodes(unittest.TestCase):
    def setUp(self):
        # We need to mock a screen surface for render calls if we were testing render,
        # but for logic we just need the classes.
        pass

    def test_input_node_toggle(self):
        node = InputNode(0, 0, value=False)
        self.assertFalse(node.value)

        node.value = True
        self.assertTrue(node.value)

    def test_and_node_logic(self):
        and_node = AndNode(0, 0)
        input1 = InputNode(0, 0, False)
        input2 = InputNode(0, 0, False)

        # Connect ports manually as `main.py` does
        # input_ports is a list of dicts: {'rect': ..., 'connected_node': ...}

        # Connect input1 -> port 0
        and_node.input_ports[0]["connected_node"] = input1
        # Connect input2 -> port 1
        and_node.input_ports[1]["connected_node"] = input2

        # 0 AND 0 = 0
        and_node.update()
        self.assertFalse(and_node.value)

        # 1 AND 0 = 0
        input1.value = True
        and_node.update()
        self.assertFalse(and_node.value)

        # 1 AND 1 = 1
        input2.value = True
        and_node.update()
        self.assertTrue(and_node.value)

        # 0 AND 1 = 0
        input1.value = False
        and_node.update()
        self.assertFalse(and_node.value)

    def test_output_node_logic(self):
        led = OutputNode(0, 0)
        inp = InputNode(0, 0, False)

        led.input_ports[0]["connected_node"] = inp

        led.update()
        self.assertFalse(led.value)

        inp.value = True
        led.update()
        self.assertTrue(led.value)


if __name__ == "__main__":
    unittest.main()
