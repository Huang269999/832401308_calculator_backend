"""Safe mathematical expression parser and evaluator."""

from __future__ import annotations

import ast
import math
import operator
from numbers import Real


class CalculationError(ValueError):
    """Raised when an expression cannot be safely calculated."""


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_MAX_EXPRESSION_LENGTH = 200
_MAX_AST_NODES = 100
_MAX_ABS_NUMBER = 1e100


def normalize_expression(expression: str) -> str:
    """Normalize symbols used by the UI to Python-style arithmetic symbols."""
    return expression.replace("×", "*").replace("÷", "/").strip()


def calculate_expression(expression: str) -> int | float:
    """Safely calculate a basic arithmetic expression without eval/exec."""
    if not isinstance(expression, str):
        raise CalculationError("表达式必须是字符串")

    normalized = normalize_expression(expression)
    if not normalized:
        raise CalculationError("表达式不能为空")
    if len(normalized) > _MAX_EXPRESSION_LENGTH:
        raise CalculationError("表达式过长")

    try:
        tree = ast.parse(normalized, mode="eval")
    except (SyntaxError, ValueError) as exc:
        raise CalculationError("表达式格式错误") from exc

    if sum(1 for _ in ast.walk(tree)) > _MAX_AST_NODES:
        raise CalculationError("表达式过于复杂")

    result = _evaluate_node(tree.body)
    if not isinstance(result, Real) or isinstance(result, bool):
        raise CalculationError("计算结果非法")
    if isinstance(result, float) and not math.isfinite(result):
        raise CalculationError("计算结果超出有效范围")
    if abs(result) > _MAX_ABS_NUMBER:
        raise CalculationError("计算结果过大")

    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result


def _evaluate_node(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant):
        value = node.value
        if type(value) not in (int, float):
            raise CalculationError("表达式中包含非法内容")
        if isinstance(value, float) and not math.isfinite(value):
            raise CalculationError("数字超出有效范围")
        if abs(value) > _MAX_ABS_NUMBER:
            raise CalculationError("数字过大")
        return value

    if isinstance(node, ast.BinOp):
        operator_type = type(node.op)
        if operator_type not in _BINARY_OPERATORS:
            raise CalculationError("包含不支持的运算符")

        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        if operator_type is ast.Div and right == 0:
            raise CalculationError("除数不能为 0")

        result = _BINARY_OPERATORS[operator_type](left, right)
        if isinstance(result, float) and not math.isfinite(result):
            raise CalculationError("计算结果超出有效范围")
        if abs(result) > _MAX_ABS_NUMBER:
            raise CalculationError("计算结果过大")
        return result

    if isinstance(node, ast.UnaryOp):
        operator_type = type(node.op)
        if operator_type not in _UNARY_OPERATORS:
            raise CalculationError("包含不支持的一元运算符")
        return _UNARY_OPERATORS[operator_type](_evaluate_node(node.operand))

    raise CalculationError("表达式中包含非法内容")
