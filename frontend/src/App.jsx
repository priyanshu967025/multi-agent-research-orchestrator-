import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import ResearchStudio from './components/ResearchStudio';
import LibraryView from './components/LibraryView';
import RAGHubView from './components/RAGHubView';
import BenchmarkArenaView from './components/BenchmarkArenaView';
import LLMMCPHubView from './components/LLMMCPHubView';
import AuthModal from './components/AuthModal';
import { api } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('studio'); // 'studio' | 'library' | 'rag' | 'benchmark' | 'mcp'
  const [user, setUser] = useState(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [health, setHealth] = useState(null);
  const [platformStats, setPlatformStats] = useState(null);

  const loadSystemInfo = useCallback(async () => {
    try {
      const h = await api.getHealth();
      setHealth(h);
    } catch {
      setHealth({ status: 'offline' });
    }

    try {
      const stats = await api.getPlatformStats();
      setPlatformStats(stats);
    } catch (e) {
      console.warn('Could not load platform stats:', e);
    }
  }, []);

  useEffect(() => {
    // Check initial user profile if token exists
    if (api.token) {
      api.getProfile()
        .then((userData) => setUser(userData))
        .catch(() => {
          api.setToken('');
          setUser(null);
        });
    }

    // Fetch system health & stats
    loadSystemInfo();
  }, [loadSystemInfo]);

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
    if (activeTab === 'library') {
      setActiveTab('studio');
    }
  };

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onOpenAuth={() => setAuthModalOpen(true)}
        onLogout={handleLogout}
        health={health}
        providerInfo={platformStats?.providers}
      />

      <main className="main-content">
        {activeTab === 'studio' && (
          <ResearchStudio
            user={user}
            onOpenAuth={() => setAuthModalOpen(true)}
          />
        )}

        {activeTab === 'library' && (
          <LibraryView
            user={user}
            onOpenAuth={() => setAuthModalOpen(true)}
          />
        )}

        {activeTab === 'rag' && (
          <RAGHubView
            user={user}
            onOpenAuth={() => setAuthModalOpen(true)}
          />
        )}

        {activeTab === 'benchmark' && (
          <BenchmarkArenaView
            user={user}
            onOpenAuth={() => setAuthModalOpen(true)}
          />
        )}

        {activeTab === 'mcp' && (
          <LLMMCPHubView
            providerInfo={platformStats?.providers}
            onRefresh={loadSystemInfo}
          />
        )}
      </main>

      {/* Footer Banner */}
      <footer style={{
        borderTop: '1px solid var(--border-card)',
        background: 'rgba(9, 13, 22, 0.95)',
        padding: '1.25rem 1.5rem',
        marginTop: 'auto',
      }}>
        <div style={{
          maxWidth: '1440px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          fontSize: '0.78rem',
          color: 'var(--text-dim)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>Multi-Agent Research Orchestrator</span>
            <span>·</span>
            <span>LangGraph State Engine</span>
            <span>·</span>
            <span>ChromaDB Vector Store</span>
            <span>·</span>
            <span>FastMCP Protocol</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
            <span>
              Total Runs: <strong style={{ color: '#ffffff' }}>{platformStats?.sessions?.total || 0}</strong>
            </span>
            <span>
              Indexed Chunks: <strong style={{ color: '#34d399' }}>{platformStats?.rag?.total_indexed_documents || 0}</strong>
            </span>
            <span>
              Revisions: <strong style={{ color: '#fbbf24' }}>{platformStats?.sessions?.total_revisions || 0}</strong>
            </span>
          </div>
        </div>
      </footer>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={(userData) => {
          setUser(userData);
          loadSystemInfo();
        }}
      />
    </div>
  );
}
