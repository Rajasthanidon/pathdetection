// @ts-nocheck
export default function LiveHUD({ state }) {
  if (!state) return null;
  const ego = state.ego || {};
  const risk = state.risk || {};

    return (
    <div className="bg-slate-950/80 backdrop-blur border border-slate-800 rounded p-3 text-xs w-56 shadow-lg pointer-events-none">
      <div className="font-bold text-slate-400 mb-2 border-b border-slate-800 pb-1">LIVE HUD</div>
      
      <div className="flex justify-between mb-1">
        <span className="text-slate-500">Speed</span>
        <span className="font-mono text-slate-200">{(ego.speed * 3.6).toFixed(1)} km/h</span>
      </div>
      <div className="flex justify-between mb-1">
        <span className="text-slate-500">Accel</span>
        <span className={`font-mono ${(ego.accel || 0) < -1.0 ? 'text-red-400' : 'text-slate-200'}`}>{(ego.accel || 0).toFixed(2)} m/s²</span>
      </div>

      <div className="my-2 border-t border-slate-800"></div>

      <div className="flex justify-between mb-1">
        <span className="text-slate-500">TTC</span>
        <span className={`font-mono ${risk.min_ttc < 2.0 ? 'text-red-400' : 'text-slate-200'}`}>{risk.min_ttc === null || risk.min_ttc > 900 ? '—' : `${risk.min_ttc?.toFixed(1)} s`}</span>
      </div>
      <div className="flex justify-between mb-1">
        <span className="text-slate-500">Clearance</span>
        <span className="font-mono text-slate-200">{risk.min_clearance === null || risk.min_clearance > 900 ? '—' : `${risk.min_clearance?.toFixed(1)} m`}</span>
      </div>
      <div className="flex justify-between mb-1">
        <span className="text-slate-500">Stop Dist.</span>
        <span className="font-mono text-slate-200">{risk.stopping_distance?.toFixed(1)} m</span>
      </div>

      <div className="my-2 border-t border-slate-800"></div>

      <div className="flex justify-between mb-1">
        <span className="text-slate-500">Risk</span>
        <span className={`font-mono font-bold ${
          risk.risk_level === 'SAFE' ? 'text-green-400' :
          risk.risk_level === 'CAUTION' ? 'text-yellow-400' :
          risk.risk_level === 'HIGH' ? 'text-orange-400' : 'text-red-500'
        }`}>{risk.risk_level || 'SAFE'}</span>
      </div>
      <div className="flex justify-between mb-1">
        <span className="text-slate-500">Behavior</span>
        <span className={`font-mono font-bold ${(state.behavior || '').includes('BRAKE') ? 'text-red-400' : 'text-blue-400'}`}>{state.behavior || 'CRUISE'}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-slate-500">Planning</span>
        <span className={`font-mono font-bold ${state.replanning ? 'text-orange-400 animate-pulse' : 'text-green-400'}`}>
          {state.replanning ? 'REPLANNING' : 'NOMINAL'}
        </span>
      </div>

      {risk.counterfactual && (
        <div className="mt-2 bg-slate-900 border border-slate-700 p-1.5 rounded">
          <div className="text-[10px] text-slate-500 mb-1 font-bold">CURRENT PATH EVALUATION</div>
          <div className="flex justify-between text-[10px]">
            <span className="text-slate-400">Predicted Collision:</span>
            <span className={risk.counterfactual.collision ? "text-red-400 font-bold" : "text-green-400"}>
              {risk.counterfactual.collision ? "YES" : "NO"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
