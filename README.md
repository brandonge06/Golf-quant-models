# Golf Quantitative Models: Markov Chain Expected Score Simulator

This project uses a Markov chain to model a par-4 golf hole and calculate the expected number of strokes to complete it. It employs both analytical linear algebra and Monte Carlo simulations to verify results and perform sensitivity analysis on player performance.

## Project Overview

The model defines a golf hole as a series of transitions between discrete states. By constructing a transition probability matrix, we can solve for the "time to absorption" (total strokes until the ball is in the hole).

### States
- **Tee**: The starting position.
- **Fairway**: Optimal position after a drive.
- **Rough**: Sub-optimal position off the fairway.
- **Bunker**: Hazard state.
- **Green**: Putting surface.
- **Hole**: The absorbing state (end of the hole).

## Methodology

### 1. Analytical Solution (Linear Algebra)
The script extracts the transient sub-matrix $Q$ (all states except the Hole) and calculates the **Fundamental Matrix** $N$:
$$N = (I - Q)^{-1}$$
The sum of the first row of $N$ provides the exact expected number of strokes from the 'Tee'.

### 2. Monte Carlo Simulation
The `simulate_hole()` function algorithmically plays the hole 10,000 times by randomly sampling transitions based on the probability matrix $P$. The average of these simulations is used to verify the analytical solution.

### 3. Sensitivity Analysis
The model evaluates how specific improvements in a golfer's game (e.g., better bunker play) impact their overall score. It calculates the potential "strokes saved per round" (18 holes) for targeted skill improvements.

## Usage

### Prerequisites
- Python 3.x
- NumPy
- Pandas

### Running the script
```bash
python markov_golf.py
```

## Results
- **Expected Score**: Calculated analytically using the fundamental matrix.
- **Simulation Verification**: Verified with 10,000 random walks.
- **Impact of Improvement**: Shows exact strokes saved per 18-hole round for improved bunker play.
