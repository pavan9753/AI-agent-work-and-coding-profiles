import json

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from ticket_triage.settings import ARTIFACT_DIR, DATA_PATH, METRICS_PATH, MODEL_PATH


def build_pipeline() -> Pipeline:
    features = FeatureUnion(
        [
            (
                "word_tfidf",
                TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode", sublinear_tf=True),
            ),
            (
                "char_tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    strip_accents="unicode",
                    sublinear_tf=True,
                ),
            ),
        ]
    )
    return Pipeline(
        [
            ("features", features),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2_000,
                    random_state=42,
                ),
            ),
        ]
    )


def main() -> None:
    frame = pd.read_csv(DATA_PATH)
    required = {"message", "category"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Dataset must include columns: {', '.join(sorted(required))}")
    if frame[list(required)].isna().any().any():
        raise ValueError("Dataset contains empty messages or category labels.")

    train_text, test_text, train_labels, test_labels = train_test_split(
        frame["message"],
        frame["category"],
        test_size=0.25,
        random_state=42,
        stratify=frame["category"],
    )

    pipeline = build_pipeline()
    pipeline.fit(train_text, train_labels)
    predictions = pipeline.predict(test_text)
    report = classification_report(
        test_labels,
        predictions,
        output_dict=True,
        zero_division=0,
    )
    categories = sorted(frame["category"].unique().tolist())
    metrics = {
        "rows": int(len(frame)),
        "train_rows": int(len(train_text)),
        "test_rows": int(len(test_text)),
        "accuracy": float(accuracy_score(test_labels, predictions)),
        "macro_f1": float(f1_score(test_labels, predictions, average="macro")),
        "categories": categories,
        "classification_report": report,
        "confusion_matrix": confusion_matrix(
            test_labels,
            predictions,
            labels=categories,
        ).tolist(),
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "categories": categories}, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Rows: {metrics['rows']} (train={metrics['train_rows']}, test={metrics['test_rows']})")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"Macro F1: {metrics['macro_f1']:.3f}")
    print(classification_report(test_labels, predictions, zero_division=0))
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved evaluation: {METRICS_PATH}")


if __name__ == "__main__":
    main()
