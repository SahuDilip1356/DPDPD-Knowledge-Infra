"""Shared test isolation for the deployable backend."""

import socket

import pytest


@pytest.fixture(autouse=True)
def block_external_sockets(monkeypatch):
    """Prevent unit tests from accidentally calling paid or production services."""
    real_connect = socket.socket.connect

    def guarded_connect(self, address):
        host = address[0] if isinstance(address, tuple) and address else str(address)
        if host in ("127.0.0.1", "localhost", "::1") or str(host).startswith("/"):
            return real_connect(self, address)
        raise RuntimeError(
            f"Outbound socket connection blocked during tests: {address}"
        )

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
