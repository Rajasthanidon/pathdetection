// @ts-nocheck
import { Play, Pause, Square, FastForward, Activity, ShieldCheck, Crosshair, Radar } from 'lucide-react';

export default function Sidebar({ state, sendCommand }) {
  const isRunning = state?.status === 'RUNNING';

  const handleStart = () => sendCommand('START');
  const handlePause = () => sendCommand('PAUSE');
  const handleReset = () => sendCommand('RESET');
  const setScenario = (e) => sendCommand('SET_SCENARIO', { scenario_id: parseInt(e.target.value) });
  const setSpeed = (speed) => sendCommand('SET_SPEED', { speed });

  if (!state) return <div className="w-72 bg-slate-900 border-r border-slate-800 p-4 text-slate-400">Loading...</div>;

  const ego = state.ego || {};
  const risk = state.risk || {};
  const metrics = state.metrics || {};
  
  return (
    <div className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col h-full overflow-y-auto overflow-x-hidden text-sm scrollbar-thin">
      {/* Simulation Controls */}
      <div className="p-4 border-b border-slate-800">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Simulation</h2>
        
        <select 
          className="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1.5 mb-4 text-slate-200 text-sm focus:outline-none focus:border-slate-500"
          value={state.scenario_id}
          onChange={setScenario}
        >
          <option value={1}>Scenario: Unmarked Village Road</option>
          <option value={2}>Scenario: Urban Intersection</option>
          <option value={3}>Scenario: Highway Merge</option>
          <option value={4}>Scenario: Dense Market Area</option>
          <option value={5}>Scenario: Sudden Cattle Crossing</option>
        </select>

        <div className="flex gap-2 mb-4">
          {!isRunning ? (
            <button onClick={handleStart} className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-1.5 rounded flex items-center justify-center gap-1 transition-colors">
              <Play size={14} /> Start
            </button>
          ) : (
            <button onClick={handlePause} className="flex-1 bg-yellow-600 hover:bg-yellow-500 text-white py-1.5 rounded flex items-center justify-center gap-1 transition-colors">
              <Pause size={14} /> Pause
            </button>
          )}
          <button onClick={handleReset} className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 py-1.5 rounded flex items-center justify-center gap-1 transition-colors border border-slate-700">
            <Square size={14} /> Reset
          </button>
        </div>

        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Speed</span>
          <div className="flex gap-1">
            {[0.5, 1, 2, 4].map(s => (
              <button 
                key={s} 
                onClick={() => setSpeed(s)}
                className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 border border-slate-700"
              >{s}x</button>
            ))}
          </div>
        </div>
      </div>

      {/* Ego Vehicle Status */}
      <div className="p-4 border-b border-slate-800">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1">
          <Activity size={14}/> Ego Vehicle
        </h2>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between"><span className="text-slate-400">Speed</span><span className="font-mono">{(ego.v * 3.6).toFixed(1)} km/h</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Acceleration</span><span className="font-mono">{ego.a?.toFixed(2) || '0.00'} m/s²</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Heading</span><span className="font-mono">{(ego.heading * 180 / Math.PI).toFixed(1)}°</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Steering</span><span className="font-mono">{(ego.steering * 180 / Math.PI).toFixed(2)}°</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Position</span><span className="font-mono">({ego.x?.toFixed(1)}, {ego.y?.toFixed(1)})</span></div>
        </div>
      </div>

      {/* Safety */}
      <div className="p-4 border-b border-slate-800">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1">
          <ShieldCheck size={14}/> Safety
        </h2>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between items-center">
            <span className="text-slate-400">Risk</span>
            <span className={`px-2 py-0.5 rounded font-bold ${
              risk.risk_level === 'SAFE' ? 'bg-green-900/50 text-green-400' :
              risk.risk_level === 'CAUTION' ? 'bg-yellow-900/50 text-yellow-400' :
              risk.risk_level === 'HIGH' ? 'bg-orange-900/50 text-orange-400' :
              'bg-red-900/50 text-red-500'
            }`}>{risk.risk_level || 'SAFE'}</span>
          </div>
          <div className="flex justify-between"><span className="text-slate-400">Behavior</span><span className={`font-mono font-bold ${(state.behavior || '').includes('BRAKE') ? 'text-red-400' : 'text-blue-400'}`}>{state.behavior || 'CRUISE'}</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Min TTC</span><span className="font-mono">{risk.min_ttc === null || risk.min_ttc > 900 ? '—' : `${risk.min_ttc?.toFixed(1)} s`}</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Clearance</span><span className="font-mono">{risk.min_clearance === null || risk.min_clearance > 900 ? '—' : `${risk.min_clearance?.toFixed(1)} m`}</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Stop Dist</span><span className="font-mono">{risk.stopping_distance?.toFixed(1) || '—'} m</span></div>
        </div>
      </div>

      {/* Planning */}
      <div className="p-4 border-b border-slate-800">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1">
          <Crosshair size={14}/> Planning
        </h2>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between"><span className="text-slate-400">Planner</span><span className="text-slate-300">Adaptive Free-Space</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Status</span><span className={`font-mono font-bold ${state.replanning ? 'text-orange-400 animate-pulse' : 'text-green-400'}`}>{state.replanning ? 'REPLANNING' : 'NOMINAL'}</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Total Replans</span><span className="font-mono">{metrics.replans || 0}</span></div>
          <div className="flex justify-between"><span className="text-slate-400">Latency</span><span className="font-mono">{(metrics.avg_plan_time_ms || 0).toFixed(2)} ms</span></div>
        </div>
      </div>

      {/* Sensors */}
      <div className="p-4">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1">
          <Radar size={14}/> Sensors
        </h2>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {['Camera', 'LiDAR', 'Radar', 'Fusion', 'Tracking', 'Prediction'].map(s => (
            <div key={s} className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
              <span className="text-slate-300">{s}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
