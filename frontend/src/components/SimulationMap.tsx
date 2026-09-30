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
      canvas.height = canvas.parentElement.height || canvas.parentElement.clientHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    const render = () => {
      animationRef.current = requestAnimationFrame(render);
      if (!state || !prevStateRef.current) return;

      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      const scale = 16; // pixels per meter

      // Clear background
      ctx.fillStyle = '#1e2329';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Camera logic
      let offsetX = cx;
      let offsetY = cy;
      if (followEgo && state.ego) {
        // SAE Coordinates: X is forward, Y is left.
        // Canvas: -Y is UP, -X is LEFT.
        // So ego screen pos: X = -ego.y, Y = -ego.x
        offsetX = cx - (-state.ego.y * scale);
        offsetY = cy - (-state.ego.x * scale) + (canvas.height * 0.25); // Offset to see ahead
      } else {
        // Overview mode (static)
        offsetX = cx;
        offsetY = cy + (canvas.height * 0.3);
      }

      ctx.save();
      ctx.translate(offsetX, offsetY);
      
      // 1. Environment / Roads
      drawEnvironment(ctx, state.scenario_id, scale);

      // 2. Planning Visualization (Technical View)
      if (viewMode === 'technical') {
        if (state.candidates && state.candidates.length > 0) {
          state.candidates.forEach(cand => {
            ctx.beginPath();
            if (cand.is_collision) {
              ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)'; // Red (collision)
              ctx.setLineDash([4, 4]);
            } else {
              ctx.strokeStyle = 'rgba(148, 163, 184, 0.3)'; // Slate (safe candidate)
              ctx.setLineDash([]);
            }
            ctx.lineWidth = 1;
            for (let i = 0; i < cand.path.length; i++) {
              const pt = cand.path[i];
              const px = pt.x !== undefined ? pt.x : pt[0];
              const py = pt.y !== undefined ? pt.y : pt[1];
              // Map to Canvas: physics X -> canvas -Y, physics Y -> canvas -X
              if (i === 0) ctx.moveTo(-py * scale, -px * scale);
              else ctx.lineTo(-py * scale, -px * scale);
            }
            ctx.stroke();
          });
          ctx.setLineDash([]);
        }
      }

      // 3. Final Planned Path
      if (state.path && state.path.length > 0) {
        ctx.beginPath();
        ctx.strokeStyle = '#3b82f6'; // Bright blue safe path
        ctx.lineWidth = 3;
        for (let i = 0; i < state.path.length; i++) {
          const pt = state.path[i];
          const px = pt.x !== undefined ? pt.x : pt[0];
          const py = pt.y !== undefined ? pt.y : pt[1];
          if (i === 0) ctx.moveTo(-py * scale, -px * scale);
          else ctx.lineTo(-py * scale, -px * scale);
        }
        ctx.stroke();
      }

      // 4. Predictions (Technical View)
      if (viewMode === 'technical' && state.predictions) {
        for (const [id, predObj] of Object.entries(state.predictions)) {
          const predPath = predObj.path;
          ctx.beginPath();
          ctx.strokeStyle = predObj.motion_class === 'crossing' ? '#ef4444' : '#f59e0b';
          ctx.lineWidth = 2;
          ctx.setLineDash([4, 4]);
          for (let i = 0; i < predPath.length; i++) {
            const pt = predPath[i];
            const px = pt.x !== undefined ? pt.x : pt[0];
            const py = pt.y !== undefined ? pt.y : pt[1];
            if (i === 0) ctx.moveTo(-py * scale, -px * scale);
            else ctx.lineTo(-py * scale, -px * scale);
          }
          ctx.stroke();
          
          if (predPath.length > 0) {
              const lastPt = predPath[predPath.length - 1];
              const px = lastPt.x !== undefined ? lastPt.x : lastPt[0];
              const py = lastPt.y !== undefined ? lastPt.y : lastPt[1];
              ctx.beginPath();
              ctx.fillStyle = predObj.motion_class === 'crossing' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)';
              ctx.arc(-py * scale, -px * scale, (predObj.uncertainty || 0.5) * scale * 2, 0, Math.PI * 2);
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
    // Base mask
    ctx.fillStyle = '#222';
    // X goes from 0 to 200 (Canvas Y from 0 to -200)
    // Y goes from -100 to 100 (Canvas X from 100 to -100)
    ctx.fillRect(-50 * scale, -250 * scale, 100 * scale, 300 * scale);

    if (scenario === 1) { // Village Road
      ctx.fillStyle = '#4a4131'; // Dirt
      ctx.fillRect(-20 * scale, -250 * scale, 40 * scale, 300 * scale);
      
      // Uneven Asphalt road. Drivable is approx Y in [-3, 3] -> Canvas X in [3, -3]
      ctx.fillStyle = '#2d333b';
      ctx.beginPath();
      ctx.moveTo(3.5 * scale, -250 * scale);
      ctx.bezierCurveTo(4.5 * scale, -100 * scale, 2.5 * scale, 0, 3.5 * scale, 50 * scale);
      ctx.lineTo(-3.5 * scale, 50 * scale);
      ctx.bezierCurveTo(-2.5 * scale, 0, -4.5 * scale, -100 * scale, -3.5 * scale, -250 * scale);
      ctx.fill();
      
      // Draw obstacles (Stalls)
      ctx.fillStyle = '#b45309';
      ctx.fillRect(-3.5 * scale, -20 * scale, -2 * scale, -5 * scale); // x=20, y=3.5 (left stall)
      ctx.fillRect(3.5 * scale, -50 * scale, 2 * scale, -5 * scale); // x=50, y=-3.5 (right stall)
    } 
    else if (scenario === 2) { // Intersection
      ctx.fillStyle = '#2d333b';
      // Vertical road
      ctx.fillRect(-5 * scale, -250 * scale, 10 * scale, 300 * scale); 
      // Horizontal road
      ctx.fillRect(-50 * scale, -35 * scale, 100 * scale, 10 * scale); 
      
      // Buildings
      ctx.fillStyle = '#1e293b';
      ctx.fillRect(-8 * scale, -45 * scale, -15 * scale, -100 * scale); // TL
      ctx.fillRect(8 * scale, -45 * scale, 15 * scale, -100 * scale); // TR
      ctx.fillRect(-8 * scale, -25 * scale, -15 * scale, 50 * scale); // BL
      ctx.fillRect(8 * scale, -25 * scale, 15 * scale, 50 * scale); // BR
      
      // Zebra crossings
      ctx.fillStyle = 'rgba(255,255,255,0.6)';
      for(let i=-4; i<=4; i+=1.5) {
        ctx.fillRect(i * scale, -22 * scale, 0.8 * scale, 4 * scale);
        ctx.fillRect(i * scale, -38 * scale, 0.8 * scale, 4 * scale);
      }
    } 
    else if (scenario === 3) { // Highway
      // Main Highway
      ctx.fillStyle = '#2d333b';
      ctx.fillRect(-6 * scale, -250 * scale, 12 * scale, 300 * scale);
      
      // Merge Lane (diagonal from right side of screen / physics -Y)
      ctx.beginPath();
      ctx.moveTo(6 * scale, -250 * scale);
      ctx.lineTo(6 * scale, -50 * scale); // Converges at X=50
      ctx.lineTo(14 * scale, 50 * scale); // Starts further right
      ctx.lineTo(14 * scale, -250 * scale);
      ctx.fill();
      
      // Lane markings
      ctx.strokeStyle = '#fff';
      ctx.setLineDash([8, 8]);
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, -250 * scale); ctx.lineTo(0, 50 * scale);
      ctx.stroke();
      ctx.setLineDash([]);
      
      // Left Shoulder
      ctx.strokeStyle = '#facc15';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(-6 * scale, -250 * scale); ctx.lineTo(-6 * scale, 50 * scale);
      ctx.stroke();
      
      // Merge Lane Boundary Marking (Right Side)
      ctx.strokeStyle = '#facc15';
      ctx.beginPath();
      ctx.moveTo(6 * scale, -250 * scale);
      ctx.lineTo(6 * scale, -50 * scale);
      ctx.lineTo(14 * scale, 50 * scale);
      ctx.stroke();
      
      // Walls
      ctx.fillStyle = '#475569';
      ctx.fillRect(-7.5 * scale, -250 * scale, -1 * scale, 300 * scale); // Left wall
      
      ctx.beginPath(); // Right wall follows merge lane
      ctx.moveTo(15 * scale, -250 * scale);
      ctx.lineTo(15 * scale, 50 * scale);
      ctx.lineTo(14 * scale, 50 * scale);
      ctx.lineTo(14 * scale, -250 * scale);
      ctx.fill();
    }
    else if (scenario === 4) { // Market
      ctx.fillStyle = '#333';
      ctx.fillRect(-20 * scale, -250 * scale, 40 * scale, 300 * scale);
      ctx.fillStyle = '#2d333b';
      ctx.fillRect(-2.5 * scale, -250 * scale, 5 * scale, 300 * scale);
      
      // Shops
      for(let x = 10; x < 150; x += 12) {
        ctx.fillStyle = (x % 24 === 0) ? '#0284c7' : '#ea580c';
        ctx.fillRect(-3.5 * scale, -x * scale, -2 * scale, -8 * scale);
        ctx.fillStyle = (x % 24 !== 0) ? '#16a34a' : '#9333ea';
        ctx.fillRect(3.5 * scale, -x * scale, 2 * scale, -8 * scale);
      }
    } 
    else if (scenario === 5) { // Cattle Crossing
      ctx.fillStyle = '#166534'; // Grass
      ctx.fillRect(-30 * scale, -250 * scale, 60 * scale, 300 * scale);
      ctx.fillStyle = '#4a4131'; // Dirt shoulders
      ctx.fillRect(-5 * scale, -250 * scale, 10 * scale, 300 * scale);
      ctx.fillStyle = '#2d333b'; // Road
      ctx.fillRect(-3.5 * scale, -250 * scale, 7 * scale, 300 * scale);
      
      // Center line
      ctx.strokeStyle = '#facc15';
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(0, -250 * scale);
      ctx.lineTo(0, 50 * scale);
      ctx.stroke();
      ctx.setLineDash([]);
      
      // Trees
      ctx.fillStyle = '#065f46';
      ctx.beginPath(); ctx.arc(-4.5 * scale, -25 * scale, 1.5 * scale, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(4.5 * scale, -40 * scale, 1.5 * scale, 0, Math.PI*2); ctx.fill();
    }
  };

  const drawActor = (ctx, actor, scale, viewMode) => {
    ctx.save();
    // Map coords
    ctx.translate(-actor.y * scale, -actor.x * scale);
    // Heading: positive is CCW (Left) in math, so Canvas must rotate negative to turn Left (which is CCW in Canvas)
    // Wait, in Canvas, rotation is clockwise. -heading turns CCW.
    ctx.rotate(-actor.heading);
    
    // In local canvas coords after translation/rotation:
    // +Y is down the screen, -Y is up the screen.
    // +X is right, -X is left.
    // The vehicle faces Forward (+X in physics), which mapped to -Y (UP) in Canvas.
    // So the FRONT of the vehicle is drawn at -Y.
    const w = actor.width * scale; // physics width (lateral Y axis) -> maps to Canvas X
    const l = actor.length * scale; // physics length (forward X axis) -> maps to Canvas Y
    const cls = actor.cls || actor.type;
    
    if (cls === 'Pedestrian') {
      ctx.fillStyle = '#fca5a5';
      ctx.beginPath();
      ctx.arc(0, 0, w/1.5, 0, Math.PI * 2);
      ctx.fill();
      // Shoulders/heading indicator
      ctx.fillStyle = '#b91c1c';
      ctx.beginPath();
      ctx.arc(0, -w/2, w/4, 0, Math.PI * 2); // Front is -Y
      ctx.fill();
    } else if (cls === 'Motorcycle' || cls === 'Bicycle') {
      ctx.fillStyle = '#ef4444';
      ctx.fillRect(-w/2, -l/2, w, l);
      ctx.fillStyle = '#111'; // Rider helmet
      ctx.beginPath(); ctx.arc(0, 0, w/2.5, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = '#fef08a'; // Headlight at front (-Y)
      ctx.fillRect(-w/4, -l/2, w/2, l/6);
    } else if (cls === 'AutoRickshaw') {
      ctx.fillStyle = '#facc15'; // yellow body
      ctx.fillRect(-w/2, -l/2, w, l);
      ctx.fillStyle = '#22c55e'; // green roof
      ctx.fillRect(-w/2.2, -l/3, w*0.9, l*0.6);
      ctx.fillStyle = '#111'; // black windshield at front (-Y)
      ctx.fillRect(-w/2.5, -l/2.5, w*0.8, l/6);
    } else if (cls === 'Animal' || cls === 'ScriptedAnimal') {
      ctx.fillStyle = '#a8a29e';
      ctx.beginPath();
      // Oval for cow body (length is along Y now)
      ctx.ellipse(0, 0, w/2, l/2, 0, 0, Math.PI*2);
      ctx.fill();
      // Head at front (-Y)
      ctx.fillStyle = '#78716c';
      ctx.beginPath(); ctx.arc(0, -l/2, w/2, 0, Math.PI*2); ctx.fill();
    } else if (cls === 'Car') {
      ctx.fillStyle = '#64748b'; // generic car
      ctx.fillRect(-w/2, -l/2, w, l);
      ctx.fillStyle = '#1e293b';
      // Windshield at front (-Y)
      ctx.fillRect(-w/2.2, -l/2.5, w*0.9, l/5); 
      // Rear window
      ctx.fillRect(-w/2.2, l/4, w*0.9, l/6); 
    } else {
      ctx.fillStyle = '#64748b';
      ctx.fillRect(-w/2, -l/2, w, l);
    }

    ctx.restore();

    // Detection label in Technical View (non-rotated)
    if (viewMode === 'technical') {
      ctx.save();
      ctx.translate(-actor.y * scale, -actor.x * scale);
      ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
      ctx.fillRect(w/2, -l/2 - 15, 60, 24);
      ctx.fillStyle = '#38bdf8';
      ctx.font = '8px monospace';
      ctx.fillText(cls.substring(0, 10).toUpperCase(), w/2 + 4, -l/2 - 5);
      ctx.fillStyle = '#94a3b8';
      ctx.fillText(`v:${actor.speed.toFixed(1)}`, w/2 + 4, -l/2 + 5);
      ctx.restore();
    }
  };

  const drawEgo = (ctx, ego, scale, risk, viewMode) => {
    ctx.save();
    ctx.translate(-ego.y * scale, -ego.x * scale);
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

    // Windshield (Front is -Y)
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(-w/2.2, -l/2.5, w*0.9, l/5); // Front
    ctx.fillRect(-w/2.2, l/4, w*0.9, l/6);    // Rear
    
    // Headlights (Front is -Y)
    ctx.fillStyle = '#fef08a';
    ctx.fillRect(-w/2.1, -l/2 - 2, 4, 4);
    ctx.fillRect(w/2.1 - 4, -l/2 - 2, 4, 4);

    // Turn signal/brake indicators
    if (ego.accel < -1.0) {
      // Brake lights at Rear (+Y)
      ctx.fillStyle = '#ef4444';
      ctx.shadowColor = '#ef4444';
      ctx.shadowBlur = 5;
      ctx.fillRect(-w/2.1, l/2 - 2, 4, 4);
      ctx.fillRect(w/2.1 - 4, l/2 - 2, 4, 4);
      ctx.shadowBlur = 0;
    }

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
              <p><strong>Objective:</strong> Detect, predict motion, evaluate TTC, strictly respect road constraints, and generate collision-free trajectory.</p>
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
              Planner evaluates lateral offsets based on dynamic predictions. Red candidates represent collision paths or road boundary violations. Blue path minimizes curvature cost and maximizes clearance without leaving the road.
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
