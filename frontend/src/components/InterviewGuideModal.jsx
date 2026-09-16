import React, { useState } from 'react';
import { 
  X, 
  Sparkles, 
  GitFork, 
  ShieldCheck, 
  Terminal, 
  HelpCircle, 
  Cpu, 
  Database, 
  CheckCircle2, 
  RefreshCw, 
  Layers, 
  Play, 
  FileText,
  ChevronRight,
  BookOpen
} from 'lucide-react';

export default function InterviewGuideModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('pitch'); // 'pitch' | 'agents' | 'decisions' | 'qa' | 'demo'

  if (!isOpen) return null;

  const tabs = [
    { id: 'pitch', label: '30s Elevator Pitch', icon: Sparkles },
    { id: 'agents', label: 'The 4 Agents & Flow', icon: GitFork },
    { id: 'decisions', label: 'Key Architecture', icon: Layers },
    { id: 'qa', label: 'Interview Q&A', icon: HelpCircle },
    { id: 'demo', label: 'Live Demo Script', icon: Play },
  ];

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 100,
      background: 'rgba(0, 0, 0, 0.85)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.5rem',
      animation: 'fadeIn 0.2s ease-out'
    }}>
      <div style={{
        background: '#0a0d14',
        border: '1px solid rgba(0, 245, 243, 0.3)',
        borderRadius: '12px',
        width: '100%',
        maxWidth: '920px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        boxShadow: '0 24px 64px rgba(0, 0, 0, 0.9), 0 0 40px rgba(0, 245, 243, 0.1)',
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '1.25rem 1.75rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'rgba(255, 255, 255, 0.02)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '6px',
              background: 'linear-gradient(135deg, rgba(0, 245, 243, 0.2), rgba(168, 85, 247, 0.2))',
              border: '1px solid var(--color-accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-accent)'
            }}>
              <BookOpen size={18} />
            </div>
            <div>
              <div style={{
                fontSize: '1.05rem',
                fontWeight: 800,
                color: '#ffffff',
                fontFamily: 'var(--font-display)',
                letterSpacing: '-0.01em',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                MARO Interview & Architecture Guide
                <span style={{
                  fontSize: '0.65rem',
                  fontFamily: 'var(--font-mono)',
                  background: 'rgba(0, 245, 243, 0.15)',
                  color: 'var(--color-accent)',
                  padding: '0.15rem 0.5rem',
                  borderRadius: '100px',
                  fontWeight: 700,
                  border: '1px solid rgba(0, 245, 243, 0.3)'
                }}>
                  INTERVIEWER CHEAT SHEET
                </span>
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, marginTop: '2px' }}>
                Use this screen to explain the project in 2 minutes or answer architectural deep dives.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              borderRadius: '6px',
              color: 'var(--text-muted)',
              width: '32px',
              height: '32px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = '#fff'; e.currentTarget.style.borderColor = '#fff'; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.15)'; }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Tab Navigation */}
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          padding: '0.75rem 1.75rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          background: '#070a0f',
          overflowX: 'auto'
        }}>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                  padding: '0.45rem 0.85rem',
                  borderRadius: '6px',
                  border: isActive ? '1px solid var(--color-accent)' : '1px solid transparent',
                  background: isActive ? 'rgba(0, 245, 243, 0.1)' : 'transparent',
                  color: isActive ? 'var(--color-accent)' : 'var(--text-muted)',
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease'
                }}
              >
                <Icon size={14} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Modal Body Content */}
        <div style={{
          padding: '1.75rem',
          overflowY: 'auto',
          flex: 1,
          fontSize: '0.86rem',
          lineHeight: 1.6,
          color: 'var(--text-normal)'
        }}>

          {/* TAB 1: 30-SECOND PITCH */}
          {activeTab === 'pitch' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{
                background: 'rgba(0, 245, 243, 0.04)',
                border: '1px solid rgba(0, 245, 243, 0.25)',
                borderRadius: '8px',
                padding: '1.25rem'
              }}>
                <div style={{
                  fontSize: '0.72rem',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--color-accent)',
                  fontWeight: 700,
                  letterSpacing: '0.08em',
                  marginBottom: '0.5rem'
                }}>
                  THE 30-SECOND SCRIPT TO RECITE
                </div>
                <blockquote style={{
                  fontSize: '0.98rem',
                  fontStyle: 'italic',
                  color: '#ffffff',
                  margin: 0,
                  lineHeight: 1.65
                }}>
                  &ldquo;<strong>Multi-Agent Research Orchestrator (MARO)</strong> is an autonomous AI research system that replaces error-prone, single-prompt LLM queries with an iterative <strong>4-agent state machine</strong> built on <strong>LangGraph</strong>, <strong>Django REST Framework</strong>, and <strong>React</strong>.
                  <br /><br />
                  Instead of one prompt trying to search, read, fact-check, and write simultaneously, MARO splits the work into specialized agents: <strong>Researcher</strong> gathers evidence, <strong>Analyst</strong> finds themes and contradictions, <strong>Fact-Checker</strong> audits claims against actual sources and triggers an autonomous feedback loop if claims lack proof, and <strong>Writer</strong> produces a publication-ready report with verified inline citations.&rdquo;
                </blockquote>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                gap: '1rem'
              }}>
                <div style={{
                  background: '#111622',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '8px',
                  padding: '1rem'
                }}>
                  <div style={{ color: '#f87171', fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                    ❌ The Problem with Single LLMs
                  </div>
                  <ul style={{ margin: 0, paddingLeft: '1.2rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    <li>Hallucinate non-existent academic citations.</li>
                    <li>Suffer cognitive overload on complex multi-angle research.</li>
                    <li>Cannot self-verify claims against live retrieved text.</li>
                  </ul>
                </div>

                <div style={{
                  background: '#111622',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '8px',
                  padding: '1rem'
                }}>
                  <div style={{ color: '#34d399', fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                    ✅ MARO Solution
                  </div>
                  <ul style={{ margin: 0, paddingLeft: '1.2rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    <li>Separation of concerns (4 specialized agent nodes).</li>
                    <li>Automated conditional revision gate (max 2 loops).</li>
                    <li>Verified inline citations with domain provenance.</li>
                  </ul>
                </div>

                <div style={{
                  background: '#111622',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '8px',
                  padding: '1rem'
                }}>
                  <div style={{ color: 'var(--color-accent)', fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                    ⚡ Key Engineering Metrics
                  </div>
                  <ul style={{ margin: 0, paddingLeft: '1.2rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    <li><strong>62 automated tests</strong> (100% pass rate).</li>
                    <li>Zero-downtime failovers (Tavily → DuckDuckGo).</li>
                    <li>Full FastMCP integration for Claude Desktop & Cursor.</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: THE 4 AGENTS */}
          {activeTab === 'agents' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{
                fontSize: '0.8rem',
                color: 'var(--text-muted)',
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '0.75rem 1rem',
                borderRadius: '6px',
                borderLeft: '3px solid var(--color-accent)'
              }}>
                <strong>The Mental Model:</strong> Each agent is an independent node in a LangGraph <code>StateGraph</code> with typed state reduction.
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {/* Agent 1 */}
                <div style={{
                  background: '#101524',
                  border: '1px solid rgba(168, 85, 247, 0.3)',
                  borderRadius: '8px',
                  padding: '1rem',
                  display: 'flex',
                  gap: '1rem',
                  alignItems: 'flex-start'
                }}>
                  <div style={{
                    background: 'rgba(168, 85, 247, 0.15)',
                    color: '#c084fc',
                    borderRadius: '6px',
                    padding: '0.5rem',
                    fontWeight: 800,
                    fontSize: '0.75rem',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    NODE 1
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 800, color: '#ffffff', fontSize: '0.92rem' }}>
                      🟣 Researcher Agent (Information Retrieval)
                    </div>
                    <p style={{ margin: '0.35rem 0 0.5rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                      Decomposes the topic into 3 distinct search angles. Queries live web sources using Tavily API (with automatic DuckDuckGo fallback) and retrieves semantic document context from ChromaDB.
                    </p>
                    <div style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: '#c084fc' }}>
                      Output: Appends raw evidence chunks to <code>research_data</code> state.
                    </div>
                  </div>
                </div>

                {/* Agent 2 */}
                <div style={{
                  background: '#101524',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: '8px',
                  padding: '1rem',
                  display: 'flex',
                  gap: '1rem',
                  alignItems: 'flex-start'
                }}>
                  <div style={{
                    background: 'rgba(59, 130, 246, 0.15)',
                    color: '#60a5fa',
                    borderRadius: '6px',
                    padding: '0.5rem',
                    fontWeight: 800,
                    fontSize: '0.75rem',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    NODE 2
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 800, color: '#ffffff', fontSize: '0.92rem' }}>
                      🔵 Analyst Agent (Thematic Synthesis)
                    </div>
                    <p style={{ margin: '0.35rem 0 0.5rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                      Reads all collected sources, clusters them into 3-5 core themes, flags direct contradictions between sources, highlights consensus points, and identifies knowledge gaps.
                    </p>
                    <div style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>
                      Output: Populates structured markdown analysis in <code>analysis</code> state.
                    </div>
                  </div>
                </div>

                {/* Agent 3 */}
                <div style={{
                  background: '#101524',
                  border: '1px solid rgba(234, 179, 8, 0.3)',
                  borderRadius: '8px',
                  padding: '1rem',
                  display: 'flex',
                  gap: '1rem',
                  alignItems: 'flex-start'
                }}>
                  <div style={{
                    background: 'rgba(234, 179, 8, 0.15)',
                    color: '#facc15',
                    borderRadius: '6px',
                    padding: '0.5rem',
                    fontWeight: 800,
                    fontSize: '0.75rem',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    NODE 3
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 800, color: '#ffffff', fontSize: '0.92rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      🟡 Fact-Checker Agent (Auditing & Revision Gate)
                      <span style={{ fontSize: '0.68rem', background: 'rgba(234, 179, 8, 0.2)', color: '#facc15', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                        CONDITIONAL EDGE
                      </span>
                    </div>
                    <p style={{ margin: '0.35rem 0 0.5rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                      Audits every claim made by the Analyst against the source text. Assigns verdicts (VERIFIED, UNVERIFIED, CONTRADICTED). If &gt;30% of claims lack proof, routes BACK to Researcher for a targeted revision (capped at 2 loops).
                    </p>
                    <div style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: '#facc15' }}>
                      Output: <code>fact_check_passed</code> (true/false) determining routing to Writer or Researcher.
                    </div>
                  </div>
                </div>

                {/* Agent 4 */}
                <div style={{
                  background: '#101524',
                  border: '1px solid rgba(52, 211, 153, 0.3)',
                  borderRadius: '8px',
                  padding: '1rem',
                  display: 'flex',
                  gap: '1rem',
                  alignItems: 'flex-start'
                }}>
                  <div style={{
                    background: 'rgba(52, 211, 153, 0.15)',
                    color: '#34d399',
                    borderRadius: '6px',
                    padding: '0.5rem',
                    fontWeight: 800,
                    fontSize: '0.75rem',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    NODE 4
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 800, color: '#ffffff', fontSize: '0.92rem' }}>
                      🟢 Writer Agent (Publication Synthesis)
                    </div>
                    <p style={{ margin: '0.35rem 0 0.5rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                      Compiles the final verified research paper: Executive Summary, Evidence Matrix Table, Technical Breakdown, Strategic Conclusion, and formal References. Automatically saves the report into ChromaDB episodic memory.
                    </p>
                    <div style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: '#34d399' }}>
                      Output: Final markdown report delivered to frontend via SSE stream and REST export.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: KEY ARCHITECTURE DECISIONS */}
          {activeTab === 'decisions' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{
                background: '#111622',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <div style={{ fontWeight: 800, color: 'var(--color-accent)', fontSize: '0.9rem', marginBottom: '0.35rem' }}>
                  1. Why LangGraph instead of linear chains or autogen?
                </div>
                <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                  LangGraph allows cyclic state machines with conditional routing (<code>should_continue</code>). Linear chains cannot loop back to gather more data when fact-checking fails. LangGraph provides deterministic state reduction, checkpointing, and strict revision limits.
                </p>
              </div>

              <div style={{
                background: '#111622',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <div style={{ fontWeight: 800, color: 'var(--color-accent)', fontSize: '0.9rem', marginBottom: '0.35rem' }}>
                  2. How do you prevent infinite loops in the feedback cycle?
                </div>
                <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                  The shared state tracks <code>revision_count</code>. The conditional edge checks <code>if revision_count &lt; MAX_REVISIONS (2)</code>. If the limit is reached, it forces progression to the Writer while appending a quality disclaimer. This guarantees execution terminates.
                </p>
              </div>

              <div style={{
                background: '#111622',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <div style={{ fontWeight: 800, color: 'var(--color-accent)', fontSize: '0.9rem', marginBottom: '0.35rem' }}>
                  3. Why Django REST Framework over FastAPI?
                </div>
                <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                  Django REST Framework provides production-ready Token Authentication, ORM database migrations, admin panel, and built-in format negotiation (exporting directly to <code>.md</code>, <code>.html</code>, <code>.json</code>, or <code>.bib</code>). Django handles Server-Sent Events (SSE) seamlessly via <code>StreamingHttpResponse</code>.
                </p>
              </div>

              <div style={{
                background: '#111622',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <div style={{ fontWeight: 800, color: 'var(--color-accent)', fontSize: '0.9rem', marginBottom: '0.35rem' }}>
                  4. What is the Model Context Protocol (FastMCP) integration?
                </div>
                <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                  Anthropic's open MCP standard connects external tools to LLMs. We wrote <code>mcp_server.py</code> using FastMCP. A developer in Claude Desktop or Cursor can type: <em>&ldquo;Run MARO research on solid-state battery breakthroughs&rdquo;</em>, and Claude invokes our backend tools natively.
                </p>
              </div>
            </div>
          )}

          {/* TAB 4: INTERVIEW Q&A */}
          {activeTab === 'qa' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{
                background: '#101524',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <div style={{ fontWeight: 700, color: '#ffffff', fontSize: '0.88rem', marginBottom: '0.3rem' }}>
                  Q: &ldquo;What happens if Tavily search API runs out of credits or is down?&rdquo;
                </div>
                <p style={{ margin: 0, color: '#34d399', fontSize: '0.82rem' }}>
                  <strong>A:</strong> &ldquo;We built an intelligent fallback pipeline: if Tavily fails or has no API key, the Researcher automatically falls back to DuckDuckGo search (<code>duckduckgo_search</code>), ensuring 100% uptime with zero external dependencies.&rdquo;
                </p>
              </div>

              <div style={{
                background: '#101524',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <div style={{ fontWeight: 700, color: '#ffffff', fontSize: '0.88rem', marginBottom: '0.3rem' }}>
                  Q: &ldquo;How does ChromaDB RAG fit into this?&rdquo;
                </div>
                <p style={{ margin: 0, color: '#34d399', fontSize: '0.82rem' }}>
                  <strong>A:</strong> &ldquo;ChromaDB serves two purposes: 1) Ingesting uploaded PDF research papers to query local context alongside live web search; 2) Storing every completed research session into an episodic memory collection, allowing subsequent queries to build upon past research.&rdquo;
                </p>
              </div>

              <div style={{
                background: '#101524',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <div style={{ fontWeight: 700, color: '#ffffff', fontSize: '0.88rem', marginBottom: '0.3rem' }}>
                  Q: &ldquo;How do you test a system that uses non-deterministic LLMs?&rdquo;
                </div>
                <p style={{ margin: 0, color: '#34d399', fontSize: '0.82rem' }}>
                  <strong>A:</strong> &ldquo;We authored 62 pytest unit and integration tests across auth, job queues, streaming endpoints, and state transitions using mocked providers and deterministic fixtures. All 62 tests execute in under 35 seconds via <code>python verify_all.py</code>.&rdquo;
                </p>
              </div>

              <div style={{
                background: '#101524',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <div style={{ fontWeight: 700, color: '#ffffff', fontSize: '0.88rem', marginBottom: '0.3rem' }}>
                  Q: &ldquo;What would you improve next?&rdquo;
                </div>
                <p style={{ margin: 0, color: '#34d399', fontSize: '0.82rem' }}>
                  <strong>A:</strong> &ldquo;I would add Human-in-the-Loop approval gates using LangGraph's <code>interrupt()</code> method so human researchers can edit search queries before synthesis, and distribute nodes across Celery/Redis workers for horizontal scalability.&rdquo;
                </p>
              </div>
            </div>
          )}

          {/* TAB 5: LIVE DEMO SCRIPT */}
          {activeTab === 'demo' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{
                background: 'rgba(0, 245, 243, 0.04)',
                border: '1px solid rgba(0, 245, 243, 0.25)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <div style={{ fontWeight: 800, color: 'var(--color-accent)', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                  🎯 5-MINUTE INTERVIEW DEMO PLAYBOOK
                </div>
                <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  Follow these 5 simple steps when screen-sharing during an interview:
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ background: '#111622', padding: '0.85rem 1rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <span style={{ color: 'var(--color-accent)', fontWeight: 800, marginRight: '0.5rem' }}>Step 1:</span>
                  <strong>Show System Verification:</strong> Open terminal and run <code>python verify_all.py</code>. Point out that all 62 automated tests pass with 100% success.
                </div>

                <div style={{ background: '#111622', padding: '0.85rem 1rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <span style={{ color: 'var(--color-accent)', fontWeight: 800, marginRight: '0.5rem' }}>Step 2:</span>
                  <strong>Show the 3D Neural DAG:</strong> Rotate the 3D orbit core on screen. Click <em>&ldquo;EXPLODED DAG VIEW&rdquo;</em> to reveal the 4 node telemetry cards.
                </div>

                <div style={{ background: '#111622', padding: '0.85rem 1rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <span style={{ color: 'var(--color-accent)', fontWeight: 800, marginRight: '0.5rem' }}>Step 3:</span>
                  <strong>Launch Research:</strong> Click one of the quick sample topics (e.g. <em>&ldquo;How do Multi-Agent architectures prevent hallucinations in RAG systems?&rdquo;</em>) and click <strong>Initiate Autonomous Research</strong>.
                </div>

                <div style={{ background: '#111622', padding: '0.85rem 1rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <span style={{ color: 'var(--color-accent)', fontWeight: 800, marginRight: '0.5rem' }}>Step 4:</span>
                  <strong>Highlight Live SSE Streaming:</strong> Show the terminal logs updating in real-time as Researcher decomposes queries, Analyst synthesizes themes, and Fact-Checker audits claims.
                </div>

                <div style={{ background: '#111622', padding: '0.85rem 1rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <span style={{ color: 'var(--color-accent)', fontWeight: 800, marginRight: '0.5rem' }}>Step 5:</span>
                  <strong>Show Verified Report & Citations:</strong> Point out inline references <code>[1]</code>, switch to the <em>&ldquo;Evidence & Sources&rdquo;</em> tab to show domain badges, and click <strong>Export</strong> to download Markdown / BibTeX.
                </div>
              </div>
            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '0.85rem 1.75rem',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          background: 'rgba(255, 255, 255, 0.02)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            PRESS ESC OR CLICK CLOSE TO RETURN TO WORKSPACE
          </span>
          <button
            onClick={onClose}
            className="btn btn-primary btn-sm"
            style={{ padding: '0.4rem 1.25rem' }}
          >
            Got It, Back to Demo
          </button>
        </div>
      </div>
    </div>
  );
}
