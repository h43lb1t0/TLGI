from decimal import getcontext
import decimal
import math


def hex_letter_to_number(number: str) -> int:
    """Converts a hexadecimal letter (A-F) to its numberical equivalent (0-15).
    
    Args:
        number (str): The hexadecimal letter to convert.

    Returns:
        int: The numerical value of the hexadecimal letter.
    """
    hex_mapping = {
        'A': 10,
        'B': 11,
        'C': 12,
        'D': 13,
        'E': 14,
        'F': 15
    }
    val = hex_mapping.get(number.upper())
    if val is not None:
        return val
    else:
        return int(number)

def number_to_hex_letter(num: int) -> str:
    """Converts a numberical value (10-15) to its hexadecimal letter equivalent (A-F).
    
    Args:
        num (int): The number to convert (0-15).
        Returns:
        str: The hexadecimal letter if num is between 10-15, else the string of the number.
    """
    number_mapping = {
        10: 'A',
        11: 'B',
        12: 'C',
        13: 'D',
        14: 'E',
        15: 'F'
    }
    return number_mapping.get(num, str(num))

def _neded_precision_in_base(frac: int, base: int, out_base: int) -> int:
    """
    Calculates how many digits are needed in the fraction part when converting from one base to another.
    Args:
        frac (int): The fraction part in the original base (e.g., for 0.75, pass 75).
        base (int): The original base.
        out_base (int): The target base.
    Returns:
        int: The number of digits needed in the fraction part in the target base.
    """

    print("Calculating how many bits are needed for the fraction part")
    r = math.ceil(len(str(frac)) * (math.log(base)/math.log(out_base)))
    print(f"{len(str(frac))} * (ln({base})/ln({out_base})) = {r}")
    return r

def _fraction_part_decimal_to_n_base(fraction_part: int, base: int) -> str:
    """
    Converts the fraction part of a number in the decimal base into a fraction in the goal base.

    Args:
        fraction_part (int): The fraction part in decimal (e.g., for 0.75, pass 75).
        base (int): The target base to convert to.
    Returns:
        str: The fraction part in the target base as a string.
    """

    p: int = _neded_precision_in_base(fraction_part, 10, base)


    print(f"\n--- Converting 0.{fraction_part} (Base 10) to Base {base} ---")
    result: str = ''

    numerator: int = fraction_part
    frac_str: str = str(fraction_part)
    width: int = len(frac_str)
    denominator: int = 10 ** len(frac_str)

    while p > 0:

        frac_print: str = f"0.{str(numerator).zfill(width)}"

        product: int = numerator * base
        intenager_part: int = product // denominator
        numerator: int = product % denominator
        product_float = f"{intenager_part}.{str(numerator).zfill(width)}"
        print(f"{frac_print} * {base} = {product_float}")

        result += number_to_hex_letter(intenager_part)

        if numerator == 0:
            break 
        p -= 1
    
    return result


def _to_decimal(num: str, base: int, fraction: bool = False) -> int:
    """Converts a number (represented as an int) from a given base to decimal.
    
    Args:
        num (str): The number to convert, represented as a string.
        base (int): The base of the input number.
        fraction (bool): Whether the number is a fraction part. Defaults to False.
    Returns:
        int: The decimal representation of the input number.
    """

    original_num_for_print = num 
    result = 0
    index = 1 if fraction else 0
    
    print(f"\n--- 1. Converting {original_num_for_print} (Base {base}) to Decimal (Base 10) ---")

    digits_list = [hex_letter_to_number(d) for d in num]
    if not fraction:
        digits_list.reverse()

    for digit in digits_list:
        index_calc = (( -1 * index) if fraction else index)
        calculation = digit * (base ** index_calc)

        print(f"{digit} * ({base} ^ {'-' if fraction else ''}{index}) ={digit} * {base ** index_calc} = {calculation}")

        result += calculation

        index += 1
    return result


def change_base(number_as_string_with_base: str, out_base: int) -> str:
    """
    Changes a number from one base to another.
    The input string format is "number_base", e.g., "1101_2" or "77_8".

    Args:
        number_as_string_with_base (str): The number with its base as a string.
        out_base (int): The target base to convert to.
    Returns:
        str: The converted number as a string in the target base.
    """
    if "_" not in number_as_string_with_base:
        number_as_string_with_base += "_10"
        
    number, input_base = number_as_string_with_base.split("_")
    input_base = int(input_base)
    if input_base < 2 or out_base < 2:
        raise ValueError("base must be 2 or greater.")
    if input_base > 10 and input_base < 16 or out_base > 10 and out_base < 16:
        raise ValueError("Base must be 2-10 or 16.")

    if input_base == out_base:
        print("Input base equals output base. No conversion needed.")
        return number
    
    number, *fraction_part = number.split(".")
    if len(fraction_part) > 0:
        fraction_part = fraction_part[0]

    if input_base == 10:
        print(f"\n--- Converting {number} (Base 10) to Base {out_base} ---")
        mod_result = []
        dr = int(number)
        current_dividend_for_print = dr 
        
        while dr != 0:
            current_dividend_for_print = dr
            dr, mr = divmod(dr, out_base)
            
            print(f"{current_dividend_for_print} : {out_base} = {dr}, Remainder: {mr}")
            
            mod_result.append(str(mr))
            
        mod_result.reverse()
        print("Reverse digits")
        final_reults = []
        if out_base == 16:
            for digi in mod_result:
                final_reults.append(number_to_hex_letter(int(digi)))
        else:
            final_reults = mod_result
        final_result_str = ''.join(final_reults)
        if not final_result_str:
            final_result_str = "0"

        if fraction_part:
            fraction_result = _fraction_part_decimal_to_n_base(int(fraction_part), out_base)
            final_result_str = f"{final_result_str}.{fraction_result}"
        
        print(f"--- Final Base {out_base} Value: {final_result_str} ---\n")
        return final_result_str

    elif out_base == 10:
        r = _to_decimal(number, input_base)
        print(r)
        if fraction_part:
            r += _to_decimal(fraction_part, input_base, True)
        return r
        
    else:
        print(f"\n--- Two-step conversion required: Base {input_base} -> Base 10 -> Base {out_base} ---")
        
        num_decimal = _to_decimal(number, input_base)
        if fraction_part:
            fraction_decimal = _to_decimal(fraction_part, input_base, True)
            num_decimal = num_decimal + fraction_decimal
        return change_base(f"{num_decimal}_10", out_base)

    
if __name__ == "__main__":
    while True:
        inp = input("Enter number with base (e.g., 1101_2 or 15_8) (or 'exit' to quit): ")
        if inp.lower() == 'exit':
            break
        try:
            out_base = int(input("Enter output base (e.g., 10 or 2): "))
            if out_base < 2:
                 print("Output base must be 2 or greater.")
                 continue
                 
            result = change_base(inp, out_base)
            print(f"Final Result: {result} (Base {out_base})")
        except Exception as e:
            print(f"An error occurred: {e}")