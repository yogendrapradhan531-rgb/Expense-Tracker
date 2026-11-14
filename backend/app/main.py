"""FastAPI main application module exposing REST endpoints for transactions, categories, and ML categorisation."""
from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import Base, SessionLocal, engine, get_db
from app.ml.predict import predict_category, reload_model
from app.ml.train import train

# Default seed categories inserted into PostgreSQL on startup
DEFAULT_CATEGORIES = [
    "Food & Dining", "Groceries", "Utilities", "Entertainment",
    "Travel", "Shopping", "Healthcare",
]

# Minimum probability score required to assign an automated category
MIN_CONFIDENCE = 0.25


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager: handles schema initialization and category seeding."""
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed missing default categories
        existing = {c.name for c in db.query(models.Category).all()}
        db.add_all([models.Category(name=n) for n in DEFAULT_CATEGORIES if n not in existing])
        db.commit()
    finally:
        db.close()
    yield


app = FastAPI(
    title="Expense Tracker with ML Categorisation",
    description="Full-stack expense tracking system with automated NLP transaction categorisation.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS) for React frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def ml_category(db: Session, description: str):
    """Utility helper: predicts category for a given description and resolves it to a Category DB model."""
    result = predict_category(description)
    if not result:
        return None, None
    name, conf = result
    if conf < MIN_CONFIDENCE:
        return None, conf
    return db.query(models.Category).filter_by(name=name).first(), conf


# ---------- Category Endpoints ----------
@app.get("/categories", response_model=list[schemas.CategoryOut], tags=["Categories"])
def list_categories(db: Session = Depends(get_db)):
    """Fetch all available expense categories sorted alphabetically."""
    return db.query(models.Category).order_by(models.Category.name).all()


# ---------- Transaction Endpoints ----------
@app.get("/transactions", response_model=list[schemas.TransactionOut], tags=["Transactions"])
def list_transactions(
    category_id: int | None = None,
    start: date | None = None,
    end: date | None = None,
    limit: int = Query(200, le=1000),
    db: Session = Depends(get_db),
):
    """Retrieve expense transactions with optional filtering by category or date range."""
    q = db.query(models.Transaction).options(joinedload(models.Transaction.category))
    if category_id:
        q = q.filter(models.Transaction.category_id == category_id)
    if start:
        q = q.filter(models.Transaction.date >= start)
    if end:
        q = q.filter(models.Transaction.date <= end)
    return q.order_by(models.Transaction.date.desc(), models.Transaction.id.desc()).limit(limit).all()


@app.post("/transactions", response_model=schemas.TransactionOut, status_code=201, tags=["Transactions"])
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db)):
    """Create a new transaction. If category_id is omitted, the ML classifier predicts it automatically."""
    data = payload.model_dump()
    is_predicted = False

    # Automatically predict category if not manually selected
    if data["category_id"] is None:
        cat, _ = ml_category(db, data["description"])
        if cat:
            data["category_id"] = cat.id
            is_predicted = True
    elif not db.get(models.Category, data["category_id"]):
        raise HTTPException(400, "Invalid category_id")

    tx = models.Transaction(**data, is_predicted=is_predicted)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@app.put("/transactions/{tx_id}", response_model=schemas.TransactionOut, tags=["Transactions"])
def update_transaction(tx_id: int, payload: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    """Update transaction details. Manual category overrides reset is_predicted=False to feed the retraining loop."""
    tx = db.get(models.Transaction, tx_id)
    if not tx:
        raise HTTPException(404, "Transaction not found")

    changes = payload.model_dump(exclude_unset=True)
    if "category_id" in changes:
        if changes["category_id"] is not None and not db.get(models.Category, changes["category_id"]):
            raise HTTPException(400, "Invalid category_id")
        # Marking is_predicted as False turns user-corrected transactions into active training samples
        tx.is_predicted = False
    for k, v in changes.items():
        setattr(tx, k, v)

    db.commit()
    db.refresh(tx)
    return tx


@app.delete("/transactions/{tx_id}", status_code=204, tags=["Transactions"])
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    """Remove a transaction by ID."""
    tx = db.get(models.Transaction, tx_id)
    if not tx:
        raise HTTPException(404, "Transaction not found")
    db.delete(tx)
    db.commit()


# ---------- Analytics & Summary ----------
@app.get("/summary", response_model=list[schemas.SummaryItem], tags=["Analytics"])
def summary(start: date | None = None, end: date | None = None, db: Session = Depends(get_db)):
    """Aggregate total spending grouped by category for dashboard charts."""
    q = (
        db.query(
            func.coalesce(models.Category.name, "Uncategorised"),
            func.sum(models.Transaction.amount),
        )
        .select_from(models.Transaction)
        .outerjoin(models.Category, models.Transaction.category_id == models.Category.id)
    )
    if start:
        q = q.filter(models.Transaction.date >= start)
    if end:
        q = q.filter(models.Transaction.date <= end)
    rows = q.group_by(models.Category.name).all()
    return [{"category": name, "total": float(total)} for name, total in rows]


# ---------- Machine Learning Endpoints ----------
@app.post("/predict", response_model=schemas.PredictResponse, tags=["Machine Learning"])
def predict(payload: schemas.PredictRequest):
    """Predict category in real time as the user types a description."""
    result = predict_category(payload.description)
    if not result:
        return {"category": None, "confidence": None}
    return {"category": result[0], "confidence": round(result[1], 3)}


@app.post("/retrain", tags=["Machine Learning"])
def retrain():
    """Trigger background model retraining on the combined seed data and verified user transactions."""
    n = train()
    reload_model()
    return {"trained_on": n}
