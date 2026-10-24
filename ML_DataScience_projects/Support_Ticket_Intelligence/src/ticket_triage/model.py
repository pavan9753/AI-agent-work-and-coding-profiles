from dataclasses import dataclass

import joblib

from ticket_triage.settings import MODEL_PATH


@dataclass(frozen=True)
class CategoryScore:
    category: str
    probability: float


@dataclass(frozen=True)
class TicketPrediction:
    category: str
    confidence: float
    ranked_categories: tuple[CategoryScore, ...]


class TicketClassifier:
    def __init__(self, artifact_path=MODEL_PATH):
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {artifact_path}. "
                "Run `python -m ticket_triage.train` first."
            )
        artifact = joblib.load(artifact_path)
        self.pipeline = artifact["pipeline"]
        self.categories = tuple(artifact["categories"])

    def predict(self, message: str) -> TicketPrediction:
        cleaned = message.strip()
        if not cleaned:
            raise ValueError("Enter a ticket message before classifying it.")

        probabilities = self.pipeline.predict_proba([cleaned])[0]
        order = probabilities.argsort()[::-1]
        ranked = tuple(
            CategoryScore(
                category=str(self.pipeline.classes_[index]),
                probability=float(probabilities[index]),
            )
            for index in order
        )
        return TicketPrediction(
            category=ranked[0].category,
            confidence=ranked[0].probability,
            ranked_categories=ranked,
        )
