import pytest

from atlas.tools.builtin.calculator import (
    safe_calculate,
)


def test_basic_calculation():
    assert safe_calculate("2 + 3 * 4") == 14


def test_parentheses():
    assert safe_calculate("(2 + 3) * 4") == 20


def test_function_calls_rejected():
    with pytest.raises(ValueError):
        safe_calculate("__import__('os')")


def test_attributes_rejected():
    with pytest.raises(ValueError):
        safe_calculate("(1).__class__")
