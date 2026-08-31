"""Small, testable HTTP client used by the Streamlit workspace."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Generator

import requests


@dataclass
class ApiError(Exception):
    message: str
    status_code: int | None = None


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _headers(self, token: str = "") -> dict[str, str]:
        return {"Authorization": f"Token {token}"} if token else {}

    def _error_from_response(self, response: requests.Response) -> ApiError:
        try:
            body = response.json()
        except ValueError:
            body = {}
        if isinstance(body, dict):
            message = body.get("error") or body.get("detail")
            if not message:
                for value in body.values():
                    if isinstance(value, list) and value:
                        message = str(value[0])
                        break
            if message:
                return ApiError(str(message), response.status_code)
        return ApiError("The API request could not be completed.", response.status_code)

    def _request(
        self,
        method: str,
        path: str,
        *,
        token: str = "",
        timeout: int = 15,
        **kwargs: Any,
    ) -> Any:
        try:
            response = self.session.request(
                method,
                f"{self.base_url}{path}",
                headers=self._headers(token),
                timeout=timeout,
                **kwargs,
            )
        except requests.RequestException as error:
            raise ApiError("Could not connect to the API. Check that the backend is running.") from error
        if not response.ok:
            raise self._error_from_response(response)
        if response.status_code == 204:
            return None
        return response.json()

    # ── Health ───────────────────────────────────────────────────────

    def health(self) -> dict:
        return self._request("GET", "/health/", timeout=5)

    # ── Auth ─────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> dict:
        return self._request("POST", "/auth/login/", json={"username": username, "password": password})

    def register(self, username: str, email: str, password: str) -> dict:
        return self._request(
            "POST", "/auth/register/", json={"username": username, "email": email, "password": password}
        )

    def logout(self, token: str) -> None:
        self._request("POST", "/auth/logout/", token=token)

    # ── Research Jobs ────────────────────────────────────────────────

    def create_job(self, token: str, topic: str) -> dict:
        return self._request("POST", "/research/jobs/", token=token, json={"topic": topic}, timeout=30)

    def get_job(self, token: str, job_id: int) -> dict:
        return self._request("GET", f"/research/sessions/{job_id}/", token=token)

    def list_jobs(self, token: str, page: int = 1, page_size: int = 20) -> dict:
        return self._request("GET", "/research/jobs/", token=token, params={"page": page, "page_size": page_size})

    def delete_job(self, token: str, job_id: int) -> None:
        self._request("DELETE", f"/research/sessions/{job_id}/", token=token)

    def upload_documents(self, token: str, uploaded_files: list[Any]) -> dict:
        files = [
            ("files", (uploaded.name, uploaded.getvalue(), "application/pdf"))
            for uploaded in uploaded_files
        ]
        return self._request("POST", "/research/documents/", token=token, files=files, timeout=120)

    # ── Streaming ────────────────────────────────────────────────────

    def stream_research(self, token: str, topic: str) -> Generator[dict[str, Any], None, None]:
        """Stream research progress as SSE events. Yields dicts with 'stage', 'message', etc."""
        try:
            response = self.session.post(
                f"{self.base_url}/research/stream/",
                json={"topic": topic},
                headers=self._headers(token),
                timeout=600,
                stream=True,
            )
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        yield json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
        except requests.RequestException as error:
            raise ApiError("Streaming failed. Check that the backend is running.") from error

    # ── Tags ─────────────────────────────────────────────────────────

    def get_tags(self, token: str, session_id: int) -> list[dict]:
        return self._request("GET", f"/research/{session_id}/tags/", token=token)

    def add_tag(self, token: str, session_id: int, name: str) -> dict:
        return self._request("POST", f"/research/{session_id}/tags/", token=token, json={"name": name})

    # ── Benchmark ────────────────────────────────────────────────────

    def run_benchmark(self, token: str, topic: str) -> dict:
        return self._request("POST", "/research/benchmark/", token=token, json={"topic": topic}, timeout=900)

    def benchmark_history(self, token: str) -> list[dict]:
        return self._request("GET", "/benchmark/history/", token=token)
