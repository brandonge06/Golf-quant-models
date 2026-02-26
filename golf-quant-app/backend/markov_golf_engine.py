import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import List
import threading

class MarkovModel(ABC):
    """Abstract base class for a Markov Chain Model."""
    
    def __init__(self, states: List[str], transition_matrix: np.ndarray):
        self._states = states
        self._P = transition_matrix.astype(float)
        self._state_to_idx = {state: i for i, state in enumerate(states)}
        self._lock = threading.Lock()
        self._validate_matrix()

    def _validate_matrix(self):
        if not np.allclose(self._P.sum(axis=1), 1.0):
            raise ValueError("Rows of the transition matrix must sum to 1.0")
        if self._P.shape != (len(self._states), len(self._states)):
            raise ValueError("Matrix dimensions must match the number of states")

    @property
    def states(self):
        return self._states

    @property
    def transition_matrix(self):
        with self._lock:
            return self._P.copy()

    @abstractmethod
    def calculate_expected_steps(self, start_state: str) -> float:
        """Analytically calculate expected steps to absorption."""
        pass

    @abstractmethod
    def simulate(self, start_state: str, num_simulations: int) -> float:
        """Simulate steps to absorption using Monte Carlo methods."""
        pass

class GolfHole(MarkovModel):
    """Concrete implementation of a Golf Hole using Markov Chains."""
    
    def __init__(self, states: List[str], transition_matrix: np.ndarray):
        super().__init__(states, transition_matrix)
        self._fundamental_matrix = None

    def _get_fundamental_matrix(self):
        """Thread-safe lazy initialization of the fundamental matrix N."""
        with self._lock:
            if self._fundamental_matrix is None:
                # Q is the transient state sub-matrix (all but the last 'Hole' state)
                Q = self._P[:-1, :-1]
                I = np.identity(Q.shape[0])
                self._fundamental_matrix = np.linalg.inv(I - Q)
            return self._fundamental_matrix

    def calculate_expected_steps(self, start_state: str) -> float:
        if start_state not in self._state_to_idx:
            raise ValueError(f"State '{start_state}' not found in model.")
            
        if start_state == self.states[-1]: # Hole
            return 0.0
        
        N = self._get_fundamental_matrix()
        start_idx = self._state_to_idx[start_state]
        expected_strokes = N.sum(axis=1)
        return float(expected_strokes[start_idx])

    def simulate(self, start_state: str, num_simulations: int = 1000) -> float:
        if start_state not in self._state_to_idx:
            raise ValueError(f"State '{start_state}' not found in model.")

        # Thread-safe simulation using a local copy of the transition matrix
        P_local = self.transition_matrix
        start_idx = self._state_to_idx[start_state]
        hole_idx = len(self.states) - 1
        
        results = []
        for _ in range(num_simulations):
            current_idx = start_idx
            strokes = 0
            while current_idx != hole_idx:
                current_idx = np.random.choice(len(self.states), p=P_local[current_idx])
                strokes += 1
            results.append(strokes)
            
        return float(np.mean(results))
