from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Load the trained model
model = joblib.load("final_xgboost_model.pkl")

# Open-Meteo setup
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Define the input schema for prediction


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


# Initialize FastAPI app
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
        # Convert input data to DataFrame
        input_data = pd.DataFrame([data.dict()])

        # Perform prediction
        prediction = model.predict(input_data)[0]
        # Convert to Python float for JSON compatibility
        prediction = float(prediction)

        return {"PredictedFloodProbability": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/query-weather")
def query_weather(
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location"),
):
    try:
        # Open-Meteo API parameters
        url = "https://flood-api.open-meteo.com/v1/flood"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "river_discharge", "river_discharge_mean", "river_discharge_median",
                "river_discharge_max", "river_discharge_min", "river_discharge_p25",
                "river_discharge_p75"
            ],
            "models": "forecast_v4",
            "forecast_days": 183,
        }

        # Fetch data from Open-Meteo API
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]  # Process the first location response

        # Extract daily data
        daily = response.Daily()

        daily_data = [
            {
                "date": date,
                "river_discharge": river_discharge,
                "river_discharge_mean": river_discharge_mean,
                "river_discharge_median": river_discharge_median,
                "river_discharge_max": river_discharge_max,
                "river_discharge_min": river_discharge_min,
                "river_discharge_p25": river_discharge_p25,
                "river_discharge_p75": river_discharge_p75,
            }
            for date, river_discharge, river_discharge_mean, river_discharge_median,
            river_discharge_max, river_discharge_min, river_discharge_p25, river_discharge_p75
            in zip(
                pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left"
                ).strftime('%Y-%m-%d').tolist(),
                sanitize_values(daily.Variables(0).ValuesAsNumpy()),
                sanitize_values(daily.Variables(1).ValuesAsNumpy()),
                sanitize_values(daily.Variables(2).ValuesAsNumpy()),
                sanitize_values(daily.Variables(3).ValuesAsNumpy()),
                sanitize_values(daily.Variables(4).ValuesAsNumpy()),
                sanitize_values(daily.Variables(5).ValuesAsNumpy()),
                sanitize_values(daily.Variables(6).ValuesAsNumpy()),
            )
        ]

        return {
            "coordinates": {
                "latitude": sanitize_values(response.Latitude()),
                "longitude": sanitize_values(response.Longitude()),
                "elevation": sanitize_values(response.Elevation()),
                "timezone": sanitize_values(response.Timezone()),
                "timezone_abbreviation": sanitize_values(response.TimezoneAbbreviation()),
                "utc_offset_seconds": sanitize_values(response.UtcOffsetSeconds()),
            },
            "daily_data": daily_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def sanitize_values(data):
    """
    Replace NaN, Infinity, and -Infinity with 0 or a default value.
    Convert to a JSON-compliant list.
    """
    return pd.Series(data).replace([float("inf"), float("-inf")], '').fillna('').tolist()
