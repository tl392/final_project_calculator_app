from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReportUserInfo(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: str


class ReportCalculationPreview(BaseModel):
    id: UUID
    type: str
    inputs: List[float]
    result: float
    created_at: str


class ReportSummaryResponse(BaseModel):
    filters: Dict[str, Optional[str]]
    user: ReportUserInfo
    total_calculations: int
    count_by_type: Dict[str, int]
    average_of_operands: float
    average_operands_per_calculation: float
    calculations: List[ReportCalculationPreview]

    model_config = ConfigDict(from_attributes=True)
