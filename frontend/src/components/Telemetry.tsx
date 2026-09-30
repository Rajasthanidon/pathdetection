// @ts-nocheck
import { Activity, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function Telemetry({ state }) {
  const { ego, risk, behavior, metrics, time } = state;

  const getRiskColor = (level) => {
    switch(level) {
      case 'SAFE': return 'text-green-400';
      case 'CAUTION': return 'text-yellow-400';
      case 'CRITICAL': return 'text-red-500 font-bold animate-pulse';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Ego State */}
      <div className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
        <h2 className="text-sm font-semibold text-slate-400 mb-2 uppercase tracking-wider">Ego Telemetry</h2>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>Speed: <span className="font-mono text-blue-300">{(ego.speed * 3.6).toFixed(1)} km/h</span></div>
          <div>Heading: <span className="font-mono text-blue-300">{(ego.heading * 180 / Math.PI).toFixed(0)}°</span></div>
          <div>Accel: <span className="font-mono text-blue-300">{ego.accel.toFixed(2)} m/s²</span></div>
          <div>Steer: <span className="font-mono text-blue-300">{ego.steer.toFixed(2)} rad</span></div>
        </div>
      </div>

      {/* Safety System */}
      <div className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
        <h2 className="text-sm font-semibold text-slate-400 mb-2 uppercase tracking-wider flex items-center gap-1">
          <ShieldCheck size={14} /> Safety & Planning
        </h2>
        <div className="flex flex-col gap-2 text-sm">
          <div className="flex justify-between">
            <span>Risk Level:</span>
            <span className={getRiskColor(risk.risk_level)}>{risk.risk_level}</span>
          </div>
          <div className="flex justify-between">
            <span>Behavior:</span>
            <span className={`font-mono ${behavior === 'EMERGENCY_BRAKE' ? 'text-red-500 font-bold' : 'text-blue-300'}`}>
              {behavior}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Min TTC:</span>
            <span className="font-mono text-slate-300">
              {risk.min_ttc === Infinity ? '∞' : `${risk.min_ttc.toFixed(1)}s`}
            </span>
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
        <h2 className="text-sm font-semibold text-slate-400 mb-2 uppercase tracking-wider flex items-center gap-1">
          <Activity size={14} /> Session Metrics
        </h2>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="bg-slate-800 p-2 rounded">
            <div className="text-slate-400">Time</div>
            <div className="text-lg font-mono">{time.toFixed(1)}s</div>
          </div>
          <div className="bg-slate-800 p-2 rounded">
            <div className="text-slate-400">Avg Plan Latency</div>
            <div className="text-lg font-mono text-green-400">{metrics.avg_plan_time_ms}ms</div>
          </div>
          <div className="bg-slate-800 p-2 rounded border border-red-500/30">
            <div className="text-slate-400">Collisions</div>
            <div className="text-lg font-mono text-red-400">{metrics.collisions}</div>
          </div>
          <div className="bg-slate-800 p-2 rounded border border-yellow-500/30">
            <div className="text-slate-400">Near Misses</div>
            <div className="text-lg font-mono text-yellow-400">{metrics.near_collisions}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
