"""Unit tests for the CodeWriter module."""

import os
import tempfile

import pytest

from codewriter import CodeWriter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_writer(stem: str = "Test") -> tuple[CodeWriter, str]:
    # Each call gets its own temp directory so file names never collide on Windows
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, f"{stem}.asm")
    return CodeWriter(path), path


def _read(path: str) -> str:
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Arithmetic – binary
# ---------------------------------------------------------------------------

class TestBinaryArithmetic:
    @pytest.mark.parametrize("cmd,expected", [
        ("add", "D+M"),
        ("sub", "M-D"),
        ("and", "D&M"),
        ("or",  "D|M"),
    ])
    def test_binary_op_uses_correct_alu_expr(self, cmd, expected):
        cw, path = _make_writer()
        cw.write_arithmetic(cmd)
        cw.close()
        assert expected in _read(path)

    def test_binary_op_decrements_sp(self):
        cw, path = _make_writer()
        cw.write_arithmetic("add")
        cw.close()
        asm = _read(path)
        assert "AM=M-1" in asm


# ---------------------------------------------------------------------------
# Arithmetic – unary
# ---------------------------------------------------------------------------

class TestUnaryArithmetic:
    def test_neg(self):
        cw, path = _make_writer()
        cw.write_arithmetic("neg")
        cw.close()
        assert "M=-M" in _read(path)

    def test_not(self):
        cw, path = _make_writer()
        cw.write_arithmetic("not")
        cw.close()
        assert "M=!M" in _read(path)

    def test_unary_does_not_change_sp(self):
        cw, path = _make_writer()
        cw.write_arithmetic("neg")
        cw.close()
        assert "M=M+1" not in _read(path)
        assert "AM=M-1" not in _read(path)


# ---------------------------------------------------------------------------
# Arithmetic – comparisons
# ---------------------------------------------------------------------------

class TestCompareArithmetic:
    @pytest.mark.parametrize("cmd,jump", [
        ("eq", "JEQ"),
        ("gt", "JGT"),
        ("lt", "JLT"),
    ])
    def test_compare_uses_correct_jump(self, cmd, jump):
        cw, path = _make_writer()
        cw.write_arithmetic(cmd)
        cw.close()
        assert jump in _read(path)

    def test_compare_emits_true_and_end_labels(self):
        cw, path = _make_writer()
        cw.write_arithmetic("eq")
        cw.close()
        asm = _read(path)
        assert "VM_TRUE_0" in asm
        assert "VM_END_0" in asm

    def test_label_counter_increments_per_comparison(self):
        cw, path = _make_writer()
        cw.write_arithmetic("eq")
        cw.write_arithmetic("lt")
        cw.close()
        asm = _read(path)
        assert "VM_TRUE_0" in asm
        assert "VM_TRUE_1" in asm


# ---------------------------------------------------------------------------
# Push – constant
# ---------------------------------------------------------------------------

class TestPushConstant:
    def test_loads_literal_value(self):
        cw, path = _make_writer()
        cw.write_push("constant", 21)
        cw.close()
        asm = _read(path)
        assert "@21" in asm
        assert "D=A" in asm

    def test_increments_sp(self):
        cw, path = _make_writer()
        cw.write_push("constant", 0)
        cw.close()
        assert "M=M+1" in _read(path)


# ---------------------------------------------------------------------------
# Push – pointer-based segments
# ---------------------------------------------------------------------------

class TestPushPointerSegments:
    @pytest.mark.parametrize("seg,reg", [
        ("local",    "LCL"),
        ("argument", "ARG"),
        ("this",     "THIS"),
        ("that",     "THAT"),
    ])
    def test_uses_base_register(self, seg, reg):
        cw, path = _make_writer()
        cw.write_push(seg, 2)
        cw.close()
        assert f"@{reg}" in _read(path)


# ---------------------------------------------------------------------------
# Push – temp / pointer / static
# ---------------------------------------------------------------------------

class TestPushSpecialSegments:
    def test_push_temp_uses_fixed_address(self):
        cw, path = _make_writer()
        cw.write_push("temp", 3)   # 5 + 3 = 8
        cw.close()
        assert "@8" in _read(path)

    def test_push_pointer_0_uses_this(self):
        cw, path = _make_writer()
        cw.write_push("pointer", 0)
        cw.close()
        assert "@THIS" in _read(path)

    def test_push_pointer_1_uses_that(self):
        cw, path = _make_writer()
        cw.write_push("pointer", 1)
        cw.close()
        assert "@THAT" in _read(path)

    def test_push_static_uses_module_label(self):
        cw, path = _make_writer(stem="Foo")
        cw.write_push("static", 5)
        cw.close()
        assert "@Foo.5" in _read(path)


# ---------------------------------------------------------------------------
# Pop – pointer-based segments
# ---------------------------------------------------------------------------

class TestPopPointerSegments:
    @pytest.mark.parametrize("seg,reg", [
        ("local",    "LCL"),
        ("argument", "ARG"),
        ("this",     "THIS"),
        ("that",     "THAT"),
    ])
    def test_uses_base_register_and_r13(self, seg, reg):
        cw, path = _make_writer()
        cw.write_pop(seg, 1)
        cw.close()
        asm = _read(path)
        assert f"@{reg}" in asm
        assert "@R13" in asm


# ---------------------------------------------------------------------------
# Pop – temp / pointer / static
# ---------------------------------------------------------------------------

class TestPopSpecialSegments:
    def test_pop_temp_uses_fixed_address(self):
        cw, path = _make_writer()
        cw.write_pop("temp", 0)    # 5 + 0 = 5
        cw.close()
        assert "@5" in _read(path)

    def test_pop_pointer_0_uses_this(self):
        cw, path = _make_writer()
        cw.write_pop("pointer", 0)
        cw.close()
        assert "@THIS" in _read(path)

    def test_pop_pointer_1_uses_that(self):
        cw, path = _make_writer()
        cw.write_pop("pointer", 1)
        cw.close()
        assert "@THAT" in _read(path)

    def test_pop_static_uses_module_label(self):
        cw, path = _make_writer(stem="Bar")
        cw.write_pop("static", 3)
        cw.close()
        assert "@Bar.3" in _read(path)
