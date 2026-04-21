from math import sqrt
from typing import Union

Number = Union[int, float]


def add(a: Number, b: Number) -> Number:
    return a + b


def subtract(a: Number, b: Number) -> Number:
    return a - b


def multiply(a: Number, b: Number) -> Number:
    return a * b


def divide(a: Number, b: Number) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero!")
    return a / b


def power(a: Number, b: Number) -> float:
    return float(a ** b)


def modulus(a: Number, b: Number) -> float:
    if b == 0:
        raise ValueError("Cannot perform modulus by zero!")
    return float(a % b)


def sqrt_value(a: Number) -> float:
    if a < 0:
        raise ValueError("Cannot take square root of a negative number!")
    return float(sqrt(a))
