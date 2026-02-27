
import numpy as np
import pandas as pd
from markov_golf_engine import GolfHole

# Define states for a par-4 golf hole
states = ['Tee', 'Fairway', 'Rough', 'Bunker', 'Green', 'Hole']

# Construct the transition probability matrix P
P = np.array([
    [0.00, 0.60, 0.30, 0.05, 0.05, 0.00],  # Tee
    [0.00, 0.00, 0.10, 0.10, 0.75, 0.05],  # Fairway
    [0.00, 0.00, 0.20, 0.20, 0.55, 0.05],  # Rough
    [0.00, 0.00, 0.10, 0.20, 0.60, 0.10],  # Bunker
    [0.00, 0.00, 0.00, 0.00, 0.50, 0.50],  # Green
    [0.00, 0.00, 0.00, 0.00, 0.00, 1.00]   # Hole
])

# Initialize the model using the engine
hole = GolfHole(states, P)

print("Markov Chain Transition Matrix for a Par-4 Golf Hole:")
print(pd.DataFrame(P, index=states, columns=states))
print("\n" + "="*50 + "\n")

# Analytical Result
expected_score = hole.calculate_expected_steps('Tee')
print(f"Expected strokes starting from the 'Tee' (Exact): {expected_score:.2f}")

# Simulation Result
num_simulations = 10000
average_score = hole.simulate('Tee', num_simulations=num_simulations)
print(f"Average score over {num_simulations:,} simulated holes: {average_score:.4f}")

# Sensitivity Analysis: Improving Bunker Play
P_improved = P.copy()
bunker_idx = states.index('Bunker')
green_idx = states.index('Green')

# Increase 'Bunker' to 'Green' by 10% and decrease 'Bunker' to 'Bunker' by 10%
P_improved[bunker_idx, green_idx] += 0.10
P_improved[bunker_idx, bunker_idx] -= 0.10

hole_improved = GolfHole(states, P_improved)
new_expected_score = hole_improved.calculate_expected_steps('Tee')

print("\n" + "="*50 + "\n")
print("Sensitivity Analysis: Improved Bunker Play")
print(f"Original Expected Score: {expected_score:.4f}")
print(f"Improved Expected Score (10% more Bunker-to-Green transitions): {new_expected_score:.4f}")
print(f"Strokes saved per round (18 holes): {(expected_score - new_expected_score) * 18:.2f}")
