// @ts-nocheck
import { Clock } from 'lucide-react';

export default function BottomPanel({ state, events }) {
  const metrics = state?.metrics || {};

  return (
    <div className="h-48 bg-slate-950 border-t border-slate-800 shrink-0 flex">
      {/* Event Timeline */}
      <div className="w-1/3 border-r border-slate-800 p-4 flex flex-col h-full">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1">
          <Clock size={14} /> Live Events
        </h2>
        <div className="flex-1 overflow-y-auto space-y-1 scrollbar-thin text-xs font-mono">
          {events.length === 0 && <div className="text-slate-600 italic">No events yet...</div>}
          {events.map((e, i) => (
            <div key={i} className="flex gap-2">
              <span className="text-slate-600">[{e.time}]</span>
              <span className={e.colorClass}>{e.text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Metrics */}
      <div className="w-2/3 p-4 flex flex-col h-full">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Metrics & Statistics</h2>
        <div className="grid grid-cols-4 gap-4 flex-1">
          <div className="bg-slate-900 rounded border border-slate-800 p-3 flex flex-col justify-center items-center">
            <div className="text-slate-400 text-xs mb-1">Collisions</div>
            <div className={`text-xl font-mono font-bold ${metrics.collisions > 0 ? 'text-red-500' : 'text-slate-200'}`}>
              {metrics.collisions || 0}
            </div>
          </div>
          <div className="bg-slate-900 rounded border border-slate-800 p-3 flex flex-col justify-center items-center">
            <div className="text-slate-400 text-xs mb-1">Near Misses</div>
            <div className="text-xl font-mono font-bold text-yellow-400">
              {metrics.near_misses || 0}
            </div>
          </div>
          <div className="bg-slate-900 rounded border border-slate-800 p-3 flex flex-col justify-center items-center">
            <div className="text-slate-400 text-xs mb-1">Total Replans</div>
            <div className="text-xl font-mono font-bold text-blue-400">
              {metrics.replans || 0}
            </div>
          </div>
          <div className="bg-slate-900 rounded border border-slate-800 p-3 flex flex-col justify-center items-center">
            <div className="text-slate-400 text-xs mb-1">Avg Plan Latency</div>
            <div className="text-xl font-mono font-bold text-green-400">
              {(metrics.avg_plan_time_ms || 0).toFixed(2)} <span className="text-sm">ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
