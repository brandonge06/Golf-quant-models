from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np
import os
import uvicorn
from markov_golf_engine import GolfHole

app = FastAPI()

class GranularStats(BaseModel):
    tee_fairway: float
    tee_rough: float
    tee_bunker: float
    fw_green_short: float
    fw_green_lag: float
    fw_rough: float
    fw_bunker: float
    rough_green_short: float
    rough_green_lag: float
    rough_rough: float
    rough_bunker: float
    sand_green_short: float
    sand_green_lag: float
    sand_bunker: float
    sand_rough: float
    # New Granular Putting
    putt_lag_make: float
    putt_lag_to_tapin: float
    putt_lag_to_short: float
    putt_short_make: float

@app.post("/calculate")
def calculate_strokes(stats: GranularStats):
    try:
        # Added Green_TapIn (< 3ft)
        states = [
            'Tee', 'Fairway_Long', 'Fairway_Short', 'Rough_Long', 'Rough_Short', 
            'Bunker_Fairway', 'Bunker_Greenside', 'Green_Lag', 'Green_Short', 
            'Green_TapIn', 'Hole'
        ]
        s = {state: i for i, state in enumerate(states)}
        P = np.zeros((len(states), len(states)))
        P[s['Hole'], s['Hole']] = 1.0

        # Tee Transitions
        P[s['Tee'], s['Fairway_Long']] = stats.tee_fairway * 0.5
        P[s['Tee'], s['Fairway_Short']] = stats.tee_fairway * 0.5
        P[s['Tee'], s['Rough_Long']] = stats.tee_rough * 0.5
        P[s['Tee'], s['Rough_Short']] = stats.tee_rough * 0.5
        P[s['Tee'], s['Bunker_Fairway']] = stats.tee_bunker

        # Fairway Transitions
        for state in ['Fairway_Long', 'Fairway_Short']:
            P[s[state], s['Green_Short']] = stats.fw_green_short
            P[s[state], s['Green_Lag']] = stats.fw_green_lag
            P[s[state], s['Rough_Short']] = stats.fw_rough
            P[s[state], s['Bunker_Greenside']] = stats.fw_bunker

        # Rough Transitions
        for state in ['Rough_Long', 'Rough_Short']:
            P[s[state], s['Green_Short']] = stats.rough_green_short
            P[s[state], s['Green_Lag']] = stats.rough_green_lag
            P[s[state], s['Rough_Short']] = stats.rough_rough
            P[s[state], s['Bunker_Greenside']] = stats.rough_bunker

        # Bunker Transitions
        P[s['Bunker_Fairway'], s['Fairway_Short']] = 0.7
        P[s['Bunker_Fairway'], s['Rough_Short']] = 0.3
        P[s['Bunker_Greenside'], s['Green_Short']] = stats.sand_green_short
        P[s['Bunker_Greenside'], s['Green_Lag']] = stats.sand_green_lag
        P[s['Bunker_Greenside'], s['Bunker_Greenside']] = stats.sand_bunker
        P[s['Bunker_Greenside'], s['Rough_Short']] = stats.sand_rough

        # Granular Putting Logic
        # 1. Lag Putt (30ft+)
        P[s['Green_Lag'], s['Hole']] = stats.putt_lag_make
        P[s['Green_Lag'], s['Green_TapIn']] = stats.putt_lag_to_tapin
        P[s['Green_Lag'], s['Green_Short']] = stats.putt_lag_to_short
        # Remainder stays in Green_Lag (represents a bad leave/3-putt territory)
        
        # 2. Short Putt (3-10ft)
        P[s['Green_Short'], s['Hole']] = stats.putt_short_make
        # Missed short putts go to Tap-in
        P[s['Green_Short'], s['Green_TapIn']] = 1.0 - stats.putt_short_make

        # 3. Tap-in (< 3ft)
        P[s['Green_TapIn'], s['Hole']] = 0.99 # Nearly automatic
        P[s['Green_TapIn'], s['Green_TapIn']] = 0.01

        # Global Normalization to handle remainders
        row_sums = P.sum(axis=1)
        for i in range(len(states)):
            if i == s['Hole']: continue
            if row_sums[i] != 1.0:
                # If a row doesn't sum to 1, distribute to a "safe" next state
                # to ensure the Markov chain is valid.
                target_state = s['Hole'] if i >= s['Green_Lag'] else s['Green_Short']
                diff = 1.0 - row_sums[i]
                if diff > 0:
                    P[i, target_state] += diff
                else:
                    P[i] = P[i] / row_sums[i]

        hole_model = GolfHole(states, P)
        return {"expected_score": round(hole_model.calculate_expected_steps('Tee'), 4)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

if os.path.exists(static_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_path, "assets")), name="assets")
    @app.get("/")
    async def serve_index(): return FileResponse(os.path.join(static_path, "index.html"))
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str): return FileResponse(os.path.join(static_path, "index.html"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
