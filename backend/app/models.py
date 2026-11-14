"""SQLAlchemy database models for Categories and Transactions."""
from datetime import date as date_type, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    """Category table storing expense classifications (e.g., Food & Dining, Utilities)."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relationship linking back to all transactions assigned to this category
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")


class Transaction(Base):
    """Transaction table storing expense records with ML prediction metadata."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Foreign key referencing categories table; set to NULL if a category is deleted
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    
    # Flag to track whether the category was auto-assigned by the ML model
    # When a user updates/corrects this category, is_predicted becomes False (feedback loop)
    is_predicted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship to parent Category model
    category: Mapped[Category | None] = relationship(back_populates="transactions")

    # Composite indexes for optimized querying by date and category
    __table_args__ = (
        Index("ix_transactions_date", "date"),
        Index("ix_transactions_category_id", "category_id"),
    )
