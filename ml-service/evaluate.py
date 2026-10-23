# evaluate.py
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold

from preprocess import load_clean_data, get_X_y
from speciality_map import DISEASE_TO_SPECIALITY

RANDOM_STATE = 42
REPEATS = 20                      # har level pe 20 baar random symptoms hatayenge
LEVELS = [None, 8, 5, 3, 2]       # None = saare symptoms, baaki = sirf itne symptoms rakho
rng = np.random.default_rng(RANDOM_STATE)


def keep_only_n_symptoms(X, n):
    """Har row me sirf n symptoms rakho, baaki random hata do (0 kar do)."""
    arr = X.to_numpy().copy()
    for i in range(arr.shape[0]):
        present = np.flatnonzero(arr[i])             # jo symptoms 1 hain unke index
        if len(present) > n:
            drop = rng.choice(present, size=len(present) - n, replace=False)
            arr[i, drop] = 0
    return pd.DataFrame(arr, columns=X.columns)


def main():
    df = load_clean_data()
    X, y, _ = get_X_y(df)
    print("Average symptoms per row in data:", round(X.sum(axis=1).mean(), 1))

    # 5 folds: har row ek baar test me aayegi (poore 304 rows pe evaluation)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    folds = list(cv.split(X, y))

    models = []
    for train_idx, _ in folds:
        m = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE)
        m.fit(X.iloc[train_idx], y.iloc[train_idx])
        models.append(m)

    print(f"\n{'Input':14s}{'Top-1':>8s}{'Top-3':>8s}{'Speciality':>12s}")
    for n in LEVELS:
        top1 = top3 = spec = total = 0
        mistakes = Counter()

        for model, (_, test_idx) in zip(models, folds):
            X_te = X.iloc[test_idx]
            y_te = y.iloc[test_idx].to_numpy()

            for _ in range(1 if n is None else REPEATS):
                Xd = X_te if n is None else keep_only_n_symptoms(X_te, n)

                order = np.argsort(model.predict_proba(Xd), axis=1)
                pred = model.classes_[order[:, -1]]          # sabse badi probability
                top3_labels = model.classes_[order[:, -3:]]  # top 3 diseases

                for true, p, row in zip(y_te, pred, top3_labels):
                    total += 1
                    top1 += int(true == p)
                    top3 += int(true in row)
                    spec += int(DISEASE_TO_SPECIALITY[true] == DISEASE_TO_SPECIALITY[p])
                    if true != p:
                        mistakes[(true, p)] += 1

        label = "all symptoms" if n is None else f"{n} symptoms"
        print(f"{label:14s}{top1/total:8.3f}{top3/total:8.3f}{spec/total:12.3f}")

        if n == 3:
            print("   Sabse common galtiyan (3 symptoms pe):")
            for (true, p), c in mistakes.most_common(8):
                print(f"     {true}  ->  {p}   ({c} baar)")


if __name__ == "__main__":
    main()