// @ts-nocheck
import { useRef, useEffect } from 'react';

export default function SimulationView({ state }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Resize canvas to match parent
    const parent = canvas.parentElement;
    canvas.width = parent.clientWidth;
    canvas.height = parent.clientHeight;
    
    const { ego, actors, tracks, path } = state;
    
    // Scale and origin (Ego-centric or Fixed Map)
    // Let's use ego-centric view
    const scale = 10; // pixels per meter
    const cx = canvas.width / 2;
    const cy = canvas.height * 0.75; // Ego is at bottom 25%
    
    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#1e293b'; // slate-800
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Grid
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.width; i += 50) {
      ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
    }
    for (let i = 0; i < canvas.height; i += 50) {
      ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(canvas.width, i); ctx.stroke();
    }

    const drawRotatedRect = (x, y, w, h, heading, color, strokeColor) => {
      ctx.save();
      // Translate to screen coords relative to ego
      const sx = cx + (x - ego.x) * scale;
      const sy = cy - (y - ego.y) * scale;
      
      ctx.translate(sx, sy);
      // Math convention: heading 0 is right (x), Pi/2 is up (y)
      // Canvas convention: y is down. So rotation is -heading
      ctx.rotate(-heading + Math.PI/2); // point upwards
      
      ctx.fillStyle = color;
      ctx.fillRect(-w*scale/2, -h*scale/2, w*scale, h*scale);
      if (strokeColor) {
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = 2;
        ctx.strokeRect(-w*scale/2, -h*scale/2, w*scale, h*scale);
      }
      ctx.restore();
    };

    // Draw Tracks (Perception bounding boxes)
    tracks.forEach(t => {
      drawRotatedRect(t.x, t.y, t.width, t.length, t.heading, 'transparent', '#ef4444');
      // Draw velocity vector
      ctx.save();
      const sx = cx + (t.x - ego.x) * scale;
      const sy = cy - (t.y - ego.y) * scale;
      ctx.translate(sx, sy);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(t.speed * Math.cos(t.heading) * scale, -t.speed * Math.sin(t.heading) * scale);
      ctx.strokeStyle = '#ef4444';
      ctx.stroke();
      ctx.restore();
    });

    // Draw Actors (Ground Truth)
    actors.forEach(a => {
      let color = '#94a3b8'; // slate-400
      if (a.cls === 'Car') color = '#3b82f6';
      else if (a.cls === 'Pedestrian') color = '#f59e0b';
      else if (a.cls === 'Motorcycle') color = '#10b981';
      else if (a.cls === 'Animal') color = '#a855f7';
      else if (a.cls === 'AutoRickshaw') color = '#eab308';
      
      drawRotatedRect(a.x, a.y, a.width, a.length, a.heading, color);
    });

    // Draw Path
    if (path && path.length > 0) {
      ctx.beginPath();
      ctx.strokeStyle = '#3b82f6'; // blue-500
      ctx.lineWidth = 3;
      path.forEach((p, i) => {
        const sx = cx + (p[0] - ego.x) * scale;
        const sy = cy - (p[1] - ego.y) * scale;
        if (i === 0) ctx.moveTo(sx, sy);
        else ctx.lineTo(sx, sy);
      });
      ctx.stroke();
    }

    // Draw Ego
    drawRotatedRect(ego.x, ego.y, ego.width, ego.length, ego.heading, '#14b8a6'); // teal-500
    
  }, [state]);

  return (
    <div className="w-full h-full relative">
      <canvas ref={canvasRef} className="absolute inset-0 block"></canvas>
      {/* Overlay status */}
      <div className="absolute top-4 right-4 bg-slate-900/80 p-2 border border-slate-700 rounded text-sm font-mono text-slate-300 pointer-events-none">
        <div>Ego Pos: ({state.ego.x.toFixed(1)}, {state.ego.y.toFixed(1)})</div>
        <div>Total Actors: {state.actors.length}</div>
      </div>
    </div>
  );
}
