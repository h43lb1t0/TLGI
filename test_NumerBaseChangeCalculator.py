import unittest
from NumerBaseChangeCalculator import change_base, hex_letter_to_number, number_to_hex_letter

class TestBaseChange(unittest.TestCase):

    def test_hex_letter_to_number(self):
        self.assertEqual(hex_letter_to_number('A'), 10)
        self.assertEqual(hex_letter_to_number('f'), 15)
        self.assertEqual(hex_letter_to_number('0'), 0)
        self.assertEqual(hex_letter_to_number('9'), 9)

    def test_number_to_hex_letter(self):
        self.assertEqual(number_to_hex_letter(10), 'A')
        self.assertEqual(number_to_hex_letter(15), 'F')
        self.assertEqual(number_to_hex_letter(0), '0')
        self.assertEqual(number_to_hex_letter(9), '9')

    def test_change_base_10_to_2(self):
        self.assertEqual(change_base("10_10", 2), "1010")
        self.assertEqual(change_base("5_10", 2), "101")

    def test_change_base_10_to_16(self):
        self.assertEqual(change_base("255_10", 16), "FF")
        self.assertEqual(change_base("10_10", 16), "A")

    def test_change_base_2_to_10(self):
        self.assertEqual(change_base("1010_2", 10), 10)
        self.assertEqual(change_base("101_2", 10), 5)

    def test_change_base_16_to_10(self):
        self.assertEqual(change_base("FF_16", 10), 255)
        self.assertEqual(change_base("A_16", 10), 10)

    def test_change_base_2_to_16(self):
        # 1010 (2) -> 10 (10) -> A (16)
        self.assertEqual(change_base("1010_2", 16), "A")
        # 1111 (2) -> 15 (10) -> F (16)
        self.assertEqual(change_base("1111_2", 16), "F")

    def test_change_base_16_to_2(self):
        # A (16) -> 10 (10) -> 1010 (2)
        self.assertEqual(change_base("A_16", 2), "1010")
        # F (16) -> 15 (10) -> 1111 (2)
        self.assertEqual(change_base("F_16", 2), "1111")

    def test_same_base(self):
        self.assertEqual(change_base("10_10", 10), "10")
        self.assertEqual(change_base("101_2", 2), "101")

    def test_default_base_10(self):
        self.assertEqual(change_base("10", 2), "1010")

    def test_fraction_10_to_2(self):
        # 0.5 (10) -> 0.1 (2)
        self.assertEqual(change_base("0.5_10", 2), "0.1")
        # 0.25 (10) -> 0.01 (2)
        self.assertEqual(change_base("0.25_10", 2), "0.01")

    def test_fraction_2_to_10(self):
        # 0.1 (2) -> 0.5 (10)
        self.assertEqual(change_base("0.1_2", 10), 0.5)
        # 0.01 (2) -> 0.25 (10)
        self.assertEqual(change_base("0.01_2", 10), 0.25)

    def test_fraction_2_to_16(self):
        # 0.1 (2) -> 0.5 (10) -> 0.8 (16)
        # Wait, 0.5 * 16 = 8.0 -> 0.8
        self.assertEqual(change_base("0.1_2", 16), "0.8")

    def test_invalid_bases(self):
        with self.assertRaises(ValueError):
            change_base("10_10", 1)
        with self.assertRaises(ValueError):
            change_base("10_12", 10) # Base 12 not allowed by code logic

if __name__ == '__main__':
    unittest.main()
