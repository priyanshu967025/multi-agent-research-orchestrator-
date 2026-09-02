import React, { useState, useEffect, useRef } from 'react';
import { Layers, Cpu, Activity, Sparkles, Orbit, ShieldCheck, Zap, Database } from 'lucide-react';

export default function Ethnocare3DCore({ isRunning = false, activeStage = '' }) {
  const [exploded, setExploded] = useState(false);
  const [activeHotspot, setActiveHotspot] = useState(0);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const containerRef = useRef(null);

  const hotspots = [
    { id: 0, tag: '01', title: 'LANGGRAPH STATE MACHINE', desc: 'Autonomous DAG state machine with conditional routing and dynamic revision feedback loops (max: 2 cycles).' },
    { id: 1, tag: '02', title: 'CHROMADB DUAL-VECTOR SPACE', desc: 'Dense RAG embeddings (all-MiniLM-L6-v2) across research_docs and past_research collections.' },
    { id: 2, tag: '03', title: 'FACT-CHECK VERIFICATION GATE', desc: 'Claim-by-claim ground truth validation against cited source snippets to eliminate hallucinations.' },
    { id: 3, tag: '04', title: 'MULTI-PROVIDER LLM FAILOVER', desc: 'Real-time failover across Groq, Gemini, OpenAI, Anthropic, and local Ollama nodes.' }
  ];

  const agentNodes = [
    { id: 'researcher', name: 'RESEARCHER', tag: '01', color: '#c084fc', angle: 0, desc: 'Multi-query web search & ChromaDB RAG' },
    { id: 'analyst', name: 'ANALYST', tag: '02', color: '#00F5F3', angle: 90, desc: 'Evidence synthesis & theme extraction' },
    { id: 'fact_checker', name: 'FACT-CHECKER', tag: '03', color: '#fbbf24', angle: 180, desc: 'Ground truth verification & QA gate' },
    { id: 'writer', name: 'WRITER', tag: '04', color: '#34d399', angle: 270, desc: 'Markdown synthesis & citation anchoring' }
  ];

  const handleMouseMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 20;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * -20;
    setMousePos({ x, y });
  };

  const handleMouseLeave = () => {
    setMousePos({ x: 0, y: 0 });
  };

  const orbitRadius = exploded ? 160 : 120;
  const speed = isRunning ? '2.5s' : '8s';

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      background: '#000000',
      border: '1px solid rgba(255, 255, 255, 0.12)',
      borderRadius: 'var(--radius-sm)',
      padding: '1.25rem',
      marginBottom: '2.5rem',
      overflow: 'hidden',
    }}>
      {/* Header Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
        paddingBottom: '0.75rem',
        marginBottom: '1rem',
        flexWrap: 'wrap',
        gap: '0.75rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: '6px',
            height: '6px',
            background: 'var(--color-accent)',
            boxShadow: '0 0 8px var(--color-accent)'
          }} />
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.74rem',
            fontWeight: 700,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: '#ffffff'
          }}>
            [ 3D ORCHESTRATION CORE // ARCHITECTURAL INSPECTOR ]
          </span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1.25rem',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.72rem',
          color: 'var(--text-muted)',
        }}>
          <div>
            STATUS: <strong style={{ color: isRunning ? 'var(--color-accent)' : '#34d399' }}>
              {isRunning ? (activeStage?.toUpperCase() || 'RUNNING') : 'STANDBY'}
            </strong>
          </div>
          <div>
            FPS: <strong style={{ color: '#ffffff' }}>60.0</strong>
          </div>
        </div>
      </div>

      {/* Interactive 3D Holographic Core Viewport */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{
          position: 'relative',
          width: '100%',
          height: '340px',
          background: 'radial-gradient(circle at 50% 50%, #0a1118 0%, #000000 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          perspective: '1000px',
          overflow: 'hidden',
          cursor: 'crosshair',
          userSelect: 'none'
        }}
      >
        {/* Ambient Grid Floor */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: '-20%',
          right: '-20%',
          height: '140px',
          background: 'linear-gradient(to top, rgba(0, 245, 243, 0.08) 1px, transparent 1px), linear-gradient(to right, rgba(0, 245, 243, 0.08) 1px, transparent 1px)',
          backgroundSize: '24px 24px',
          transform: 'rotateX(75deg)',
          pointerEvents: 'none',
          maskImage: 'linear-gradient(to top, rgba(0,0,0,1), rgba(0,0,0,0))'
        }} />

        {/* Dynamic 3D Rotating Assembly Container */}
        <div style={{
          position: 'relative',
          width: '320px',
          height: '320px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transformStyle: 'preserve-3d',
          transform: `rotateX(${mousePos.y * 0.5 + 15}deg) rotateY(${mousePos.x * 0.5}deg)`,
          transition: 'transform 0.15s ease-out'
        }}>
          
          {/* Orbital Gimbal Ring 1 */}
          <div style={{
            position: 'absolute',
            width: '260px',
            height: '260px',
            borderRadius: '50%',
            border: '1px dashed rgba(0, 245, 243, 0.35)',
            boxShadow: '0 0 15px rgba(0, 245, 243, 0.15)',
            transform: 'rotateX(65deg) rotateZ(30deg)',
            animation: `spinRing1 ${speed} linear infinite`,
            pointerEvents: 'none'
          }} />

          {/* Orbital Gimbal Ring 2 */}
          <div style={{
            position: 'absolute',
            width: '290px',
            height: '290px',
            borderRadius: '50%',
            border: '1px solid rgba(192, 132, 252, 0.25)',
            transform: 'rotateY(55deg) rotateX(-20deg)',
            animation: `spinRing2 ${speed} linear infinite reverse`,
            pointerEvents: 'none'
          }} />

          {/* Central Quantum Reactor Core */}
          <div style={{
            position: 'relative',
            width: '74px',
            height: '74px',
            borderRadius: '50%',
            background: 'radial-gradient(circle at 35% 35%, #00F5F3 0%, #092c3a 60%, #000000 100%)',
            boxShadow: '0 0 35px rgba(0, 245, 243, 0.6), inset 0 0 15px rgba(255, 255, 255, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10,
            animation: 'pulseCore 2.5s ease-in-out infinite'
          }}>
            {/* Inner Rotating Tech Glyph */}
            <Cpu size={32} color="#ffffff" style={{ filter: 'drop-shadow(0 0 8px rgba(0,245,243,0.9))' }} />
            
            {/* Core Label */}
            <div style={{
              position: 'absolute',
              bottom: '-22px',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.62rem',
              fontWeight: 800,
              color: 'var(--color-accent)',
              letterSpacing: '0.1em',
              textShadow: '0 0 8px var(--color-accent)'
            }}>
              LANGGRAPH
            </div>
          </div>

          {/* Orbiting Agent Satellite Nodes */}
          {agentNodes.map((agent, i) => {
            const angleRad = (agent.angle * Math.PI) / 180;
            const x = Math.cos(angleRad) * orbitRadius;
            const y = Math.sin(angleRad) * (orbitRadius * 0.75);
            const isStageActive = activeStage?.toLowerCase() === agent.id;

            return (
              <div
                key={agent.id}
                onClick={() => setActiveHotspot(i)}
                style={{
                  position: 'absolute',
                  transform: `translate(${x}px, ${y}px)`,
                  transition: 'all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1)',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  cursor: 'pointer',
                  zIndex: 20
                }}
              >
                {/* Laser Connector Line to Core */}
                <svg
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    width: '300px',
                    height: '300px',
                    transform: 'translate(-50%, -50%)',
                    pointerEvents: 'none',
                    overflow: 'visible',
                    zIndex: -1
                  }}
                >
                  <line
                    x1="150"
                    y1="150"
                    x2={150 - x}
                    y2={150 - y}
                    stroke={agent.color}
                    strokeWidth={isStageActive ? '2' : '1'}
                    strokeDasharray={isStageActive ? 'none' : '3, 3'}
                    strokeOpacity={isStageActive ? '0.9' : '0.35'}
                  />
                </svg>

                {/* Satellite Node Badge */}
                <div style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '6px',
                  background: isStageActive ? agent.color : '#0e141f',
                  border: `1.5px solid ${agent.color}`,
                  boxShadow: `0 0 18px ${agent.color}${isStageActive ? 'cc' : '55'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'transform 0.2s ease',
                  transform: activeHotspot === i ? 'scale(1.2)' : 'scale(1)',
                }}>
                  {agent.id === 'researcher' && <Orbit size={18} color={isStageActive ? '#000000' : agent.color} />}
                  {agent.id === 'analyst' && <Activity size={18} color={isStageActive ? '#000000' : agent.color} />}
                  {agent.id === 'fact_checker' && <ShieldCheck size={18} color={isStageActive ? '#000000' : agent.color} />}
                  {agent.id === 'writer' && <Sparkles size={18} color={isStageActive ? '#000000' : agent.color} />}
                </div>

                {/* Node Label */}
                <div style={{
                  marginTop: '0.4rem',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.64rem',
                  fontWeight: 700,
                  color: agent.color,
                  letterSpacing: '0.06em',
                  background: 'rgba(0,0,0,0.85)',
                  padding: '0.15rem 0.45rem',
                  borderRadius: '2px',
                  border: `1px solid ${agent.color}44`,
                  whiteSpace: 'nowrap'
                }}>
                  [{agent.tag}] {agent.name}
                </div>
              </div>
            );
          })}
        </div>

        {/* Global Keyframe Animations */}
        <style>{`
          @keyframes spinRing1 {
            from { transform: rotateX(65deg) rotateZ(0deg); }
            to { transform: rotateX(65deg) rotateZ(360deg); }
          }
          @keyframes spinRing2 {
            from { transform: rotateY(55deg) rotateX(-20deg) rotateZ(0deg); }
            to { transform: rotateY(55deg) rotateX(-20deg) rotateZ(360deg); }
          }
          @keyframes pulseCore {
            0%, 100% { transform: scale(1); filter: drop-shadow(0 0 15px rgba(0,245,243,0.5)); }
            50% { transform: scale(1.08); filter: drop-shadow(0 0 30px rgba(0,245,243,0.85)); }
          }
        `}</style>
      </div>

      {/* Hotspots Bar & Controls */}
      <div style={{
        marginTop: '1rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        paddingTop: '0.75rem',
      }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {hotspots.map((spot) => (
            <button
              key={spot.id}
              onClick={() => setActiveHotspot(spot.id)}
              style={{
                background: activeHotspot === spot.id ? 'rgba(0, 245, 243, 0.15)' : 'rgba(255, 255, 255, 0.04)',
                border: `1px solid ${activeHotspot === spot.id ? 'var(--color-accent)' : 'rgba(255, 255, 255, 0.1)'}`,
                color: activeHotspot === spot.id ? 'var(--color-accent)' : 'var(--text-muted)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.74rem',
                padding: '0.35rem 0.75rem',
                cursor: 'pointer',
                borderRadius: '2px',
                transition: 'all 0.15s ease',
              }}
            >
              [{spot.tag}]
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '0.4rem' }}>
          <button
            onClick={() => setExploded(!exploded)}
            className="btn btn-secondary btn-sm"
            style={{
              fontSize: '0.72rem',
              fontFamily: 'var(--font-mono)',
              borderColor: exploded ? 'var(--color-accent)' : 'rgba(255, 255, 255, 0.2)',
              color: exploded ? 'var(--color-accent)' : '#ffffff'
            }}
          >
            <Layers size={12} />
            <span>{exploded ? 'ASSEMBLE CORE' : 'EXPLODED VIEW'}</span>
          </button>
        </div>
      </div>

      {/* Active Hotspot Telemetry Card */}
      <div style={{
        marginTop: '0.75rem',
        padding: '0.75rem 1rem',
        background: '#0a0a0a',
        border: '1px solid rgba(255, 255, 255, 0.12)',
        borderRadius: '2px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.5rem',
      }}>
        <div>
          <div style={{ fontSize: '0.7rem', color: 'var(--color-accent)', fontFamily: 'var(--font-mono)', fontWeight: 700, letterSpacing: '0.08em' }}>
            TELEMETRY [{hotspots[activeHotspot].tag}] // {hotspots[activeHotspot].title}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#e5e5e5', marginTop: '0.2rem' }}>
            {hotspots[activeHotspot].desc}
          </div>
        </div>
        <div style={{ fontSize: '0.68rem', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
          INTERACTION: MOVE MOUSE OVER CORE TO INSPECT · CLICK SATELLITE TO FOCUS
        </div>
      </div>
    </div>
  );
}
