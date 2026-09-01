import React, { Component } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('App ErrorBoundary caught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          background: '#000000',
          color: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem',
          fontFamily: 'system-ui, sans-serif'
        }}>
          <h1 style={{ fontSize: '1.8rem', color: '#00F5F3', marginBottom: '1rem' }}>
            Multi-Agent Research Orchestrator
          </h1>
          <p style={{ color: '#888888', marginBottom: '1.5rem', maxWidth: '500px', textAlign: 'center' }}>
            A temporary component error occurred. Click below to reload the workspace.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: '#00F5F3',
              color: '#000000',
              border: 'none',
              padding: '0.75rem 1.5rem',
              fontWeight: 700,
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Reload Application
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>,
)
