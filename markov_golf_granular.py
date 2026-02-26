import numpy as np
import pandas as pd
from markov_golf_engine import GolfHole

"""
GRANULAR DISTANCE-BASED MARKOV MODEL
This model solves the 'memoryless' issue by splitting states into distance ranges.
Data based on 2024 PGA Tour Proximity and Putting stats.

KEY TRANSITIONS:
- Lag Putts (40+ ft) have a ~5% make rate and a ~90% chance of becoming a 'Short' putt.
- Short Approaches (<175yd) yield a 55% chance of a 'Short' putt vs a 25% 'Lag' putt.
- Long Approaches (>175yd) yield a 40% 'Lag' putt vs only 20% 'Short' putt.
"""

states = [
    'Tee', 
    'Fairway_Long', 'Fairway_Short', 
    'Rough_Long', 'Rough_Short', 
    'Bunker_Fairway', 'Bunker_Greenside',
    'Green_Lag', 'Green_Short', 
    'Hole'
]

# Map names to indices for easier matrix construction
s = {state: i for i, state in enumerate(states)}
P = np.zeros((len(states), len(states)))

# 1. TEE SHOT (Par 4, 440 yards)
# 60% Fairway (split 50/50 Long/Short), 30% Rough, 10% Bunker/Penalty
P[s['Tee'], s['Fairway_Long']] = 0.30
P[s['Tee'], s['Fairway_Short']] = 0.30
P[s['Tee'], s['Rough_Long']] = 0.15
P[s['Tee'], s['Rough_Short']] = 0.15
P[s['Tee'], s['Bunker_Fairway']] = 0.08
P[s['Tee'], s['Bunker_Greenside']] = 0.02 # Driven green-side bunker

# 2. FAIRWAY LONG (>175 yards)
# 60% GIR (Mostly Lag), 20% Rough, 15% Bunker, 5% Fairway Short (layup)
P[s['Fairway_Long'], s['Green_Lag']] = 0.40
P[s['Fairway_Long'], s['Green_Short']] = 0.20
P[s['Fairway_Long'], s['Rough_Short']] = 0.20
P[s['Fairway_Long'], s['Bunker_Greenside']] = 0.15
P[s['Fairway_Long'], s['Fairway_Short']] = 0.05

# 3. FAIRWAY SHORT (<175 yards)
# 85% GIR (Mostly Short), 10% Rough, 4% Bunker, 1% Hole Out
P[s['Fairway_Short'], s['Green_Short']] = 0.60
P[s['Fairway_Short'], s['Green_Lag']] = 0.25
P[s['Fairway_Short'], s['Rough_Short']] = 0.10
P[s['Fairway_Short'], s['Bunker_Greenside']] = 0.04
P[s['Fairway_Short'], s['Hole']] = 0.01

# 4. ROUGH LONG
P[s['Rough_Long'], s['Green_Lag']] = 0.30
P[s['Rough_Long'], s['Rough_Short']] = 0.40
P[s['Rough_Long'], s['Bunker_Greenside']] = 0.20
P[s['Rough_Long'], s['Fairway_Short']] = 0.10

# 5. ROUGH SHORT
P[s['Rough_Short'], s['Green_Short']] = 0.40
P[s['Rough_Short'], s['Green_Lag']] = 0.25
P[s['Rough_Short'], s['Rough_Short']] = 0.20 # Chunked
P[s['Rough_Short'], s['Bunker_Greenside']] = 0.14
P[s['Rough_Short'], s['Hole']] = 0.01

# 6. BUNKER FAIRWAY
P[s['Bunker_Fairway'], s['Fairway_Short']] = 0.60
P[s['Bunker_Fairway'], s['Rough_Short']] = 0.30
P[s['Bunker_Fairway'], s['Bunker_Fairway']] = 0.10

# 7. BUNKER GREENSIDE
P[s['Bunker_Greenside'], s['Green_Short']] = 0.70
P[s['Bunker_Greenside'], s['Green_Lag']] = 0.20
P[s['Bunker_Greenside'], s['Bunker_Greenside']] = 0.10

# 8. GREEN LAG (40+ feet)
# 92% to Short Green (Lagged), 5% still in Lag, 3% Miracle make
P[s['Green_Lag'], s['Green_Short']] = 0.92
P[s['Green_Lag'], s['Green_Lag']] = 0.05
P[s['Green_Lag'], s['Hole']] = 0.03

# 9. GREEN SHORT (<40 feet)
# 62% Hole (Average of 1-putt and 2-putt from within 40ft), 38% Stay in Short
P[s['Green_Short'], s['Hole']] = 0.62
P[s['Green_Short'], s['Green_Short']] = 0.38

# 10. HOLE
P[s['Hole'], s['Hole']] = 1.0

# Verify
assert np.allclose(P.sum(axis=1), 1.0), "Matrix rows do not sum to 1.0"

granular_hole = GolfHole(states, P)

print("="*75)
print("GRANULAR DISTANCE-BASED PRO MODEL (PAR 4)")
print("="*75)

# Calculate Expected Strokes
results = {state: granular_hole.calculate_expected_steps(state) for state in states[:-1]}
df_results = pd.DataFrame(list(results.items()), columns=['State', 'Expected Strokes to Hole'])

print(df_results)

# Analyze Lag Putting vs Short Putting
lag_expected = granular_hole.calculate_expected_steps('Green_Lag')
short_expected = granular_hole.calculate_expected_steps('Green_Short')

print("\n" + "-"*75)
print(f"Expected Putts from LAG (40+ ft): {lag_expected:.2f}")
print(f"Expected Putts from SHORT (<40 ft): {short_expected:.2f}")
print(f"Lag Penalty: {lag_expected - short_expected:.2f} additional strokes")

# Analyze Approach Distance
fw_long_exp = granular_hole.calculate_expected_steps('Fairway_Long')
fw_short_exp = granular_hole.calculate_expected_steps('Fairway_Short')

print(f"\nExpected Strokes from Fairway (>175yd): {fw_long_exp:.2f}")
print(f"Expected Strokes from Fairway (<175yd): {fw_short_exp:.2f}")
print(f"Distance Penalty: {fw_long_exp - fw_short_exp:.2f} strokes")
print("-" * 75)
