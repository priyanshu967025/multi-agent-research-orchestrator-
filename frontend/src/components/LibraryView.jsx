import React, { useState, useEffect, useCallback } from 'react';
import { 
  BookOpen, 
  Search, 
  Trash2, 
  Eye, 
  Download, 
  Layers, 
  RefreshCw, 
  Calendar,
  X
} from 'lucide-react';
import { marked } from 'marked';
import { api } from '../api';

export default function LibraryView({ user, onOpenAuth }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedJob, setSelectedJob] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const loadJobs = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listJobs(1, 50);
      setJobs(data.jobs || []);
    } catch (e) {
      console.error('Failed to load jobs:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) {
      loadJobs();
    } else {
      setLoading(false);
    }
  }, [user, loadJobs]);

  const handleOpenJob = async (jobId) => {
    try {
      const job = await api.getJob(jobId);
      setSelectedJob(job);
      setModalOpen(true);
    } catch (e) {
      alert(`Failed to load job details: ${e.message}`);
    }
  };

  const handleDeleteJob = async (jobId, e) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this research run?')) return;
    try {
      await api.deleteJob(jobId);
      setJobs((prev) => prev.filter((j) => j.id !== jobId));
      if (selectedJob?.id === jobId) {
        setModalOpen(false);
        setSelectedJob(null);
      }
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  if (!user) {
    return (
      <div className="glass-panel" style={{ padding: '3rem 2rem', textAlign: 'center' }}>
        <BookOpen size={40} color="#818cf8" style={{ marginBottom: '1rem' }} />
        <h2 style={{ fontSize: '1.4rem', marginBottom: '0.5rem' }}>Your Private Research Library</h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: '480px', margin: '0 auto 1.5rem', fontSize: '0.9rem' }}>
          Sign in to automatically store all your multi-agent research sessions, access evidence citations, and download reports anytime.
        </p>
        <button onClick={onOpenAuth} className="btn btn-primary">
          Sign In / Create Account
        </button>
      </div>
    );
  }

  const filteredJobs = jobs.filter((job) => 
    job.topic.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      {/* Header & Search */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BookOpen size={20} color="#818cf8" />
            <span>Research Library</span>
          </h2>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-dim)' }}>
            All saved research sessions with verified evidence and durable markdown reports
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={15} color="var(--text-dim)" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search past research..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-control"
              style={{ paddingLeft: '2.2rem', fontSize: '0.85rem' }}
            />
          </div>
          <button onClick={loadJobs} className="btn btn-secondary btn-sm" title="Refresh Library">
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Grid of Saved Research Cards */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <RefreshCw size={24} className="spinning-icon" style={{ marginBottom: '0.5rem' }} />
          <div>Loading your research sessions...</div>
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="glass-panel" style={{ padding: '3rem 2rem', textAlign: 'center' }}>
          <BookOpen size={36} color="var(--text-dim)" style={{ marginBottom: '0.75rem' }} />
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.4rem', color: '#cbd5e1' }}>No research runs found</h3>
          <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>
            {searchTerm ? 'No results matched your search query.' : 'Run your first research inquiry from the Research Studio to save reports here.'}
          </p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
          gap: '1.25rem',
        }}>
          {filteredJobs.map((job) => {
            const dateStr = new Date(job.created_at).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            });

            return (
              <div
                key={job.id}
                onClick={() => handleOpenJob(job.id)}
                className="glass-panel"
                style={{
                  padding: '1.25rem',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  transition: 'all 0.2s ease',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
                    <span className={`badge ${job.status === 'completed' ? 'badge-success' : 'badge-error'}`} style={{ fontSize: '0.7rem' }}>
                      {job.status.toUpperCase()}
                    </span>
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <Calendar size={12} /> {dateStr}
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.02rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.75rem', lineHeight: 1.35 }}>
                    {job.topic}
                  </h3>
                </div>

                <div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    paddingTop: '0.75rem',
                    borderTop: '1px solid var(--border-subtle)',
                    fontSize: '0.78rem',
                    color: 'var(--text-muted)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <Layers size={13} color="#818cf8" /> {job.web_sources_count} sources
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                        <RefreshCw size={13} color="#fbbf24" /> {job.revision_count} revs
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <button
                        onClick={(e) => handleDeleteJob(job.id, e)}
                        className="btn btn-ghost btn-sm"
                        style={{ padding: '0.3rem 0.5rem', color: '#f87171' }}
                        title="Delete research run"
                      >
                        <Trash2 size={14} />
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        style={{ padding: '0.3rem 0.6rem' }}
                      >
                        <Eye size={13} />
                        <span>Inspect</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Full Report Inspection Modal */}
      {modalOpen && selectedJob && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          backdropFilter: 'blur(8px)',
          zIndex: 100,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1.5rem',
        }}>
          <div className="glass-panel" style={{
            maxWidth: '960px',
            width: '100%',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            background: '#0e131f',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            overflow: 'hidden',
          }}>
            {/* Modal Header */}
            <div style={{
              padding: '1.25rem 1.5rem',
              borderBottom: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'rgba(14, 19, 31, 0.95)',
            }}>
              <div>
                <span className="badge badge-purple" style={{ fontSize: '0.72rem', marginBottom: '0.3rem' }}>
                  RESEARCH RUN #{selectedJob.id}
                </span>
                <h3 style={{ fontSize: '1.15rem', color: '#ffffff' }}>{selectedJob.topic}</h3>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <a
                  href={api.getExportUrl(selectedJob.id, 'markdown')}
                  download={`research-${selectedJob.id}.md`}
                  className="btn btn-secondary btn-sm"
                >
                  <Download size={14} />
                  <span>Download MD</span>
                </a>
                <button
                  onClick={() => setModalOpen(false)}
                  className="btn btn-ghost btn-sm"
                  style={{ padding: '0.4rem' }}
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Modal Scrollable Content */}
            <div style={{ padding: '1.75rem', overflowY: 'auto', flex: 1 }}>
              <div 
                className="markdown-body"
                dangerouslySetInnerHTML={{ __html: marked.parse(selectedJob.final_report || 'No report available.') }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
