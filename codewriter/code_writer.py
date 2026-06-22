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
        self._module = Path(filename).stem
        self._label_count = 0
        self._current_function = "OS"

    def set_filename(self, filename: str) -> None:
        """Informa ao CodeWriter que a tradução de um novo arquivo .vm foi iniciada."""
        self._module = filename

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

    def write_push_pop(self, command_type: str, segment: str, index: int) -> None:
        """Método despachante chamado pelo laço principal do vmtranslator.py."""
        if command_type == "C_PUSH":
            self.write_push(segment, index)
        elif command_type == "C_POP":
            self.write_pop(segment, index)

    def write_push(self, segment: str, index: int) -> None:
        self._emit(f"// push {segment} {index}")
        self._emit(*self._push_code(segment, index))

    def write_pop(self, segment: str, index: int) -> None:
        self._emit(f"// pop {segment} {index}")
        self._emit(*self._pop_code(segment, index))

    # --- Program Flow ---

    def write_label(self, label: str) -> None:
        self._emit(f"// label {label}")
        self._emit(f"({self._current_function}${label})")

    def write_goto(self, label: str) -> None:
        self._emit(f"// goto {label}")
        self._emit(f"@{self._current_function}${label}", "0;JMP")

    def write_if(self, label: str) -> None:
        self._emit(f"// if-goto {label}")
        self._emit(
            "@SP",
            "AM=M-1",
            "D=M",
            f"@{self._current_function}${label}",
            "D;JNE"
        )

    # --- Subroutines ---

    def write_function(self, function_name: str, num_locals: int) -> None:
        self._emit(f"// function {function_name} {num_locals}")
        self._current_function = function_name
        self._emit(f"({function_name})")
        for _ in range(num_locals):
            self._emit("@SP", "A=M", "M=0", "@SP", "M=M+1")

    def write_call(self, function_name: str, num_args: int) -> None:
        self._emit(f"// call {function_name} {num_args}")
        ret_label = f"{function_name}$ret.{self._label_count}"
        self._label_count += 1

        # 1. Push return-address
        self._emit(f"@{ret_label}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1")
        # 2. Push LCL, ARG, THIS, THAT
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            self._emit(f"@{segment}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1")
        # 3. ARG = SP - 5 - num_args
        self._emit("@SP", "D=M", f"@{5 + num_args}", "D=D-A", "@ARG", "M=D")
        # 4. LCL = SP
        self._emit("@SP", "D=M", "@LCL", "M=D")
        # 5. goto function_name
        self._emit(f"@{function_name}", "0;JMP")
        # 6. (return-address)
        self._emit(f"({ret_label})")

    def write_return(self) -> None:
        self._emit("// return")
        # endFrame (R14) = LCL
        self._emit("@LCL", "D=M", "@R14", "M=D")
        # retAddr (R15) = *(endFrame - 5)
        self._emit("@5", "A=D-A", "D=M", "@R15", "M=D")
        # *ARG = pop()
        self._emit("@SP", "AM=M-1", "D=M", "@ARG", "A=M", "M=D")
        # SP = ARG + 1
        self._emit("@ARG", "D=M+1", "@SP", "M=D")
        # Restaura THAT, THIS, ARG, LCL de endFrame - 1 até endFrame - 4
        for i, segment in enumerate(["THAT", "THIS", "ARG", "LCL"], 1):
            self._emit("@R14", "D=M", f"@{i}", "A=D-A", "D=M", f"@{segment}", "M=D")
        # goto retAddr
        self._emit("@R15", "A=M", "0;JMP")

    def close(self) -> None:
        self._file.close()

    # ------------------------------------------------------------------
    # Code Helpers & Bootstrap
    # ------------------------------------------------------------------

    def write_bootstrap(self) -> None:
        """Inicializa o ponteiro da pilha (SP=256) e chama Sys.init."""
        self._emit("// --- BOOTSTRAP INITIALIZATION ---", "@256", "D=A", "@SP", "M=D")
        self.write_call("Sys.init", 0)

    def _binary_op(self, command: str) -> list[str]:
        return [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
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
            "D=M-D",
            f"@{true_lbl}",
            f"D;{jump}",
            "@SP",
            "A=M-1",
            "M=0",
            f"@{end_lbl}",
            "0;JMP",
            f"({true_lbl})",
            "@SP",
            "A=M-1",
            "M=-1",
            f"({end_lbl})",
        ]

    def _push_code(self, segment: str, index: int) -> list[str]:
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

    def _pop_code(self, segment: str, index: int) -> list[str]:
        if segment in _PTR_SEGMENTS:
            base = _PTR_SEGMENTS[segment]
            return [
                f"@{index}", "D=A", f"@{base}", "D=D+M",
                "@R13", "M=D",
                "@SP", "AM=M-1",
                "D=M",
                "@R13", "A=M", "M=D",
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

    def _emit(self, *lines: str) -> None:
        for line in lines:
            self._file.write(line + "\n")