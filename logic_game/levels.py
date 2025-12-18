from nodes import (
    AndNode,
    OrNode,
    NotNode,
    NandNode,
    NorNode,
    XorNode,
    XnorNode,
    InputNode,
    OutputNode,
)


class Level:
    def __init__(
        self,
        id,
        title,
        description,
        allowed_nodes,
        check_func,
        input_count=2,
        output_count=1,
        expect_output_on=True,
        hint=None,
        output_labels=None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.allowed_nodes = allowed_nodes
        self.check_func = check_func
        self.input_count = input_count
        self.output_count = output_count
        self.expect_output_on = expect_output_on
        self.hint = hint
        self.output_labels = output_labels


# --- Phase 1: Axioms ---
def check_lvl_01(inputs):
    # AND: Both must be True
    return all(inputs)


def check_lvl_02(inputs):
    # OR: At least one is True
    return any(inputs)


def check_lvl_03(inputs):
    # NOT: Determine based on first input
    return not inputs[0]


# --- Phase 2: Negated Gates ---
def check_lvl_04(inputs):
    # NAND: NOT(A AND B)
    # Output OFF only when both inputs are ON
    return not all(inputs)


def check_lvl_05(inputs):
    # NOR: NOT(A OR B)
    # Output ON only when both inputs are OFF
    return not any(inputs)


# --- Phase 3: Exclusive Gates ---
def check_lvl_06(inputs):
    # XOR: Output ON if inputs are different
    return inputs[0] != inputs[1]


def check_lvl_07(inputs):
    # XNOR: Output ON if inputs are identical
    return inputs[0] == inputs[1]


# --- Phase 4: Arithmetic ---
def check_lvl_08(inputs):
    # Half Adder: Inputs A, B -> Outputs Sum, Carry
    a, b = inputs[0], inputs[1]
    sum_val = a != b
    carry_val = a and b
    return (sum_val, carry_val)


def check_lvl_09(inputs):
    # Full Adder: Inputs A, B, Cin -> Outputs Sum, Cout
    a, b, cin = inputs[0], inputs[1], inputs[2]
    # Sum = A XOR B XOR Cin
    # Cout = (A AND B) OR (Cin AND (A XOR B))
    sum_val = (a != b) != cin
    cout_val = (a and b) or (cin and (a != b))
    return (sum_val, cout_val)


def check_lvl_10(inputs):
    # 2-Bit Adder: Inputs A0, A1, B0, B1 -> Outputs S0, S1, Cout
    # A = A0 + 2*A1
    # B = B0 + 2*B1
    a0, a1 = inputs[0], inputs[1]
    b0, b1 = inputs[2], inputs[3]

    val_a = (1 if a0 else 0) + (2 if a1 else 0)
    val_b = (1 if b0 else 0) + (2 if b1 else 0)

    total = val_a + val_b
    s0 = bool(total & 1)
    s1 = bool(total & 2)
    cout = bool(total & 4)

    return (s0, s1, cout)


# --- Phase 5: Deconstruction ---
def check_lvl_11(inputs):
    # Rebuild NOT using NAND
    # NAND(A, A) = NOT A
    return not inputs[0]


def check_lvl_12(inputs):
    # Rebuild AND using NAND, NOT
    # NOT(NAND(A, B))
    return all(inputs)


def check_lvl_13(inputs):
    # Rebuild OR using NAND, NOT
    # NAND(NOT A, NOT B) = NOT(NOT A AND NOT B) = A OR B
    return any(inputs)


# --- Phase 6: Architecture ---
def check_lvl_14(inputs):
    # Multiplexer: Inputs A, B, Select -> Output
    # If Sel=0 -> A, If Sel=1 -> B
    # Order: A, B, Select
    a, b, sel = inputs[0], inputs[1], inputs[2]
    return b if sel else a


LEVELS = [
    # Phase 1
    Level(
        id=1,
        title="The Conjunction",
        description="Goal: Activate output only when BOTH inputs are ON.",
        hint="Node: AND",
        allowed_nodes=[AndNode],
        check_func=check_lvl_01,
        input_count=2,
    ),
    Level(
        id=2,
        title="The Disjunction",
        description="Goal: Activate output if AT LEAST ONE input is ON.",
        hint="Node: OR",
        allowed_nodes=[OrNode],
        check_func=check_lvl_02,
        input_count=2,
    ),
    Level(
        id=3,
        title="The Inverter",
        description="Goal: Output ON when input is OFF.",
        hint="Node: NOT",
        allowed_nodes=[NotNode],
        check_func=check_lvl_03,
        input_count=1,
    ),
    # Phase 2
    Level(
        id=4,
        title="The NAND Gate",
        description="Goal: Output OFF only when both inputs are ON.",
        hint="Logic: NOT( A AND B )",
        allowed_nodes=[AndNode, OrNode, NotNode],  # "Composing negative conditions"
        check_func=check_lvl_04,
        input_count=2,
        expect_output_on=False,
    ),
    Level(
        id=5,
        title="The NOR Gate",
        description="Goal: Output ON only when both inputs are OFF.",
        hint="Logic: NOT( A OR B )",
        allowed_nodes=[AndNode, OrNode, NotNode],
        check_func=check_lvl_05,
        input_count=2,
    ),
    # Phase 3
    Level(
        id=6,
        title="The XOR Gate",
        description="Goal: Output ON if inputs are different.\nInventory: Basic + NAND/NOR",
        hint="Logic: (A OR B) AND (A NAND B)",
        allowed_nodes=[AndNode, OrNode, NotNode, NandNode, NorNode],
        check_func=check_lvl_06,
        input_count=2,
    ),
    Level(
        id=7,
        title="The XNOR Gate",
        description="Goal: Output ON if inputs are identical.",
        hint="Logic: NOT( XOR(A, B) )",
        allowed_nodes=[AndNode, OrNode, NotNode, NandNode, NorNode, XorNode],
        check_func=check_lvl_07,
        input_count=2,
    ),
    # Phase 4
    Level(
        id=8,
        title="The Half Adder",
        description="Goal: Add two 1-bit numbers (A, B).\nOutputs: Sum, Carry.",
        allowed_nodes=[AndNode, OrNode, NotNode, NandNode, NorNode, XorNode, XnorNode],
        check_func=check_lvl_08,
        input_count=2,
        output_count=2,
        output_labels=["Sum", "Carry"],
        # Hint Added: Standard Half Adder logic
        hint="Sum: A XOR B\nCarry: A AND B",
    ),
    Level(
        id=9,
        title="The Full Adder",
        description="Goal: Add three 1-bit numbers (A, B, Cin).\nOutputs: Sum, Cout.",
        allowed_nodes=[AndNode, OrNode, NotNode, NandNode, NorNode, XorNode, XnorNode],
        check_func=check_lvl_09,
        input_count=3,
        output_count=2,
        output_labels=["Sum", "Cout"],
        # Hint Added: Logic for cascading carry
        hint="Sum: A XOR B XOR Cin\nCout: (A AND B) OR (Cin AND (A XOR B))",
    ),
    Level(
        id=10,
        title="2-Bit Ripple Carry Adder",
        description="Goal: Add two 2-bit numbers.\nInputs: A0, A1, B0, B1.\nOutputs: S0, S1, Cout.",
        allowed_nodes=[AndNode, OrNode, NotNode, NandNode, NorNode, XorNode, XnorNode],
        check_func=check_lvl_10,
        input_count=4,
        output_count=3,
        output_labels=["S0", "S1", "Cout"],
        # Hint Added: How to chain the previous two levels
        hint="Bit 0: Half Adder(A0, B0)\nBit 1: Full Adder(A1, B1, CarryFrom0)",
    ),
    # Phase 5
    Level(
        id=11,
        title="The Universal Spark",
        description="Goal: Build a NOT gate using ONLY NAND.",
        hint="Logic: NAND(A, A)",
        allowed_nodes=[NandNode],
        check_func=check_lvl_11,
        input_count=1,
    ),
    Level(
        id=12,
        title="Reconstructing AND",
        description="Goal: Build an AND gate using NAND and NOT.",
        hint="Logic: NOT( NAND(A, B) )",
        allowed_nodes=[NandNode, NotNode],
        check_func=check_lvl_12,
        input_count=2,
    ),
    Level(
        id=13,
        title="Reconstructing OR",
        description="Goal: Build an OR gate using NAND and NOT.",
        hint="Logic: NAND( NOT(A), NOT(B) )",
        allowed_nodes=[NandNode, NotNode],
        check_func=check_lvl_13,
        input_count=2,
    ),
    # Phase 6
    Level(
        id=14,
        title="The Multiplexer",
        description="Goal: Build a switch.\nInputs: A, B, Select.\nIf Select=0, Out=A. If Select=1, Out=B.",
        allowed_nodes=[AndNode, OrNode, NotNode, NandNode, NorNode, XorNode, XnorNode],
        check_func=check_lvl_14,
        input_count=3,
        # Hint Added: Selecting pathways based on negation
        hint="Logic: (A AND NOT Sel) OR (B AND Sel)",
    ),
]

PLAYGROUND_LEVEL = Level(
    id=0,
    title="Playground",
    description="Free sandbox mode.\nNo goals, just logic.",
    allowed_nodes=[
        InputNode,
        OutputNode,
        AndNode,
        OrNode,
        NotNode,
        NandNode,
        NorNode,
        XorNode,
        XnorNode,
    ],
    check_func=None,
    input_count=0,
    output_count=0,
)
