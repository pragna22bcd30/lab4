from fastapi import FastAPI, Body
import joblib

app = FastAPI()

model = joblib.load("model/model.pkl")

@app.post("/predict")
def predict(features: list = Body(...)):
    """
    Predict wine quality given input features.
    Input: JSON list of numerical features
    Output: JSON with name, roll number, and predicted wine quality
    """
    prediction = model.predict([features])[0]

    return {
        "name": "Pragna Sri C",
        "roll_no": "2022BCD0030",
        "wine_quality": int(round(prediction))
    }
