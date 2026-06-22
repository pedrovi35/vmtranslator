"""VM parser: tokenises .vm source files, strips comments and blank lines."""

from __future__ import annotations

_ARITHMETIC = frozenset({"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"})


class Parser:
    """Reads a .vm file and exposes one command at a time."""

    def __init__(self, filename: str) -> None:
        with open(filename) as fh:
            self._commands: list[list[str]] = [
                tokens
                for line in fh
                if (tokens := line.split("//")[0].split()) != []
            ]
        self._index = -1
        self._current: list[str] = []

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def has_more_commands(self) -> bool:
        return self._index + 1 < len(self._commands)

    def advance(self) -> None:
        self._index += 1
        self._current = self._commands[self._index]

    # ------------------------------------------------------------------
    # Current-command accessors
    # ------------------------------------------------------------------

    def command_type(self) -> str:
        cmd = self._current[0].lower()
        if cmd in _ARITHMETIC:
            return "C_ARITHMETIC"
        if cmd == "push":
            return "C_PUSH"
        if cmd == "pop":
            return "C_POP"
        if cmd == "label":
            return "C_LABEL"
        if cmd == "goto":
            return "C_GOTO"
        if cmd == "if-goto":
            return "C_IF"
        if cmd == "function":
            return "C_FUNCTION"
        if cmd == "call":
            return "C_CALL"
        if cmd == "return":
            return "C_RETURN"
        raise ValueError(f"Unknown VM command: {cmd!r}")

    def arg1(self) -> str:
        """
        Returns the first argument of the current command.
        In the case of C_ARITHMETIC, the command itself (e.g., 'add', 'sub') is returned.
        Should not be called if the current command is C_RETURN.
        """
        cmd_type = self.command_type()
        if cmd_type == "C_ARITHMETIC":
            return self._current[0].lower()
        return self._current[1]  # Mantém o case original para nomes de funções/labels se necessário

    def arg2(self) -> int:
        """
        Returns the second argument of the current command.
        Should be called only if the current command is C_PUSH, C_POP, C_FUNCTION, or C_CALL.
        """
        return int(self._current[2])