def hex_letter_to_number(number: str) -> int:
    """Converts a hexadecimal letter (A-F) to its numberical equivalent (10-15)."""
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
    """Converts a numberical value (10-15) to its hexadecimal letter equivalent (A-F)."""
    number_mapping = {
        10: 'A',
        11: 'B',
        12: 'C',
        13: 'D',
        14: 'E',
        15: 'F'
    }
    return number_mapping.get(num, str(num))


def _to_decimal(num: str, base: int) -> int:
    """Converts a number (represented as an int) from a given base to decimal."""

    original_num_for_print = num 
    result = 0
    index = 0
    
    print(f"\n--- 1. Converting {original_num_for_print} (Base {base}) to Decimal (Base 10) ---")

    digits_list = [hex_letter_to_number(d) for d in num]
    digits_list.reverse()
    
    for digit in digits_list:
        calculation = digit * (base ** index)

        print(f"{digit} * ({base} ^ {index}) ={digit} * {base ** index} = {calculation}")

        result += calculation

        index += 1
    return result


def change_base(number_as_string_with_base: str, out_base: int) -> str:
    """
    Changes a number from one base to another.
    The input string format is "number_base", e.g., "1101_2" or "77_8".
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

    if input_base == 10:
        print(f"\n--- Converting {number} (Base 10) to Base {out_base} ---")
        mod_result = []
        dr = int(number)
        current_dividend_for_print = dr 
        
        while dr != 0:
            current_dividend_for_print = dr
            dr, mr = divmod(dr, out_base)
            
            print(f"{current_dividend_for_print} // {out_base} = {dr}, Remainder: {mr}")
            
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
        
        print(f"--- Final Base {out_base} Value: {final_result_str} ---\n")
        return final_result_str

    elif out_base == 10:
        return _to_decimal(number, input_base)
        
    else:
        print(f"\n--- Two-step conversion required: Base {input_base} -> Base 10 -> Base {out_base} ---")
        
        number_decimal = _to_decimal(number, input_base)
        return change_base(f"{number_decimal}_10", out_base)

    
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