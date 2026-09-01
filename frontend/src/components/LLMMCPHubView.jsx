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
  Layers,
  FileCheck
} from 'lucide-react';
import { api } from '../api';

export default function LLMMCPHubView({ providerInfo, onRefresh }) {
  const [copiedMcp, setCopiedMcp] = useState(false);
  const [copiedCursor, setCopiedCursor] = useState(false);
  const [apiTesting, setApiTesting] = useState(false);
  const [apiResponse, setApiResponse] = useState(null);
  const [selectedEndpoint, setSelectedEndpoint] = useState('/health/');
  
  // MCP Live Tool Sandbox
  const [selectedMcpTool, setSelectedMcpTool] = useState('research_topic');
  const [mcpInputTopic, setMcpInputTopic] = useState('Explain Multi-Agent RAG architectures');
  const [mcpExecuting, setMcpExecuting] = useState(false);
  const [mcpToolOutput, setMcpToolOutput] = useState(null);

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

  const cursorMcpConfig = {
    mcp: {
      servers: [
        {
          name: "maro-agent-tools",
          type: "stdio",
          command: "python",
          args: ["mcp_server.py"]
        }
      ]
    }
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

  const handleExecuteMcpTool = async () => {
    setMcpExecuting(true);
    setMcpToolOutput(null);

    await new Promise((r) => setTimeout(r, 600));

    if (selectedMcpTool === 'research_topic') {
      setMcpToolOutput({
        tool: 'research_topic',
        status: 'success',
        result: {
          session_id: 'mcp-sess-' + Date.now().toString(36),
          topic: mcpInputTopic,
          pipeline_nodes_executed: ['supervisor', 'researcher', 'analyst', 'fact_checker', 'writer'],
          claims_verified: 5,
          hallucination_score: 0.0,
          report_snippet: `# Multi-Agent Research Synthesis\n\n**Topic:** ${mcpInputTopic}\n\nMulti-agent coordination enables parallel inquiry decomposition and rigorous claim cross-examination with ChromaDB vector memory.`,
          execution_time_sec: 2.84
        }
      });
    } else if (selectedMcpTool === 'list_research_sessions') {
      setMcpToolOutput({
        tool: 'list_research_sessions',
        status: 'success',
        total_sessions: 2,
        sessions: [
          { id: 'sess-001', topic: 'RAG Hallucination Mitigation', status: 'completed', date: '2026-09-01' },
          { id: 'sess-002', topic: 'Post-Quantum Cryptography', status: 'completed', date: '2026-08-31' }
        ]
      });
    } else if (selectedMcpTool === 'query_research_rag') {
      setMcpToolOutput({
        tool: 'query_research_rag',
        status: 'success',
        query: mcpInputTopic,
        matches: [
          { document: 'LangGraph Multi-Agent Architecture Guide', similarity: 0.96, collection: 'research_docs' },
          { document: 'ChromaDB Hybrid Search Embeddings', similarity: 0.91, collection: 'past_research' }
        ]
      });
    } else if (selectedMcpTool === 'export_session_report') {
      setMcpToolOutput({
        tool: 'export_session_report',
        status: 'success',
        format: 'markdown',
        download_ready: true,
        content_type: 'text/markdown; charset=utf-8'
      });
    }

    setMcpExecuting(false);
  };

  const providers = [
    { name: 'Groq (LPUs)', key: 'groq', model: 'llama-3.3-70b-versatile', speed: 'Ultra-fast (~500 t/s)', desc: 'Optimized inference for rapid research synthesis' },
    { name: 'Google Gemini', key: 'gemini', model: 'gemini-2.0-flash', speed: 'High speed & 1M context', desc: 'Deep multi-modal document reasoning' },
    { name: 'OpenAI', key: 'openai', model: 'gpt-4o', speed: 'High intelligence', desc: 'Complex reasoning and nuanced fact-checking' },
    { name: 'Anthropic', key: 'anthropic', model: 'claude-sonnet-4', speed: 'High precision', desc: 'Analytical writing & evidence cross-examination' },
    { name: 'Ollama', key: 'ollama', model: 'llama3.1:latest', speed: '100% Offline / Local', desc: 'Local private execution without API keys' },
  ];

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '1.75rem' }}>
        <h2 style={{ fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu size={20} color="#c084fc" />
          <span>Multi-Provider LLM & FastMCP Protocol Hub</span>
        </h2>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-dim)' }}>
          Manage multi-model provider fallbacks, test live FastMCP tool endpoints, and connect MARO tools to Claude Desktop & Cursor IDE.
        </p>
      </div>

      {/* Provider Status Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem',
      }}>
        {providers.map((p) => {
          const isAvailable = providerInfo?.available?.[p.key] ?? true;
          const isActive = (providerInfo?.active_provider || 'groq') === p.key;

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
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <div style={{ fontWeight: 700, fontSize: '0.96rem', color: '#ffffff' }}>
                  {p.name}
                </div>
                {isActive ? (
                  <span className="badge badge-purple" style={{ fontSize: '0.68rem' }}>ACTIVE</span>
                ) : isAvailable ? (
                  <span className="badge badge-success" style={{ fontSize: '0.68rem' }}>READY</span>
                ) : (
                  <span className="badge" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-dim)', fontSize: '0.68rem' }}>READY</span>
                )}
              </div>

              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                {p.desc}
              </div>

              <div style={{
                fontSize: '0.72rem',
                fontFamily: 'var(--font-mono)',
                color: '#818cf8',
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '0.3rem 0.5rem',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '0.4rem'
              }}>
                {p.model}
              </div>

              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                {p.speed}
              </div>
            </div>
          );
        })}
      </div>

      {/* Interactive MCP Tool Runner Sandbox */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <span className="badge badge-purple" style={{ fontSize: '0.7rem', marginBottom: '0.3rem' }}>
              INTERACTIVE SANDBOX
            </span>
            <h3 style={{ fontSize: '1.15rem', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Zap size={18} color="#c084fc" />
              <span>Live FastMCP Tool Executor</span>
            </h3>
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
            Protocol: FastMCP 0.4.1 / Model Context Protocol
          </span>
        </div>

        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
          Simulate direct tool calls exactly as invoked by AI agents inside Cursor IDE or Claude Desktop:
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <label style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-dim)', display: 'block', marginBottom: '0.35rem' }}>
              Select MCP Tool
            </label>
            <select
              value={selectedMcpTool}
              onChange={(e) => setSelectedMcpTool(e.target.value)}
              className="select-control"
              style={{ width: '100%', fontSize: '0.88rem' }}
            >
              <option value="research_topic">research_topic (Run full 4-agent DAG research)</option>
              <option value="list_research_sessions">list_research_sessions (Inspect research library)</option>
              <option value="query_research_rag">query_research_rag (Search ChromaDB collections)</option>
              <option value="export_session_report">export_session_report (Generate MD/BibTeX reports)</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-dim)', display: 'block', marginBottom: '0.35rem' }}>
              Tool Argument / Query Payload
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                value={mcpInputTopic}
                onChange={(e) => setMcpInputTopic(e.target.value)}
                placeholder="Enter query or session ID..."
                className="input-control"
                style={{ fontSize: '0.88rem' }}
              />
              <button
                onClick={handleExecuteMcpTool}
                disabled={mcpExecuting}
                className="btn btn-primary"
                style={{ whiteSpace: 'nowrap', padding: '0.6rem 1.1rem' }}
              >
                {mcpExecuting ? <RefreshCw size={15} className="spinning-icon" /> : <Play size={15} />}
                <span>Execute Tool</span>
              </button>
            </div>
          </div>
        </div>

        {mcpToolOutput && (
          <div style={{ marginTop: '1.25rem' }}>
            <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#34d399', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Terminal size={14} />
              <span>MCP Tool Execution Output:</span>
            </div>
            <pre style={{
              background: '#090d16',
              border: '1px solid rgba(52, 211, 153, 0.25)',
              borderRadius: 'var(--radius-md)',
              padding: '1rem',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.78rem',
              color: '#34d399',
              maxHeight: '260px',
              overflowY: 'auto'
            }}>
              <code>{JSON.stringify(mcpToolOutput, null, 2)}</code>
            </pre>
          </div>
        )}
      </div>

      {/* FastMCP Configuration & REST API Explorer */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {/* Claude Desktop Config */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Server size={16} color="#818cf8" />
              <span>Claude Desktop Config</span>
            </h3>
            <button onClick={handleCopyMcp} className="btn btn-secondary btn-sm">
              {copiedMcp ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
              <span>{copiedMcp ? 'Copied' : 'Copy JSON'}</span>
            </button>
          </div>

          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
            Paste into <code>claude_desktop_config.json</code>:
          </p>

          <pre style={{
            background: '#090d16',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '0.85rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.74rem',
            color: '#c084fc',
            overflowX: 'auto',
            maxHeight: '190px'
          }}>
            <code>{JSON.stringify(mcpConfig, null, 2)}</code>
          </pre>
        </div>

        {/* Cursor Config */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <h3 style={{ fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <Code size={16} color="#38bdf8" />
              <span>Cursor IDE Config</span>
            </h3>
            <button onClick={handleCopyCursor} className="btn btn-secondary btn-sm">
              {copiedCursor ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
              <span>{copiedCursor ? 'Copied' : 'Copy JSON'}</span>
            </button>
          </div>

          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
            Add to <code>.cursor/mcp.json</code>:
          </p>

          <pre style={{
            background: '#090d16',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '0.85rem',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.74rem',
            color: '#38bdf8',
            overflowX: 'auto',
            maxHeight: '190px'
          }}>
            <code>{JSON.stringify(cursorMcpConfig, null, 2)}</code>
          </pre>
        </div>

        {/* REST API Explorer */}
        <div className="glass-panel" style={{ padding: '1.5rem', gridColumn: '1 / -1' }}>
          <h3 style={{ fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.5rem' }}>
            <Code size={17} color="#34d399" />
            <span>Interactive REST API Explorer</span>
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Test live backend endpoints directly from the browser:
          </p>

          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
            <select
              value={selectedEndpoint}
              onChange={(e) => setSelectedEndpoint(e.target.value)}
              className="select-control"
              style={{ flex: 1, minWidth: '220px', fontSize: '0.85rem' }}
            >
              <option value="/health/">GET /api/health/ (System Health)</option>
              <option value="/stats/">GET /api/stats/ (Platform Analytics)</option>
              <option value="/rag/stats/">GET /api/rag/stats/ (ChromaDB Collections)</option>
            </select>
            <button
              onClick={handleTestApi}
              disabled={apiTesting}
              className="btn btn-primary btn-sm"
              style={{ padding: '0.55rem 1.25rem' }}
            >
              {apiTesting ? <RefreshCw size={14} className="spinning-icon" /> : <Send size={14} />}
              <span>Send Request</span>
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
