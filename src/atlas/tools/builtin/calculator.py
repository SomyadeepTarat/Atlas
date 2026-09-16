import ast
import math
import operator
from collections.abc import Callable

from pydantic import BaseModel, Field

from atlas.tools.base import Tool
from atlas.tools.types import (
    ToolPermission,
    ToolPolicy,
    ToolRisk,
)

MAX_ABS_NUMBER = 1_000_000_000_000
MAX_EXPONENT = 100


class CalculatorInput(BaseModel):
    expression: str = Field(
        min_length=1,
        max_length=500,
    )


class CalculatorOutput(BaseModel):
    result: float


BinaryOperator = Callable[
    [float, float],
    float,
]

UnaryOperator = Callable[
    [float],
    float,
]


_ALLOWED_BINARY_OPERATORS: dict[
    type[ast.operator],
    BinaryOperator,
] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}


_ALLOWED_UNARY_OPERATORS: dict[
    type[ast.unaryop],
    UnaryOperator,
] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _validate_number(
    value: float,
) -> float:
    if not math.isfinite(value):
        raise ValueError("Numeric result must be finite.")

    if abs(value) > MAX_ABS_NUMBER:
        raise ValueError("Numeric value exceeds allowed range.")

    return value


def _evaluate_node(
    node: ast.AST,
) -> float:
    if isinstance(
        node,
        ast.Constant,
    ):
        if isinstance(node.value, bool) or not isinstance(
            node.value,
            (int, float),
        ):
            raise ValueError("Only numbers are allowed.")

        return _validate_number(float(node.value))

    if isinstance(
        node,
        ast.BinOp,
    ):
        binary_operator_fn = _ALLOWED_BINARY_OPERATORS.get(type(node.op))

        if binary_operator_fn is None:
            raise ValueError("Unsupported operator.")

        left = _evaluate_node(node.left)

        right = _evaluate_node(node.right)

        if isinstance(
            node.op,
            ast.Pow,
        ):
            if abs(right) > MAX_EXPONENT:
                raise ValueError("Exponent exceeds allowed range.")

        result = binary_operator_fn(
            left,
            right,
        )

        return _validate_number(float(result))

    if isinstance(
        node,
        ast.UnaryOp,
    ):
        unary_operator_fn = _ALLOWED_UNARY_OPERATORS.get(type(node.op))

        if unary_operator_fn is None:
            raise ValueError("Unsupported unary operator.")

        value = _evaluate_node(node.operand)

        result = unary_operator_fn(value)

        return _validate_number(float(result))

    raise ValueError("Unsupported expression.")


def safe_calculate(
    expression: str,
) -> float:
    parsed = ast.parse(
        expression,
        mode="eval",
    )

    return _evaluate_node(parsed.body)


class CalculatorTool(
    Tool[
        CalculatorInput,
        CalculatorOutput,
    ]
):
    name = "calculate"

    description = "Safely evaluate arithmetic expressions."

    input_schema = CalculatorInput
    output_schema = CalculatorOutput

    policy = ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        required_permissions=frozenset(
            {
                ToolPermission.CALCULATE,
            }
        ),
        requires_approval=False,
        timeout_seconds=2.0,
        max_attempts=1,
        idempotent=True,
    )

    async def execute(
        self,
        input_data: CalculatorInput,
    ) -> CalculatorOutput:
        try:
            result = safe_calculate(input_data.expression)

        except (
            SyntaxError,
            ValueError,
            ZeroDivisionError,
            OverflowError,
        ) as exc:
            raise ValueError("Invalid calculator expression.") from exc

        return CalculatorOutput(
            result=result,
        )
