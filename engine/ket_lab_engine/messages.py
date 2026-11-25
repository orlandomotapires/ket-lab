"""Engine messages (in English, the platform's language)."""

from __future__ import annotations


def t(key: str, **params) -> str:
    return MESSAGES[key].format(**params)


def percent(value: float, decimals: int = 1) -> str:
    return f"{value * 100:.{decimals}f}%"


MESSAGES: dict[str, str] = {
    # --- static check ------------------------------------------------
    "guard.relative_import": "Relative imports are not allowed here.",
    "guard.forbidden_name": "`{name}` is not available in the lab.",
    "guard.dunder": "Access to internal attributes (`{name}`) is not allowed in the lab.",
    "guard.private": "`{name}` starts with an underscore, which marks it as internal to a library, so the lab does not allow it. Use the library's public functions instead.",
    "guard.files": "`{name}` reads or writes files, which the lab does not allow.",
    "guard.module": "The module `{name}` is not available in the lab. Available: {allowed}.",
    "guard.module_short": "The module `{name}` is not available in the lab.",
    # --- execution ------------------------------------------------------------
    "run.syntax": "Syntax error: {detail}",
    "run.memory": "The code tried to use too much memory. Reduce the size of the circuit or the data.",
    "run.recursion": "Infinite recursion detected.",
    "run.no_circuit": "No circuit found. Create one with `qc = QuantumCircuit(1)`.",
    "run.reduced": "This circuit is large ({steps} steps on {qubits} qubits), so amplitudes and probabilities are kept for {kept} evenly spaced steps and the last one. The Bloch spheres are shown for every step.",
    "run.shots_heavy": "Sampling the shots took longer than {seconds} s and was stopped. Measuring in the middle of a circuit (or using `reset`) means simulating the whole circuit once per shot, so try fewer shots or fewer qubits. If your code has a loop that never ends, fix that first.",
    "run.cancelled": "Execution stopped.",
    "export.unsupported": "This circuit cannot be exported to {format}: {detail}",
    "export.noise": "Noise channels (density matrix) do not exist in OpenQASM. Export the circuit without noise.",
    "run.timeout": "Execution took longer than {seconds} s and was stopped. Check for an infinite loop.",
    "run.crash": "The simulation engine stopped unexpectedly, probably out of memory. It has been restarted.",
    "run.engine_closed": "The engine has been shut down.",
    "run.engine_start": "The simulation engine did not start in time.",
    "run.exit": "The code tried to exit the program (`exit()`, `quit()` or `raise SystemExit`). Remove that line: the lab stops by itself when the code ends.",
    "run.internal": "Internal engine error: {detail}",
    "run.unknown_job": "Unknown job type: {kind}",
    # --- simulator -----------------------------------------------------------
    "sim.no_qubits": "The circuit has no qubits. Use, for example, `QuantumCircuit(1)`.",
    "sim.too_many_qubits": "The circuit has {count} qubits; the limit here is {limit}. Each extra qubit doubles the memory needed to simulate it.",
    "sim.too_many_instructions": "The circuit has {count} instructions; the limit is {limit}.",
    "sim.control_flow": "In-circuit control flow `{name}` is not supported yet. Use a regular Python loop to repeat gates.",
    "sim.unsupported": "The instruction `{name}` is not supported by the simulator.",
    "sim.expr_condition": "Conditions with classical expressions are not supported yet. Use `qc.if_test((classical_bit, 1))`.",
    "sim.bad_condition": "Unrecognized classical condition in `if_test`.",
    "sim.no_matrix": "Could not compute the matrix of gate `{name}` (symbolic parameters without a value?).",
    # --- validation -----------------------------------------------------------
    "val.unsupported": "Validation type `{kind}` is not implemented yet.",
    "val.forbidden_gate": "This mission does not allow {names}. Try to solve it with the gates from the lesson.",
    "val.required_gate": "The mission requires using {names} in the circuit.",
    "val.gate_count": "The mission allows exactly {expected} call(s) to `{name}`, and your circuit has {actual}.",
    "val.forbidden_pair": "In this mission no gate may act on qubits {a} and {b} at the same time: they are far apart. Connect them with measurements and corrections conditioned on classical bits.",
    "val.too_many_gates": "The mission allows at most {limit} gate(s); your circuit uses {count}.",
    "val.qubit_count": "The mission uses {expected} qubit(s), but your circuit has {actual}.",
    "val.state_ok": "Target state reached with a fidelity of {fidelity}.",
    "val.phase": "The measurement probabilities are right, but the relative phase is wrong. Check the gates that rotate about the Z axis (Z, S, T, Rz, P).",
    "val.state_wrong": "Not yet: the fidelity with the target state is {fidelity}.",
    "val.no_measurement": "The circuit has no measurement, so it produces no classical result. Measure the qubit into a classical bit.",
    "val.clbit_count": "The mission stores the result in {expected} classical bit(s), but your circuit uses {actual}.",
    "val.distribution_ok": "Correct distribution: {observed}.",
    "val.distribution_wrong": "The measurement distribution does not match yet. Got: {observed}. Expected: {expected}.",
    "val.reduced_qubit_missing": "The mission checks qubit {qubit}, but your circuit has only {actual} qubit(s).",
    "val.reduced_ok": "Qubit {qubit} ended in the right state for {total} combinations of input and measurement outcome.",
    "val.reduced_partial": "Correct for {ok} of {total} runs. Check the conditional corrections: each pair of measurement outcomes needs its own correction.",
    "val.reduced_wrong": "Qubit {qubit} does not end in the expected state yet (worst fidelity: {fidelity}).",
    "val.oracle_ok": "Correct result for all {total} secret oracles tested.",
    "val.oracle_partial": "Correct for {ok} of {total} secret oracles. The solution must work for any oracle, not just one specific case.",
    "val.oracle_wrong": "The measured register does not give the expected result yet. Got: {observed}. Expected: {expected}.",
    "val.cases_ok": "Correct for all {total} test inputs.",
    "val.cases_partial": "Correct for {ok} of {total} test inputs. The circuit must work for any input, including superpositions.",
    "val.variable_missing": "Define the variable `{name}` with your answer.",
    "val.variable_wrong": "The variable `{name}` is {actual}, but {expected} is expected.",
    "val.all_ok": "{first} And the answer in `{name}` is right: {value}.",
    # --- PennyLane -------------------------------------------------------------
    "pl.no_qnode": "No circuit found. Define a QNode with `@qml.qnode(dev)`.",
    "pl.missing_argument": "The variable `{name}` is not defined yet. It is needed to draw the circuit.",
    "pl.unsupported": "The operation `{name}` is not supported in the visualization yet.",
    "pl.unknown_wire": "The wire `{wire}` does not exist on the device.",
    # --- real hardware (IBM) --------------------------------------------------
    "hw.no_token": "Paste your IBM Quantum API key to run on real hardware.",
    "hw.not_installed": "Running on hardware needs the qiskit-ibm-runtime package: pip install -e \"engine[hardware]\".",
    "hw.login_failed": "IBM Quantum did not accept the API key or instance: {detail}",
    "hw.bad_circuit": "The circuit could not be prepared for hardware: {detail}",
    "hw.no_backend": "No real device with enough qubits is available to your account: {detail}",
    "hw.no_job": "Job not found: {detail}",
    "hw.timeout": "IBM Quantum did not answer within {seconds} s while {what}. Check your connection and try again; the job, if one was sent, keeps running on IBM's side.",
    "hw.public": "Running on hardware is only available when the engine runs on your own computer.",
    # --- server and content ---------------------------------------------------
    "server.bad_code": "Code is missing or too large.",
    "server.bad_request": "Invalid request: {detail}",
    "server.unknown_type": "Unknown message type: {kind}",
    "server.internal": "Something went wrong inside the engine. Try again; if it keeps happening, restart the engine.",
    "server.bad_field": "The request has an invalid `{field}`.",
    "server.unavailable": "{what} is kept in your browser on this server, not by the engine.",
    "notes.bad_key": "A note key must be \"general\" or \"lesson:<lesson id>\".",
    "notes.bad_body": "A note must be text.",
    "notes.too_long": "A note can be at most {limit} KB long.",
    "notes.image_type": "An image must be PNG, JPEG, WebP or GIF.",
    "notes.image_bad": "The image data is not valid base64.",
    "notes.image_bad_id": "Malformed image id.",
    "notes.image_too_big": "An image can be at most {limit} KB.",
    "notes.too_many_images": "A note can hold at most {limit} images.",
    "import.bad_file": "That file is not a progress backup from this platform.",
    "import.too_big": "That backup is too large to import.",
    "content.unknown_lesson": "Unknown lesson: {lesson_id}",
    "content.no_challenge": "Lesson {lesson_id} has no challenge.",
    "content.no_review": "Track {track} has no review.",
}
