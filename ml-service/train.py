# train.py
import joblib
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

from preprocess import load_clean_data, get_X_y
from speciality_map import DISEASE_TO_SPECIALITY

RANDOM_STATE = 42


def top_k_accuracy(model, X_test, y_test, k=3):
    proba = model.predict_proba(X_test)                  # har disease ki probability
    top_k_idx = np.argsort(proba, axis=1)[:, -k:]        # sabse badi k ke index
    top_k_labels = model.classes_[top_k_idx]             # index -> disease ka naam
    hits = [true in row for true, row in zip(y_test, top_k_labels)]
    return float(np.mean(hits))


def main():
    df = load_clean_data()
    X, y, symptom_cols = get_X_y(df)

    # ---- 1. Models ka comparison (cross-validation) ----
    models = {
        "Naive Bayes": BernoulliNB(),
        "Decision Tree": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X, y, cv=cv)
        results[name] = scores.mean()
        print(f"{name:15s} CV accuracy: {scores.mean():.3f} (+/- {scores.std():.3f})")

    best_name = max(results, key=results.get)
    print("\nBest model:", best_name)

    # ---- 2. Hold-out test ----
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    model = models[best_name]
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"\nTest accuracy (disease)   : {accuracy_score(y_test, y_pred):.3f}")
    print(f"Test top-3 accuracy       : {top_k_accuracy(model, X_test, y_test):.3f}")

    true_spec = y_test.map(DISEASE_TO_SPECIALITY)
    pred_spec = [DISEASE_TO_SPECIALITY[d] for d in y_pred]
    print(f"Test accuracy (speciality): {accuracy_score(true_spec, pred_spec):.3f}")

    # ---- 3. Final model: poore data pe train karke save ----
    model.fit(X, y)
    joblib.dump(model, "model.pkl")
    print("\nSaved: model.pkl")


if __name__ == "__main__":
    main()