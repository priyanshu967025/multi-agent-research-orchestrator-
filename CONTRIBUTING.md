# Contributing to Multi-Agent Research Orchestrator

Thank you for your interest in contributing to MARO! We welcome contributions from the open-source community.

---

## 🛠️ Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/multi-agent-research-orchestrator.git
   cd multi-agent-research-orchestrator
   ```

2. **Set up Python Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Set up Frontend**:
   ```bash
   cd frontend
   npm install
   ```

4. **Run Backend Test Suites**:
   ```bash
   cd backend
   python -m pytest -v
   ```

---

## 📜 Pull Request Guidelines

1. Create a descriptive feature branch (`git checkout -b feature/new-agent-tool`).
2. Ensure all 62 test suites pass with 100% green rate.
3. Keep code modular and adhere to PEP 8 (Python) and ESLint/Oxlint (React).
4. Submit a clear PR description detailing what was changed and why.
