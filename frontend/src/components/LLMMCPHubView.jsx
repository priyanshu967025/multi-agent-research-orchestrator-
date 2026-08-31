import React, { useState } from 'react';
import { 
  Cpu, 
  Copy, 
  Check, 
  Code, 
  Server, 
  RefreshCw,
  Send
} from 'lucide-react';
import { api } from '../api';

export default function LLMMCPHubView({ providerInfo }) {
  const [copiedMcp, setCopiedMcp] = useState(false);
  const [apiTesting, setApiTesting] = useState(false);
  const [apiResponse, setApiResponse] = useState(null);
  const [selectedEndpoint, setSelectedEndpoint] = useState('/health/');

  const mcpConfig = {
    mcpServers: {
      "research-orchestrator": {
        command: "python",
        args: ["d:/GEN AI PROJECT CV/Multi Agent Research Orchestrator/mcp_server.py"],
        env: {
          GROQ_API_KEY: "your_groq_api_key",
          GEMINI_API_KEY: "your_gemini_api_key",
          TAVILY_API_KEY: "your_tavily_api_key"
        }
      }
    }
  };

  const handleCopyMcp = () => {
    navigator.clipboard.writeText(JSON.stringify(mcpConfig, null, 2));
    setCopiedMcp(true);
    setTimeout(() => setCopiedMcp(false), 2000);
  };

  const handleTestApi = async () => {
    setApiTesting(true);
    setApiResponse(null);
    try {
      let res;
      if (selectedEndpoint === '/health/') {
        res = await api.getHealth();
      } else if (selectedEndpoint === '/stats/') {
        res = await api.getPlatformStats();
      } else if (selectedEndpoint === '/rag/stats/') {
        res = await api.getRAGStats();
      }
      setApiResponse(res);
    } catch (err) {
      setApiResponse({ error: err.message });
    } finally {
      setApiTesting(false);
    }
  };

  const providers = [
    { name: 'Groq', key: 'groq', model: 'llama-3.3-70b-versatile', speed: 'Ultra-fast (~500 t/s)', desc: 'Optimized inference on LPUs' },
    { name: 'Google Gemini', key: 'gemini', model: 'gemini-2.0-flash', speed: 'High speed & large context', desc: 'Google Generative AI 2.0 Flash / Pro' },
    { name: 'OpenAI', key: 'openai', model: 'gpt-4o', speed: 'High intelligence', desc: 'GPT-4o multimodal reasoning' },
    { name: 'Anthropic', key: 'anthropic', model: 'claude-sonnet-4-20250514', speed: 'High precision', desc: 'Claude Sonnet analytical writing' },
    { name: 'Ollama', key: 'ollama', model: 'llama3.1', speed: 'Local private execution', desc: 'Runs locally on CPU/GPU without cloud API keys' },
  ];

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '1.75rem' }}>
        <h2 style={{ fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu size={20} color="#c084fc" />
          <span>Multi-Provider LLM & FastMCP Integration Hub</span>
        </h2>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-dim)' }}>
          Manage multi-model provider fallbacks, inspect platform metrics, and integrate MARO tools directly into Claude Desktop or Cursor IDE via FastMCP.
        </p>
      </div>

      {/* Provider Status Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '1.25rem',
        marginBottom: '2rem',
      }}>
        {providers.map((p) => {
          const isAvailable = providerInfo?.available?.[p.key];
          const isActive = providerInfo?.active_provider === p.key;

          return (
            <div
              key={p.key}
              className="glass-panel"
              style={{
                padding: '1.25rem',
                border: `1px solid ${isActive ? 'rgba(168, 85, 247, 0.45)' : 'var(--border-subtle)'}`,
                background: isActive ? 'rgba(168, 85, 247, 0.08)' : 'rgba(14, 19, 31, 0.7)',
                position: 'relative'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: '#ffffff' }}>
                  {p.name}
                </div>
                {isActive ? (
                  <span className="badge badge-purple" style={{ fontSize: '0.7rem' }}>ACTIVE</span>
                ) : isAvailable ? (
                  <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>READY</span>
                ) : (
                  <span className="badge" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-dim)', fontSize: '0.7rem' }}>NO KEY</span>
                )}
              </div>

              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                {p.desc}
              </div>

              <div style={{
                fontSize: '0.74rem',
                fontFamily: 'var(--font-mono)',
                color: '#818cf8',
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '0.35rem 0.5rem',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '0.5rem'
              }}>
                Default: {p.model}
              </div>

              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                Speed profile: {p.speed}
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.75rem' }}>
        {/* FastMCP Configuration */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <h3 style={{ fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Server size={17} color="#818cf8" />
              <span>FastMCP Server Configuration</span>
            </h3>
            <button onClick={handleCopyMcp} className="btn btn-secondary btn-sm">
              {copiedMcp ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
              <span>{copiedMcp ? 'Copied' : 'Copy JSON'}</span>
            </button>
          </div>

          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Add this configuration to your <code>claude_desktop_config.json</code> or Cursor MCP settings to let your coding assistants orchestrate deep multi-agent research tools natively:
          </p>

          <pre style={{
            background: '#090d16',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '1rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.78rem',
            color: '#c084fc',
            overflowX: 'auto'
          }}>
            <code>{JSON.stringify(mcpConfig, null, 2)}</code>
          </pre>
        </div>

        {/* REST API Explorer */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.5rem' }}>
            <Code size={17} color="#34d399" />
            <span>Interactive REST API Explorer</span>
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Test live backend endpoints directly from the browser:
          </p>

          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
            <select
              value={selectedEndpoint}
              onChange={(e) => setSelectedEndpoint(e.target.value)}
              className="select-control"
              style={{ flex: 1, fontSize: '0.85rem' }}
            >
              <option value="/health/">GET /api/health/ (System Health)</option>
              <option value="/stats/">GET /api/stats/ (Platform Analytics)</option>
              <option value="/rag/stats/">GET /api/rag/stats/ (ChromaDB Collections)</option>
            </select>
            <button
              onClick={handleTestApi}
              disabled={apiTesting}
              className="btn btn-primary btn-sm"
              style={{ padding: '0 1rem' }}
            >
              {apiTesting ? <RefreshCw size={14} className="spinning-icon" /> : <Send size={14} />}
              <span>Send</span>
            </button>
          </div>

          {apiResponse && (
            <pre style={{
              background: '#090d16',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '1rem',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.78rem',
              color: '#34d399',
              maxHeight: '220px',
              overflowY: 'auto'
            }}>
              <code>{JSON.stringify(apiResponse, null, 2)}</code>
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
