"""
Pytest Configuration & Unit Test Network Isolation (Phase E3)

Ensures that unit tests are 100% offline, deterministic, and execute in seconds.
Blocks accidental live network/socket connections to paid APIs (OpenAI, Gemini, Pinecone, Supabase).
"""

import sys
import os
import socket
import pytest

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


@pytest.fixture(autouse=True)
def block_external_sockets(monkeypatch):
    """
    Prevents unit tests from opening outbound WAN sockets.
    Permits loopback/local test client communication.
    """
    real_connect = socket.socket.connect

    def guarded_connect(self, address):
        host = address[0] if isinstance(address, tuple) and len(address) > 0 else str(address)
        if host in ("127.0.0.1", "localhost", "::1") or str(host).startswith("/"):
            return real_connect(self, address)
        raise RuntimeError(
            f"[E3 Network Violation] Outbound socket connection blocked to {address}. "
            "Unit tests must run offline with MockModelClient / mocks."
        )

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
