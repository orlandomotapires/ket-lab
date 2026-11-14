"""Mensagens do motor (em inglês, o idioma da plataforma)."""

from __future__ import annotations


def t(key: str, **params) -> str:
    return MESSAGES[key].format(**params)


def percent(value: float, decimals: int = 1) -> str:
    return f"{value * 100:.{decimals}f}%"


MESSAGES: dict[str, str] = {
    # --- verificação estática ------------------------------------------------
    "guard.relative_import": "Relative imports are not allowed here.",
    "guard.forbidden_name": "`{name}` is not available in the lab.",
    "guard.dunder": "Access to internal attributes (`{name}`) is not allowed in the lab.",
    "guard.module": "The module `{name}` is not available in the lab. Available: {allowed}.",
    "guard.module_short": "The module `{name}` is not available in the lab.",
    # --- execução ------------------------------------------------------------
    "run.syntax": "Syntax error: {detail}",
    "run.memory": "The code tried to use too much memory. Reduce the size of the circuit or the data.",
    "run.recursion": "Infinite recursion detected.",
    "run.no_circuit": "No circuit found. Create one with `qc = QuantumCircuit(1)`.",
    "run.cancelled": "Execution stopped.",
    "export.unsupported": "This circuit cannot be exported to {format}: {detail}",
    "export.noise": "Noise channels (density matrix) do not exist in OpenQASM. Export the circuit without noise.",
    "run.timeout": "Execution took longer than {seconds} s and was stopped. Is there an infinite loop in the code?",
    "run.crash": "The simulation engine stopped unexpectedly (out of memory?). It has already been restarted.",
    "run.engine_closed": "The engine has been shut down.",
    "run.engine_start": "The simulation engine did not start in time.",
    "run.internal": "Internal engine error: {detail}",
    "run.unknown_job": "Unknown job type: {kind}",
    # --- simulador -----------------------------------------------------------
    "sim.no_qubits": "The circuit has no qubits. Use, for example, `QuantumCircuit(1)`.",
    "sim.too_many_qubits": "The circuit has {count} qubits; the limit here is {limit}. Each extra qubit doubles the memory needed to simulate it.",
    "sim.too_many_instructions": "The circuit has {count} instructions; the limit is {limit}.",
    "sim.control_flow": "In-circuit control flow `{name}` is not supported yet. Use a regular Python loop to repeat gates.",
    "sim.unsupported": "The instruction `{name}` is not supported by the simulator.",
    "sim.expr_condition": "Conditions with classical expressions are not supported yet. Use `qc.if_test((classical_bit, 1))`.",
    "sim.bad_condition": "Unrecognized classical condition in `if_test`.",
    "sim.no_matrix": "Could not compute the matrix of gate `{name}` (symbolic parameters without a value?).",
    # --- validação -----------------------------------------------------------
    "val.unsupported": "Validation type `{kind}` is not implemented yet.",
    "val.forbidden_gate": "This mission does not allow {names}. Try to solve it with the gates from the lesson.",
    "val.required_gate": "The mission requires using {names} in the circuit.",
    "val.gate_count": "The mission allows exactly {expected} call(s) to `{name}`, and your circuit has {actual}.",
    "val.forbidden_pair": "In this mission no gate may act on qubits {a} and {b} at the same time: they are far apart. Connect them with measurements and corrections conditioned on classical bits.",
    "val.too_many_gates": "The mission allows at most {limit} gate(s); your circuit uses {count}.",
    "val.qubit_count": "The mission uses {expected} qubit(s), but your circuit has {actual}.",
    "val.state_ok": "Target state reached with a fidelity of {fidelity}.",
    "val.phase": "The probability of measuring each state is right, but the relative phase between them is wrong. Check the rotations about the Z axis and the angle of the vector around the equator of the Bloch sphere.",
    "val.state_wrong": "Not yet: the fidelity with the target state is {fidelity}.",
    "val.no_measurement": "A measurement is missing: without one, the circuit produces no classical result. Measure the qubit and store the result in a classical bit.",
    "val.clbit_count": "The mission stores the result in {expected} classical bit(s), but your circuit uses {actual}.",
    "val.distribution_ok": "Correct distribution: {observed}.",
    "val.distribution_wrong": "The distribution of measurements does not match yet. Got: {observed}. Expected: {expected}.",
    "val.reduced_qubit_missing": "The mission checks qubit {qubit}, but your circuit has only {actual} qubit(s).",
    "val.reduced_ok": "Qubit {qubit} ended in the right state for {total} combinations of input and measurement outcome.",
    "val.reduced_partial": "It works for some measurement outcomes but not all ({ok} of {total} runs). Check the conditional corrections: each measured outcome needs a different correction.",
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
    "pl.missing_argument": "The variable `{name}` does not exist yet: it is used to draw the circuit.",
    "pl.unsupported": "The operation `{name}` is not supported in the visualization yet.",
    "pl.unknown_wire": "The wire `{wire}` does not exist on the device.",
    # --- servidor e conteúdo ---------------------------------------------------
    "server.bad_code": "Code is missing or too large.",
    "server.bad_request": "Invalid request: {detail}",
    "server.unknown_type": "Unknown message type: {kind}",
    "content.unknown_lesson": "Unknown lesson: {lesson_id}",
}
