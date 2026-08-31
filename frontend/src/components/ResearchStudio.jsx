import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Play, 
  FileText, 
  Download, 
  Copy, 
  Check, 
  ExternalLink, 
  ShieldCheck, 
  Terminal, 
  FileCode, 
  BookOpen, 
  Clock, 
  Layers, 
  RefreshCw, 
  Tag as TagIcon,
  Plus,
  Database,
  UploadCloud,
  FileCheck,
  X,
  Paperclip,
  Sliders,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { marked } from 'marked';
import confetti from 'canvas-confetti';
import { api } from '../api';
import AgentGraph from './AgentGraph';
import Ethnocare3DCore from './Ethnocare3DCore';

export default function ResearchStudio({ user, onOpenAuth }) {
  const [topic, setTopic] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [events, setEvents] = useState([]);
  const [currentStage, setCurrentStage] = useState('');
  const [currentJob, setCurrentJob] = useState(null);
  const [copied, setCopied] = useState(false);
  const [activeViewTab, setActiveViewTab] = useState('report'); // 'report' | 'evidence' | 'factcheck'
  const [newTag, setNewTag] = useState('');
  const [tags, setTags] = useState([]);
  const [attachedDocs, setAttachedDocs] = useState([]);
  const [uploadingDoc, setUploadingDoc] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [ragStats, setRagStats] = useState(null);
  const [showRAGUpload, setShowRAGUpload] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [useRAG, setUseRAG] = useState(true);
  
  // Pipeline Parameters
  const [maxRevisions, setMaxRevisions] = useState(2);
  const [topK, setTopK] = useState(5);
  const [strictness, setStrictness] = useState('Balanced');

  const terminalBottomRef = useRef(null);
  const fileInputRef = useRef(null);

  const sampleTopics = [
    'How do Multi-Agent architectures prevent hallucinations in RAG systems?',
    'Current state of CRISPR gene editing therapies approved by the FDA',
    'Quantum computing breakthroughs in cryptographic post-quantum standards',
    'Comparison of speculative decoding vs standard decoding in LLM inference',
  ];

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalBottomRef.current) {
      terminalBottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [events]);

  const loadRagInfo = useCallback(async () => {
    try {
      const stats = await api.getRAGStats();
      setRagStats(stats);
    } catch {
      // ignore
    }
  }, []);

  // Load initial RAG knowledge base statistics
  useEffect(() => {
    loadRagInfo();
  }, [loadRagInfo]);

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;

    if (!user) {
      onOpenAuth();
      return;
    }

    setUploadingDoc(true);
    setUploadMessage('');

    try {
      const res = await api.uploadDocuments(files);
      const newFiles = Array.from(files).map((f) => ({
        name: f.name,
        size: (f.size / 1024).toFixed(1) + ' KB',
        chunks: res.chunks_added,
      }));

      setAttachedDocs((prev) => [...prev, ...newFiles]);
      setUploadMessage(`Indexed ${res.chunks_added} chunks into ChromaDB from ${newFiles.length} file(s)`);
      loadRagInfo();
    } catch (err) {
      setUploadMessage(`Upload failed: ${err.message}`);
    } finally {
      setUploadingDoc(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleStartResearch = async () => {
    if (!topic.trim()) return;

    if (!user) {
      onOpenAuth();
      return;
    }

    setIsRunning(true);
    setEvents([]);
    setCurrentStage('queued');
    setCurrentJob(null);
    setTags([]);

    try {
      await api.streamResearch(topic, {
        onEvent: (event) => {
          setEvents((prev) => [...prev, { ...event, timestamp: new Date().toLocaleTimeString() }]);
          if (event.stage) {
            setCurrentStage(event.stage);
          }
          if (event.session_id) {
            fetchCompletedJob(event.session_id);
          }
        },
        onError: (err) => {
          setIsRunning(false);
          setCurrentStage('failed');
          setEvents((prev) => [
            ...prev,
            { stage: 'failed', message: `Execution error: ${err.message}`, timestamp: new Date().toLocaleTimeString() },
          ]);
        },
        onComplete: ({ sessionId }) => {
          setIsRunning(false);
          setCurrentStage('completed');
          if (sessionId) {
            fetchCompletedJob(sessionId);
          }
          try {
            confetti({
              particleCount: 50,
              spread: 50,
              origin: { y: 0.7 }
            });
          } catch {
            // ignore
          }
        },
      });
    } catch (err) {
      setIsRunning(false);
      setCurrentStage('failed');
      setEvents((prev) => [
        ...prev,
        { stage: 'failed', message: `Failed to stream: ${err.message}`, timestamp: new Date().toLocaleTimeString() },
      ]);
    }
  };

  const fetchCompletedJob = async (id) => {
    try {
      const data = await api.getJob(id);
      setCurrentJob(data);
      if (data.tags) {
        setTags(data.tags);
      }
    } catch (e) {
      console.error('Failed to fetch job details:', e);
    }
  };

  const handleCopyReport = () => {
    if (!currentJob?.final_report) return;
    navigator.clipboard.writeText(currentJob.final_report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleAddTag = async (e) => {
    e.preventDefault();
    if (!newTag.trim() || !currentJob?.id) return;
    try {
      const tag = await api.addTag(currentJob.id, newTag.trim());
      setTags((prev) => [...prev.filter((t) => t.id !== tag.id), tag]);
      setNewTag('');
    } catch (err) {
      alert(err.message);
    }
  };

  const totalIndexedChunks = (ragStats?.collections?.research_docs || 0) + (ragStats?.collections?.past_research || 0);

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
      {/* ══════════════════════════════════════════════════════════════════
          1. Ethnocare Minimalist Architectural Hero Header
          ══════════════════════════════════════════════════════════════════ */}
      <header style={{ marginBottom: '2.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.12)', paddingBottom: '1.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{
            fontSize: '0.72rem',
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'var(--color-accent)',
            fontWeight: 700,
          }}>
            [ 01 // AUTONOMOUS AI RESEARCH PLATFORM ]
          </div>
          <div style={{
            fontSize: '0.72rem',
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.08em',
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
          }}>
            SYS: LANGGRAPH v0.3 · CHROMADB RAG · MULTI-PROVIDER
          </div>
        </div>

        <h1 style={{
          fontSize: 'clamp(2rem, 4vw, 3rem)',
          fontWeight: 800,
          letterSpacing: '-0.03em',
          color: '#ffffff',
          marginBottom: '0.6rem',
          lineHeight: 1.1,
        }}>
          Multi-Agent Research Orchestrator
        </h1>

        <p style={{
          fontSize: '1.02rem',
          color: 'var(--text-muted)',
          maxWidth: '750px',
          lineHeight: 1.55,
          fontWeight: 400,
        }}>
          High-precision research synthesis powered by stateful agent graphs, dual-collection vector retrieval, and automated claim-by-claim verification gates.
        </p>
      </header>

      {/* ══════════════════════════════════════════════════════════════════
          2. Ethnocare 3D Interactive Telemetry Core (Scroll & Explode)
          ══════════════════════════════════════════════════════════════════ */}
      <Ethnocare3DCore isRunning={isRunning} activeStage={currentStage} />

      {/* ══════════════════════════════════════════════════════════════════
          3. LangGraph 4-Agent Pipeline Workflow
          ══════════════════════════════════════════════════════════════════ */}
      <AgentGraph 
        currentStage={currentStage} 
        revisionCount={currentJob?.revision_count || 0} 
        isRunning={isRunning} 
      />

      {/* ══════════════════════════════════════════════════════════════════
          3. Research Query Input & Controls
          ══════════════════════════════════════════════════════════════════ */}
      <div className="glass-panel" style={{ padding: '1.75rem', marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <label style={{ fontWeight: 750, fontSize: '0.92rem', color: '#ffffff', textTransform: 'uppercase', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ color: 'var(--color-accent)' }}>//</span>
            <span>Research Topic & Inquiry</span>
          </label>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <button
              onClick={() => setShowRAGUpload(!showRAGUpload)}
              className="btn btn-secondary btn-sm"
              style={{
                borderColor: attachedDocs.length > 0 ? 'var(--color-accent)' : 'rgba(255, 255, 255, 0.2)',
                color: attachedDocs.length > 0 ? 'var(--color-accent)' : '#ffffff'
              }}
            >
              <Paperclip size={13} />
              <span>{attachedDocs.length > 0 ? `${attachedDocs.length} PDF(s) Attached` : '+ Attach RAG Document'}</span>
            </button>

            <button
              onClick={() => setShowSettings(!showSettings)}
              className="btn btn-secondary btn-sm"
            >
              <Sliders size={13} />
              <span>Parameters</span>
              {showSettings ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
          </div>
        </div>

        <textarea
          className="textarea-control"
          rows={3}
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a technical inquiry or deep research question (e.g., 'Analyze the latest consensus and contradictions in post-quantum cryptography standards')..."
          disabled={isRunning}
          style={{ fontSize: '0.96rem', minHeight: '90px', marginBottom: '1rem' }}
        />

        {/* Expandable Pipeline Settings Drawer */}
        {showSettings && (
          <div style={{
            background: '#080808',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: 'var(--radius-sm)',
            padding: '1.25rem',
            marginBottom: '1.25rem',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '1.5rem',
          }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.4rem', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>
                <span style={{ color: 'var(--text-muted)' }}>Max Revisions:</span>
                <span style={{ color: 'var(--color-accent)', fontWeight: 700 }}>{maxRevisions} loops</span>
              </div>
              <input
                type="range"
                min="1"
                max="3"
                value={maxRevisions}
                onChange={(e) => setMaxRevisions(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--color-accent)' }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.4rem', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>
                <span style={{ color: 'var(--text-muted)' }}>ChromaDB Top-K:</span>
                <span style={{ color: 'var(--color-accent)', fontWeight: 700 }}>{topK} chunks</span>
              </div>
              <input
                type="range"
                min="3"
                max="10"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--color-accent)' }}
              />
            </div>

            <div>
              <div style={{ fontSize: '0.78rem', marginBottom: '0.4rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Verification Rigor:
              </div>
              <div style={{ display: 'flex', gap: '0.4rem' }}>
                {['Permissive', 'Balanced', 'Rigorous'].map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    onClick={() => setStrictness(lvl)}
                    style={{
                      flex: 1,
                      padding: '0.35rem',
                      fontSize: '0.72rem',
                      fontFamily: 'var(--font-mono)',
                      textTransform: 'uppercase',
                      borderRadius: 'var(--radius-sm)',
                      border: strictness === lvl ? '1px solid var(--color-accent)' : '1px solid rgba(255, 255, 255, 0.15)',
                      background: strictness === lvl ? 'rgba(0, 245, 243, 0.12)' : 'transparent',
                      color: strictness === lvl ? 'var(--color-accent)' : 'var(--text-muted)',
                      cursor: 'pointer'
                    }}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Expandable RAG PDF Ingestion Sandbox */}
        {showRAGUpload && (
          <div style={{
            background: '#080808',
            border: '1px dashed rgba(0, 245, 243, 0.35)',
            borderRadius: 'var(--radius-sm)',
            padding: '1.25rem',
            marginBottom: '1.25rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.82rem', fontWeight: 700, textTransform: 'uppercase', color: '#ffffff' }}>
                <Database size={15} color="var(--color-accent)" />
                <span>RAG Knowledge Vector Ingestion</span>
              </div>
              <span style={{ fontSize: '0.72rem', color: 'var(--color-accent)', fontFamily: 'var(--font-mono)' }}>
                {totalIndexedChunks} vector chunks currently indexed in ChromaDB
              </span>
            </div>

            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.85rem' }}>
              Upload local research PDFs or papers. The Researcher & Analyst agents will extract semantic chunks alongside web search.
            </p>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                multiple
                style={{ display: 'none' }}
                onChange={(e) => handleFileUpload(e.target.files)}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadingDoc}
                className="btn btn-secondary btn-sm"
              >
                {uploadingDoc ? <RefreshCw size={13} className="spinning-icon" /> : <UploadCloud size={13} />}
                <span>{uploadingDoc ? 'Ingesting PDF...' : 'Choose PDF Files'}</span>
              </button>

              <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={useRAG}
                  onChange={(e) => setUseRAG(e.target.checked)}
                  style={{ accentColor: 'var(--color-accent)' }}
                />
                <span>Include ChromaDB RAG retrieval</span>
              </label>

              {uploadMessage && (
                <span style={{ fontSize: '0.76rem', color: uploadMessage.includes('failed') ? '#f87171' : '#34d399', display: 'flex', alignItems: 'center', gap: '0.3rem', fontFamily: 'var(--font-mono)' }}>
                  <FileCheck size={13} /> {uploadMessage}
                </span>
              )}
            </div>

            {/* List of Attached Documents in this Session */}
            {attachedDocs.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45rem', marginTop: '0.85rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                {attachedDocs.map((doc, i) => (
                  <div
                    key={i}
                    style={{
                      background: '#141414',
                      border: '1px solid var(--color-accent)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '0.25rem 0.65rem',
                      fontSize: '0.74rem',
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.45rem'
                    }}
                  >
                    <FileText size={12} color="var(--color-accent)" />
                    <span>{doc.name}</span>
                    <span style={{ color: 'var(--color-accent)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>({doc.chunks} chunks)</span>
                    <button
                      type="button"
                      onClick={() => setAttachedDocs((prev) => prev.filter((_, idx) => idx !== i))}
                      style={{ background: 'transparent', border: 'none', color: 'var(--text-dim)', cursor: 'pointer', display: 'flex', padding: 0 }}
                    >
                      <X size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Suggestion Chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center', marginBottom: '1.5rem' }}>
          <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>Suggestions:</span>
          {sampleTopics.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => setTopic(sample)}
              disabled={isRunning}
              style={{
                background: '#0a0a0a',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.3rem 0.75rem',
                fontSize: '0.76rem',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-accent)'; e.currentTarget.style.color = '#ffffff'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.12)'; e.currentTarget.style.color = 'var(--text-muted)'; }}
            >
              {sample.length > 60 ? sample.slice(0, 60) + '...' : sample}
            </button>
          ))}
        </div>

        {/* Launch Button & Status */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <button
            onClick={handleStartResearch}
            disabled={isRunning || !topic.trim()}
            className="btn btn-primary"
            style={{ padding: '0.75rem 1.85rem', fontSize: '0.86rem' }}
          >
            {isRunning ? (
              <>
                <RefreshCw size={16} className="spinning-icon" />
                <span>Orchestrating Pipeline...</span>
              </>
            ) : (
              <>
                <Play size={16} />
                <span>Execute Autonomous Pipeline</span>
              </>
            )}
          </button>

          {currentJob && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Layers size={13} color="var(--color-accent)" />
                <span><strong>{currentJob.web_sources_count + currentJob.rag_chunks_count}</strong> SOURCES</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <RefreshCw size={13} color="#fbbf24" />
                <span><strong>{currentJob.revision_count}</strong> REVISIONS</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Clock size={13} color="#34d399" />
                <span><strong>{currentJob.duration_seconds || 0}s</strong></span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════════════
          4. Live Streaming Timeline
          ══════════════════════════════════════════════════════════════════ */}
      {isRunning && (
        <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '2.5rem', background: '#050505' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', paddingBottom: '0.6rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--color-accent)', textTransform: 'uppercase' }}>
              <Terminal size={14} />
              <span>Execution Stream // Live Console</span>
            </div>
            <span className="badge badge-info" style={{ fontSize: '0.68rem' }}>
              STREAMING
            </span>
          </div>

          <div style={{
            maxHeight: '220px',
            overflowY: 'auto',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.8rem',
            lineHeight: 1.6,
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem',
          }}>
            {events.map((ev, index) => (
              <div key={index} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                <span style={{ color: 'var(--text-dim)', fontSize: '0.72rem' }}>{ev.timestamp}</span>
                <span style={{
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  padding: '0.08rem 0.45rem',
                  borderRadius: 'var(--radius-sm)',
                  textTransform: 'uppercase',
                  background: ev.stage === 'researcher' ? 'rgba(192, 132, 252, 0.2)' : (ev.stage === 'analyst' ? 'rgba(0, 245, 243, 0.2)' : (ev.stage === 'fact_checker' ? 'rgba(251, 191, 36, 0.2)' : 'rgba(52, 211, 153, 0.2)')),
                  color: ev.stage === 'researcher' ? '#c084fc' : (ev.stage === 'analyst' ? '#00F5F3' : (ev.stage === 'fact_checker' ? '#fbbf24' : '#34d399')),
                }}>
                  {ev.stage || 'STAGE'}
                </span>
                <span style={{ color: '#e5e5e5', flex: 1 }}>{ev.message}</span>
              </div>
            ))}
            <div ref={terminalBottomRef} />
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════
          5. Research Results Panel
          ══════════════════════════════════════════════════════════════════ */}
      {currentJob && (
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
            paddingBottom: '1rem',
            marginBottom: '1.5rem',
            flexWrap: 'wrap',
            gap: '0.75rem',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <button
                onClick={() => setActiveViewTab('report')}
                className={`btn btn-sm ${activeViewTab === 'report' ? 'btn-primary' : 'btn-secondary'}`}
              >
                <FileText size={13} />
                <span>Synthesized Report</span>
              </button>

              <button
                onClick={() => setActiveViewTab('evidence')}
                className={`btn btn-sm ${activeViewTab === 'evidence' ? 'btn-primary' : 'btn-secondary'}`}
              >
                <Layers size={13} />
                <span>Evidence Sources ({currentJob.sources?.length || currentJob.web_sources_count || 0})</span>
              </button>

              <button
                onClick={() => setActiveViewTab('factcheck')}
                className={`btn btn-sm ${activeViewTab === 'factcheck' ? 'btn-primary' : 'btn-secondary'}`}
              >
                <ShieldCheck size={13} />
                <span>Verification Scorecard</span>
              </button>
            </div>

            {/* Export Actions */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <button
                onClick={handleCopyReport}
                className="btn btn-secondary btn-sm"
                title="Copy Markdown Report"
              >
                {copied ? <Check size={13} color="#34d399" /> : <Copy size={13} />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>

              <a
                href={api.getExportUrl(currentJob.id, 'markdown')}
                download={`research-${currentJob.id}.md`}
                className="btn btn-secondary btn-sm"
              >
                <Download size={13} />
                <span>MD</span>
              </a>

              <a
                href={api.getExportUrl(currentJob.id, 'html')}
                download={`research-${currentJob.id}.html`}
                className="btn btn-secondary btn-sm"
              >
                <FileCode size={13} />
                <span>HTML</span>
              </a>

              <a
                href={api.getExportUrl(currentJob.id, 'bibtex')}
                download={`citations-${currentJob.id}.bib`}
                className="btn btn-secondary btn-sm"
              >
                <BookOpen size={13} />
                <span>BibTeX</span>
              </a>
            </div>
          </div>

          {/* Report Tab */}
          {activeViewTab === 'report' && (
            <div>
              <div style={{
                background: '#0a0a0a',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.85rem 1.15rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}>
                <div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--color-accent)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', fontFamily: 'var(--font-mono)' }}>
                    SYNTHESIS COMPLETE // VERIFIED REPORT
                  </div>
                  <div style={{ fontSize: '0.96rem', color: '#ffffff', fontWeight: 700, marginTop: '0.2rem' }}>
                    {currentJob.topic}
                  </div>
                </div>
                <span className="badge badge-success">
                  {currentJob.revision_count > 0 ? `VERIFIED (${currentJob.revision_count} REVISIONS)` : 'VERIFIED & CITED'}
                </span>
              </div>

              <div 
                className="markdown-body"
                dangerouslySetInnerHTML={{ __html: marked.parse(currentJob.final_report || 'No report generated.') }}
              />

              {/* Tags Section */}
              <div style={{
                marginTop: '2.5rem',
                paddingTop: '1.25rem',
                borderTop: '1px solid rgba(255, 255, 255, 0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '0.75rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <TagIcon size={14} color="var(--text-dim)" />
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>TAGS:</span>
                  {tags.map((t) => (
                    <span key={t.id || t.name} className="badge badge-purple">
                      #{t.name}
                    </span>
                  ))}
                  {tags.length === 0 && (
                    <span style={{ fontSize: '0.76rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>NO TAGS</span>
                  )}
                </div>

                <form onSubmit={handleAddTag} style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <input
                    type="text"
                    placeholder="Add tag..."
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    className="input-control"
                    style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem', width: '150px' }}
                  />
                  <button type="submit" className="btn btn-secondary btn-sm" disabled={!newTag.trim()}>
                    <Plus size={12} />
                    <span>Add</span>
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* Evidence Tab */}
          {activeViewTab === 'evidence' && (
            <div>
              <div style={{ marginBottom: '1.25rem', color: 'var(--text-muted)', fontSize: '0.84rem', fontFamily: 'var(--font-mono)' }}>
                EVIDENCE EXTRACTED FROM WEB SEARCH (TAVILY/DDG) & CHROMADB RAG RETRIEVAL:
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {(currentJob.sources || []).map((source, index) => (
                  <div 
                    key={index}
                    style={{
                      background: '#0a0a0a',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '1.1rem',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span className={`badge ${source.source_type === 'web' ? 'badge-info' : 'badge-purple'}`}>
                          {source.source_type === 'web' ? 'WEB' : 'RAG CHUNK'}
                        </span>
                        <span style={{ fontWeight: 700, fontSize: '0.88rem', color: '#ffffff' }}>
                          {source.domain || source.title || `Evidence Reference #${index + 1}`}
                        </span>
                      </div>

                      {source.url && (
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noreferrer"
                          className="btn btn-ghost btn-sm"
                          style={{ fontSize: '0.74rem' }}
                        >
                          <span>Open Source</span>
                          <ExternalLink size={12} />
                        </a>
                      )}
                    </div>

                    <div style={{
                      fontSize: '0.84rem',
                      color: '#d4d4d4',
                      lineHeight: 1.6,
                      background: '#000000',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      padding: '0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      fontFamily: 'var(--font-mono)'
                    }}>
                      {source.snippet}
                    </div>
                  </div>
                ))}

                {(!currentJob.sources || currentJob.sources.length === 0) && (
                  <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    NO GRANULAR EVIDENCE RECORDED FOR THIS RUN.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Verification QA Tab */}
          {activeViewTab === 'factcheck' && (
            <div>
              <div style={{
                background: '#0a0a0a',
                border: '1px solid rgba(251, 191, 36, 0.25)',
                borderRadius: 'var(--radius-sm)',
                padding: '1rem 1.25rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <ShieldCheck size={20} color="#fbbf24" />
                  <div>
                    <div style={{ fontWeight: 700, color: '#fbbf24', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      Fact-Checker Verification Analysis
                    </div>
                    <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                      Automated claim validation and quality scoring
                    </div>
                  </div>
                </div>

                <span className="badge badge-success">
                  {currentJob.revision_count === 0 ? 'PASSED (Cycle 1)' : `PASSED (${currentJob.revision_count} Revisions)`}
                </span>
              </div>

              <div 
                className="markdown-body"
                dangerouslySetInnerHTML={{ __html: marked.parse(currentJob.fact_check_result || 'No detailed fact-check report returned.') }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
