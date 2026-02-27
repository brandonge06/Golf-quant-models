import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Target, ArrowRight, ChevronDown, ChevronRight } from 'lucide-react';

const GROUPS = {
  tee: ['tee_fairway', 'tee_rough', 'tee_bunker'],
  fw: ['fw_green_short', 'fw_green_lag', 'fw_rough', 'fw_bunker'],
  rough: ['rough_green_short', 'rough_green_lag', 'rough_rough', 'rough_bunker'],
  sand: ['sand_green_short', 'sand_green_lag', 'sand_bunker', 'sand_rough'],
  putt: ['putt_lag_make', 'putt_lag_to_tapin', 'putt_lag_to_short'],
};

const DEFAULT_PRO = {
  tee_fairway: 0.60, tee_rough: 0.30, tee_bunker: 0.10,
  fw_green_short: 0.25, fw_green_lag: 0.55, fw_rough: 0.15, fw_bunker: 0.05,
  rough_green_short: 0.10, rough_green_lag: 0.45, rough_rough: 0.35, rough_bunker: 0.10,
  sand_green_short: 0.70, sand_green_lag: 0.20, sand_bunker: 0.05, sand_rough: 0.05,
  // Pro Putting
  putt_lag_make: 0.06, 
  putt_lag_to_tapin: 0.75, 
  putt_lag_to_short: 0.15, 
  putt_short_make: 0.94
};

const DEFAULT_USER = {
  tee_fairway: 0.40, tee_rough: 0.50, tee_bunker: 0.10,
  fw_green_short: 0.10, fw_green_lag: 0.25, fw_rough: 0.50, fw_bunker: 0.15,
  rough_green_short: 0.05, rough_green_lag: 0.10, rough_rough: 0.65, rough_bunker: 0.20,
  sand_green_short: 0.30, sand_green_lag: 0.30, sand_bunker: 0.30, sand_rough: 0.10,
  // User Putting
  putt_lag_make: 0.02, 
  putt_lag_to_tapin: 0.50, 
  putt_lag_to_short: 0.30, 
  putt_short_make: 0.75
};

