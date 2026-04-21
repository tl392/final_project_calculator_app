import uuid
import pytest

from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Exponentiation,
    Modulus,
    SquareRoot,
)


def dummy_user_id():
    return uuid.uuid4()


def test_addition_get_result():
    calc = Addition(user_id=dummy_user_id(), inputs=[10, 5, 3.5])
    assert calc.get_result() == 18.5


def test_subtraction_get_result():
    calc = Subtraction(user_id=dummy_user_id(), inputs=[20, 5, 3])
    assert calc.get_result() == 12


def test_multiplication_get_result():
    calc = Multiplication(user_id=dummy_user_id(), inputs=[2, 3, 4])
    assert calc.get_result() == 24


def test_division_get_result():
    calc = Division(user_id=dummy_user_id(), inputs=[100, 2, 5])
    assert calc.get_result() == 10


def test_exponentiation_get_result():
    calc = Exponentiation(user_id=dummy_user_id(), inputs=[2, 3])
    assert calc.get_result() == 8


def test_modulus_get_result():
    calc = Modulus(user_id=dummy_user_id(), inputs=[10, 3])
    assert calc.get_result() == 1


def test_square_root_get_result():
    calc = SquareRoot(user_id=dummy_user_id(), inputs=[81])
    assert calc.get_result() == 9


def test_division_by_zero():
    calc = Division(user_id=dummy_user_id(), inputs=[50, 0, 5])
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.get_result()


def test_modulus_by_zero():
    calc = Modulus(user_id=dummy_user_id(), inputs=[50, 0])
    with pytest.raises(ValueError, match="Cannot perform modulus by zero"):
        calc.get_result()


def test_square_root_negative_value():
    calc = SquareRoot(user_id=dummy_user_id(), inputs=[-4])
    with pytest.raises(ValueError, match="Cannot take square root of a negative number"):
        calc.get_result()


@pytest.mark.parametrize(
    "calculation_type,expected_class,inputs,expected_result",
    [
        ('addition', Addition, [1, 2, 3], 6),
        ('subtraction', Subtraction, [10, 4], 6),
        ('multiplication', Multiplication, [3, 4, 2], 24),
        ('division', Division, [100, 2, 5], 10),
        ('exponentiation', Exponentiation, [2, 3], 8),
        ('modulus', Modulus, [10, 3], 1),
        ('sqrt', SquareRoot, [81], 9),
    ]
)
def test_calculation_factory(calculation_type, expected_class, inputs, expected_result):
    calc = Calculation.create(calculation_type=calculation_type, user_id=dummy_user_id(), inputs=inputs)
    assert isinstance(calc, expected_class)
    assert calc.get_result() == expected_result


def test_calculation_factory_invalid_type():
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create(calculation_type='unknown', user_id=dummy_user_id(), inputs=[1, 2])
