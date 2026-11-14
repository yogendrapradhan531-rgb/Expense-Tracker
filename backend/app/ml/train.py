"""Model training pipeline using Scikit-Learn (TF-IDF + Logistic Regression).

Usage:
    python -m app.ml.train (from backend/)
"""
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_PATH = Path(__file__).parent / "classifier.pkl"

# Starter seed dataset covering everyday transaction descriptions
SAMPLES = {
    "Food & Dining": [
        "Starbucks Coffee downtown", "McDonalds burger meal", "Dominos pizza order",
        "Zomato food delivery", "Swiggy dinner order", "Cafe Coffee Day", "KFC chicken bucket",
        "Subway sandwich lunch", "Restaurant dinner with friends", "Biryani house",
        "Dunkin donuts", "Chipotle burrito bowl", "Uber Eats order",
    ],
    "Groceries": [
        "Walmart grocery shopping", "Whole Foods market", "BigBasket vegetables",
        "Costco bulk groceries", "Fresh fruits and vegetables", "DMart supermarket",
        "Trader Joes", "Milk eggs and bread", "Reliance Fresh", "Kroger weekly groceries",
        "Blinkit groceries", "Instamart essentials",
    ],
    "Utilities": [
        "Electricity bill payment", "Water bill", "Internet broadband bill", "Airtel postpaid recharge",
        "Jio mobile recharge", "Gas cylinder refill", "Comcast cable bill", "Phone bill Verizon",
        "BESCOM power bill", "Sewage and waste charges", "Wifi monthly plan",
    ],
    "Entertainment": [
        "Netflix subscription", "Spotify premium", "Movie tickets PVR", "Amazon Prime video",
        "Steam game purchase", "Concert tickets", "Disney Plus subscription", "BookMyShow booking",
        "PlayStation store", "YouTube Premium", "Bowling alley night", "Hotstar subscription",
    ],
    "Travel": [
        "Uber ride to airport", "Ola cab", "Flight ticket Delta", "IndiGo airline booking",
        "Hotel booking Marriott", "Airbnb stay", "Train ticket IRCTC", "Petrol pump fuel",
        "Shell gas station", "Metro card recharge", "Booking.com hotel", "Lyft ride",
        "Toll plaza charges", "Bus ticket RedBus",
    ],
    "Shopping": [
        "Amazon order electronics", "Flipkart purchase", "Nike running shoes", "Zara clothing",
        "H&M apparel", "IKEA furniture", "Myntra fashion order", "Best Buy laptop",
        "Apple store accessories", "Target household items", "Uniqlo jacket", "Nykaa cosmetics",
    ],
    "Healthcare": [
        "Apollo pharmacy medicines", "Doctor consultation fee", "CVS pharmacy", "Dental checkup",
        "Hospital bill", "Lab blood test", "Health insurance premium", "Eye exam and glasses",
        "Walgreens prescription", "Physiotherapy session", "Practo appointment", "1mg medicines order",
    ],
}


def build_dataset():
    """Combines seed training samples with verified user corrections from PostgreSQL."""
    texts, labels = [], []
    for label, items in SAMPLES.items():
        for t in items:
            texts.append(t.lower())
            labels.append(label)

    # Active learning loop: incorporate user-confirmed transactions (is_predicted = False)
    try:
        from app.database import SessionLocal
        from app.models import Transaction

        db = SessionLocal()
        try:
            rows = (
                db.query(Transaction)
                .filter(Transaction.is_predicted.is_(False), Transaction.category_id.isnot(None))
                .all()
            )
            for r in rows:
                texts.append(r.description.lower())
                labels.append(r.category.name)
            print(f"Added {len(rows)} user-labelled transactions from the DB.")
        finally:
            db.close()
    except Exception as e:
        print(f"Skipping DB data ({e})")

    return texts, labels


def train():
    """Trains the NLP classification pipeline and serializes the resulting model artifact."""
    texts, labels = build_dataset()
    
    # Character n-grams (analyzer='char_wb') effectively handle merchant abbreviations, typos, and brands
    model = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=2000, C=10)),
    ])
    model.fit(texts, labels)
    joblib.dump(model, MODEL_PATH)
    print(f"Trained on {len(texts)} samples -> {MODEL_PATH}")
    return len(texts)


if __name__ == "__main__":
    train()
