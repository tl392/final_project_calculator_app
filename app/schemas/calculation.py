from enum import Enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator


class CalculationType(str, Enum):
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"
    EXPONENTIATION = "exponentiation"
    MODULUS = "modulus"
    SQRT = "sqrt"


class CalculationBase(BaseModel):
    type: CalculationType = Field(..., description="Type of calculation", example="addition")
    inputs: List[float] = Field(..., description="List of numeric inputs for the calculation", example=[10.5, 3])

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value):
        allowed = {e.value for e in CalculationType}
        if not isinstance(value, str) or value.lower() not in allowed:
            raise ValueError(f"Type must be one of: {', '.join(sorted(allowed))}")
        return value.lower()

    @field_validator("inputs", mode="before")
    @classmethod
    def check_inputs_is_list(cls, value):
        if not isinstance(value, list):
            raise ValueError("Input should be a valid list")
        return value

    @model_validator(mode='after')
    def validate_inputs(self):
        rules = {
            CalculationType.ADDITION: (2, None),
            CalculationType.SUBTRACTION: (2, None),
            CalculationType.MULTIPLICATION: (2, None),
            CalculationType.DIVISION: (2, None),
            CalculationType.EXPONENTIATION: (2, 2),
            CalculationType.MODULUS: (2, 2),
            CalculationType.SQRT: (1, 1),
        }
        min_items, exact_items = rules[self.type]
        if exact_items is not None and len(self.inputs) != exact_items:
            raise ValueError(f"{self.type.value} requires exactly {exact_items} number(s)")
        if len(self.inputs) < min_items:
            raise ValueError("At least two numbers are required for calculation")
        if self.type == CalculationType.DIVISION and any(x == 0 for x in self.inputs[1:]):
            raise ValueError("Cannot divide by zero")
        if self.type == CalculationType.MODULUS and self.inputs[1] == 0:
            raise ValueError("Cannot perform modulus by zero")
        if self.type == CalculationType.SQRT and self.inputs[0] < 0:
            raise ValueError("Cannot take square root of a negative number")
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"type": "addition", "inputs": [10.5, 3, 2]},
                {"type": "sqrt", "inputs": [81]},
                {"type": "modulus", "inputs": [10, 3]},
            ]
        },
    )


class CalculationCreate(CalculationBase):
    user_id: UUID = Field(..., description="UUID of the user who owns this calculation")


class CalculationUpdate(BaseModel):
    inputs: Optional[List[float]] = Field(None, description="Updated list of numeric inputs for the calculation")

    @field_validator("inputs", mode="before")
    @classmethod
    def check_inputs_is_list(cls, value):
        if value is not None and not isinstance(value, list):
            raise ValueError("Input should be a valid list")
        return value

    @model_validator(mode='after')
    def validate_inputs(self):
        if self.inputs is not None and len(self.inputs) == 0:
            raise ValueError("At least one number is required for calculation")
        return self

    model_config = ConfigDict(from_attributes=True, json_schema_extra={"example": {"inputs": [42, 7]}})


class CalculationResponse(CalculationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    result: float

    model_config = ConfigDict(from_attributes=True)
