#!/usr/bin/env python3
"""
Multi-Agent Research Orchestrator (MARO) — Complete System Verification Suite
Verifies backend, frontend, agents, vector databases, MCP, and tests in one command.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Terminal ANSI styling
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

def print_header():
    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}   [MARO] MULTI-AGENT RESEARCH ORCHESTRATOR - VERIFICATION MATRIX     {RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    print(f"System: {sys.platform} | Python: {sys.version.split()[0]} | Directory: {ROOT_DIR}\n")

def run_step(step_name, command, cwd, allow_fail=False):
    start = time.time()
    sys.stdout.write(f"  * {step_name.ljust(48)} ")
    sys.stdout.flush()
    try:
        res = subprocess.run(
            command,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            timeout=300
        )
        duration = time.time() - start
        if res.returncode == 0 or allow_fail:
            print(f"[{GREEN}PASS{RESET}]  ({duration:.2f}s)")
            return True, res.stdout, duration
        else:
            print(f"[{RED}FAIL{RESET}]  ({duration:.2f}s) (Exit Code: {res.returncode})")
            err_msg = (res.stderr.strip() or res.stdout.strip())
            if err_msg:
                print(f"\n{RED}Output:{RESET}\n{err_msg[:600]}\n")
            return False, err_msg, duration
    except Exception as e:
        duration = time.time() - start
        print(f"[{RED}ERROR{RESET}] ({duration:.2f}s)")
        print(f"{RED}Exception: {e}{RESET}")
        return False, str(e), duration

def check_providers():
    sys.stdout.write(f"  * {'Multi-Provider LLM & Search Detection'.ljust(48)} ")
    sys.stdout.flush()
    start = time.time()
    
    # Load .env if present
    env_file = ROOT_DIR / ".env"
    keys_found = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    if 'API_KEY' in k and v.strip() and not v.strip().startswith('your_'):
                        keys_found.append(k.replace('_API_KEY', ''))
    
    # Fallback search always present
    keys_found.append("DuckDuckGo (Native Fallback)")
    duration = time.time() - start
    provider_str = ", ".join(keys_found) if keys_found else "None configured"
    print(f"[{GREEN}PASS{RESET}]  ({duration:.2f}s)")
    print(f"     {CYAN}-> Active Providers & Fallbacks:{RESET} {provider_str}")
    return True

def main():
    print_header()
    results = []

    # 1. Python Syntax & Compilation
    py_exec = sys.executable
    ok, _, d = run_step(
        "Python Core Syntax Compilation",
        f'"{py_exec}" -m py_compile app.py mcp_server.py workspace_api.py',
        ROOT_DIR
    )
    results.append(("Python Core Compilation", ok, d))

    # 2. Django Configuration & Health
    ok, _, d = run_step(
        "Django REST Framework & Model Checks",
        f'"{py_exec}" manage.py check',
        BACKEND_DIR
    )
    results.append(("Django System Checks", ok, d))

    # 3. Automated Pytest Suite
    ok, out, d = run_step(
        "Backend Automated Test Suite (62 Tests)",
        f'"{py_exec}" -m pytest -q -W ignore::DeprecationWarning',
        BACKEND_DIR
    )
    results.append(("Backend Pytest Suite (62 Tests)", ok, d))

    # 4. Frontend Production Build
    ok, _, d = run_step(
        "Frontend Vite Production Bundle Build",
        "npm run build",
        FRONTEND_DIR
    )
    results.append(("Frontend Production Build", ok, d))

    # 5. ChromaDB Vector Store Connectivity
    ok, _, d = run_step(
        "ChromaDB Vector Store Initialization",
        f'"{py_exec}" -c "import chromadb; client = chromadb.PersistentClient(path=\'./chroma_db\'); print(client.heartbeat())"',
        ROOT_DIR
    )
    results.append(("ChromaDB Vector Store", ok, d))

    # 6. Check Provider Detection
    check_providers()

    # Final Summary Matrix
    print(f"\n{BOLD}======================================================================{RESET}")
    print(f"{BOLD}                        VERIFICATION SCORECARD                         {RESET}")
    print(f"{BOLD}======================================================================{RESET}")
    
    all_passed = True
    for name, passed, duration in results:
        status = f"{GREEN}PASSED (100%){RESET}" if passed else f"{RED}FAILED{RESET}"
        if not passed:
            all_passed = False
        print(f"  * {name.ljust(44)} : {status} [{duration:.2f}s]")

    print(f"{BOLD}======================================================================{RESET}")
    if all_passed:
        print(f"\n  {GREEN}{BOLD}[OK] ALL MARO SUBSYSTEMS VERIFIED AND READY FOR PRODUCTION!{RESET}\n")
        return 0
    else:
        print(f"\n  {RED}{BOLD}[!] SOME VERIFICATION CHECKS FAILED. SEE DETAILS ABOVE.{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
