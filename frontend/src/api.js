/**
 * Multi-Agent Research Orchestrator — Frontend API Client
 * Seamlessly handles Token Auth, REST Endpoints, and Live SSE Streaming.
 */

const API_BASE = (import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace(/\/$/, '') : '') + '/api';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('maro_auth_token') || '';
  }

  setToken(token) {
    this.token = token || '';
    if (token) {
      localStorage.setItem('maro_auth_token', token);
    } else {
      localStorage.removeItem('maro_auth_token');
    }
  }

  getHeaders(isMultipart = false) {
    const headers = {};
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }
    if (this.token) {
      headers['Authorization'] = `Token ${this.token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const isMultipart = options.body instanceof FormData;
    const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(isMultipart),
        ...(options.headers || {}),
      },
    };

    try {
      const res = await fetch(url, config);
      
      if (res.status === 204) {
        return null;
      }

      const data = await res.json().catch(() => ({}));
      
      if (!res.ok) {
        const errorMsg = data.error || data.detail || (typeof data === 'object' ? JSON.stringify(data) : 'Request failed');
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  }

  // ── Auth ──────────────────────────────────────────────────────────

  async login(username, password) {
    const data = await this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    this.setToken(data.token);
    return data;
  }

  async register(username, email, password) {
    const data = await this.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
    this.setToken(data.token);
    return data;
  }

  async logout() {
    try {
      await this.request('/auth/logout/', { method: 'POST' });
    } catch {
      // Ignore token invalidation errors on logout
    } finally {
      this.setToken('');
    }
  }

  async getProfile() {
    return this.request('/auth/profile/');
  }

  // ── Platform & Stats ──────────────────────────────────────────────

  async getHealth() {
    return this.request('/health/');
  }

  async getPlatformStats() {
    return this.request('/stats/');
  }

  // ── Research Jobs ─────────────────────────────────────────────────

  async createJob(topic) {
    return this.request('/research/jobs/', {
      method: 'POST',
      body: JSON.stringify({ topic }),
    });
  }

  async listJobs(page = 1, pageSize = 20) {
    return this.request(`/research/jobs/?page=${page}&page_size=${pageSize}`);
  }

  async getJob(id) {
    return this.request(`/research/sessions/${id}/`);
  }

  async deleteJob(id) {
    return this.request(`/research/sessions/${id}/`, {
      method: 'DELETE',
    });
  }

  async addTag(sessionId, name) {
    return this.request(`/research/${sessionId}/tags/`, {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  async getTags(sessionId) {
    return this.request(`/research/${sessionId}/tags/`);
  }

  // ── Live SSE Streaming ────────────────────────────────────────────

  async streamResearch(topic, { onEvent, onError, onComplete }) {
    const url = `${API_BASE}/research/stream/`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${this.token}`,
      },
      body: JSON.stringify({ topic }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to initialize stream');
    }

    let completedSessionId = response.headers.get('X-Research-Session-Id');
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep partial line in buffer

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data:')) {
            const dataStr = trimmed.slice(5).trim();
            if (dataStr === '[DONE]') {
              if (onComplete) onComplete({ sessionId: completedSessionId });
              return;
            }
            try {
              const eventData = JSON.parse(dataStr);
              if (eventData.session_id) {
                completedSessionId = eventData.session_id;
              }
              if (onEvent) onEvent(eventData);
            } catch {
              console.warn('Could not parse SSE payload:', dataStr);
            }
          }
        }
      }
      if (onComplete) onComplete({ sessionId: completedSessionId });
    } catch (err) {
      if (onError) onError(err);
    }
  }

  // ── RAG & PDF Ingestion ───────────────────────────────────────────

  async uploadDocuments(files) {
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }
    return this.request('/research/documents/', {
      method: 'POST',
      body: formData,
    });
  }

  async getRAGStats() {
    return this.request('/rag/stats/');
  }

  async searchRAG(query, collection = 'research_docs', k = 5) {
    return this.request('/rag/search/', {
      method: 'POST',
      body: JSON.stringify({ query, collection, k }),
    });
  }

  // ── Benchmark ─────────────────────────────────────────────────────

  async runBenchmark(topic) {
    return this.request('/research/benchmark/', {
      method: 'POST',
      body: JSON.stringify({ topic }),
    });
  }

  async getBenchmarkHistory(limit = 20) {
    return this.request(`/benchmark/history/?limit=${limit}`);
  }

  // ── Export ────────────────────────────────────────────────────────

  getExportUrl(sessionId, format = 'markdown') {
    return `${API_BASE}/research/sessions/${sessionId}/export/?format=${format}`;
  }
}

export const api = new ApiClient();
