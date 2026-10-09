import pytest

from app.calculator_service import CalculationError, calculate_expression


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1+2", 3),
        ("5-8", -3),
        ("3*7", 21),
        ("10/2", 5),
        ("1.5+2.8", 4.3),
        ("1+2*3", 7),
        ("(1+2)*3", 9),
        ("-5+8", 3),
        ("3*-2", -6),
        ("+5", 5),
        ("8÷4+2×3", 8),
    ],
)
def test_valid_expressions(expression, expected):
    assert calculate_expression(expression) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "1/0",
        "1+++",
        "2**8",
        "__import__('os').system('echo bad')",
        "[1, 2, 3]",
        "True+1",
    ],
)
def test_invalid_expressions(expression):
    with pytest.raises(CalculationError):
        calculate_expression(expression)
