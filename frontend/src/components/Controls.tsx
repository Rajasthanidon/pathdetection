// @ts-nocheck
import { Play, Square, RefreshCw } from 'lucide-react';

export default function Controls({ sendCommand }) {
  return (
    <div className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
      <h2 className="text-lg font-semibold mb-3">Controls</h2>
      <div className="flex gap-2 mb-4">
        <button 
          onClick={() => sendCommand('START')}
          className="flex-1 bg-blue-600 hover:bg-blue-500 py-2 rounded flex items-center justify-center gap-1"
        >
          <Play size={16} /> Start
        </button>
        <button 
          onClick={() => sendCommand('PAUSE')}
          className="flex-1 bg-slate-600 hover:bg-slate-500 py-2 rounded flex items-center justify-center gap-1"
        >
          <Square size={16} /> Pause
        </button>
        <button 
          onClick={() => sendCommand('RESET')}
          className="flex-1 bg-slate-600 hover:bg-slate-500 py-2 rounded flex items-center justify-center gap-1"
        >
          <RefreshCw size={16} /> Reset
        </button>
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-sm text-slate-400">Select Scenario</label>
        <select 
          className="bg-slate-800 border border-slate-600 rounded p-2 text-sm"
          onChange={(e) => sendCommand('SET_SCENARIO', { scenario_id: parseInt(e.target.value) })}
        >
          <option value="1">1. Unmarked Village Road</option>
          <option value="2">2. Urban Intersection</option>
          <option value="3">3. Highway Merge</option>
          <option value="4">4. Dense Market</option>
          <option value="5">5. Sudden Cattle Crossing</option>
        </select>
      </div>
    </div>
  );
}
