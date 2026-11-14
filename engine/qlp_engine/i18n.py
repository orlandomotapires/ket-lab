"""Mensagens do motor em português, inglês e alemão.

O idioma vale por requisição: o servidor o define num ContextVar, que acompanha
a tarefa assíncrona e a thread do pool; o worker o define a cada job.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar

LANGS = ("pt", "en", "de")
DEFAULT_LANG = "en"

_current: ContextVar[str] = ContextVar("qlp_lang", default=DEFAULT_LANG)


def normalize(lang: str | None) -> str:
    """'pt-BR' -> 'pt'; idiomas não suportados caem no padrão."""
    if not lang:
        return DEFAULT_LANG
    base = str(lang).lower().replace("_", "-").split("-")[0]
    return base if base in LANGS else DEFAULT_LANG


def current() -> str:
    return _current.get()


def set_lang(lang: str | None) -> None:
    _current.set(normalize(lang))


@contextmanager
def use(lang: str | None):
    token = _current.set(normalize(lang))
    try:
        yield
    finally:
        _current.reset(token)


def t(key: str, **params) -> str:
    entry = MESSAGES[key]
    template = entry.get(current()) or entry[DEFAULT_LANG]
    return template.format(**params)


def percent(value: float, decimals: int = 1) -> str:
    text = f"{value * 100:.{decimals}f}%"
    return text if current() == "en" else text.replace(".", ",")


MESSAGES: dict[str, dict[str, str]] = {
    # --- verificação estática ------------------------------------------------
    "guard.relative_import": {
        "pt": "Imports relativos não são permitidos aqui.",
        "en": "Relative imports are not allowed here.",
        "de": "Relative Importe sind hier nicht erlaubt.",
    },
    "guard.forbidden_name": {
        "pt": "`{name}` não está disponível no laboratório.",
        "en": "`{name}` is not available in the lab.",
        "de": "`{name}` ist im Labor nicht verfügbar.",
    },
    "guard.dunder": {
        "pt": "Acesso a atributos internos (`{name}`) não é permitido no laboratório.",
        "en": "Access to internal attributes (`{name}`) is not allowed in the lab.",
        "de": "Zugriff auf interne Attribute (`{name}`) ist im Labor nicht erlaubt.",
    },
    "guard.module": {
        "pt": "O módulo `{name}` não está disponível no laboratório. Disponíveis: {allowed}.",
        "en": "The module `{name}` is not available in the lab. Available: {allowed}.",
        "de": "Das Modul `{name}` ist im Labor nicht verfügbar. Verfügbar: {allowed}.",
    },
    "guard.module_short": {
        "pt": "O módulo `{name}` não está disponível no laboratório.",
        "en": "The module `{name}` is not available in the lab.",
        "de": "Das Modul `{name}` ist im Labor nicht verfügbar.",
    },
    # --- execução ------------------------------------------------------------
    "run.syntax": {
        "pt": "Erro de sintaxe: {detail}",
        "en": "Syntax error: {detail}",
        "de": "Syntaxfehler: {detail}",
    },
    "run.memory": {
        "pt": "O código tentou usar memória demais. Reduza o tamanho do circuito ou dos dados.",
        "en": "The code tried to use too much memory. Reduce the size of the circuit or the data.",
        "de": "Der Code hat zu viel Speicher angefordert. Verkleinere den Schaltkreis oder die Daten.",
    },
    "run.recursion": {
        "pt": "Recursão infinita detectada.",
        "en": "Infinite recursion detected.",
        "de": "Endlose Rekursion erkannt.",
    },
    "run.no_circuit": {
        "pt": "Nenhum circuito encontrado. Crie um com `qc = QuantumCircuit(1)`.",
        "en": "No circuit found. Create one with `qc = QuantumCircuit(1)`.",
        "de": "Kein Schaltkreis gefunden. Erstelle einen mit `qc = QuantumCircuit(1)`.",
    },
    "run.timeout": {
        "pt": "A execução passou de {seconds} s e foi interrompida. Há algum laço infinito no código?",
        "en": "Execution took longer than {seconds} s and was stopped. Is there an infinite loop in the code?",
        "de": "Die Ausführung dauerte länger als {seconds} s und wurde abgebrochen. Gibt es eine Endlosschleife im Code?",
    },
    "run.crash": {
        "pt": "O motor de simulação foi encerrado inesperadamente (memória insuficiente?). Ele já foi reiniciado.",
        "en": "The simulation engine stopped unexpectedly (out of memory?). It has already been restarted.",
        "de": "Die Simulations-Engine wurde unerwartet beendet (zu wenig Speicher?). Sie wurde bereits neu gestartet.",
    },
    "run.engine_closed": {
        "pt": "O motor foi encerrado.",
        "en": "The engine has been shut down.",
        "de": "Die Engine wurde beendet.",
    },
    "run.engine_start": {
        "pt": "O motor de simulação não iniciou a tempo.",
        "en": "The simulation engine did not start in time.",
        "de": "Die Simulations-Engine ist nicht rechtzeitig gestartet.",
    },
    "run.internal": {
        "pt": "Erro interno do motor: {detail}",
        "en": "Internal engine error: {detail}",
        "de": "Interner Fehler der Engine: {detail}",
    },
    "run.unknown_job": {
        "pt": "Tipo de tarefa desconhecido: {kind}",
        "en": "Unknown job type: {kind}",
        "de": "Unbekannter Auftragstyp: {kind}",
    },
    # --- simulador -----------------------------------------------------------
    "sim.no_qubits": {
        "pt": "O circuito não tem qubits. Use, por exemplo, `QuantumCircuit(1)`.",
        "en": "The circuit has no qubits. Use, for example, `QuantumCircuit(1)`.",
        "de": "Der Schaltkreis hat keine Qubits. Verwende zum Beispiel `QuantumCircuit(1)`.",
    },
    "sim.too_many_qubits": {
        "pt": "O circuito tem {count} qubits; o limite aqui é {limit}. Cada qubit a mais dobra a memória necessária para simular.",
        "en": "The circuit has {count} qubits; the limit here is {limit}. Each extra qubit doubles the memory needed to simulate it.",
        "de": "Der Schaltkreis hat {count} Qubits; das Limit liegt hier bei {limit}. Jedes weitere Qubit verdoppelt den Speicherbedarf der Simulation.",
    },
    "sim.too_many_instructions": {
        "pt": "O circuito tem {count} instruções; o limite é {limit}.",
        "en": "The circuit has {count} instructions; the limit is {limit}.",
        "de": "Der Schaltkreis hat {count} Anweisungen; das Limit liegt bei {limit}.",
    },
    "sim.control_flow": {
        "pt": "O controle de fluxo `{name}` dentro do circuito ainda não é suportado. Use um laço Python comum para repetir portas.",
        "en": "In-circuit control flow `{name}` is not supported yet. Use a regular Python loop to repeat gates.",
        "de": "Kontrollfluss `{name}` innerhalb des Schaltkreises wird noch nicht unterstützt. Verwende eine normale Python-Schleife, um Gatter zu wiederholen.",
    },
    "sim.unsupported": {
        "pt": "A instrução `{name}` não é suportada pelo simulador.",
        "en": "The instruction `{name}` is not supported by the simulator.",
        "de": "Die Anweisung `{name}` wird vom Simulator nicht unterstützt.",
    },
    "sim.expr_condition": {
        "pt": "Condições com expressões clássicas ainda não são suportadas. Use `qc.if_test((bit_classico, 1))`.",
        "en": "Conditions with classical expressions are not supported yet. Use `qc.if_test((classical_bit, 1))`.",
        "de": "Bedingungen mit klassischen Ausdrücken werden noch nicht unterstützt. Verwende `qc.if_test((klassisches_bit, 1))`.",
    },
    "sim.bad_condition": {
        "pt": "Condição clássica não reconhecida em `if_test`.",
        "en": "Unrecognized classical condition in `if_test`.",
        "de": "Unbekannte klassische Bedingung in `if_test`.",
    },
    "sim.no_matrix": {
        "pt": "Não foi possível obter a matriz da porta `{name}` (parâmetros simbólicos sem valor?).",
        "en": "Could not compute the matrix of gate `{name}` (symbolic parameters without a value?).",
        "de": "Die Matrix des Gatters `{name}` konnte nicht berechnet werden (symbolische Parameter ohne Wert?).",
    },
    # --- validação -----------------------------------------------------------
    "val.unsupported": {
        "pt": "Tipo de validação `{kind}` ainda não implementado.",
        "en": "Validation type `{kind}` is not implemented yet.",
        "de": "Der Validierungstyp `{kind}` ist noch nicht implementiert.",
    },
    "val.forbidden_gate": {
        "pt": "Esta missão não permite usar {names}. Tente resolver só com as portas da lição.",
        "en": "This mission does not allow {names}. Try to solve it with the gates from the lesson.",
        "de": "Diese Aufgabe erlaubt {names} nicht. Versuche, sie mit den Gattern der Lektion zu lösen.",
    },
    "val.required_gate": {
        "pt": "A missão pede usar {names} no circuito.",
        "en": "The mission requires using {names} in the circuit.",
        "de": "Die Aufgabe verlangt, {names} im Schaltkreis zu verwenden.",
    },
    "val.forbidden_pair": {
        "pt": "Nesta missão nenhuma porta pode atuar ao mesmo tempo nos qubits {a} e {b}: eles estão longe um do outro. Ligue-os com medições e correções condicionadas aos bits clássicos.",
        "en": "In this mission no gate may act on qubits {a} and {b} at the same time: they are far apart. Connect them with measurements and corrections conditioned on classical bits.",
        "de": "In dieser Aufgabe darf kein Gatter gleichzeitig auf die Qubits {a} und {b} wirken: Sie sind weit voneinander entfernt. Verbinde sie über Messungen und Korrekturen, die von klassischen Bits abhängen.",
    },
    "val.too_many_gates": {
        "pt": "A missão pede no máximo {limit} porta(s); seu circuito usa {count}.",
        "en": "The mission allows at most {limit} gate(s); your circuit uses {count}.",
        "de": "Die Aufgabe erlaubt höchstens {limit} Gatter; dein Schaltkreis verwendet {count}.",
    },
    "val.qubit_count": {
        "pt": "A missão usa {expected} qubit(s), mas seu circuito tem {actual}.",
        "en": "The mission uses {expected} qubit(s), but your circuit has {actual}.",
        "de": "Die Aufgabe verwendet {expected} Qubit(s), dein Schaltkreis hat aber {actual}.",
    },
    "val.state_ok": {
        "pt": "Estado alvo atingido com fidelidade de {fidelity}.",
        "en": "Target state reached with a fidelity of {fidelity}.",
        "de": "Zielzustand mit einer Fidelity von {fidelity} erreicht.",
    },
    "val.phase": {
        "pt": "As probabilidades de medir cada estado estão corretas, mas a fase relativa entre eles está incorreta. Verifique as rotações no eixo Z e o ângulo do vetor em torno do equador da Esfera de Bloch.",
        "en": "The probability of measuring each state is right, but the relative phase between them is wrong. Check the rotations about the Z axis and the angle of the vector around the equator of the Bloch sphere.",
        "de": "Die Wahrscheinlichkeiten der einzelnen Messergebnisse stimmen, aber die relative Phase zwischen ihnen ist falsch. Prüfe die Rotationen um die Z-Achse und den Winkel des Vektors am Äquator der Bloch-Kugel.",
    },
    "val.state_wrong": {
        "pt": "Ainda não: a fidelidade com o estado alvo é de {fidelity}.",
        "en": "Not yet: the fidelity with the target state is {fidelity}.",
        "de": "Noch nicht: Die Fidelity mit dem Zielzustand beträgt {fidelity}.",
    },
    "val.no_measurement": {
        "pt": "Falta medir: sem medição o circuito não produz nenhum resultado clássico. Meça o qubit e guarde o resultado em um bit clássico.",
        "en": "A measurement is missing: without one, the circuit produces no classical result. Measure the qubit and store the result in a classical bit.",
        "de": "Es fehlt eine Messung: Ohne sie liefert der Schaltkreis kein klassisches Ergebnis. Miss das Qubit und speichere das Ergebnis in einem klassischen Bit.",
    },
    "val.clbit_count": {
        "pt": "A missão registra o resultado em {expected} bit(s) clássico(s), mas seu circuito usa {actual}.",
        "en": "The mission stores the result in {expected} classical bit(s), but your circuit uses {actual}.",
        "de": "Die Aufgabe speichert das Ergebnis in {expected} klassischen Bit(s), dein Schaltkreis verwendet aber {actual}.",
    },
    "val.distribution_ok": {
        "pt": "Distribuição correta: {observed}.",
        "en": "Correct distribution: {observed}.",
        "de": "Verteilung korrekt: {observed}.",
    },
    "val.distribution_wrong": {
        "pt": "A distribuição das medições ainda não bate. Obtido: {observed}. Esperado: {expected}.",
        "en": "The distribution of measurements does not match yet. Got: {observed}. Expected: {expected}.",
        "de": "Die Verteilung der Messergebnisse stimmt noch nicht. Erhalten: {observed}. Erwartet: {expected}.",
    },
    "val.reduced_qubit_missing": {
        "pt": "A missão avalia o qubit {qubit}, mas seu circuito tem só {actual} qubit(s).",
        "en": "The mission checks qubit {qubit}, but your circuit has only {actual} qubit(s).",
        "de": "Die Aufgabe prüft Qubit {qubit}, dein Schaltkreis hat aber nur {actual} Qubit(s).",
    },
    "val.reduced_ok": {
        "pt": "O qubit {qubit} terminou no estado certo para {total} combinações de entrada e resultado de medição.",
        "en": "Qubit {qubit} ended in the right state for {total} combinations of input and measurement outcome.",
        "de": "Qubit {qubit} endete für {total} Kombinationen aus Eingabe und Messergebnis im richtigen Zustand.",
    },
    "val.reduced_partial": {
        "pt": "Funciona para alguns resultados da medição, mas não para todos ({ok} de {total} execuções). Confira as correções condicionais: cada resultado medido pede uma correção diferente.",
        "en": "It works for some measurement outcomes but not all ({ok} of {total} runs). Check the conditional corrections: each measured outcome needs a different correction.",
        "de": "Es funktioniert für einige Messergebnisse, aber nicht für alle ({ok} von {total} Durchläufen). Prüfe die bedingten Korrekturen: Jedes Messergebnis braucht eine andere Korrektur.",
    },
    "val.reduced_wrong": {
        "pt": "O qubit {qubit} ainda não termina no estado esperado (pior fidelidade: {fidelity}).",
        "en": "Qubit {qubit} does not end in the expected state yet (worst fidelity: {fidelity}).",
        "de": "Qubit {qubit} endet noch nicht im erwarteten Zustand (schlechteste Fidelity: {fidelity}).",
    },
    "val.oracle_ok": {
        "pt": "Resultado correto para todos os {total} oráculos secretos testados.",
        "en": "Correct result for all {total} secret oracles tested.",
        "de": "Korrektes Ergebnis für alle {total} getesteten geheimen Orakel.",
    },
    "val.oracle_partial": {
        "pt": "Correto para {ok} de {total} oráculos secretos. A solução precisa funcionar para qualquer oráculo, não só para um caso específico.",
        "en": "Correct for {ok} of {total} secret oracles. The solution must work for any oracle, not just one specific case.",
        "de": "Korrekt für {ok} von {total} geheimen Orakeln. Die Lösung muss für jedes Orakel funktionieren, nicht nur für einen bestimmten Fall.",
    },
    "val.oracle_wrong": {
        "pt": "O registrador medido ainda não dá o resultado esperado. Obtido: {observed}. Esperado: {expected}.",
        "en": "The measured register does not give the expected result yet. Got: {observed}. Expected: {expected}.",
        "de": "Das gemessene Register liefert noch nicht das erwartete Ergebnis. Erhalten: {observed}. Erwartet: {expected}.",
    },
    "val.cases_ok": {
        "pt": "Correto para todas as {total} entradas de teste.",
        "en": "Correct for all {total} test inputs.",
        "de": "Korrekt für alle {total} Testeingaben.",
    },
    "val.cases_partial": {
        "pt": "Correto para {ok} de {total} entradas de teste. O circuito precisa funcionar para qualquer entrada, inclusive superposições.",
        "en": "Correct for {ok} of {total} test inputs. The circuit must work for any input, including superpositions.",
        "de": "Korrekt für {ok} von {total} Testeingaben. Der Schaltkreis muss für jede Eingabe funktionieren, auch für Superpositionen.",
    },
    "val.variable_missing": {
        "pt": "Defina a variável `{name}` com a resposta.",
        "en": "Define the variable `{name}` with your answer.",
        "de": "Lege die Variable `{name}` mit deiner Antwort an.",
    },
    "val.variable_wrong": {
        "pt": "A variável `{name}` vale {actual}, mas o esperado é {expected}.",
        "en": "The variable `{name}` is {actual}, but {expected} is expected.",
        "de": "Die Variable `{name}` hat den Wert {actual}, erwartet wird aber {expected}.",
    },
    "val.all_ok": {
        "pt": "{first} E a resposta em `{name}` está certa: {value}.",
        "en": "{first} And the answer in `{name}` is right: {value}.",
        "de": "{first} Und die Antwort in `{name}` stimmt: {value}.",
    },
    # --- servidor e conteúdo ---------------------------------------------------
    "server.bad_code": {
        "pt": "Código ausente ou grande demais.",
        "en": "Code is missing or too large.",
        "de": "Der Code fehlt oder ist zu groß.",
    },
    "server.bad_request": {
        "pt": "Requisição inválida: {detail}",
        "en": "Invalid request: {detail}",
        "de": "Ungültige Anfrage: {detail}",
    },
    "server.unknown_type": {
        "pt": "Tipo de mensagem desconhecido: {kind}",
        "en": "Unknown message type: {kind}",
        "de": "Unbekannter Nachrichtentyp: {kind}",
    },
    "content.unknown_lesson": {
        "pt": "Lição desconhecida: {lesson_id}",
        "en": "Unknown lesson: {lesson_id}",
        "de": "Unbekannte Lektion: {lesson_id}",
    },
}
