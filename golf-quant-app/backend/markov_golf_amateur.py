import numpy as np
import pandas as pd
from markov_golf_engine import GolfHole

"""
AMATEUR (20-HANDICAP) GRANULAR PERFORMANCE MODEL
Uses distance-based states to model amateur struggles.
Data: Arccos/ShotScope average amateur statistics.

STATE DEFINITIONS:
- Tee: The starting point of the hole (Par 4, ~440 yards).
- Fairway_Long: Ball in fairway, distance to green > 175 yards.
- Fairway_Short: Ball in fairway, distance to green < 175 yards (scoring distance).
- Rough_Long: Ball in rough, distance to green > 175 yards (high penalty).
- Rough_Short: Ball in rough, distance to green < 175 yards (low precision).
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
# Lower accuracy (40% fairway), high miss into rough/hazards.
P[s['Tee'], s['Fairway_Long']] = 0.20
P[s['Tee'], s['Fairway_Short']] = 0.20
P[s['Tee'], s['Rough_Long']] = 0.25
P[s['Tee'], s['Rough_Short']] = 0.25
P[s['Tee'], s['Bunker_Fairway']] = 0.10

# 2. FAIRWAY LONG (>175 yards)
# Amateurs struggle with long irons; high chance of rough or short.
P[s['Fairway_Long'], s['Green_Lag']] = 0.15
P[s['Fairway_Long'], s['Rough_Short']] = 0.50
P[s['Fairway_Long'], s['Bunker_Greenside']] = 0.25
P[s['Fairway_Long'], s['Fairway_Long']] = 0.10

# 3. FAIRWAY SHORT (<175 yards)
# Precision is still difficult; lots of misses to 'Rough Short'.
P[s['Fairway_Short'], s['Green_Short']] = 0.25
P[s['Fairway_Short'], s['Green_Lag']] = 0.25
P[s['Fairway_Short'], s['Rough_Short']] = 0.40
P[s['Fairway_Short'], s['Bunker_Greenside']] = 0.10

# 4. ROUGH LONG (>175 yards)
# Often results in a layup or difficult recovery.
P[s['Rough_Long'], s['Rough_Short']] = 0.50
P[s['Rough_Long'], s['Bunker_Greenside']] = 0.30
P[s['Rough_Long'], s['Rough_Long']] = 0.20

# 5. ROUGH SHORT (<175 yards)
# Misses often end up in more rough or the bunker.
P[s['Rough_Short'], s['Green_Lag']] = 0.15
P[s['Rough_Short'], s['Rough_Short']] = 0.60
P[s['Rough_Short'], s['Bunker_Greenside']] = 0.25

# 6. BUNKER FAIRWAY
# Most amateurs take multiple shots to escape.
P[s['Bunker_Fairway'], s['Rough_Short']] = 0.70
P[s['Bunker_Fairway'], s['Bunker_Fairway']] = 0.30

# 7. BUNKER GREENSIDE
# Low precision leads to high chance of staying in bunker or missing far.
P[s['Bunker_Greenside'], s['Green_Lag']] = 0.30
P[s['Bunker_Greenside'], s['Bunker_Greenside']] = 0.40
P[s['Bunker_Greenside'], s['Rough_Short']] = 0.30

# 8. GREEN LAG (40+ feet)
# Significant chance of leaving the next putt also in 'Lag' distance.
P[s['Green_Lag'], s['Green_Short']] = 0.75
P[s['Green_Lag'], s['Green_Lag']] = 0.25

# 9. GREEN SHORT (<40 feet)
# Amateurs are roughly 45% to hole it in 1 from here.
P[s['Green_Short'], s['Hole']] = 0.45
P[s['Green_Short'], s['Green_Short']] = 0.55

# 10. HOLE
P[s['Hole'], s['Hole']] = 1.0

am_hole = GolfHole(states, P)
expected = am_hole.calculate_expected_steps('Tee')

print("="*60)
print(f"AMATEUR GRANULAR MODEL | Expected Score: {expected:.2f}")
print("="*60)
print(pd.DataFrame(P, index=states, columns=states))
