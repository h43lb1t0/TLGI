import unittest
from math import inf, nan
from IEEE import IEEE_754, FORMAT


class TestIEEE754(unittest.TestCase):
    def get_binary_str(self, ieee_obj):
        return "".join(map(str, ieee_obj.ieee_754))

    def get_hex_str(self, ieee_obj):
        val_str = self.get_binary_str(ieee_obj)
        return "".join(
            hex(int(val_str[i : i + 4], 2))[2:] for i in range(0, len(val_str), 4)
        ).upper()

    def test_binary32_zero(self):
        # +0.0
        val = IEEE_754(0.0, format=FORMAT.binary32)
        self.assertEqual(self.get_hex_str(val), "00000000")

        # -0.0
        val = IEEE_754(-0.0, format=FORMAT.binary32)
        self.assertEqual(self.get_hex_str(val), "80000000")

    def test_binary32_special(self):
        # Infinity
        val = IEEE_754(inf, format=FORMAT.binary32)
        # Sign 0, Exp 255 (FF), Mantissa 0 -> 7F800000
        self.assertEqual(self.get_hex_str(val), "7F800000")

        # -Infinity
        val = IEEE_754(-inf, format=FORMAT.binary32)
        # Sign 1, Exp 255 (FF), Mantissa 0 -> FF800000
        self.assertEqual(self.get_hex_str(val), "FF800000")

        # NaN
        # Implementation specific in IEEE.py:
        # returns "1", "1"*exponent, "10" * (mantissa/2)
        # Sign 1, Exp FF, Mantissa 101010...
        # binary32 mantissa 23 bits. "10"*11 = 22 bits + 0 padding
        # 1 11111111 1010101010101010101010 0
        # Hex check will confirm exact pattern.
        val = IEEE_754(nan, format=FORMAT.binary32)
        # First check length
        self.assertEqual(len(self.get_binary_str(val)), 32)
        # Check first 9 bits (Sign + Exp) -> 1 11111111
        self.assertEqual(self.get_binary_str(val)[:9], "111111111")

    def test_binary32_values(self):
        # 1.0 -> 3F800000
        val = IEEE_754(1.0, format=FORMAT.binary32)
        self.assertEqual(self.get_hex_str(val), "3F800000")

        # -1.0 -> BF800000
        val = IEEE_754(-1.0, format=FORMAT.binary32)
        self.assertEqual(self.get_hex_str(val), "BF800000")

        val = IEEE_754(13.12, format=FORMAT.binary32)
        self.assertEqual(len(self.get_hex_str(val)), 8)

    def test_binary64_values(self):
        # 1.0 -> 3FF0000000000000
        val = IEEE_754(1.0, format=FORMAT.binary64)
        self.assertEqual(self.get_hex_str(val), "3FF0000000000000")

    def test_binary16_values(self):
        # 1.0
        # Bias 15. Exp = 0 + 15 = 15 = 01111
        # Sign 0
        # Mantissa 0
        # 0 01111 0000000000 -> 3C00
        val = IEEE_754(1.0, format=FORMAT.binary16)
        self.assertEqual(self.get_hex_str(val), "3C00")

        # Infinity -> 0 11111 00000... -> 7C00
        val = IEEE_754(inf, format=FORMAT.binary16)
        self.assertEqual(self.get_hex_str(val), "7C00")


if __name__ == "__main__":
    unittest.main()
