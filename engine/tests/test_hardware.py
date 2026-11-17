"""Execution on real hardware, with a fake service in place of IBM Quantum."""


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
    qiskit_ibm_runtime = pytest.importorskip("qiskit_ibm_runtime")

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
    assert any(i.operation.name == "measure" for i in isa.data)  # measurement added


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


# -- one login per burst of polls, and timeouts ---------------------------------------------------------


@pytest.fixture
def counted_login(monkeypatch):
    qiskit_ibm_runtime = pytest.importorskip("qiskit_ibm_runtime")
    logins = []

    class CountingService(FakeService):
        def __init__(self, channel, token, instance=None):
            logins.append(token)
            super().__init__(channel, token, instance)

    monkeypatch.setattr(qiskit_ibm_runtime, "QiskitRuntimeService", CountingService)
    hardware.clear_cache()
    yield logins
    hardware.clear_cache()


def test_status_polls_reuse_the_logged_in_service(counted_login):
    for _ in range(4):
        assert hardware.status("job-123", "chave-certa")["status"] == "DONE"
    assert len(counted_login) == 1
    hardware.status("job-123", "chave-certa", instance="crn:other")  # another account: a new login
    assert len(counted_login) == 2


def test_cached_service_expires(counted_login, monkeypatch):
    hardware.status("job-123", "chave-certa")
    monkeypatch.setattr(hardware, "SERVICE_TTL_S", 0.0)
    hardware.status("job-123", "chave-certa")
    assert len(counted_login) == 2


def test_a_bad_key_is_not_cached(counted_login):
    for _ in range(2):
        with pytest.raises(hardware.HardwareError):
            hardware.status("job-123", "errada")
    assert len(counted_login) == 2


def test_a_hung_login_gives_a_clear_message(monkeypatch):
    import time

    qiskit_ibm_runtime = pytest.importorskip("qiskit_ibm_runtime")

    class Hung:
        def __init__(self, *args, **kwargs):
            time.sleep(5)

    monkeypatch.setattr(qiskit_ibm_runtime, "QiskitRuntimeService", Hung)
    monkeypatch.setattr(hardware, "LOGIN_TIMEOUT_S", 0.2)
    hardware.clear_cache()
    start = time.monotonic()
    with pytest.raises(hardware.HardwareError, match="did not answer within"):
        hardware.status("job-123", "chave-certa")
    assert time.monotonic() - start < 2


def test_a_hung_status_call_gives_a_clear_message_and_drops_the_cached_login(counted_login, monkeypatch):
    import time

    class HungJob(FakeJob):
        def status(self):
            time.sleep(5)

    monkeypatch.setattr(FakeService, "job", lambda self, job_id: HungJob())
    monkeypatch.setattr(hardware, "CALL_TIMEOUT_S", 0.2)
    with pytest.raises(hardware.HardwareError, match="reading the job status"):
        hardware.status("job-123", "chave-certa")
    assert not hardware._service_cache
