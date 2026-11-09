from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).parent / "classifier.pkl"
_model = None


def _load():
    global _model
    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    return _model


def reload_model() -> bool:
    """Call after retraining so the API picks up the new file."""
    global _model
    _model = None
    return _load() is not None


def predict_category(description: str):
    """Returns (category_name, confidence) or None if no model is trained yet."""
    model = _load()
    if model is None:
        return None
    probs = model.predict_proba([description.lower()])[0]
    i = int(probs.argmax())
    return str(model.classes_[i]), float(probs[i])