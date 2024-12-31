from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd

model = joblib.load("final_xgboost_model.pkl")


class FloodPredictionInput(BaseModel):
    MonsoonIntensity: float
    TopographyDrainage: float
    RiverManagement: float
    Deforestation: float
    Urbanization: float
    ClimateChange: float
    DamsQuality: float
    Siltation: float
    AgriculturalPractices: float
    Encroachments: float
    IneffectiveDisasterPreparedness: float
    DrainageSystems: float
    CoastalVulnerability: float
    Landslides: float
    Watersheds: float
    DeterioratingInfrastructure: float
    PopulationScore: float
    WetlandLoss: float
    InadequatePlanning: float
    PoliticalFactors: float


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Flood Prediction API!"}


@app.post("/predict")
def predict_flood(data: FloodPredictionInput):
    try:
        input_data = pd.DataFrame([data.dict()])

        prediction = model.predict(input_data)[0]

        prediction = float(prediction)

        return {"PredictedFloodProbability": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app using `uvicorn api:app --reload`
