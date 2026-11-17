import { t } from "../strings";
import { sandboxCode } from "../state/store";

/** Starting points for the free lab. */
export const SANDBOX_EXAMPLES = ["bell", "training"] as const;
export type SandboxExample = (typeof SANDBOX_EXAMPLES)[number];

export function exampleCode(example: SandboxExample): string {
  if (example === "bell") return sandboxCode();
  return `import pennylane as qml
from pennylane import numpy as np

${t("lab.exampleTrainingCode")}
dev = qml.device("default.qubit", wires=2)


@qml.qnode(dev)
def circuit(params):
    qml.RY(params[0], wires=0)
    qml.RY(params[1], wires=1)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(1))


params = np.array([0.6, 0.4], requires_grad=True)
opt = qml.GradientDescentOptimizer(stepsize=0.2)

for epoch in range(80):
    params, cost = opt.step_and_cost(circuit, params)
    report(cost)
`;
}
