# preprocess.py
import json
import pandas as pd
from speciality_map import DISEASE_TO_SPECIALITY


def load_clean_data(path="data/Training.csv"):
    df = pd.read_csv(path)

    # 1. Khali extra column hatao
    df = df.drop(columns=["Unnamed: 133"], errors="ignore")

    # 2. Disease ke naam ke extra spaces saaf karo
    df["prognosis"] = (
        df["prognosis"].str.strip().str.replace(r"\s+", " ", regex=True)
    )

    # 3. Duplicate rows hatao (data leakage rokne ke liye)
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True).copy()
    print(f"Rows: {before} -> {len(df)} (duplicates hataye)")

    # 4. Har disease ke liye speciality dhundo
    unmapped = set(df["prognosis"]) - set(DISEASE_TO_SPECIALITY)
    if unmapped:
        raise ValueError(f"Ye diseases mapping me nahi hain: {unmapped}")
    df["speciality"] = df["prognosis"].map(DISEASE_TO_SPECIALITY)

    return df


def get_X_y(df):
    # Features = saare symptom columns, label = disease
    symptom_cols = [c for c in df.columns if c not in ("prognosis", "speciality")]
    X = df[symptom_cols]
    y = df["prognosis"]
    return X, y, symptom_cols


if __name__ == "__main__":
    df = load_clean_data()
    X, y, symptom_cols = get_X_y(df)

    print("Features (X):", X.shape)
    print("Label (y):", y.shape)
    print("\nSpeciality counts:")
    print(df["speciality"].value_counts())
    print("\nPer disease rows (min/max):", y.value_counts().min(), y.value_counts().max())

    # API ko baad me yahi symptom order chahiye
    with open("symptoms.json", "w") as f:
        json.dump(symptom_cols, f)

    df.to_csv("data/clean.csv", index=False)
    print("\nSaved: symptoms.json, data/clean.csv")