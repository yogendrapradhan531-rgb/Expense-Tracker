"""Pydantic schemas for request validation and API response serialization."""
from datetime import date as date_type, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Category Schemas ----------
class CategoryOut(BaseModel):
    """Schema for returning category details."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


# ---------- Transaction Schemas ----------
class TransactionCreate(BaseModel):
    """Schema for creating a new transaction. Leaving category_id empty triggers ML prediction."""
    date: date_type
    description: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(gt=0)
    category_id: int | None = None  # None indicates automatic ML classification


class TransactionUpdate(BaseModel):
    """Schema for updating an existing transaction (supports partial updates)."""
    date: date_type | None = None
    description: str | None = Field(default=None, min_length=1, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0)
    category_id: int | None = None


class TransactionOut(BaseModel):
    """Schema for serializing transaction records in responses."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date_type
    description: str
    amount: float
    category_id: int | None
    category: CategoryOut | None
    is_predicted: bool
    created_at: datetime


# ---------- ML Prediction Schemas ----------
class PredictRequest(BaseModel):
    """Schema for real-time category prediction requests."""
    description: str


class PredictResponse(BaseModel):
    """Schema returning predicted category name and classifier confidence score."""
    category: str | None
    confidence: float | None


# ---------- Analytics & Summary Schemas ----------
class SummaryItem(BaseModel):
    """Schema for category spending totals in summary charts."""
    category: str
    total: float
