import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime

from app.schemas.calculation import CalculationCreate, CalculationUpdate, CalculationResponse


def test_calculation_create_valid_exponentiation():
    calc = CalculationCreate(type='exponentiation', inputs=[2, 4], user_id=uuid4())
    assert calc.type == 'exponentiation'
    assert calc.inputs == [2.0, 4.0]


def test_calculation_create_valid_sqrt():
    calc = CalculationCreate(type='sqrt', inputs=[81], user_id=uuid4())
    assert calc.type == 'sqrt'
    assert calc.inputs == [81.0]


def test_calculation_create_invalid_modulus_zero():
    with pytest.raises(ValidationError, match='Cannot perform modulus by zero'):
        CalculationCreate(type='modulus', inputs=[10, 0], user_id=uuid4())


def test_calculation_create_invalid_sqrt_negative():
    with pytest.raises(ValidationError, match='Cannot take square root of a negative number'):
        CalculationCreate(type='sqrt', inputs=[-4], user_id=uuid4())


def test_calculation_create_invalid_exponentiation_length():
    with pytest.raises(ValidationError, match='requires exactly 2'):
        CalculationCreate(type='exponentiation', inputs=[2, 3, 4], user_id=uuid4())


def test_calculation_update_valid():
    update = CalculationUpdate(inputs=[42, 7])
    assert update.inputs == [42.0, 7.0]


def test_calculation_update_invalid_empty_list():
    with pytest.raises(ValidationError, match='At least one number is required'):
        CalculationUpdate(inputs=[])


def test_calculation_response_model():
    payload = {
        'id': uuid4(),
        'user_id': uuid4(),
        'type': 'modulus',
        'inputs': [10, 3],
        'result': 1,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    response = CalculationResponse(**payload)
    assert response.type == 'modulus'
    assert response.result == 1
