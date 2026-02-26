from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from markov_golf_engine import GolfHole
from typing import List, Dict

app = FastAPI()

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GolfStats(BaseModel):
    driving_accuracy: float  # 0 to 1
    gir_fairway: float       # 0 to 1
    gir_rough: float         # 0 to 1
    putts_per_hole: float    # e.g., 1.6 to 2.5

@app.get("/presets")
def get_presets():
    return {
        "pro": {
            "driving_accuracy": 0.60,
            "gir_fairway": 0.80,
            "gir_rough": 0.50,
            "putts_per_hole": 1.64
        },
        "amateur": {
            "driving_accuracy": 0.40,
            "gir_fairway": 0.30,
            "gir_rough": 0.15,
            "putts_per_hole": 2.20
        }
    }

@app.post("/calculate")
def calculate_strokes(stats: GolfStats):
    states = ['Tee', 'Fairway', 'Rough', 'Bunker', 'Green', 'Hole']
    s = {state: i for i, state in enumerate(states)}
    P = np.zeros((len(states), len(states)))
    P[s['Hole'], s['Hole']] = 1.0

    # Tee logic
    P[s['Tee'], s['Fairway']] = stats.driving_accuracy
    P[s['Tee'], s['Rough']] = (1.0 - stats.driving_accuracy) * 0.8
    P[s['Tee'], s['Bunker']] = (1.0 - stats.driving_accuracy) * 0.2

    # Fairway logic
    P[s['Fairway'], s['Green']] = stats.gir_fairway
    P[s['Fairway'], s['Rough']] = (1.0 - stats.gir_fairway) * 0.7
    P[s['Fairway'], s['Bunker']] = (1.0 - stats.gir_fairway) * 0.3

    # Rough logic
    P[s['Rough'], s['Green']] = stats.gir_rough
    P[s['Rough'], s['Rough']] = (1.0 - stats.gir_rough) * 0.6
    P[s['Rough'], s['Bunker']] = (1.0 - stats.gir_rough) * 0.4

    # Bunker logic
    P[s['Bunker'], s['Green']] = 0.60
    P[s['Bunker'], s['Bunker']] = 0.10
    P[s['Bunker'], s['Rough']] = 0.30

    # Putting logic (Memoryless adjustment)
    green_to_hole = 1.0 / stats.putts_per_hole
    P[s['Green'], s['Hole']] = green_to_hole
    P[s['Green'], s['Green']] = 1.0 - green_to_hole

    hole_model = GolfHole(states, P)
    expected_score = hole_model.calculate_expected_steps('Tee')

    return {
        "expected_score": round(expected_score, 4),
        "matrix": P.tolist(),
        "states": states
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
