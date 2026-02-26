import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Target, Flag, Calculator, Percent } from 'lucide-react';

const App = () => {
  const [stats, setStats] = useState({
    driving_accuracy: 0.60,
    gir_fairway: 0.80,
    gir_rough: 0.50,
    putts_per_hole: 1.64
  });
  const [expectedScore, setExpectedScore] = useState(0);

  const calculate = async () => {
    try {
      const res = await axios.post('http://localhost:8000/calculate', stats);
      setExpectedScore(res.data.expected_score);
    } catch (e) {
      console.error("Error connecting to backend", e);
    }
  };

  useEffect(() => {
    calculate();
  }, [stats]);

  const loadPreset = (type: 'pro' | 'amateur') => {
    if (type === 'pro') {
      setStats({ driving_accuracy: 0.60, gir_fairway: 0.80, gir_rough: 0.50, putts_per_hole: 1.64 });
    } else {
      setStats({ driving_accuracy: 0.40, gir_fairway: 0.30, gir_rough: 0.15, putts_per_hole: 2.20 });
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
              <Target className="text-green-600 w-10 h-10" />
              Golf Quant Models
            </h1>
            <p className="text-gray-600 mt-2">Interactive Markov Performance Simulation</p>
          </div>
          <div className="flex gap-4">
            <button 
              onClick={() => loadPreset('pro')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition"
            >
              Pro Preset
            </button>
            <button 
              onClick={() => loadPreset('amateur')}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium transition"
            >
              Amateur Preset
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-200">
            <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
              <Flag className="w-6 h-6 text-blue-500" />
              Performance Metrics
            </h2>
            
            <div className="space-y-8">
              {[
                { label: 'Driving Accuracy', key: 'driving_accuracy', icon: Percent },
                { label: 'GIR from Fairway', key: 'gir_fairway', icon: Percent },
                { label: 'GIR from Rough', key: 'gir_rough', icon: Percent }
              ].map(({ label, key, icon: Icon }) => (
                <div key={key}>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                      <Icon className="w-4 h-4 text-gray-400" /> {label}
                    </label>
                    <span className="text-blue-600 font-bold">{(stats[key] * 100).toFixed(0)}%</span>
                  </div>
                  <input
                    type="range" min="0" max="1" step="0.01"
                    value={stats[key]}
                    onChange={(e) => setStats({ ...stats, [key]: parseFloat(e.target.value) })}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                </div>
              ))}

              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <Calculator className="w-4 h-4 text-gray-400" /> Putts Per Hole
                  </label>
                  <span className="text-green-600 font-bold">{stats.putts_per_hole.toFixed(2)}</span>
                </div>
                <input
                  type="range" min="1.0" max="3.0" step="0.01"
                  value={stats.putts_per_hole}
                  onChange={(e) => setStats({ ...stats, putts_per_hole: parseFloat(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600"
                />
              </div>
            </div>
          </div>

          <div className="bg-green-600 p-12 rounded-2xl shadow-xl flex flex-col justify-center items-center text-white">
            <h3 className="text-xl opacity-80 mb-2 font-medium">Expected Total Score</h3>
            <div className="text-8xl font-black mb-4">
              {expectedScore.toFixed(2)}
            </div>
            <p className="text-center opacity-70 max-w-xs leading-relaxed">
              Calculated using the fundamental matrix of your Markov engine based on current statistics.
            </p>
            <div className="mt-8 pt-8 border-t border-white/20 w-full text-center">
              <span className="text-sm uppercase tracking-widest opacity-60">Status: Live Engine</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
