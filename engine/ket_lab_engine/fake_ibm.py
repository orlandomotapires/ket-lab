"""Simulated IBM Quantum service, for tests only (variable KET_LAB_FAKE_IBM=1).

Accepts the key "test-key", uses a generic 5-qubit backend and returns a job
that is already finished with fixed counts. It makes no network calls.
"""

from __future__ import annotations

COUNTS = {"00": 498, "11": 470, "01": 31, "10": 25}


class _Data:
    def join_data(self):
        return self

    def get_counts(self):
        return dict(COUNTS)


class _Job:
    def job_id(self):
        return "fake-job-1"

    def status(self):
        return "DONE"

    def result(self):
        return [type("Pub", (), {"data": _Data()})()]


class Service:
    def __init__(self, channel, token, instance=None):
        if token != "test-key":
            raise ValueError("invalid API key")

    def least_busy(self, operational, simulator, min_num_qubits):
        from qiskit.providers.fake_provider import GenericBackendV2

        return GenericBackendV2(num_qubits=max(5, min_num_qubits))

    def job(self, job_id):
        return _Job()


class Sampler:
    def __init__(self, mode):
        self.mode = mode

    def run(self, pubs, shots):
        return _Job()
