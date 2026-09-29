"""Small in-process trace model for reasoning-stage latency and outcomes."""

import time
from typing import Any, Dict, List, Optional


class Span:
    def __init__(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.metadata = metadata or {}
        self.start_time = 0.0
        self.end_time = 0.0
        self.duration_ms = 0.0
        self.error: Optional[str] = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        if exc_val:
            self.error = str(exc_val)
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "error": self.error,
        }


class TraceContext:
    def __init__(self, query: str):
        self.query = query
        self.spans: List[Span] = []
        self.start_time = time.perf_counter()
        self.end_time: Optional[float] = None
        self.total_duration_ms = 0.0
        self.metadata: Dict[str, Any] = {}

    def span(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Span:
        span = Span(name, metadata)
        self.spans.append(span)
        return span

    def finish(self) -> Dict[str, Any]:
        self.end_time = time.perf_counter()
        self.total_duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "total_duration_ms": self.total_duration_ms,
            "spans": [span.to_dict() for span in self.spans],
            "metadata": self.metadata,
        }
