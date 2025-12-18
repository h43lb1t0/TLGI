from enum import Enum, auto
from typing import Dict, Tuple
from math import inf, nan, isnan, copysign
from NumerBaseChangeCalculator import change_base


class FORMAT(Enum):
    binary16 = auto()
    binary32 = auto()
    binary64 = auto()


FORMATS_SPECS: Dict[FORMAT, Dict[str, int]] = {
    FORMAT.binary16: {"size": 16, "exponent": 5, "mantissa": 10, "bias": 15},
    FORMAT.binary32: {"size": 32, "exponent": 8, "mantissa": 23, "bias": 127},
    FORMAT.binary64: {"size": 64, "exponent": 11, "mantissa": 52, "bias": 1023},
}


class IEEE_754:
    def __init__(
        self, value: float, base: int = 10, format: FORMAT = FORMAT.binary32
    ) -> None:
        self.input_value = value
        self.base = base
        self.format = format
        specs = FORMATS_SPECS[self.format]
        self.size_in_bits = specs["size"]
        self.exponent = specs["exponent"]
        self.mantissa = specs["mantissa"]
        self.bias = specs["bias"]
        self.ieee_754 = [0 for i in range(self.size_in_bits)]
        self.value = self._convert()

    def __str__(self) -> str:
        val_str = "".join(map(str, self.ieee_754))
        val_hex = "".join(
            hex(int(val_str[i : i + 4], 2))[2:] for i in range(0, len(val_str), 4)
        )
        return f"{self.input_value}_{self.base} as IEEE754 {self.format.name} is HEX: {val_hex.upper()} binary: {val_str}"

    def _normalize(self, binary_value: str) -> Tuple[str, int]:
        if "." not in binary_value:
            binary_value += ".0"

        original_dot_idx = binary_value.find(".")
        left, right = binary_value.split(".")

        shift = 0
        combined = binary_value.replace(".", "")

        # shift to right
        if int(left) == 0:
            first_one_idx = combined.find("1")
            right = combined[first_one_idx + 1 :]
            shift = original_dot_idx - (
                first_one_idx if first_one_idx < original_dot_idx else first_one_idx + 1
            )
        # shift to left
        else:
            shift = len(left) - 1
            right = left[1:] + right

        norm = float(f"1.{right}")
        # Round to fit mantissa
        norm = round(norm, self.mantissa)

        norm = str(norm).replace("1.", "")

        return (norm, shift)

    def _special_values(self) -> Tuple[str, str, str]:
        if self.input_value == 0:
            if copysign(1, self.input_value) == -1.0:
                return ("1", "0" * self.exponent, "0" * self.mantissa)
            return ("0", "0" * self.exponent, "0" * self.mantissa)
        elif self.input_value == float("-inf"):
            return ("1", "1" * self.exponent, "0" * self.mantissa)
        elif isnan(self.input_value):  # Check for NaN
            return ("1", "1" * self.exponent, "10" * int((self.mantissa / 2)))
        elif self.input_value == float("inf"):
            return ("0", "1" * self.exponent, "0" * self.mantissa)
        else:
            return ("normal", "", "")

    def _convert(self):
        v, exponent, norm = self._special_values()
        self.ieee_754[0] = int(v) if v != "normal" else 0
        if v == "normal":
            self.ieee_754[0] = 1 if self.input_value < 0 else 0
            value = (
                (self.input_value * -1) if self.input_value < 0 else self.input_value
            )
            binary_value = change_base(f"{value}_{self.base}", 2)
            norm, shift = self._normalize(str(binary_value))
            exponent = shift + self.bias
            exponent = str(change_base(f"{exponent}_10", 2))
        while len(exponent) < self.exponent:
            exponent = "0" + exponent
        for i in range(self.exponent):
            self.ieee_754[i + 1] = int(exponent[i])
        for i in range(self.mantissa):
            self.ieee_754[1 + self.exponent + i] = int(norm[i]) if i < len(norm) else 0


if __name__ == "__main__":
    foo = IEEE_754(13.12, format=FORMAT.binary64)
    print(foo)
