"""Inference module for categorising transaction descriptions using the trained NLP pipeline."""
from pathlib import Path
import joblib

# Path to the serialized Scikit-learn model artifact
MODEL_PATH = Path(__file__).parent / "classifier.pkl"
_model = None


def _load():
    """Lazily loads the serialized model pipeline into memory on first invocation."""
    global _model
    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    return _model


def reload_model() -> bool:
    """Reloads the model from disk after a background retraining process finishes."""
    global _model
    _model = None
    return _load() is not None


def predict_category(description: str):
    """Predicts the category of a transaction based on its textual description.
    
    Returns:
        tuple (category_name: str, confidence: float) or None if model is unavailable.
    """
    model = _load()
    if model is None:
        return None
        
    # Get class probabilities from logistic regression
    probs = model.predict_proba([description.lower()])[0]
    best_index = int(probs.argmax())
    
    return str(model.classes_[best_index]), float(probs[best_index])
