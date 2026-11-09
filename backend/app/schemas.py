from datetime import date as date_type, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TransactionCreate(BaseModel):
    date: date_type
    description: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0)
    category_id: int | None = None  # leave empty -> ML predicts


class TransactionUpdate(BaseModel):
    date: date_type | None = None
    description: str | None = Field(default=None, min_length=1, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0)
    category_id: int | None = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date_type
    description: str
    amount: float
    category_id: int | None
    category: CategoryOut | None
    is_predicted: bool
    created_at: datetime


class PredictRequest(BaseModel):
    description: str


class PredictResponse(BaseModel):
    category: str | None
    confidence: float | None


class SummaryItem(BaseModel):
    category: str
    total: float