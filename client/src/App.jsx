import { useState } from "react";
import axios from "axios";
import "./App.css";

const App = () => {
  const [formData, setFormData] = useState({
    MonsoonIntensity: 2.5,
    TopographyDrainage: 3.1,
    RiverManagement: 4.2,
    Deforestation: 1.8,
    Urbanization: 3.3,
    ClimateChange: 4.0,
    DamsQuality: 2.9,
    Siltation: 3.7,
    AgriculturalPractices: 2.2,
    Encroachments: 3.5,
    IneffectiveDisasterPreparedness: 2.8,
    DrainageSystems: 4.3,
    CoastalVulnerability: 3.6,
    Landslides: 3.9,
    Watersheds: 4.1,
    DeterioratingInfrastructure: 2.7,
    PopulationScore: 3.4,
    WetlandLoss: 3.2,
    InadequatePlanning: 3.0,
    PoliticalFactors: 2.6,
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/predict",
        formData,
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      setResult(response.data.PredictedFloodProbability);
    } catch (err) {
      console.log(err);
      setError("Error fetching the prediction. Please try again.");
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Flood Prediction</h1>
        <form onSubmit={handleSubmit} className="form">
          {Object.keys(formData).map((field) => (
            <div key={field} className="form-group">
              <label htmlFor={field}>{field}</label>
              <input
                type="number"
                id={field}
                name={field}
                value={formData[field]}
                onChange={handleChange}
                required
              />
            </div>
          ))}
          <button type="submit">Get Prediction</button>
        </form>
        {result !== null && (
          <div className="result">
            <h2>Predicted Flood Probability:</h2>
            <p>{result.toFixed(2)}%</p>
          </div>
        )}
        {error && <p className="error">{error}</p>}
      </header>
    </div>
  );
};

export default App;
