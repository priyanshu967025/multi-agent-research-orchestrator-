import React from 'react';
import { Search, Brain, ShieldCheck, PenTool, RefreshCw, Check } from 'lucide-react';

export default function AgentGraph({ currentStage, revisionCount = 0, isRunning = false }) {
  const steps = [
    { id: 'researcher', num: '01', label: 'RESEARCHER', role: 'Dual-Vector & Web Search', icon: Search },
    { id: 'analyst', num: '02', label: 'ANALYST', role: 'Contradiction & Theme Synthesis', icon: Brain },
    { id: 'fact_checker', num: '03', label: 'FACT-CHECKER', role: 'Claim Verification Gate', icon: ShieldCheck },
    { id: 'writer', num: '04', label: 'WRITER', role: 'Synthesis & Memory Storage', icon: PenTool }
  ];

  const getStageIndex = (stage) => {
    switch (stage) {
      case 'researcher': return 0;
      case 'analyst': return 1;
      case 'fact_checker': return 2;
      case 'writer': return 3;
      case 'completed': return 4;
      default: return -1;
    }
  };

  const activeIdx = getStageIndex(currentStage);

  return (
    <div style={{
      background: '#0a0a0a',
      border: '1px solid rgba(255, 255, 255, 0.12)',
      borderRadius: 'var(--radius-sm)',
      padding: '1rem 1.25rem',
      marginBottom: '2rem',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
        <div style={{ fontSize: '0.74rem', fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-accent)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
          [ 02 // LANGGRAPH STATEFUL PIPELINE ]
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {revisionCount > 0 && (
            <span className="badge badge-warning" style={{ fontSize: '0.68rem' }}>
              <RefreshCw size={11} className="spinning-icon" /> REVISION LOOP #{revisionCount}
            </span>
          )}
          <span className={`badge ${currentStage === 'completed' ? 'badge-success' : (isRunning ? 'badge-info' : 'badge-purple')}`} style={{ fontSize: '0.68rem' }}>
            STATUS: {currentStage ? currentStage.replace('_', ' ').toUpperCase() : 'IDLE'}
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem' }}>
        {steps.map((step, idx) => {
          const isActive = currentStage === step.id && isRunning;
          const isDone = currentStage === 'completed' || activeIdx > idx;

          return (
            <div
              key={step.id}
              style={{
                background: isActive ? '#141414' : (isDone ? '#0f0f0f' : '#000000'),
                border: `1px solid ${isActive ? 'var(--color-accent)' : (isDone ? 'rgba(52, 211, 153, 0.4)' : 'rgba(255, 255, 255, 0.1)')}`,
                borderRadius: 'var(--radius-sm)',
                padding: '0.75rem 0.9rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                transition: 'all var(--transition-fast)',
                boxShadow: isActive ? '0 0 16px rgba(0, 245, 243, 0.25)' : 'none'
              }}
            >
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.78rem',
                fontWeight: 700,
                color: isDone ? '#34d399' : (isActive ? 'var(--color-accent)' : 'var(--text-dim)'),
                letterSpacing: '0.05em'
              }}>
                {isDone ? <Check size={16} /> : step.num}
              </div>
              <div style={{ minWidth: 0, flex: 1 }}>
                <div style={{ fontWeight: 750, fontSize: '0.84rem', color: isDone ? '#ffffff' : (isActive ? 'var(--color-accent)' : '#e5e5e5'), letterSpacing: '0.03em' }}>
                  {step.label}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {step.role}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
