import numpy as np
import pandas as pd
from markov_golf_engine import GolfHole

"""
AMATEUR GOLFER MARKOV MODEL (Approx. 15-20 Handicap)
Based on Arccos/ShotScope average amateur statistics.

STATISTICAL FOUNDATION:
- Driving Accuracy: 45% (Fairway), 45% (Rough), 10% (Bunker/Penalty)
- Approach (Fairway): 25% GIR, 50% Miss to Rough, 20% Miss to Bunker, 5% duff/stay in fairway
- Approach (Rough): 10% GIR, 60% Miss to Rough, 25% Miss to Bunker, 5% duff/stay in rough
- Sand Play: 40% to Green, 40% to Rough, 20% left in Bunker
- Putting: Amateur average is 2.2 putts per hole. 
  To achieve an expected value of 2.2 in a memoryless Markov chain, 
  the Green->Hole probability must be 1 / 2.2 = 45%.
"""

states = ['Tee', 'Fairway', 'Rough', 'Bunker', 'Green', 'Hole']

P_amateur = np.array([
    # Tee -> [Tee, Fairway, Rough, Bunker, Green, Hole]
    [0.00, 0.45, 0.45, 0.10, 0.00, 0.00],  
    # Fairway -> [Tee, Fairway, Rough, Bunker, Green, Hole]
    [0.00, 0.05, 0.50, 0.20, 0.25, 0.00],  
    # Rough -> [Tee, Fairway, Rough, Bunker, Green, Hole]
    [0.00, 0.00, 0.65, 0.25, 0.10, 0.00],  
    # Bunker -> [Tee, Fairway, Rough, Bunker, Green, Hole]
    [0.00, 0.00, 0.40, 0.20, 0.40, 0.00],  
    # Green -> [Tee, Fairway, Rough, Bunker, Green, Hole]
    [0.00, 0.00, 0.00, 0.00, 0.55, 0.45],  
    # Hole (Absorbing State)
    [0.00, 0.00, 0.00, 0.00, 0.00, 1.00]   
])

# Ensure all rows sum to 1.0
assert np.allclose(P_amateur.sum(axis=1), 1.0), "Probabilities do not sum to 1.0"

amateur_hole = GolfHole(states, P_amateur)

print("="*70)
print("AMATEUR GOLFER MARKOV MODEL (PAR 4 - 15-20 HANDICAP)")
print("="*70)
print(pd.DataFrame(P_amateur, index=states, columns=states))

am_expected = amateur_hole.calculate_expected_steps('Tee')
print(f"\\nExpected Strokes for Average Amateur: {am_expected:.2f}")

# Sensitivity Analysis: What if they practice putting?
# Improve putting to 2.0 per hole (Green->Hole = 50%)
P_better_putter = P_amateur.copy()
P_better_putter[states.index('Green'), states.index('Green')] = 0.50
P_better_putter[states.index('Green'), states.index('Hole')] = 0.50

better_putter_hole = GolfHole(states, P_better_putter)
improved_expected = better_putter_hole.calculate_expected_steps('Tee')

print("\\n" + "-"*70)
print(f"Original Expected Score: {am_expected:.4f}")
print(f"Improved Putting (2.0 putts/hole): {improved_expected:.4f}")
print(f"Strokes saved per 18 holes: {(am_expected - improved_expected) * 18:.2f}")
print("-"*70)
