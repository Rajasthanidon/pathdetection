// @ts-nocheck
import { useEffect, useState, useRef } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import SimulationMap from './components/SimulationMap';
import BottomPanel from './components/BottomPanel';
import LiveHUD from './components/LiveHUD';

export default function App() {
  const [state, setState] = useState(null);
  const [events, setEvents] = useState([]);
  const ws = useRef(null);
  const [connected, setConnected] = useState(false);
  const [followEgo, setFollowEgo] = useState(true);
  const [viewMode, setViewMode] = useState('technical'); // 'simple' or 'technical'
  const [demoState, setDemoState] = useState(null); // 'intro', 'running', null

  const [connectionState, setConnectionState] = useState('DISCONNECTED'); // CONNECTING, CONNECTED, DISCONNECTED, RECONNECTING

  useEffect(() => {
    let reconnectTimeout = null;
    let isMounted = true;
    let reconnectAttempts = 0;
    const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8001/ws';

    const connect = () => {
      if (!isMounted) return;
      setConnectionState(reconnectAttempts > 0 ? 'RECONNECTING' : 'CONNECTING');
      
      if (ws.current) {
        ws.current.close();
      }

      const socket = new WebSocket(WS_URL);
      ws.current = socket;

      socket.onopen = () => {
        reconnectAttempts = 0;
        // Handshake
        socket.send(JSON.stringify({ type: 'HELLO', client: 'frontend' }));
      };

      socket.onclose = () => {
        if (!isMounted) return;
        setConnected(false);
        setConnectionState('DISCONNECTED');
        ws.current = null;
        
        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
        reconnectAttempts++;
        reconnectTimeout = setTimeout(connect, delay);
      };

      socket.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'READY') {
          setConnected(true);
          setConnectionState('CONNECTED');
        } else if (msg.type === 'STATE') {
          setState(msg.data);
          if (!connected && connectionState === 'CONNECTING') {
             setConnected(true);
             setConnectionState('CONNECTED');
          }
          
          const prevState = stateRef.current;
          if (prevState) {
              const timeStr = msg.data.time?.toFixed(2) + 's';
              const addSimEvent = (text, color) => {
                  setEvents(prev => [...prev, { time: timeStr, text, colorClass: color }].slice(-20));
              };

              // Tracks
              if (msg.data.tracks.length > prevState.tracks.length) {
                 const newTrack = msg.data.tracks[msg.data.tracks.length - 1];
                 addSimEvent(`✓ Track established: ${newTrack.cls} (${newTrack.id})`, 'text-blue-400');
              }
              
              // TTC
              if (msg.data.risk.min_ttc < 2.5 && prevState.risk.min_ttc >= 2.5) {
                 addSimEvent(`⚠ TTC dropped to ${msg.data.risk.min_ttc.toFixed(1)}s`, 'text-yellow-400');
              }
              
              // Counterfactual
              if (msg.data.risk.counterfactual?.collision && !prevState.risk.counterfactual?.collision) {
                 addSimEvent(`✕ Current trajectory rejected (Predicted collision)`, 'text-red-400');
              }
              
              // Replanning
              if (msg.data.replanning && !prevState.replanning) {
                 addSimEvent(`↻ Replanning started: evaluating alternatives`, 'text-orange-400');
              }
              if (!msg.data.replanning && prevState.replanning && !msg.data.risk.counterfactual?.collision) {
                 addSimEvent(`✓ Safe trajectory selected`, 'text-green-400');
              }

              // Risk
              if (msg.data.risk.risk_level !== prevState.risk.risk_level) {
                 if (msg.data.risk.risk_level === 'CRITICAL') addSimEvent(`🔴 Collision risk = CRITICAL`, 'text-red-500');
                 if (msg.data.risk.risk_level === 'HIGH') addSimEvent(`⚠ Collision risk = HIGH`, 'text-orange-500');
                 if (msg.data.risk.risk_level === 'SAFE') addSimEvent(`✓ Risk returned to SAFE. Clearance: ${msg.data.risk.min_clearance?.toFixed(1)}m`, 'text-green-400');
              }
              
              // Behavior
              if ((msg.data.behavior || '').includes('BRAKE') && !(prevState.behavior || '').includes('BRAKE')) {
                 addSimEvent(`↓ Autonomous braking initiated`, 'text-red-400');
              }
              if (msg.data.behavior === 'CRUISE' && prevState.behavior !== 'CRUISE') {
                 addSimEvent(`→ Resume CRUISE`, 'text-slate-300');
              }
          }
          stateRef.current = msg.data;
        }
      };
    };

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (ws.current) {
        ws.current.close();
        ws.current = null;
      }
    };
  }, []); // Run exactly once on mount

  const stateRef = useRef(null);

  const addEvent = (text, colorClass = 'text-slate-300', overrideTime = null) => {
    const timeStr = overrideTime || new Date().toLocaleTimeString('en-US', { hour12: false });
    setEvents(prev => [...prev, { time: timeStr, text, colorClass }].slice(-20)); // Keep last 20
  };

  const sendCommand = (cmd, data = {}) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: cmd, ...data }));
      if (cmd === 'START') addEvent('Simulation Started', 'text-blue-400');
      if (cmd === 'PAUSE') addEvent('Simulation Paused', 'text-yellow-400');
      if (cmd === 'RESET') {
        addEvent('Simulation Reset', 'text-slate-400');
        setEvents([]);
      }
      if (cmd === 'SET_SCENARIO') {
        addEvent(`Scenario changed to ${data.scenario_id}`, 'text-blue-400');
        setDemoState('intro');
        setTimeout(() => setDemoState(null), 3000); // hide intro after 3s
      }
    }
  };

  const runDemo = () => {
    sendCommand('SET_SCENARIO', { scenario_id: 5 });
    setDemoState('intro');
    setTimeout(() => {
      setDemoState('running');
      sendCommand('START');
    }, 3000);
  };

  return (
    <div className="flex flex-col h-screen w-full bg-slate-900 text-slate-200 overflow-hidden font-sans">
      <Header connected={connected} connectionState={connectionState} state={state} viewMode={viewMode} setViewMode={setViewMode} runDemo={runDemo} />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar state={state} sendCommand={sendCommand} />
        
        <div className="flex-1 relative flex flex-col bg-[#1e2329]">
          <div className="absolute top-4 right-4 z-10">
            <LiveHUD state={state} />
          </div>
          
          <div className="absolute top-4 left-4 z-10 flex gap-2">
            <button 
              onClick={() => setFollowEgo(!followEgo)}
              className={`px-3 py-1 text-xs rounded border ${followEgo ? 'bg-blue-600/80 border-blue-500 text-white' : 'bg-slate-800/80 border-slate-600 text-slate-300'}`}
            >
              {followEgo ? '● Follow Ego' : '○ Free Camera'}
            </button>
            <button 
              onClick={() => setFollowEgo(false)}
              className="px-3 py-1 text-xs rounded border bg-slate-800/80 border-slate-600 text-slate-300 hover:bg-slate-700"
            >
              Overview
            </button>
          </div>

          <SimulationMap state={state} followEgo={followEgo} viewMode={viewMode} demoState={demoState} />
        </div>
      </div>
      
      <BottomPanel state={state} events={events} />
    </div>
  );
}
