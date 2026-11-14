"""Execução em hardware real, com um serviço falso no lugar do IBM Quantum."""


import pytest
from websockets.asyncio.client import connect

from qlp_engine import hardware

from .test_server import TOKEN, Client, with_server

BELL = "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n"


class FakeData:
    def join_data(self):
        return self

    def get_counts(self):
        return {"11": 480, "00": 500, "01": 20}


class FakeJob:
    def __init__(self, state="DONE"):
        self.state = state

    def job_id(self):
        return "job-123"

    def status(self):
        return self.state

    def result(self):
        return [type("Pub", (), {"data": FakeData()})()]


class FakeService:
    last = {}

    def __init__(self, channel, token, instance=None):
        if token != "chave-certa":
            raise ValueError("invalid token")
        FakeService.last = {"channel": channel, "instance": instance}

    def least_busy(self, operational, simulator, min_num_qubits):
        from qiskit.providers.fake_provider import GenericBackendV2

        assert operational and not simulator
        backend = GenericBackendV2(num_qubits=max(5, min_num_qubits))
        return backend

    def job(self, job_id):
        return FakeJob()


class FakeSampler:
    submitted = None

    def __init__(self, mode):
        self.mode = mode

    def run(self, pubs, shots):
        FakeSampler.submitted = (pubs, shots)
        return FakeJob("QUEUED")


@pytest.fixture
def fake_ibm(monkeypatch):
    import qiskit_ibm_runtime

    monkeypatch.setattr(qiskit_ibm_runtime, "QiskitRuntimeService", FakeService)
    monkeypatch.setattr(qiskit_ibm_runtime, "SamplerV2", FakeSampler)


def test_submit_transpiles_adds_measurements_and_returns_the_job(fake_ibm):
    from qiskit import QuantumCircuit, qasm3

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    result = hardware.submit(qasm3.dumps(qc), "chave-certa", shots=99_999)
    assert result["job_id"] == "job-123" and result["backend"]
    (isa,), shots = FakeSampler.submitted
    assert shots == hardware.MAX_SHOTS
    assert any(i.operation.name == "measure" for i in isa.data)  # medição acrescentada


def test_bad_token_and_status(fake_ibm):
    with pytest.raises(hardware.HardwareError):
        hardware.status("job-123", "errada")
    with pytest.raises(hardware.HardwareError):
        hardware.submit("OPENQASM 3.0;", "")
    done = hardware.status("job-123", "chave-certa", instance="crn:minha")
    assert done["status"] == "DONE" and done["counts"]["00"] == 500
    assert FakeService.last["instance"] == "crn:minha"


def test_server_flow_and_public_mode(fake_ibm, library):
    async def test(url, _):
        async with connect(f"{url}/?token={TOKEN}") as websocket:
            client = Client(websocket)
            assert (await client.call(type="hardware.available"))["available"] is True
            submitted = await client.call(type="hardware.submit", code=BELL, token="chave-certa", shots=100)
            assert submitted["ok"] and submitted["job_id"] == "job-123", submitted
            refused = await client.call(type="hardware.submit", code=BELL, token="errada")
            assert refused["ok"] is False and refused["error"]["kind"] == "hardware"
            status = await client.call(type="hardware.status", job_id="job-123", token="chave-certa")
            assert status["status"] == "DONE"

    with_server(test, library=library)

    from .test_server import with_public_server

    async def public(url):
        async with connect(url, origin="https://quantum.example") as websocket:
            client = Client(websocket)
            assert (await client.call(type="hardware.available"))["available"] is False
            refused = await client.call(type="hardware.submit", code=BELL, token="chave-certa")
            assert refused["ok"] is False and "own computer" in refused["error"]["message"]

    with_public_server(public, library)
