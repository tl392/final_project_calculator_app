import math
import pytest

from app.operations import add, subtract, multiply, divide, power, modulus, sqrt_value

Number = float


@pytest.mark.parametrize("a,b,expected", [(2, 3, 5), (-2, 3, 1), (2.5, 3, 5.5)])
def test_add(a, b, expected):
    assert add(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [(5, 3, 2), (5.5, 2, 3.5), (-2, 3, -5)])
def test_subtract(a, b, expected):
    assert subtract(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [(2, 3, 6), (-2, 3, -6), (2.5, 4, 10)])
def test_multiply(a, b, expected):
    assert multiply(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [(6, 3, 2), (-6, 3, -2), (5, 2, 2.5)])
def test_divide(a, b, expected):
    assert divide(a, b) == expected


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(6, 0)


@pytest.mark.parametrize("a,b,expected", [(2, 3, 8), (9, 0.5, 3), (10, 2, 100)])
def test_power(a, b, expected):
    assert power(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [(10, 3, 1), (20, 6, 2), (9, 2, 1)])
def test_modulus(a, b, expected):
    assert modulus(a, b) == expected


def test_modulus_by_zero():
    with pytest.raises(ValueError, match="Cannot perform modulus by zero"):
        modulus(10, 0)


@pytest.mark.parametrize("value,expected", [(81, 9), (0, 0), (2.25, 1.5)])
def test_sqrt_value(value, expected):
    assert math.isclose(sqrt_value(value), expected)


def test_sqrt_value_negative():
    with pytest.raises(ValueError, match="Cannot take square root of a negative number"):
        sqrt_value(-1)
