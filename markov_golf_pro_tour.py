import numpy as np
import pandas as pd
from markov_golf_engine import GolfHole

"""
PGA TOUR GRANULAR PERFORMANCE MODEL
Uses distance-based states to solve the 'memoryless' limitation of standard Markov chains.
Data: 2024 PGA Tour ShotLink Averages.

STATE DEFINITIONS:
- Tee: The starting point of the hole (Par 4, ~440 yards).
- Fairway_Long: Ball in fairway, distance to green > 175 yards.
- Fairway_Short: Ball in fairway, distance to green < 175 yards (scoring distance).
- Rough_Long: Ball in rough, distance to green > 175 yards (low control).
- Rough_Short: Ball in rough, distance to green < 175 yards (partial control).
- Bunker_Fairway: Ball in a fairway bunker, typically 200+ yards from green.
- Bunker_Greenside: Ball in a bunker immediately adjacent to the green.
- Green_Lag: Ball on the green, distance to hole > 40 feet (high 3-putt risk).
- Green_Short: Ball on the green, distance to hole < 40 feet (1-putt/2-putt zone).
- Hole: Ball is in the hole (absorbing state).
"""

states = [
    'Tee', 'Fairway_Long', 'Fairway_Short', 'Rough_Long', 'Rough_Short', 
    'Bunker_Fairway', 'Bunker_Greenside', 'Green_Lag', 'Green_Short', 'Hole'
]
s = {state: i for i, state in enumerate(states)}
P = np.zeros((len(states), len(states)))

# 1. TEE SHOT (440yd Par 4)
# 60% Fairway (split 50/50), 30% Rough, 10% Bunker/Penalty
P[s['Tee'], s['Fairway_Long']] = 0.30
P[s['Tee'], s['Fairway_Short']] = 0.30
P[s['Tee'], s['Rough_Long']] = 0.15
P[s['Tee'], s['Rough_Short']] = 0.15
P[s['Tee'], s['Bunker_Fairway']] = 0.10

# 2. FAIRWAY LONG (>175 yards)
# Pros hit ~65% GIR from here, mostly into 'Lag' distance.
P[s['Fairway_Long'], s['Green_Lag']] = 0.45
P[s['Fairway_Long'], s['Green_Short']] = 0.20
P[s['Fairway_Long'], s['Rough_Short']] = 0.20
P[s['Fairway_Long'], s['Bunker_Greenside']] = 0.15

# 3. FAIRWAY SHORT (<175 yards)
# Pros hit ~90% GIR from here, high chance of 'Short' putts.
P[s['Fairway_Short'], s['Green_Short']] = 0.65
P[s['Fairway_Short'], s['Green_Lag']] = 0.25
P[s['Fairway_Short'], s['Rough_Short']] = 0.09
P[s['Fairway_Short'], s['Hole']] = 0.01

# 4. ROUGH LONG (>175 yards)
# Lower control; reaching the green usually results in a 'Lag' putt.
P[s['Rough_Long'], s['Green_Lag']] = 0.35
P[s['Rough_Long'], s['Rough_Short']] = 0.45
P[s['Rough_Long'], s['Bunker_Greenside']] = 0.20

# 5. ROUGH SHORT (<175 yards)
# Partial control allows for some 'Short' green hits.
P[s['Rough_Short'], s['Green_Short']] = 0.45
P[s['Rough_Short'], s['Green_Lag']] = 0.20
P[s['Rough_Short'], s['Rough_Short']] = 0.20
P[s['Rough_Short'], s['Bunker_Greenside']] = 0.15

# 6. BUNKER FAIRWAY
# Primarily a 'layup' or recovery shot.
P[s['Bunker_Fairway'], s['Fairway_Short']] = 0.70
P[s['Bunker_Fairway'], s['Rough_Short']] = 0.30

# 7. BUNKER GREENSIDE
# Pros get 'up and down' ~50% of the time.
P[s['Bunker_Greenside'], s['Green_Short']] = 0.75
P[s['Bunker_Greenside'], s['Green_Lag']] = 0.20
P[s['Bunker_Greenside'], s['Bunker_Greenside']] = 0.05

# 8. GREEN LAG (40+ feet)
# Primary goal is to lag into 'Short' range; low miracle make rate.
P[s['Green_Lag'], s['Green_Short']] = 0.94
P[s['Green_Lag'], s['Hole']] = 0.06

# 9. GREEN SHORT (<40 feet)
# Majority are 2-putts (stay in Short) or 1-putts (Hole).
P[s['Green_Short'], s['Hole']] = 0.65
P[s['Green_Short'], s['Green_Short']] = 0.35

# 10. HOLE
P[s['Hole'], s['Hole']] = 1.0

pro_hole = GolfHole(states, P)
expected = pro_hole.calculate_expected_steps('Tee')

print("="*60)
print(f"PGA TOUR GRANULAR MODEL | Expected Score: {expected:.2f}")
print("="*60)
print(pd.DataFrame(P, index=states, columns=states))
