import unittest
import numpy as np
import threading
from markov_golf_engine import GolfHole

class TestGolfHole(unittest.TestCase):
    def setUp(self):
        # A simple model: Tee -> Green -> Hole
        self.states = ['Tee', 'Green', 'Hole']
        # Tee (0): 80% Green, 20% Hole
        # Green (1): 50% Green, 50% Hole
        # Hole (2): 100% Hole
        self.P = np.array([
            [0.0, 0.8, 0.2],
            [0.0, 0.5, 0.5],
            [0.0, 0.0, 1.0]
        ])
        self.model = GolfHole(self.states, self.P)

    def test_expected_strokes_analytical(self):
        """Verify the analytical calculation of expected strokes."""
        # Expected from Tee: 1 (to Green/Hole) + 0.8 * (2 additional from Green) = 2.6
        # From Green: (1 - 0.5)^-1 = 2
        # From Tee: Q = [[0.0, 0.8], [0.0, 0.5]]
        # I - Q = [[1.0, -0.8], [0.0, 0.5]]
        # (I-Q)^-1 = [[1.0, 1.6], [0.0, 2.0]]
        # Sum of row 0: 1.0 + 1.6 = 2.6
        # Sum of row 1: 0.0 + 2.0 = 2.0
        self.assertAlmostEqual(self.model.calculate_expected_steps('Tee'), 2.6, places=5)
        self.assertAlmostEqual(self.model.calculate_expected_steps('Green'), 2.0, places=5)
        self.assertEqual(self.model.calculate_expected_steps('Hole'), 0.0)

    def test_simulation_vs_analytical(self):
        """Verify that simulation results converge to analytical results."""
        np.random.seed(42)
        sim_result = self.model.simulate('Tee', num_simulations=10000)
        analytical_result = self.model.calculate_expected_steps('Tee')
        # Tolerance for stochastic convergence
        self.assertAlmostEqual(sim_result, analytical_result, delta=0.1)

    def test_thread_safety(self):
        """Verify that multiple threads can access the model safely."""
        num_threads = 10
        results = [0.0] * num_threads

        def run_sim(idx):
            results[idx] = self.model.simulate('Tee', num_simulations=100)

        threads = [threading.Thread(target=run_sim, args=(i,)) for i in range(num_threads)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Check if all threads completed successfully and returned valid results
        for res in results:
            self.assertGreater(res, 0)
            self.assertAlmostEqual(res, 2.6, delta=1.0) # High delta due to small n

    def test_invalid_matrix(self):
        """Test validation logic for transition matrices."""
        invalid_P = np.array([[0.1, 0.1], [0.1, 0.1]]) # Doesn't sum to 1.0
        with self.assertRaises(ValueError):
            GolfHole(['A', 'B'], invalid_P)

if __name__ == '__main__':
    unittest.main()
