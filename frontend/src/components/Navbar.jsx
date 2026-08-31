import React from 'react';
import { 
  Bot, 
  Sparkles, 
  BookOpen, 
  Database, 
  Scale, 
  Cpu, 
  User as UserIcon, 
  LogOut, 
  LogIn
} from 'lucide-react';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  user, 
  onOpenAuth, 
  onLogout, 
  health, 
  providerInfo 
}) {
  const isHealthy = health?.status === 'ok';
  const activeProvider = providerInfo?.active_provider || 'auto';

  const navItems = [
    { id: 'studio', label: 'RESEARCH STUDIO', icon: Sparkles },
    { id: 'library', label: 'LIBRARY', icon: BookOpen },
    { id: 'rag', label: 'RAG KNOWLEDGE', icon: Database },
    { id: 'benchmark', label: 'BENCHMARKS', icon: Scale },
    { id: 'mcp', label: 'LLM & FASTMCP', icon: Cpu },
  ];

  return (
    <header style={{
      borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
      background: '#000000',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      width: '100%'
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '0.75rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1.25rem',
      }}>
        {/* Brand Logo */}
        <div 
          onClick={() => setActiveTab('studio')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            cursor: 'pointer',
            userSelect: 'none',
          }}
        >
          <div style={{
            width: '28px',
            height: '28px',
            background: '#ffffff',
            borderRadius: '2px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#000000'
          }}>
            <Bot size={18} />
          </div>
          <div>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontWeight: 800,
              fontSize: '1.05rem',
              color: '#ffffff',
              letterSpacing: '-0.02em',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              lineHeight: 1
            }}>
              MARO
              <span style={{ 
                fontSize: '0.65rem', 
                fontFamily: 'var(--font-mono)',
                color: 'var(--color-accent)', 
                fontWeight: 700, 
                border: '1px solid var(--color-accent)', 
                padding: '0.05rem 0.35rem', 
                borderRadius: '2px' 
              }}>
                v2.5
              </span>
            </div>
          </div>
        </div>

        {/* Center Navigation Tabs */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  padding: '0.4rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  border: isActive ? '1px solid var(--color-accent)' : '1px solid transparent',
                  background: isActive ? 'rgba(0, 245, 243, 0.08)' : 'transparent',
                  color: isActive ? 'var(--color-accent)' : 'var(--text-muted)',
                  fontSize: '0.76rem',
                  fontFamily: 'var(--font-sans)',
                  fontWeight: 700,
                  letterSpacing: '0.05em',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                }}
              >
                <Icon size={13} color={isActive ? 'var(--color-accent)' : 'currentColor'} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Section: System Status & User Profile */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          {/* Provider Pill */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.45rem',
            padding: '0.25rem 0.65rem',
            background: '#0a0a0a',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.72rem',
            fontFamily: 'var(--font-mono)'
          }}>
            <div style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: isHealthy ? '#34d399' : '#f87171',
              boxShadow: isHealthy ? '0 0 8px #34d399' : 'none'
            }} />
            <span style={{ color: 'var(--text-dim)' }}>PROVIDER:</span>
            <span style={{ color: 'var(--color-accent)', fontWeight: 700, textTransform: 'uppercase' }}>
              {activeProvider}
            </span>
          </div>

          {/* User Account / Auth */}
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.25rem 0.65rem',
                background: '#141414',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.78rem',
                color: '#ffffff',
                fontFamily: 'var(--font-mono)'
              }}>
                <UserIcon size={12} color="var(--color-accent)" />
                <span style={{ fontWeight: 700 }}>{user.username}</span>
              </div>
              <button
                onClick={onLogout}
                title="Sign out"
                style={{
                  background: 'transparent',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-muted)',
                  padding: '0.35rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <LogOut size={13} />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="btn btn-primary btn-sm"
            >
              <LogIn size={13} />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
