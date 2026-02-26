import numpy as np
import pandas as pd

# Define states for a par-4 golf hole
states = ['Tee', 'Fairway', 'Rough', 'Bunker', 'Green', 'Hole']

# Construct the transition probability matrix P
# Realistic probabilities for a scratch golfer:
# Tee: 60% Fairway, 30% Rough, 5% Bunker, 5% Green (long drive on a par 4 or conservative approach)
# Fairway: 75% Green, 10% Rough, 10% Bunker, 5% Hole (eagle/hole-out)
# Rough: 60% Green, 20% Rough, 20% Bunker
# Bunker: 70% Green, 20% Bunker, 10% Hole (sand save)
# Green: 50% Hole (one-putt), 50% Green (two-putt/miss)
# Hole: 100% Hole (absorbing state)

P = np.array([
    [0.00, 0.60, 0.30, 0.05, 0.05, 0.00],  # Tee
    [0.00, 0.00, 0.10, 0.10, 0.75, 0.05],  # Fairway
    [0.00, 0.00, 0.20, 0.20, 0.55, 0.05],  # Rough
    [0.00, 0.00, 0.10, 0.20, 0.60, 0.10],  # Bunker
    [0.00, 0.00, 0.00, 0.00, 0.50, 0.50],  # Green
    [0.00, 0.00, 0.00, 0.00, 0.00, 1.00]   # Hole
])

# Verify rows sum to 1.0
if not np.allclose(P.sum(axis=1), 1.0):
    raise ValueError("Rows of the transition matrix must sum to 1.0")

# Create a pandas DataFrame for readability
df_P = pd.DataFrame(P, index=states, columns=states)

print("Markov Chain Transition Matrix for a Par-4 Golf Hole:")
print(df_P)
print("\n" + "="*50 + "\n")

# Calculate expected strokes analytically
# Q is the sub-matrix of transient states (everything except 'Hole')
Q = P[:-1, :-1]

# Create identity matrix I of the same size as Q
I = np.identity(Q.shape[0])

# Calculate the Fundamental Matrix N = (I - Q)^-1
N = np.linalg.inv(I - Q)

# The sum of each row of N gives the expected number of steps to absorption 
# (total strokes) starting from that state.
expected_strokes = N.sum(axis=1)

# Display expected strokes from each state
df_N = pd.DataFrame(N, index=states[:-1], columns=states[:-1])
print("Fundamental Matrix N (Expected visits to each transient state):")
print(df_N)

print(f"\nExpected strokes starting from the 'Tee' (Exact): {expected_strokes[0]:.2f}")
print("\n" + "="*50 + "\n")

# Monte Carlo Simulation
def simulate_hole(P, states):
    """Simulate a single hole using the transition matrix P."""
    current_state_idx = 0  # Start at 'Tee'
    hole_idx = len(states) - 1  # Index of 'Hole' state
    strokes = 0
    
    while current_state_idx != hole_idx:
        # Sample next state based on current row's probabilities
        current_state_idx = np.random.choice(len(states), p=P[current_state_idx])
        strokes += 1
        
    return strokes

# Run 10,000 simulations
num_simulations = 10000
simulation_results = [simulate_hole(P, states) for _ in range(num_simulations)]

average_score = np.mean(simulation_results)

print(f"Average score over {num_simulations:,} simulated holes: {average_score:.4f}")
print(f"Exact linear algebra expected value: {expected_strokes[0]:.4f}")
print(f"Absolute difference: {abs(average_score - expected_strokes[0]):.6f}")

# Sensitivity Analysis: Improving Bunker Play
def get_expected_score(P_matrix):
    """Calculates the expected strokes from the 'Tee' for a given transition matrix."""
    Q_matrix = P_matrix[:-1, :-1]
    I_matrix = np.identity(Q_matrix.shape[0])
    N_matrix = np.linalg.inv(I_matrix - Q_matrix)
    return N_matrix.sum(axis=1)[0]

# Modify matrix P to simulate improved bunker play
# Current Bunker state (index 3) transitions:
# Rough: 0.1, Bunker: 0.2, Green: 0.6, Hole: 0.1
P_improved = P.copy()
bunker_idx = states.index('Bunker')
green_idx = states.index('Green')

# Increase 'Bunker' to 'Green' by 10% and decrease 'Bunker' to 'Bunker' by 10%
P_improved[bunker_idx, green_idx] += 0.10
P_improved[bunker_idx, bunker_idx] -= 0.10

new_expected_score = get_expected_score(P_improved)

print("\n" + "="*50 + "\n")
print("Sensitivity Analysis: Improved Bunker Play")
print(f"Original Expected Score: {expected_strokes[0]:.4f}")
print(f"Improved Expected Score (10% more Bunker-to-Green transitions): {new_expected_score:.4f}")
print(f"Strokes saved per round (18 holes): {(expected_strokes[0] - new_expected_score) * 18:.2f}")
