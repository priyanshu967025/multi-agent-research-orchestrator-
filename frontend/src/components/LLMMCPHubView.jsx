import React, { useState } from 'react';
import {
  Cpu,
  Copy,
  Check,
  Code,
  Server,
  RefreshCw,
  Send,
  Zap,
  Play,
  Terminal,
  ChevronRight,
  Globe,
  Shield,
  Activity,
  Layers,
  Lock,
  Wifi,
  WifiOff,
  Settings,
  BookOpen,
} from 'lucide-react';
import { api } from '../api';

const PROVIDERS = [
  {
    key: 'groq',
    name: 'Groq (LPUs)',
    model: 'llama-3.3-70b-versatile',
    speed: '~500 tokens/sec',
    desc: 'Ultra-fast LPU inference for rapid research synthesis',
    color: '#f97316',
    glow: 'rgba(249,115,22,0.18)',
    border: 'rgba(249,115,22,0.4)',
    icon: '⚡',
  },
  {
    key: 'gemini',
    name: 'Google Gemini',
    model: 'gemini-2.0-flash',
    speed: '1M token context',
    desc: 'Deep multi-modal document reasoning & analysis',
    color: '#4ade80',
    glow: 'rgba(74,222,128,0.14)',
    border: 'rgba(74,222,128,0.35)',
    icon: '✦',
  },
  {
    key: 'openai',
    name: 'OpenAI GPT-4o',
    model: 'gpt-4o',
    speed: 'High intelligence',
    desc: 'Complex multi-step reasoning & nuanced fact-checking',
    color: '#60a5fa',
    glow: 'rgba(96,165,250,0.14)',
    border: 'rgba(96,165,250,0.35)',
    icon: '◈',
  },
  {
    key: 'anthropic',
    name: 'Anthropic Claude',
    model: 'claude-sonnet-4-5',
    speed: 'High precision',
    desc: 'Analytical writing & evidence cross-examination',
    color: '#c084fc',
    glow: 'rgba(192,132,252,0.14)',
    border: 'rgba(192,132,252,0.35)',
    icon: '◆',
  },
  {
    key: 'ollama',
    name: 'Ollama (Local)',
    model: 'llama3.1:latest',
    speed: '100% Offline',
    desc: 'Private local inference — zero API keys required',
    color: '#38bdf8',
    glow: 'rgba(56,189,248,0.14)',
    border: 'rgba(56,189,248,0.35)',
    icon: '⬡',
  },
];

const MCP_TOOLS = [
  { value: 'research_topic', label: 'research_topic', desc: 'Run full 4-agent DAG research pipeline' },
  { value: 'list_research_sessions', label: 'list_research_sessions', desc: 'Inspect the research session library' },
  { value: 'query_research_rag', label: 'query_research_rag', desc: 'Semantic search across ChromaDB collections' },
  { value: 'export_session_report', label: 'export_session_report', desc: 'Generate MD / BibTeX / HTML reports' },
];

const API_ENDPOINTS = [
  { value: '/health/', label: 'GET /api/health/', desc: 'System health & uptime' },
  { value: '/stats/', label: 'GET /api/stats/', desc: 'Platform analytics & session counts' },
  { value: '/rag/stats/', label: 'GET /api/rag/stats/', desc: 'ChromaDB vector store stats' },
];

