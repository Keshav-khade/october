# app.py
import json
from typing import List
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from speciality_map import DISEASE_TO_SPECIALITY

# ---- Server start hone par ek baar load (har request pe nahi) ----
model = joblib.load("model.pkl")
with open("symptoms.json") as f:
    SYMPTOMS = json.load(f)
SYMPTOM_INDEX = {name: i for i, name in enumerate(SYMPTOMS)}

MIN_SYMPTOMS = 3
LOW_CONFIDENCE = 0.30   # yeh andaza hai, baad me tune karenge
# Sirf andaza, kisi doctor ne validate nahi kiya
EMERGENCY_SYMPTOMS = {"chest_pain", "breathlessness", "weakness_of_one_body_side",
                      "altered_sensorium", "slurred_speech", "coma"}
DISCLAIMER = "Ye sirf suggestion hai, diagnosis nahi. Doctor se consult karein."

app = FastAPI(title="CareSync ML Service")


class PredictRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/symptoms")
def list_symptoms():
    return {"symptoms": SYMPTOMS}


@app.post("/predict")
def predict(req: PredictRequest):
    chosen = sorted({s.strip() for s in req.symptoms})

    unknown = [s for s in chosen if s not in SYMPTOM_INDEX]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown symptoms: {unknown}")
    if len(chosen) < MIN_SYMPTOMS:
        raise HTTPException(status_code=400,
                            detail=f"Kam se kam {MIN_SYMPTOMS} symptoms chuniye")

    # 132 columns ka 0/1 vector, wahi order jo training me tha
    row = [0] * len(SYMPTOMS)
    for s in chosen:
        row[SYMPTOM_INDEX[s]] = 1
    X = pd.DataFrame([row], columns=SYMPTOMS)

    proba = model.predict_proba(X)[0]

    # Top 3 diseases
    top_idx = proba.argsort()[::-1][:3]
    conditions = [
        {
            "disease": str(model.classes_[i]),
            "score": round(float(proba[i]), 3),
            "speciality": DISEASE_TO_SPECIALITY[model.classes_[i]],
        }
        for i in top_idx
    ]

    # Speciality-wise score = us speciality ki sab diseases ki probability ka jod
    spec_scores = {}
    for disease, p in zip(model.classes_, proba):
        spec = DISEASE_TO_SPECIALITY[disease]
        spec_scores[spec] = spec_scores.get(spec, 0.0) + float(p)

    low_confidence = conditions[0]["score"] < LOW_CONFIDENCE
    speciality = "General Physician" if low_confidence else max(spec_scores, key=spec_scores.get)

    return {
        "conditions": conditions,
        "speciality": speciality,
        "speciality_scores": {k: round(v, 3) for k, v in spec_scores.items()},
        "low_confidence": low_confidence,
        "emergency": bool(EMERGENCY_SYMPTOMS & set(chosen)),
        "disclaimer": DISCLAIMER,
    }