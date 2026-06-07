"""CodeWriter: translates VM commands into Hack assembly instructions."""

from __future__ import annotations
from pathlib import Path


# Segments that use a base-pointer stored in a named register
_PTR_SEGMENTS: dict[str, str] = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
}

# Arithmetic/logic binary operations → ALU expression
_BINARY_OP: dict[str, str] = {
    "add": "D+M",
    "sub": "M-D",
    "and": "D&M",
    "or": "D|M",
}

# Unary operations → ALU expression
_UNARY_OP: dict[str, str] = {
    "neg": "-M",
    "not": "!M",
}

# Comparison operations → Hack jump mnemonic
_COMPARE_JUMP: dict[str, str] = {
    "eq": "JEQ",
    "gt": "JGT",
    "lt": "JLT",
}


class CodeWriter:
    """Writes Hack assembly for a single .vm translation unit."""

    def __init__(self, filename: str) -> None:
        self._file = open(filename, "w")
        # Stem of the output file used for static variable labels (e.g. Foo.2)
        self._module = Path(filename).stem
        # Unique counter for comparison labels so they never collide
        self._label_count = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write_arithmetic(self, command: str) -> None:
        self._emit(f"// {command}")
        if command in _BINARY_OP:
            self._emit(*self._binary_op(command))
        elif command in _UNARY_OP:
            self._emit(*self._unary_op(command))
        elif command in _COMPARE_JUMP:
            self._emit(*self._compare_op(command))
        else:
            raise ValueError(f"Unknown arithmetic command: {command!r}")

    def write_push(self, segment: str, index: int) -> None:
        self._emit(f"// push {segment} {index}")
        self._emit(*self._push_code(segment, index))

    def write_pop(self, segment: str, index: int) -> None:
        self._emit(f"// pop {segment} {index}")
        self._emit(*self._pop_code(segment, index))

    def close(self) -> None:
        self._file.close()

    # ------------------------------------------------------------------
    # Arithmetic helpers
    # ------------------------------------------------------------------

    def _binary_op(self, command: str) -> list[str]:
        return [
            "@SP",
            "AM=M-1",   # SP--, A → top of stack
            "D=M",      # D = popped value
            "A=A-1",    # A → new top (second operand stays in-place)
            f"M={_BINARY_OP[command]}",
        ]

    def _unary_op(self, command: str) -> list[str]:
        return [
            "@SP",
            "A=M-1",
            f"M={_UNARY_OP[command]}",
        ]

    def _compare_op(self, command: str) -> list[str]:
        true_lbl = f"VM_TRUE_{self._label_count}"
        end_lbl = f"VM_END_{self._label_count}"
        self._label_count += 1
        jump = _COMPARE_JUMP[command]
        return [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            "D=M-D",        # D = x - y
            f"@{true_lbl}",
            f"D;{jump}",
            "@SP",
            "A=M-1",
            "M=0",          # false → 0
            f"@{end_lbl}",
            "0;JMP",
            f"({true_lbl})",
            "@SP",
            "A=M-1",
            "M=-1",         # true → -1 (0xFFFF)
            f"({end_lbl})",
        ]

    # ------------------------------------------------------------------
    # Push helpers
    # ------------------------------------------------------------------

    def _push_code(self, segment: str, index: int) -> list[str]:
        # Load value into D, then push D onto stack
        load = self._load_segment_to_d(segment, index)
        return load + [
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]

    def _load_segment_to_d(self, segment: str, index: int) -> list[str]:
        if segment == "constant":
            return [f"@{index}", "D=A"]

        if segment in _PTR_SEGMENTS:
            base = _PTR_SEGMENTS[segment]
            return [f"@{index}", "D=A", f"@{base}", "A=D+M", "D=M"]

        if segment == "temp":
            return [f"@{5 + index}", "D=M"]

        if segment == "pointer":
            reg = "THIS" if index == 0 else "THAT"
            return [f"@{reg}", "D=M"]

        if segment == "static":
            return [f"@{self._module}.{index}", "D=M"]

        raise ValueError(f"Unknown segment: {segment!r}")

    # ------------------------------------------------------------------
    # Pop helpers
    # ------------------------------------------------------------------

    def _pop_code(self, segment: str, index: int) -> list[str]:
        if segment in _PTR_SEGMENTS:
            # Compute target address, park it in R13, then write
            base = _PTR_SEGMENTS[segment]
            return [
                f"@{index}", "D=A", f"@{base}", "D=D+M",
                "@R13", "M=D",         # R13 = target address
                "@SP", "AM=M-1",       # SP--, A → top of stack
                "D=M",                 # D = popped value
                "@R13", "A=M", "M=D",  # RAM[target] = D
            ]

        if segment == "temp":
            return [
                "@SP", "AM=M-1",
                "D=M",
                f"@{5 + index}", "M=D",
            ]

        if segment == "pointer":
            reg = "THIS" if index == 0 else "THAT"
            return [
                "@SP", "AM=M-1",
                "D=M",
                f"@{reg}", "M=D",
            ]

        if segment == "static":
            return [
                "@SP", "AM=M-1",
                "D=M",
                f"@{self._module}.{index}", "M=D",
            ]

        raise ValueError(f"Unknown segment: {segment!r}")

    # ------------------------------------------------------------------
    # Internal writer
    # ------------------------------------------------------------------

    def _emit(self, *lines: str) -> None:
        for line in lines:
            self._file.write(line + "\n")