export default function LLMMCPHubView({ providerInfo, onRefresh }) {
  const [copiedMcp, setCopiedMcp] = useState(false);
  const [copiedCursor, setCopiedCursor] = useState(false);
  const [apiTesting, setApiTesting] = useState(false);
  const [apiResponse, setApiResponse] = useState(null);
  const [selectedEndpoint, setSelectedEndpoint] = useState('/health/');

  const [selectedMcpTool, setSelectedMcpTool] = useState('research_topic');
  const [mcpInput, setMcpInput] = useState('Explain Multi-Agent RAG architectures');
  const [mcpExecuting, setMcpExecuting] = useState(false);
  const [mcpOutput, setMcpOutput] = useState(null);
  const [mcpError, setMcpError] = useState(null);

  const mcpConfig = {
    mcpServers: {
      'research-orchestrator': {
        command: 'python',
        args: ['mcp_server.py'],
        env: {
          GROQ_API_KEY: 'your_groq_api_key',
          GEMINI_API_KEY: 'your_gemini_api_key',
          TAVILY_API_KEY: 'your_tavily_api_key',
        },
      },
    },
  };

  const cursorMcpConfig = {
    mcp: {
      servers: [
        { name: 'maro-agent-tools', type: 'stdio', command: 'python', args: ['mcp_server.py'] },
      ],
    },
  };

  const handleCopyMcp = () => {
    navigator.clipboard.writeText(JSON.stringify(mcpConfig, null, 2));
    setCopiedMcp(true);
    setTimeout(() => setCopiedMcp(false), 2000);
  };

  const handleCopyCursor = () => {
    navigator.clipboard.writeText(JSON.stringify(cursorMcpConfig, null, 2));
    setCopiedCursor(true);
    setTimeout(() => setCopiedCursor(false), 2000);
  };

  const handleTestApi = async () => {
    setApiTesting(true);
    setApiResponse(null);
    try {
      let res;
      if (selectedEndpoint === '/health/') res = await api.getHealth();
      else if (selectedEndpoint === '/stats/') res = await api.getPlatformStats();
      else if (selectedEndpoint === '/rag/stats/') res = await api.getRAGStats();
      setApiResponse(res);
    } catch (err) {
      setApiResponse({ error: err.message });
    } finally {
      setApiTesting(false);
    }
  };

  const handleExecuteMcpTool = async () => {
    setMcpExecuting(true);
    setMcpOutput(null);
    setMcpError(null);
    try {
      const result = await api.executeMcpTool(selectedMcpTool, mcpInput);
      setMcpOutput(result);
    } catch (err) {
      setMcpError(err.message);
    } finally {
      setMcpExecuting(false);
    }
  };

  const activeProvider = providerInfo?.active_provider || 'groq';

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      {/* ── Header ── */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
          <div style={{
            width: 36, height: 36, borderRadius: '10px',
            background: 'linear-gradient(135deg, #c084fc, #818cf8)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 20px rgba(192,132,252,0.35)',
          }}>
            <Cpu size={18} color="#fff" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#ffffff', lineHeight: 1 }}>
              Multi-Provider LLM &amp; FastMCP Protocol Hub
            </h2>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>
              Multi-model provider fallbacks · Live MCP tool sandbox · Claude Desktop &amp; Cursor IDE integration
            </p>
          </div>
        </div>
      </div>

      {/* ── Provider Grid ── */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <Layers size={15} color="var(--text-dim)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Provider Fallback Chain
          </span>
          {onRefresh && (
            <button onClick={onRefresh} className="btn btn-ghost btn-sm" style={{ marginLeft: 'auto', padding: '0.25rem 0.6rem' }}>
              <RefreshCw size={13} />
              <span>Refresh</span>
            </button>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '0.85rem' }}>
          {PROVIDERS.map((p, idx) => {
            const isActive = activeProvider === p.key;
            const isAvail = providerInfo?.available?.[p.key] ?? true;
            return (
              <div
                key={p.key}
                style={{
                  background: isActive ? p.glow : 'rgba(14,19,31,0.75)',
                  border: `1px solid ${isActive ? p.border : 'rgba(255,255,255,0.06)'}`,
                  borderRadius: '12px',
                  padding: '1.1rem',
                  position: 'relative',
                  transition: 'all 0.2s ease',
                  boxShadow: isActive ? `0 0 24px ${p.glow}` : 'none',
                }}
              >
                {/* Priority badge */}
                <div style={{
                  position: 'absolute', top: '0.55rem', right: '0.6rem',
                  fontSize: '0.6rem', color: 'var(--text-dim)',
                  background: 'rgba(255,255,255,0.05)', borderRadius: '4px',
                  padding: '0.1rem 0.35rem', fontFamily: 'var(--font-mono)',
                }}>
                  #{idx + 1}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem' }}>
                  <span style={{ fontSize: '1.1rem', color: p.color }}>{p.icon}</span>
                  <span style={{ fontWeight: 700, fontSize: '0.88rem', color: '#ffffff' }}>{p.name}</span>
                </div>

                <div style={{
                  fontSize: '0.68rem', fontFamily: 'var(--font-mono)',
                  color: p.color, background: 'rgba(0,0,0,0.3)',
                  padding: '0.2rem 0.45rem', borderRadius: '5px',
                  marginBottom: '0.5rem', display: 'inline-block',
                }}>
                  {p.model}
                </div>

                <p style={{ fontSize: '0.74rem', color: 'var(--text-dim)', margin: '0.3rem 0', lineHeight: 1.4 }}>{p.desc}</p>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '0.6rem' }}>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>{p.speed}</span>
                  {isActive ? (
                    <span style={{
                      fontSize: '0.62rem', fontWeight: 700, padding: '0.15rem 0.5rem',
                      background: p.glow, border: `1px solid ${p.border}`,
                      borderRadius: '99px', color: p.color,
                    }}>ACTIVE</span>
                  ) : isAvail ? (
                    <span style={{ fontSize: '0.62rem', color: '#34d399', display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <Wifi size={10} /> READY
                    </span>
                  ) : (
                    <span style={{ fontSize: '0.62rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <WifiOff size={10} /> OFFLINE
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── MCP Tool Sandbox ── */}
      <div className="glass-panel" style={{
        padding: '1.75rem', marginBottom: '1.5rem',
        border: '1px solid rgba(192,132,252,0.2)',
        background: 'rgba(192,132,252,0.04)',
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem' }}>
              <Zap size={17} color="#c084fc" />
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#ffffff' }}>Live FastMCP Tool Executor</h3>
              <span style={{
                fontSize: '0.62rem', padding: '0.1rem 0.45rem',
                background: 'rgba(192,132,252,0.15)', border: '1px solid rgba(192,132,252,0.35)',
                borderRadius: '99px', color: '#c084fc', fontWeight: 700,
              }}>SANDBOX</span>
            </div>
            <p style={{ fontSize: '0.79rem', color: 'var(--text-dim)' }}>
              Simulate tool calls exactly as invoked by AI agents inside Cursor IDE or Claude Desktop
            </p>
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', background: 'rgba(0,0,0,0.3)', padding: '0.3rem 0.65rem', borderRadius: '6px', fontFamily: 'var(--font-mono)' }}>
            FastMCP 0.4.1 · stdio transport
          </div>
        </div>

        {/* Tool selector row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', display: 'block', marginBottom: '0.35rem' }}>
              Tool Name
            </label>
            <select
              value={selectedMcpTool}
              onChange={(e) => setSelectedMcpTool(e.target.value)}
              className="select-control"
              style={{ width: '100%', fontSize: '0.86rem' }}
            >
              {MCP_TOOLS.map(t => (
                <option key={t.value} value={t.value}>{t.label} — {t.desc}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', display: 'block', marginBottom: '0.35rem' }}>
              Argument / Payload
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                value={mcpInput}
                onChange={(e) => setMcpInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !mcpExecuting && handleExecuteMcpTool()}
                placeholder="Enter topic, session ID, or query..."
                className="input-control"
                style={{ fontSize: '0.86rem' }}
              />
              <button
                onClick={handleExecuteMcpTool}
                disabled={mcpExecuting}
                className="btn btn-primary"
                style={{ whiteSpace: 'nowrap', padding: '0.6rem 1.1rem' }}
              >
                {mcpExecuting
                  ? <RefreshCw size={15} className="spinning-icon" />
                  : <Play size={15} />}
                <span>{mcpExecuting ? 'Running…' : 'Execute'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Output terminal */}
        {(mcpOutput || mcpError) && (
          <div style={{ marginTop: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.4rem' }}>
              <Terminal size={13} color={mcpError ? '#f87171' : '#34d399'} />
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: mcpError ? '#f87171' : '#34d399' }}>
                {mcpError ? 'Execution Error' : `Tool Output · ${mcpOutput?.execution_time_ms ?? '?'}ms`}
              </span>
            </div>
            <pre style={{
              background: '#06090f',
              border: `1px solid ${mcpError ? 'rgba(248,113,113,0.25)' : 'rgba(52,211,153,0.2)'}`,
              borderRadius: '10px',
              padding: '1rem 1.1rem',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.77rem',
              color: mcpError ? '#f87171' : '#a7f3d0',
              maxHeight: '280px',
              overflowY: 'auto',
              lineHeight: 1.6,
              margin: 0,
            }}>
              <code>{mcpError || JSON.stringify(mcpOutput, null, 2)}</code>
            </pre>
          </div>
        )}
      </div>

      {/* ── Bottom Row: Configs + API Explorer ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
        {/* Claude Desktop Config */}
        <ConfigCard
          icon={<Server size={15} color="#818cf8" />}
          title="Claude Desktop Config"
          subtitle={<>Paste into <code style={{ color: '#c084fc' }}>claude_desktop_config.json</code></>}
          code={JSON.stringify(mcpConfig, null, 2)}
          codeColor="#c084fc"
          copied={copiedMcp}
          onCopy={handleCopyMcp}
        />

        {/* Cursor IDE Config */}
        <ConfigCard
          icon={<Code size={15} color="#38bdf8" />}
          title="Cursor IDE Config"
          subtitle={<>Add to <code style={{ color: '#38bdf8' }}>.cursor/mcp.json</code></>}
          code={JSON.stringify(cursorMcpConfig, null, 2)}
          codeColor="#38bdf8"
          copied={copiedCursor}
          onCopy={handleCopyCursor}
        />

        {/* REST API Explorer */}
        <div className="glass-panel" style={{ padding: '1.5rem', gridColumn: 'span 2' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
            <Globe size={15} color="#34d399" />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>Interactive REST API Explorer</h3>
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Fire live requests against the Django backend directly from the browser:
          </p>

          <div style={{ display: 'flex', gap: '0.6rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
            <select
              value={selectedEndpoint}
              onChange={(e) => setSelectedEndpoint(e.target.value)}
              className="select-control"
              style={{ flex: 1, minWidth: '220px', fontSize: '0.84rem' }}
            >
              {API_ENDPOINTS.map(ep => (
                <option key={ep.value} value={ep.value}>{ep.label} — {ep.desc}</option>
              ))}
            </select>
            <button
              onClick={handleTestApi}
              disabled={apiTesting}
              className="btn btn-primary btn-sm"
              style={{ padding: '0.55rem 1.3rem' }}
            >
              {apiTesting ? <RefreshCw size={14} className="spinning-icon" /> : <Send size={14} />}
              <span>Send Request</span>
            </button>
          </div>

          {apiResponse && (
            <pre style={{
              background: '#06090f',
              border: '1px solid rgba(52,211,153,0.2)',
              borderRadius: '10px',
              padding: '1rem',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.76rem',
              color: apiResponse?.error ? '#f87171' : '#a7f3d0',
              maxHeight: '220px',
              overflowY: 'auto',
              margin: 0,
            }}>
              <code>{JSON.stringify(apiResponse, null, 2)}</code>
            </pre>
          )}
        </div>
      </div>

      {/* ── Setup Guide strip ── */}
      <div style={{
        marginTop: '1.5rem',
        padding: '1rem 1.25rem',
        background: 'rgba(99,102,241,0.06)',
        border: '1px solid rgba(99,102,241,0.2)',
        borderRadius: '12px',
        display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '1rem',
        fontSize: '0.79rem', color: 'var(--text-muted)',
      }}>
        <BookOpen size={14} color="#818cf8" style={{ flexShrink: 0 }} />
        <span>
          <strong style={{ color: '#c7d2fe' }}>Quick start:</strong>{' '}
          Set <code style={{ color: '#818cf8' }}>LLM_PROVIDER=groq</code> in your <code style={{ color: '#818cf8' }}>.env</code>,
          then run <code style={{ color: '#818cf8' }}>python mcp_server.py</code> and paste the config above into Claude Desktop or Cursor.
        </span>
        <span style={{ marginLeft: 'auto', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Shield size={12} color="var(--text-dim)" />
          Supports Groq · Gemini · OpenAI · Anthropic · Ollama
        </span>
      </div>
    </div>
  );
}

/* ── Config Card Sub-component ── */
function ConfigCard({ icon, title, subtitle, code, codeColor, copied, onCopy }) {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
        <h3 style={{ fontSize: '0.97rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          {icon}
          <span>{title}</span>
        </h3>
        <button onClick={onCopy} className="btn btn-secondary btn-sm" style={{ padding: '0.25rem 0.65rem' }}>
          {copied ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>
      <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.7rem' }}>{subtitle}</p>
      <pre style={{
        background: '#06090f',
        border: '1px solid rgba(255,255,255,0.06)',
        borderRadius: '9px',
        padding: '0.85rem',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.72rem',
        color: codeColor,
        overflowX: 'auto',
        maxHeight: '190px',
        margin: 0,
      }}>
        <code>{code}</code>
      </pre>
    </div>
  );
}
