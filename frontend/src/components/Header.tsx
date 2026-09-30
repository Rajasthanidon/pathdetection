// @ts-nocheck
import { ShieldCheck, Server, CarFront, Zap } from 'lucide-react';

export default function Header({ connected, connectionState, state, viewMode, setViewMode, runDemo }) {
  const getScenarioName = (id) => {
    const names = {
      1: 'Unmarked Village Road',
      2: 'Urban Intersection',
      3: 'Highway Merge',
      4: 'Dense Market Area',
      5: 'Sudden Cattle Crossing'
    };
    return names[id] || 'Unknown';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'RUNNING': return 'text-green-400';
      case 'PAUSED': return 'text-yellow-400';
      case 'ERROR': return 'text-red-500 font-bold animate-pulse';
      case 'COMPLETED': return 'text-blue-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <header className="h-14 bg-slate-950 border-b border-slate-800 flex items-center justify-between px-6 shrink-0 shadow-md">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <CarFront className="text-teal-400" size={24} />
          <div>
            <h1 className="text-lg font-bold text-slate-100 leading-none">AUTONOMOUS INDIA</h1>
            <p className="text-[10px] text-slate-400 uppercase tracking-widest mt-1">Adaptive Path Planning & Collision Avoidance</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex flex-col items-end">
          <div className="text-xs text-slate-400">Scenario</div>
          <div className="text-sm font-semibold text-slate-200">
            {state ? getScenarioName(state.scenario_id) : 'Loading...'}
          </div>
        </div>
        
        <div className="h-8 w-px bg-slate-800"></div>

        <div className="flex items-center gap-4 text-xs font-medium">
          <div className="flex items-center bg-slate-900 p-1 rounded-md border border-slate-800">
            <button onClick={() => setViewMode('simple')} className={`px-2 py-1 rounded ${viewMode === 'simple' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}>Simple View</button>
            <button onClick={() => setViewMode('technical')} className={`px-2 py-1 rounded ${viewMode === 'technical' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}>Technical View</button>
          </div>
          
          <button onClick={runDemo} className="bg-purple-600 hover:bg-purple-500 text-white px-3 py-1.5 rounded flex items-center gap-1 ml-2 font-bold transition-all shadow-[0_0_10px_rgba(147,51,234,0.5)]">
            ▶ RUN DEMO
          </button>
          
          <div className="h-8 w-px bg-slate-800 mx-2"></div>
          
          <div className="flex items-center gap-2">
            <Server size={14} className={connectionState === 'CONNECTED' ? 'text-green-500' : connectionState === 'RECONNECTING' || connectionState === 'CONNECTING' ? 'text-yellow-500 animate-pulse' : 'text-red-500'} />
            <span className={connectionState === 'CONNECTED' ? 'text-green-400' : connectionState === 'RECONNECTING' || connectionState === 'CONNECTING' ? 'text-yellow-400' : 'text-red-400'}>
              {connectionState === 'CONNECTED' ? 'Backend Connected' : connectionState === 'RECONNECTING' ? 'Reconnecting...' : connectionState === 'CONNECTING' ? 'Connecting...' : 'Disconnected'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Zap size={14} className={state && state.status === 'RUNNING' ? 'text-yellow-400' : 'text-slate-500'} />
            <span className={state ? getStatusColor(state.status) : 'text-slate-500'}>
              {state ? `● ${state.status}` : '● WAITING'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