const RenderColumn = ({ title, stats, onUpdate, score, type }: any) => {
  const isPro = type === 'pro';
  const accent = isPro ? 'accent-blue-600' : 'accent-green-600';
  const text = isPro ? 'text-blue-600' : 'text-green-600';
  
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({
    "Off the Tee": false,
    "From Fairway": false,
    "From Rough": false,
    "Short Game": true,
    "Putting": false
  });

  const toggleSection = (label: string) => {
    setCollapsed(prev => ({ ...prev, [label]: !prev[label] }));
  };

  const sections = [
    { label: "Off the Tee", keys: GROUPS.tee },
    { label: "From Fairway", keys: GROUPS.fw },
    { label: "From Rough", keys: GROUPS.rough },
    { label: "Short Game", keys: GROUPS.sand },
    { 
        label: "Putting", 
        keys: [...GROUPS.putt, 'putt_short_make'],
        descriptions: {
            'putt_lag_make': 'Lag Make % (30ft+)',
            'putt_lag_to_tapin': 'Lag to Tap-in (<3ft)',
            'putt_lag_to_short': 'Lag to Short (3-10ft)',
            'putt_short_make': 'Short Putt Make % (3-10ft)'
        }
    }
  ];

  return (
    <div className="p-4 md:p-8 bg-white border-x border-gray-100 w-full overflow-y-auto">
      <div className={`mb-8 border-b-4 pb-4 flex justify-between items-end ${isPro ? 'border-blue-600' : 'border-green-600'}`}>
        <h2 className={`text-lg md:text-2xl font-black uppercase leading-tight ${text}`}>{title}</h2>
        <div className="text-right">
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Expected</div>
          <div className={`text-3xl md:text-5xl font-black ${text}`}>{score.toFixed(2)}</div>
        </div>
      </div>

      <div className="space-y-4">
        {sections.map(sec => {
          const isCollapsed = collapsed[sec.label];
          return (
            <div key={sec.label} className="bg-gray-50 rounded-xl overflow-hidden">
              <button 
                onClick={() => toggleSection(sec.label)}
                className="w-full p-3 md:p-4 flex items-center justify-between hover:bg-gray-100 transition-colors"
              >
                <h3 className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{sec.label}</h3>
                {isCollapsed ? <ChevronRight className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
              </button>
              
              {!isCollapsed && (
                <div className="px-3 pb-3 md:px-4 md:pb-4 space-y-3">
                  {sec.keys.map(key => (
                    <div key={key}>
                      <div className="flex justify-between text-[10px] md:text-xs font-bold mb-1">
                        <span className="text-gray-600 capitalize">
                            {(sec as any).descriptions?.[key] || key.replace(/_/g, ' ')}
                        </span>
                        <span className={text}>{( (stats[key] || 0) * 100).toFixed(0)}%</span>
                      </div>
                      <input
                        type="range" min="0" max="1" step="0.01"
                        value={stats[key] || 0}
                        onChange={(e) => onUpdate(key, parseFloat(e.target.value))}
                        className={`w-full h-1 rounded-lg appearance-none cursor-pointer ${accent}`}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

const App = () => {
  const [proStats, setProStats] = useState<Record<string, number>>(DEFAULT_PRO);
  const [userStats, setUserStats] = useState<Record<string, number>>(DEFAULT_USER);
  const [proScore, setProScore] = useState(0);
  const [userScore, setUserScore] = useState(0);

  const calculate = async (stats: any, setScore: any) => {
    try {
      const res = await axios.post('/calculate', stats);
      setScore(res.data.expected_score);
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    const timer = setTimeout(() => calculate(proStats, setProScore), 200);
    return () => clearTimeout(timer);
  }, [proStats]);

  useEffect(() => {
    const timer = setTimeout(() => calculate(userStats, setUserScore), 200);
    return () => clearTimeout(timer);
  }, [userStats]);

  const handleUpdate = useCallback((setStats: any, defaultRef: any) => (key: string, newVal: number) => {
    setStats((prev: any) => {
      const newStats = { ...prev };
      const oldVal = prev[key] || 0;
      newStats[key] = newVal;
      
      const groupKey = Object.keys(GROUPS).find(g => (GROUPS as any)[g].includes(key));
      if (groupKey) {
        const group = (GROUPS as any)[groupKey];
        const otherKeys = group.filter((k: string) => k !== key);
        const remaining = 1.0 - newVal;
        
        // Calculate the sum of others in the CURRENT state
        const currentOtherSum = otherKeys.reduce((sum: number, k: string) => sum + (prev[k] || 0), 0);

        if (remaining <= 0) {
          // If active slider is 100%, others must be 0
          otherKeys.forEach((k: string) => { newStats[k] = 0; });
        } else if (currentOtherSum > 0.001) {
          // Proportional redistribution based on CURRENT ratios
          otherKeys.forEach((k: string) => {
            newStats[k] = (prev[k] / currentOtherSum) * remaining;
          });
        } else {
          // FALLBACK: If others are all 0, use the ORIGINAL DEFAULT ratios to redistribute
          const defaultOtherSum = otherKeys.reduce((sum: number, k: string) => sum + (defaultRef[k] || 0), 0);
          otherKeys.forEach((k: string) => {
            const weight = defaultOtherSum > 0 ? (defaultRef[k] / defaultOtherSum) : (1 / otherKeys.length);
            newStats[k] = weight * remaining;
          });
        }

        // Final sanity check to ensure floating point math sums to exactly 1.0
        const total = group.reduce((sum: number, k: string) => sum + newStats[k], 0);
        if (total > 0) {
          group.forEach((k: string) => { newStats[k] = newStats[k] / total; });
        }
      }
      return newStats;
    });
  }, []);

  return (
    <div className="h-screen bg-white flex flex-col font-sans overflow-hidden">
      <header className="p-4 border-b border-gray-100 flex items-center justify-center gap-2 flex-shrink-0">
        <Target className="text-green-600 w-6 h-6" />
        <h1 className="text-xl font-black uppercase tracking-tighter">Golf Quant <span className="text-green-600">Comparison</span></h1>
      </header>

      <div className="grid grid-cols-2 w-full max-w-[2000px] mx-auto flex-grow overflow-hidden">
        <RenderColumn 
          title="Pro Tour" 
          stats={proStats} 
          onUpdate={handleUpdate(setProStats, DEFAULT_PRO)} 
          score={proScore} 
          type="pro" 
        />
        <RenderColumn 
          title="Your Game" 
          stats={userStats} 
          onUpdate={handleUpdate(setUserStats, DEFAULT_USER)} 
          score={userScore} 
          type="user" 
        />
      </div>

      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-6 md:px-8 py-2 md:py-3 rounded-full shadow-2xl flex items-center gap-4 border border-white/10 z-50">
        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Gap</span>
        <span className="text-xl md:text-2xl font-black">{(userScore - proScore).toFixed(2)}</span>
        <ArrowRight className="text-green-500 w-5 h-5" />
      </div>
    </div>
  );
};

export default App;
