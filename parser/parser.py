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
        raise ValueError(f"Unknown VM command: {cmd!r}")

    def arg1(self) -> str:
        """For C_ARITHMETIC returns the command itself; otherwise the segment."""
        if self.command_type() == "C_ARITHMETIC":
            return self._current[0].lower()
        return self._current[1].lower()

    def arg2(self) -> int:
        """Index operand – valid only for C_PUSH and C_POP."""
        return int(self._current[2])
