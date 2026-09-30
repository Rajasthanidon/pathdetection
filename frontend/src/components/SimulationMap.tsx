// @ts-nocheck
import { useEffect, useRef } from 'react';

export default function SimulationMap({ state, followEgo, viewMode, demoState }) {
  const canvasRef = useRef(null);
  const prevStateRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    if (state && canvasRef.current) {
      prevStateRef.current = state;
    }
  }, [state]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    const resize = () => {
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    const render = () => {
      animationRef.current = requestAnimationFrame(render);
      if (!state || !prevStateRef.current) return;

      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      const scale = 16; // 16 pixels per meter for better detail

      ctx.fillStyle = '#1e2329'; // Base dark ground
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      let offsetX = cx;
      let offsetY = cy;
      if (followEgo && state.ego) {
        offsetX = cx - (state.ego.y * scale);
        offsetY = cy - (state.ego.x * scale) + (canvas.height * 0.25); // Offset down so we see ahead
      } else {
        // Overview mode
        offsetX = cx;
        offsetY = cy + (canvas.height * 0.3);
      }

      ctx.save();
      ctx.translate(offsetX, offsetY);
      
      // 1. Environment
      drawEnvironment(ctx, state.scenario_id, scale);

      // 2. Planning Visualization (Technical View)
      if (viewMode === 'technical') {
        if (state.candidates && state.candidates.length > 0) {
          state.candidates.forEach(cand => {
            ctx.beginPath();
            if (cand.is_collision) {
              ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)'; // Red for collision
              ctx.setLineDash([4, 4]);
            } else {
              ctx.strokeStyle = 'rgba(148, 163, 184, 0.3)'; // Slate for safe
              ctx.setLineDash([]);
            }
            ctx.lineWidth = 1;
            for (let i = 0; i < cand.path.length; i++) {
              const pt = cand.path[i];
              const px = pt.x !== undefined ? pt.x : pt[0];
              const py = pt.y !== undefined ? pt.y : pt[1];
              if (i === 0) ctx.moveTo(py * scale, px * scale);
              else ctx.lineTo(py * scale, px * scale);
            }
            ctx.stroke();
          });
          ctx.setLineDash([]);
        }
      }

      // 3. Final Planned Path
      if (state.path && state.path.length > 0) {
        ctx.beginPath();
        ctx.strokeStyle = '#3b82f6'; // Bright blue
        ctx.lineWidth = 3;
        for (let i = 0; i < state.path.length; i++) {
          const pt = state.path[i];
          const px = pt.x !== undefined ? pt.x : pt[0];
          const py = pt.y !== undefined ? pt.y : pt[1];
          if (i === 0) ctx.moveTo(py * scale, px * scale);
          else ctx.lineTo(py * scale, px * scale);
        }
        ctx.stroke();
      }

      // 4. Predictions (Technical View)
      if (viewMode === 'technical' && state.predictions) {
        for (const [id, predObj] of Object.entries(state.predictions)) {
          const predPath = predObj.path;
          ctx.beginPath();
          ctx.strokeStyle = predObj.motion_class === 'crossing' ? '#ef4444' : '#f59e0b'; // Red if crossing, amber if normal
          ctx.lineWidth = 2;
          ctx.setLineDash([4, 4]);
          for (let i = 0; i < predPath.length; i++) {
            const pt = predPath[i];
            const px = pt.x !== undefined ? pt.x : pt[0];
            const py = pt.y !== undefined ? pt.y : pt[1];
            if (i === 0) ctx.moveTo(py * scale, px * scale);
            else ctx.lineTo(py * scale, px * scale);
          }
          ctx.stroke();
          
          // Draw Uncertainty Ellipse at end of prediction
          if (predPath.length > 0) {
              const lastPt = predPath[predPath.length - 1];
              const px = lastPt.x !== undefined ? lastPt.x : lastPt[0];
              const py = lastPt.y !== undefined ? lastPt.y : lastPt[1];
              ctx.beginPath();
              ctx.fillStyle = predObj.motion_class === 'crossing' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)';
              ctx.arc(py * scale, px * scale, (predObj.uncertainty || 0.5) * scale * 2, 0, Math.PI * 2);
              ctx.fill();
          }
        }
        ctx.setLineDash([]);
      }

      // 5. Actors
      if (state.actors) {
        state.actors.forEach(actor => drawActor(ctx, actor, scale, viewMode));
      }

      // 6. Ego Vehicle
      if (state.ego) {
        drawEgo(ctx, state.ego, scale, state.risk, viewMode);
      }

      ctx.restore();
    };

    animationRef.current = requestAnimationFrame(render);
    return () => {
      cancelAnimationFrame(animationRef.current);
      window.removeEventListener('resize', resize);
    };
  }, [state, followEgo, viewMode]);

  const drawEnvironment = (ctx, scenario, scale) => {
    ctx.fillStyle = '#222';
    ctx.fillRect(-100 * scale, -200 * scale, 200 * scale, 400 * scale); // background mask

    if (scenario === 1) { // Village Road
      ctx.fillStyle = '#4a4131'; // Dirt
      ctx.fillRect(-15 * scale, -200 * scale, 30 * scale, 400 * scale);
      ctx.fillStyle = '#2d333b'; // Uneven Asphalt
      ctx.beginPath();
      ctx.moveTo(-6 * scale, -200 * scale);
      ctx.bezierCurveTo(-8 * scale, -100 * scale, -4 * scale, 0, -6 * scale, 100 * scale);
      ctx.lineTo(6 * scale, 100 * scale);
      ctx.bezierCurveTo(4 * scale, 0, 8 * scale, -100 * scale, 6 * scale, -200 * scale);
      ctx.fill();
    } 
    else if (scenario === 2) { // Intersection
      ctx.fillStyle = '#2d333b';
      ctx.fillRect(-10 * scale, -200 * scale, 20 * scale, 400 * scale); // Vertical
      ctx.fillRect(-100 * scale, -10 * scale, 200 * scale, 20 * scale); // Horizontal
      
      // Zebra crossings
      ctx.fillStyle = 'rgba(255,255,255,0.7)';
      for(let i=-8; i<=8; i+=2) {
        ctx.fillRect(i * scale, -15 * scale, 1 * scale, 4 * scale);
        ctx.fillRect(i * scale, 11 * scale, 1 * scale, 4 * scale);
      }
    } 
    else if (scenario === 3) { // Highway
      ctx.fillStyle = '#2d333b';
      ctx.fillRect(-12 * scale, -200 * scale, 24 * scale, 400 * scale);
      ctx.fillRect(12 * scale, -20 * scale, 8 * scale, 200 * scale); // Merge ramp
      ctx.beginPath();
      ctx.moveTo(12 * scale, -20 * scale);
      ctx.lineTo(20 * scale, -20 * scale);
      ctx.lineTo(12 * scale, -100 * scale);
      ctx.fill(); // Ramp taper

      // Lane markings
      ctx.strokeStyle = '#fff';
      ctx.setLineDash([8, 8]);
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(-4 * scale, -200 * scale); ctx.lineTo(-4 * scale, 200 * scale);
      ctx.moveTo(4 * scale, -200 * scale); ctx.lineTo(4 * scale, 200 * scale);
      ctx.stroke();
      ctx.setLineDash([]);
      
      // Shoulders
      ctx.strokeStyle = '#facc15'; // yellow edge
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(-11.5 * scale, -200 * scale); ctx.lineTo(-11.5 * scale, 200 * scale);
      ctx.moveTo(11.5 * scale, -200 * scale); ctx.lineTo(11.5 * scale, 200 * scale);
      ctx.stroke();
    } 
    else if (scenario === 4) { // Market
      ctx.fillStyle = '#333';
      ctx.fillRect(-20 * scale, -200 * scale, 40 * scale, 400 * scale);
      ctx.fillStyle = '#2d333b';
      ctx.fillRect(-6 * scale, -200 * scale, 12 * scale, 400 * scale);
      
      // Shops
      for(let y = -150; y < 150; y += 15) {
        ctx.fillStyle = (y % 2 === 0) ? '#0284c7' : '#ea580c';
        ctx.fillRect(-18 * scale, y * scale, 6 * scale, 10 * scale);
        ctx.fillStyle = (y % 2 !== 0) ? '#16a34a' : '#9333ea';
        ctx.fillRect(12 * scale, y * scale, 6 * scale, 10 * scale);
      }
    } 
    else if (scenario === 5) { // Cattle Crossing
      ctx.fillStyle = '#166534'; // Grass
      ctx.fillRect(-50 * scale, -200 * scale, 100 * scale, 400 * scale);
      ctx.fillStyle = '#4a4131'; // Dirt shoulders
      ctx.fillRect(-10 * scale, -200 * scale, 20 * scale, 400 * scale);
      ctx.fillStyle = '#2d333b'; // Road
      ctx.fillRect(-7 * scale, -200 * scale, 14 * scale, 400 * scale);
      // Center line
      ctx.strokeStyle = '#facc15';
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(0, -200 * scale);
      ctx.lineTo(0, 200 * scale);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  };

  const drawActor = (ctx, actor, scale, viewMode) => {
    ctx.save();
    ctx.translate(actor.y * scale, actor.x * scale);
    ctx.rotate(-actor.heading);
    
    const w = actor.width * scale;
    const l = actor.length * scale;
    const cls = actor.cls || actor.type;
    
    if (cls === 'Pedestrian') {
      ctx.fillStyle = '#fca5a5';
      ctx.beginPath();
      ctx.arc(0, 0, w/1.5, 0, Math.PI * 2);
      ctx.fill();
    } else if (cls === 'Motorcycle' || cls === 'Bicycle') {
      ctx.fillStyle = '#ef4444';
      ctx.fillRect(-w/2, -l/2, w, l);
      ctx.fillStyle = '#111';
      ctx.beginPath(); ctx.arc(0, l/2.5, w/3, 0, Math.PI*2); ctx.fill();
    } else if (cls === 'AutoRickshaw') {
      ctx.fillStyle = '#facc15'; // yellow body
      ctx.fillRect(-w/2, -l/2, w, l);
      ctx.fillStyle = '#22c55e'; // green roof
      ctx.fillRect(-w/2.2, -l/4, w*0.9, l*0.6);
      ctx.fillStyle = '#111'; // black windshield
      ctx.fillRect(-w/2.5, l/3, w*0.8, l/6);
    } else if (cls === 'Animal' || cls === 'ScriptedAnimal') {
      ctx.fillStyle = '#a8a29e';
      ctx.beginPath();
      ctx.ellipse(0, 0, w/2, l/2, 0, 0, Math.PI*2);
      ctx.fill();
    } else if (cls === 'Car') {
      ctx.fillStyle = '#64748b'; // generic car
      ctx.fillRect(-w/2, -l/2, w, l);
      ctx.fillStyle = '#1e293b';
      ctx.fillRect(-w/2.2, l/5, w*0.9, l/5); // windshield
      ctx.fillRect(-w/2.2, -l/2.5, w*0.9, l/6); // rear window
    } else {
      ctx.fillStyle = '#64748b';
      ctx.fillRect(-w/2, -l/2, w, l);
    }

    ctx.restore();

    // Detection label in Technical View
    if (viewMode === 'technical') {
      ctx.save();
      ctx.translate(actor.y * scale, actor.x * scale);
      ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
      ctx.fillRect(w, -l, 60, 24);
      ctx.fillStyle = '#38bdf8';
      ctx.font = '8px monospace';
      ctx.fillText(cls.substring(0, 10).toUpperCase(), w + 4, -l + 10);
      ctx.fillStyle = '#94a3b8';
      ctx.fillText(`v:${actor.speed.toFixed(1)}`, w + 4, -l + 20);
      ctx.restore();
    }
  };

  const drawEgo = (ctx, ego, scale, risk, viewMode) => {
    ctx.save();
    ctx.translate(ego.y * scale, ego.x * scale);
    ctx.rotate(-ego.heading);
    
    const w = ego.width * scale;
    const l = ego.length * scale;
    
    // Sensor field (Technical View)
    if (viewMode === 'technical') {
      ctx.fillStyle = 'rgba(56, 189, 248, 0.05)';
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.2)';
      ctx.beginPath();
      ctx.arc(0, 0, 80 * scale, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }

    // Risk aura
    if (risk && risk.risk_level === 'CRITICAL') {
      ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
      ctx.beginPath(); ctx.arc(0, 0, l*1.2, 0, Math.PI * 2); ctx.fill();
    } else if (risk && risk.risk_level === 'HIGH') {
      ctx.fillStyle = 'rgba(249, 115, 22, 0.2)';
      ctx.beginPath(); ctx.arc(0, 0, l*1.2, 0, Math.PI * 2); ctx.fill();
    }

    // Ego Body
    ctx.fillStyle = '#3b82f6';
    ctx.shadowColor = '#60a5fa';
    ctx.shadowBlur = 10;
    ctx.fillRect(-w/2, -l/2, w, l);
    ctx.shadowBlur = 0;

    // Windshield
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(-w/2.2, l/5, w*0.9, l/5);
    ctx.fillRect(-w/2.2, -l/2.5, w*0.9, l/6);
    
    // Headlights
    ctx.fillStyle = '#fef08a';
    ctx.fillRect(-w/2.1, l/2 - 2, 4, 4);
    ctx.fillRect(w/2.1 - 4, l/2 - 2, 4, 4);

    ctx.restore();
  };

  return (
    <div className="w-full h-full relative">
      <canvas ref={canvasRef} className="w-full h-full block" />
      
      {/* Demo Overlay */}
      {demoState === 'intro' && (
        <div className="absolute inset-0 bg-slate-950/80 flex items-center justify-center z-50">
          <div className="bg-slate-900 border border-slate-700 p-8 rounded-lg max-w-md text-center shadow-2xl">
            <h2 className="text-2xl font-bold text-blue-400 mb-2">SCENARIO {state?.scenario_id}</h2>
            <h3 className="text-xl text-slate-200 mb-6 font-semibold">
              {state?.scenario_id === 5 ? 'SUDDEN CATTLE CROSSING' : 
               state?.scenario_id === 1 ? 'UNMARKED VILLAGE ROAD' :
               state?.scenario_id === 2 ? 'URBAN INTERSECTION' :
               state?.scenario_id === 3 ? 'HIGHWAY MERGE' : 'DENSE MARKET AREA'}
            </h3>
            <div className="text-sm text-slate-400 text-left space-y-4">
              <p><strong>Challenge:</strong> Unpredictable dynamic obstacle intersecting trajectory in unstructured environment.</p>
              <p><strong>Objective:</strong> Detect, predict motion, evaluate TTC, and generate collision-free trajectory.</p>
            </div>
            <div className="mt-8">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            </div>
          </div>
        </div>
      )}

      {/* Planning Explainer Overlay */}
      {viewMode === 'technical' && state?.risk?.risk_level && state.risk.risk_level !== 'SAFE' && (
        <div className="absolute top-20 right-4 w-64 bg-slate-900/90 border border-slate-700 rounded p-4 text-xs shadow-lg backdrop-blur-sm z-40">
          <h4 className="font-bold text-slate-300 mb-2 border-b border-slate-800 pb-1">PLANNING EXPLAINER</h4>
          <div className="space-y-2 font-mono">
            <div><span className="text-slate-500">Risk:</span> <span className={state.risk.risk_level === 'CRITICAL' ? 'text-red-400' : 'text-orange-400'}>{state.risk.risk_level}</span></div>
            <div><span className="text-slate-500">Min TTC:</span> <span className="text-slate-300">{state.risk.min_ttc?.toFixed(2) || '—'}s</span></div>
            <div><span className="text-slate-500">Decision:</span> <span className="text-blue-400 font-bold">{state.behavior}</span></div>
            <div><span className="text-slate-500">Action:</span> Replanning using Adaptive Free-Space generation.</div>
            <div className="mt-2 text-[10px] text-slate-400 leading-tight">
              Planner evaluates lateral offsets based on dynamic predictions. Red candidates represent collision paths. Blue path minimizes curvature cost and maximizes clearance.
            </div>
          </div>
        </div>
      )}

      <div className="absolute bottom-4 left-4 bg-slate-950/80 p-3 rounded border border-slate-800 text-[10px] text-slate-300">
        <div className="font-bold mb-1 text-slate-400">LEGEND</div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          <div className="flex items-center gap-1"><div className="w-2 h-2 bg-[#3b82f6]"></div> Ego Vehicle</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 bg-[#64748b]"></div> Car/SUV</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 bg-[#facc15]"></div> Auto-rickshaw</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-[#fca5a5]"></div> Pedestrian</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-[#a8a29e]"></div> Animal / Cattle</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 bg-[#ef4444]"></div> 2-Wheeler</div>
          <div className="flex items-center gap-1"><div className="w-2 h-0.5 bg-[#3b82f6]"></div> Safe Path</div>
          {viewMode === 'technical' && <div className="flex items-center gap-1"><div className="w-2 h-0.5 bg-red-500 border-dashed"></div> Collision Candidate</div>}
          {viewMode === 'technical' && <div className="flex items-center gap-1"><div className="w-2 h-0.5 bg-orange-400 border-dashed"></div> Obstacle Prediction</div>}
        </div>
      </div>
    </div>
  );
}
