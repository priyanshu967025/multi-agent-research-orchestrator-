import React, { useState, useEffect, useCallback } from 'react';
import { 
  Database, 
  UploadCloud, 
  Search, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw
} from 'lucide-react';
import { api } from '../api';

export default function RAGHubView({ user, onOpenAuth }) {
  const [stats, setStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCollection, setSelectedCollection] = useState('research_docs');
  const [topK, setTopK] = useState(4);
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const loadStats = useCallback(async () => {
    try {
      const data = await api.getRAGStats();
      setStats(data);
    } catch (e) {
      console.error('Failed to load RAG stats:', e);
    }
  }, []);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;

    if (!user) {
      onOpenAuth();
      return;
    }

    setUploading(true);
    setUploadResult(null);

    try {
      const res = await api.uploadDocuments(files);
      setUploadResult({ success: true, ...res });
      loadStats();
    } catch (err) {
      setUploadResult({ success: false, error: err.message });
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const res = await api.searchRAG(searchQuery, selectedCollection, topK);
      setSearchResults(res);
    } catch (err) {
      alert(`Search failed: ${err.message}`);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '1.75rem' }}>
        <h2 style={{ fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Database size={20} color="#34d399" />
          <span>RAG Knowledge Base Hub</span>
        </h2>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-dim)' }}>
          Ingest research papers, view ChromaDB vector collections, and inspect semantic similarity retrieval with dense embeddings.
        </p>
      </div>

      {/* Vector Store Overview Metrics */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1.25rem',
        marginBottom: '2rem',
      }}>
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.35rem' }}>
            Uploaded Research Docs
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-display)' }}>
            {stats?.collections?.research_docs || 0} <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)', fontWeight: 500 }}>chunks</span>
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Targeted collection: <code style={{ color: '#818cf8' }}>research_docs</code>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.35rem' }}>
            Past Research Memory
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#c084fc', fontFamily: 'var(--font-display)' }}>
            {stats?.collections?.past_research || 0} <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)', fontWeight: 500 }}>chunks</span>
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Self-reinforcing past agent session memory
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.35rem' }}>
            Embedding Engine
          </div>
          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#ffffff', marginTop: '0.4rem', fontFamily: 'var(--font-mono)' }}>
            all-MiniLM-L6-v2
          </div>
          <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.45rem' }}>
            Chunk Size: {stats?.chunk_size || 1000} | Overlap: {stats?.chunk_overlap || 200}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.75rem', alignItems: 'start' }}>
        {/* PDF Ingestion Area */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.05rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <UploadCloud size={17} color="#818cf8" />
            <span>PDF Ingestion Sandbox</span>
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
            Upload research papers, arXiv preprints, or technical briefs (max 10MB each) to index into the RAG vector store.
          </p>

          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragOver ? '#818cf8' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-lg)',
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              background: dragOver ? 'rgba(99, 102, 241, 0.1)' : 'rgba(14, 19, 31, 0.6)',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
              marginBottom: '1rem',
            }}
            onClick={() => document.getElementById('pdf-file-input').click()}
          >
            <input
              id="pdf-file-input"
              type="file"
              accept=".pdf"
              multiple
              style={{ display: 'none' }}
              onChange={(e) => handleFileUpload(e.target.files)}
            />
            <UploadCloud size={36} color={dragOver ? '#818cf8' : 'var(--text-dim)'} style={{ margin: '0 auto 0.75rem' }} />
            <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#ffffff', marginBottom: '0.25rem' }}>
              Drag & Drop PDF papers here, or <span style={{ color: '#818cf8', textDecoration: 'underline' }}>browse</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
              Supports academic PDFs, whitepapers & documentation
            </div>
          </div>

          {uploading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#818cf8', fontSize: '0.85rem' }}>
              <RefreshCw size={15} className="spinning-icon" />
              <span>Splitting into embeddings & storing in ChromaDB...</span>
            </div>
          )}

          {uploadResult && (
            <div style={{
              marginTop: '1rem',
              padding: '0.85rem 1rem',
              borderRadius: 'var(--radius-md)',
              background: uploadResult.success ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
              border: `1px solid ${uploadResult.success ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
              fontSize: '0.82rem',
              color: uploadResult.success ? '#34d399' : '#f87171',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              {uploadResult.success ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
              <span>
                {uploadResult.success 
                  ? `Successfully ingested ${uploadResult.chunks_added} chunks across ${uploadResult.files_processed?.length || 0} document(s).` 
                  : `Ingestion failed: ${uploadResult.error}`}
              </span>
            </div>
          )}
        </div>

        {/* Semantic Similarity Search Sandbox */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.05rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <Search size={17} color="#c084fc" />
            <span>Semantic Vector Search Sandbox</span>
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
            Query ChromaDB embeddings directly with cosine distance scoring to inspect retrieved context.
          </p>

          <form onSubmit={handleSearch} style={{ marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter query (e.g. 'retrieval accuracy in multihop RAG')..."
                className="input-control"
                style={{ flex: 1, fontSize: '0.88rem' }}
              />
              <button type="submit" className="btn btn-primary" disabled={searching || !searchQuery.trim()}>
                {searching ? <RefreshCw size={14} className="spinning-icon" /> : <Search size={14} />}
                <span>Query</span>
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span>Collection:</span>
                <select
                  value={selectedCollection}
                  onChange={(e) => setSelectedCollection(e.target.value)}
                  className="select-control"
                  style={{ padding: '0.2rem 0.5rem', fontSize: '0.78rem', width: '140px' }}
                >
                  <option value="research_docs">research_docs</option>
                  <option value="past_research">past_research</option>
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span>Top K: {topK}</span>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={topK}
                  onChange={(e) => setTopK(parseInt(e.target.value))}
                  style={{ width: '80px', accentColor: '#a855f7' }}
                />
              </div>
            </div>
          </form>

          {/* Retrieved Similarity Chunks */}
          {searchResults && (
            <div style={{ maxHeight: '340px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ fontSize: '0.76rem', color: 'var(--text-dim)', fontWeight: 600 }}>
                Retrieved {searchResults.results?.length || 0} chunks for "{searchResults.query}":
              </div>

              {searchResults.results?.map((res, index) => (
                <div
                  key={index}
                  style={{
                    background: 'rgba(14, 19, 31, 0.8)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '0.85rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                    <span className="badge badge-purple" style={{ fontSize: '0.68rem' }}>
                      Chunk #{index + 1}
                    </span>
                    <span style={{ fontSize: '0.72rem', color: '#34d399', fontFamily: 'var(--font-mono)' }}>
                      Distance Score: {res.score}
                    </span>
                  </div>
                  <div style={{
                    fontSize: '0.8rem',
                    color: 'var(--text-main)',
                    lineHeight: 1.45,
                    fontFamily: 'var(--font-mono)',
                    maxHeight: '100px',
                    overflowY: 'auto'
                  }}>
                    {res.content}
                  </div>
                </div>
              ))}

              {searchResults.results?.length === 0 && (
                <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                  No matching chunks found in collection '{selectedCollection}'.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
