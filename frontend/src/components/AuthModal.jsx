import React, { useState } from 'react';
import { X, LogIn, UserPlus, AlertCircle, Bot } from 'lucide-react';
import { api } from '../api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [tab, setTab] = useState('login'); // 'login' | 'register'
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let data;
      if (tab === 'login') {
        data = await api.login(username, password);
      } else {
        data = await api.register(username, email, password);
      }
      onAuthSuccess(data.user);
      onClose();
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      zIndex: 150,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem',
    }}>
      <div className="glass-panel" style={{
        maxWidth: '420px',
        width: '100%',
        background: '#0e131f',
        border: '1px solid rgba(255, 255, 255, 0.12)',
        borderRadius: 'var(--radius-xl)',
        padding: '2rem',
        position: 'relative',
        boxShadow: 'var(--shadow-lg)',
      }}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.25rem',
            right: '1.25rem',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
          }}
        >
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--brand-gradient)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 0.75rem',
            boxShadow: '0 0 16px rgba(99, 102, 241, 0.45)',
          }}>
            <Bot size={24} color="#ffffff" />
          </div>
          <h2 style={{ fontSize: '1.3rem', color: '#ffffff', marginBottom: '0.25rem' }}>
            {tab === 'login' ? 'Welcome Back' : 'Create Account'}
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
            Access persistent research workspaces & library
          </p>
        </div>

        {/* Tabs */}
        <div style={{
          display: 'flex',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: 'var(--radius-md)',
          padding: '0.25rem',
          marginBottom: '1.25rem',
        }}>
          <button
            onClick={() => { setTab('login'); setError(''); }}
            style={{
              flex: 1,
              padding: '0.5rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: tab === 'login' ? 'var(--brand-primary)' : 'transparent',
              color: tab === 'login' ? '#ffffff' : 'var(--text-muted)',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            Sign In
          </button>
          <button
            onClick={() => { setTab('register'); setError(''); }}
            style={{
              flex: 1,
              padding: '0.5rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: tab === 'register' ? 'var(--brand-primary)' : 'transparent',
              color: tab === 'register' ? '#ffffff' : 'var(--text-muted)',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            Create Account
          </button>
        </div>

        {error && (
          <div style={{
            padding: '0.65rem 0.85rem',
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            color: '#f87171',
            fontSize: '0.78rem',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}>
            <AlertCircle size={14} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 600, display: 'block', marginBottom: '0.3rem' }}>
              Username
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. researcher_alex"
              className="input-control"
              style={{ fontSize: '0.88rem' }}
            />
          </div>

          {tab === 'register' && (
            <div>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 600, display: 'block', marginBottom: '0.3rem' }}>
                Email (Optional)
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="alex@research.org"
                className="input-control"
                style={{ fontSize: '0.88rem' }}
              />
            </div>
          )}

          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 600, display: 'block', marginBottom: '0.3rem' }}>
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="input-control"
              style={{ fontSize: '0.88rem' }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '0.5rem', padding: '0.7rem' }}
          >
            {tab === 'login' ? (
              <>
                <LogIn size={16} />
                <span>{loading ? 'Signing in...' : 'Sign In'}</span>
              </>
            ) : (
              <>
                <UserPlus size={16} />
                <span>{loading ? 'Creating...' : 'Create Account'}</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
