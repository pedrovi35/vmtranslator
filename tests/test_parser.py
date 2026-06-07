"""Unit tests for the Parser module."""

import os
import tempfile

import pytest

from parser import Parser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _vm_file(content: str) -> str:
    """Write *content* to a temp .vm file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".vm")
    with os.fdopen(fd, "w") as fh:
        fh.write(content)
    return path


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

class TestFiltering:
    def test_comment_lines_are_skipped(self):
        path = _vm_file("// full-line comment\npush constant 1\n")
        p = Parser(path)
        p.advance()
        assert p.command_type() == "C_PUSH"
        assert not p.has_more_commands()

    def test_inline_comments_are_stripped(self):
        path = _vm_file("push constant 42 // inline comment\n")
        p = Parser(path)
        p.advance()
        assert p.arg2() == 42

    def test_blank_lines_are_skipped(self):
        path = _vm_file("\n\n  \nadd\n\n")
        p = Parser(path)
        p.advance()
        assert not p.has_more_commands()


# ---------------------------------------------------------------------------
# CommandType
# ---------------------------------------------------------------------------

class TestCommandType:
    @pytest.mark.parametrize("cmd", ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"])
    def test_arithmetic_commands(self, cmd):
        path = _vm_file(cmd)
        p = Parser(path)
        p.advance()
        assert p.command_type() == "C_ARITHMETIC"

    def test_push_command(self):
        path = _vm_file("push local 3")
        p = Parser(path)
        p.advance()
        assert p.command_type() == "C_PUSH"

    def test_pop_command(self):
        path = _vm_file("pop argument 1")
        p = Parser(path)
        p.advance()
        assert p.command_type() == "C_POP"


# ---------------------------------------------------------------------------
# Arg1 / Arg2
# ---------------------------------------------------------------------------

class TestArgs:
    def test_arg1_for_arithmetic_returns_command(self):
        path = _vm_file("add")
        p = Parser(path)
        p.advance()
        assert p.arg1() == "add"

    def test_arg1_for_push_returns_segment(self):
        path = _vm_file("push local 0")
        p = Parser(path)
        p.advance()
        assert p.arg1() == "local"

    def test_arg2_for_push_returns_index(self):
        path = _vm_file("push argument 7")
        p = Parser(path)
        p.advance()
        assert p.arg2() == 7

    def test_arg2_for_pop_returns_index(self):
        path = _vm_file("pop that 3")
        p = Parser(path)
        p.advance()
        assert p.arg2() == 3


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

class TestNavigation:
    def test_has_more_commands_false_on_empty_file(self):
        path = _vm_file("// only comments\n")
        p = Parser(path)
        assert not p.has_more_commands()

    def test_advances_through_all_commands(self):
        path = _vm_file("push constant 1\nadd\npop local 0\n")
        p = Parser(path)
        types = []
        while p.has_more_commands():
            p.advance()
            types.append(p.command_type())
        assert types == ["C_PUSH", "C_ARITHMETIC", "C_POP"]
