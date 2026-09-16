import pytest

from atlas.tools.builtin.calculator import (
    safe_calculate,
)


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('echo pwned')",
        "(1).__class__",
        "open('/etc/passwd').read()",
        "globals()",
        "lambda: 1",
    ],
)
def test_python_execution_payloads_rejected(
    expression: str,
):
    with pytest.raises(ValueError):
        safe_calculate(expression)


def test_huge_exponent_rejected():
    with pytest.raises(ValueError):
        safe_calculate("2 ** 1000000")
