import React, { useState, useEffect, useCallback } from 'react';
import { 
  Scale, 
  Play, 
  RefreshCw, 
  Award, 
  History
} from 'lucide-react';
import { marked } from 'marked';
import { api } from '../api';

export default function BenchmarkArenaView({ user: _user, onOpenAuth: _onOpenAuth }) {
  const [topic, setTopic] = useState('');
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [activeTab, setActiveTab] = useState('multi'); // 'multi' | 'single'

  const loadHistory = useCallback(async () => {
    setLoadingHistory(true);
    try {
      const data = await api.getBenchmarkHistory(20);
      setHistory(data || []);
    } catch (e) {
      console.error('Failed to load benchmark history:', e);
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleRunBenchmark = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setRunning(true);
    setResult(null);

    try {
      const data = await api.runBenchmark(topic.trim());
      setResult(data);
      loadHistory();
    } catch (err) {
      alert(`Benchmark run failed: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  const singleMetrics = result?.evaluation_metrics?.single_agent || {};
  const multiMetrics = result?.evaluation_metrics?.multi_agent || {};
  const verdict = result?.evaluation_metrics?.verdict || '';

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '1.75rem' }}>
        <h2 style={{ fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Scale size={20} color="#60a5fa" />
          <span>Multi-Agent vs Single-Agent Benchmark Arena</span>
        </h2>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-dim)' }}>
          Run direct head-to-head empirical evaluations comparing single-shot LLM baselines against the autonomous multi-agent pipeline on depth, claim verifiability, and hallucination avoidance.
        </p>
      </div>

      {/* Input Arena Form */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <form onSubmit={handleRunBenchmark}>
          <label style={{ fontWeight: 700, fontSize: '0.92rem', color: '#ffffff', display: 'block', marginBottom: '0.5rem' }}>
            Benchmark Inquiry Topic
          </label>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <input
              type="text"
              placeholder="e.g. Best practices for RAG evaluation in enterprise knowledge systems"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              disabled={running}
              className="input-control"
              style={{ fontSize: '0.92rem' }}
            />
            <button
              type="submit"
              disabled={running || !topic.trim()}
              className="btn btn-primary"
              style={{ padding: '0.65rem 1.4rem' }}
            >
              {running ? (
                <>
                  <RefreshCw size={16} className="spinning-icon" />
                  <span>Evaluating Both Pipelines...</span>
                </>
              ) : (
                <>
                  <Play size={16} />
                  <span>Run Benchmark Arena</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Live Benchmark Result Cards */}
      {result && (
        <div style={{ marginBottom: '2.5rem' }}>
          {/* Head-to-Head Visual Metrics Dashboard */}
          <div className="glass-panel" style={{ padding: '1.75rem', marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <span className="badge badge-info" style={{ fontSize: '0.72rem', marginBottom: '0.3rem' }}>
                  HEAD-TO-HEAD RESULTS
                </span>
                <h3 style={{ fontSize: '1.2rem', color: '#ffffff' }}>{result.topic}</h3>
              </div>

              {verdict && (
                <div style={{
                  padding: '0.45rem 1rem',
                  borderRadius: 'var(--radius-full)',
                  background: 'rgba(59, 130, 246, 0.15)',
                  border: '1px solid rgba(59, 130, 246, 0.35)',
                  color: '#60a5fa',
                  fontWeight: 700,
                  fontSize: '0.82rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem'
                }}>
                  <Award size={16} />
                  <span>Verdict: {verdict.replace('_', ' ').toUpperCase()}</span>
                </div>
              )}
            </div>

            {/* Side-by-side Score Bars */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
              {/* Single Agent Box */}
              <div style={{
                background: 'rgba(15, 23, 42, 0.75)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '1.25rem',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-muted)' }}>
                    Single-Agent Baseline
                  </div>
                  <span className="badge badge-warning" style={{ fontSize: '0.7rem' }}>SINGLE-SHOT</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem', color: 'var(--text-dim)' }}>
                      <span>Depth Score</span>
                      <strong style={{ color: '#ffffff' }}>{singleMetrics.depth_score || 0}/10</strong>
                    </div>
                    <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${(singleMetrics.depth_score || 0) * 10}%`, height: '100%', background: '#f59e0b', borderRadius: '4px' }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem', color: 'var(--text-dim)' }}>
                      <span>Verifiability Score</span>
                      <strong style={{ color: '#ffffff' }}>{singleMetrics.verifiability_score || 0}/10</strong>
                    </div>
                    <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${(singleMetrics.verifiability_score || 0) * 10}%`, height: '100%', background: '#f59e0b', borderRadius: '4px' }} />
                    </div>
                  </div>
                </div>
              </div>

              {/* Multi-Agent Orchestrator Box */}
              <div style={{
                background: 'rgba(99, 102, 241, 0.08)',
                border: '1px solid rgba(99, 102, 241, 0.35)',
                borderRadius: 'var(--radius-md)',
                padding: '1.25rem',
                boxShadow: '0 0 20px rgba(99, 102, 241, 0.15)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Award size={16} /> Multi-Agent Orchestrator
                  </div>
                  <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>VERIFIED PIPELINE</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem', color: 'var(--text-dim)' }}>
                      <span>Depth Score</span>
                      <strong style={{ color: '#34d399' }}>{multiMetrics.depth_score || 0}/10</strong>
                    </div>
                    <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${(multiMetrics.depth_score || 0) * 10}%`, height: '100%', background: 'linear-gradient(90deg, #6366f1, #34d399)', borderRadius: '4px' }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem', color: 'var(--text-dim)' }}>
                      <span>Verifiability Score</span>
                      <strong style={{ color: '#34d399' }}>{multiMetrics.verifiability_score || 0}/10</strong>
                    </div>
                    <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${(multiMetrics.verifiability_score || 0) * 10}%`, height: '100%', background: 'linear-gradient(90deg, #6366f1, #34d399)', borderRadius: '4px' }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Output Comparison Switcher */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
              <button
                onClick={() => setActiveTab('multi')}
                className={`btn btn-sm ${activeTab === 'multi' ? 'btn-primary' : 'btn-secondary'}`}
              >
                <span>Multi-Agent Synthesized Output</span>
              </button>
              <button
                onClick={() => setActiveTab('single')}
                className={`btn btn-sm ${activeTab === 'single' ? 'btn-primary' : 'btn-secondary'}`}
              >
                <span>Single-Agent Raw Baseline Output</span>
              </button>
            </div>

            <div style={{
              background: 'rgba(14, 19, 31, 0.9)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '1.5rem',
              maxHeight: '400px',
              overflowY: 'auto'
            }}>
              <div 
                className="markdown-body"
                dangerouslySetInnerHTML={{ 
                  __html: marked.parse(activeTab === 'multi' ? (result.multi_agent_report || '') : (result.single_agent_baseline?.text || '')) 
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Benchmark History Table */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <h3 style={{ fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <History size={16} color="var(--text-dim)" />
            <span>Benchmark Evaluation History</span>
          </h3>
          <button onClick={loadHistory} className="btn btn-ghost btn-sm">
            <RefreshCw size={13} />
            <span>Refresh</span>
          </button>
        </div>

        {loadingHistory ? (
          <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-muted)' }}>
            Loading history...
          </div>
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
            No prior benchmark runs recorded yet.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.84rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-dim)', textAlign: 'left' }}>
                  <th style={{ padding: '0.6rem 0.85rem' }}>Topic</th>
                  <th style={{ padding: '0.6rem 0.85rem' }}>Single Agent (D/V)</th>
                  <th style={{ padding: '0.6rem 0.85rem' }}>Multi-Agent (D/V)</th>
                  <th style={{ padding: '0.6rem 0.85rem' }}>Verdict</th>
                  <th style={{ padding: '0.6rem 0.85rem' }}>Date</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={h.id || i} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '0.65rem 0.85rem', fontWeight: 600, color: '#ffffff' }}>{h.topic}</td>
                    <td style={{ padding: '0.65rem 0.85rem', color: '#fbbf24', fontFamily: 'var(--font-mono)' }}>
                      {h.single_agent_depth}/{h.single_agent_verifiability}
                    </td>
                    <td style={{ padding: '0.65rem 0.85rem', color: '#34d399', fontFamily: 'var(--font-mono)' }}>
                      {h.multi_agent_depth}/{h.multi_agent_verifiability}
                    </td>
                    <td style={{ padding: '0.65rem 0.85rem' }}>
                      <span className="badge badge-info" style={{ fontSize: '0.68rem' }}>
                        {(h.verdict || 'N/A').replace('_', ' ')}
                      </span>
                    </td>
                    <td style={{ padding: '0.65rem 0.85rem', color: 'var(--text-dim)', fontSize: '0.78rem' }}>
                      {new Date(h.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
